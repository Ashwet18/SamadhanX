"""
Challenge AI analysis service.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.challenge import (
    Challenge,
    ChallengeAIAnalysis,
    ChallengeEmbedding,
    ChallengeDuplicate
)
from app.models.enums import ChallengeStatus, PriorityLevel, DuplicateStatus
from app.models.platform import AuditLog
from app.services.ai.provider import get_ai_provider
from app.services.ai.duplicate_detector import DuplicateDetector
from app.services.ai.prompts import build_embedding_text
from app.services.ai.schemas import AIAnalysisResult, DuplicateCandidate


class ChallengeAIService:
    """Service for AI-powered challenge analysis."""
    
    def __init__(self, db: Session):
        """
        Initialize AI service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.provider = get_ai_provider()
        self.duplicate_detector = DuplicateDetector(db)
    
    def analyze(self, challenge_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Run complete AI analysis pipeline for a challenge.
        
        Pipeline:
        1. Load challenge
        2. Call AI provider for analysis
        3. Calculate deterministic priority
        4. Generate embedding
        5. Search for duplicates
        6. Store all results in transaction
        7. Update challenge status
        8. Create audit logs
        
        Args:
            challenge_id: Challenge ID to analyze
            user_id: User ID triggering analysis
            
        Returns:
            Analysis results including duplicates
            
        Raises:
            ValueError: If challenge not found or invalid state
            RuntimeError: If AI analysis fails
        """
        
        # Create audit log for analysis start
        self._create_audit_log(
            challenge_id=challenge_id,
            user_id=user_id,
            action="CHALLENGE_AI_ANALYSIS_STARTED",
            details={"status": "started"}
        )
        
        try:
            # Load challenge
            challenge = self._load_challenge(challenge_id)
            
            # Get category names
            category_names = [cc.category.name for cc in challenge.categories]
            
            # Call AI provider
            ai_result = self.provider.analyze_challenge(
                title=challenge.title,
                description=challenge.description,
                district=challenge.district or "Unknown",
                categories=category_names
            )
            
            # Calculate deterministic priority
            priority_data = self._calculate_priority(
                severity_score=ai_result.severity.severity_score,
                urgency_score=ai_result.urgency.urgency_score,
                affected_population=challenge.affected_population or ai_result.affected_population_estimate
            )
            
            # Generate embedding
            embedding_text = build_embedding_text(
                title=challenge.title,
                description=challenge.description,
                summary=ai_result.summary,
                primary_domain=ai_result.classification.primary_domain
            )
            embedding_vector = self.provider.generate_embedding(embedding_text)
            
            # Verify embedding dimension
            expected_dim = self.provider.get_embedding_dimension()
            if len(embedding_vector) != expected_dim:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {expected_dim}, got {len(embedding_vector)}"
                )
            
            # Search for duplicates
            duplicate_candidates = self.duplicate_detector.find_duplicates(
                embedding=embedding_vector,
                challenge_id=challenge_id,
                threshold=DuplicateDetector.POSSIBLE_DUPLICATE_THRESHOLD,
                limit=5
            )
            
            # Store results in transaction
            self._store_analysis_results(
                challenge=challenge,
                ai_result=ai_result,
                priority_data=priority_data,
                embedding_vector=embedding_vector,
                duplicate_candidates=duplicate_candidates
            )
            
            # Create audit log for success
            self._create_audit_log(
                challenge_id=challenge_id,
                user_id=user_id,
                action="CHALLENGE_AI_ANALYSIS_COMPLETED",
                details={
                    "status": "completed",
                    "priority_level": priority_data["level"].value,
                    "duplicates_found": len(duplicate_candidates)
                }
            )
            
            # Return results
            return {
                "challenge_id": str(challenge_id),
                "challenge_code": challenge.challenge_code,
                "status": challenge.status.value,
                "priority": {
                    "score": priority_data["score"],
                    "level": priority_data["level"].value,
                    "formula": priority_data["formula"]
                },
                "ai_analysis": {
                    "summary": ai_result.summary,
                    "detected_language": ai_result.detected_language,
                    "primary_domain": ai_result.classification.primary_domain,
                    "secondary_domains": ai_result.classification.secondary_domains,
                    "severity_score": ai_result.severity.severity_score,
                    "severity_reason": ai_result.severity.severity_reason,
                    "urgency_score": ai_result.urgency.urgency_score,
                    "urgency_reason": ai_result.urgency.urgency_reason,
                    "skills": [{"name": s.name, "confidence": s.confidence} for s in ai_result.skills],
                    "solution_types": [{"type": s.type, "confidence": s.confidence} for s in ai_result.solution_types],
                    "confidence_score": ai_result.confidence_score
                },
                "duplicate_candidates": [
                    {
                        "challenge_id": d.challenge_id,
                        "challenge_code": d.challenge_code,
                        "title": d.title,
                        "similarity_score": d.similarity_score,
                        "classification": self.duplicate_detector.classify_similarity(d.similarity_score)
                    }
                    for d in duplicate_candidates
                ]
            }
            
        except Exception as e:
            # Create audit log for failure
            self._create_audit_log(
                challenge_id=challenge_id,
                user_id=user_id,
                action="CHALLENGE_AI_ANALYSIS_FAILED",
                details={
                    "status": "failed",
                    "error": str(e)
                }
            )
            
            # Re-raise exception
            raise RuntimeError(f"AI analysis failed: {e}")
    
    def _load_challenge(self, challenge_id: UUID) -> Challenge:
        """Load challenge from database."""
        
        challenge = self.db.query(Challenge).filter(Challenge.id == challenge_id).first()
        
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        return challenge
    
    def _calculate_priority(
        self,
        severity_score: int,
        urgency_score: int,
        affected_population: Optional[int]
    ) -> Dict[str, Any]:
        """
        Calculate deterministic priority score.
        
        Formula:
        - Base: (severity * 0.4) + (urgency * 0.4)
        - Population bonus: min(20, log10(population) * 4) if population > 0
        - Final: 0-100 scale
        
        Mapping:
        - 0-29: LOW
        - 30-59: MEDIUM
        - 60-79: HIGH
        - 80-100: CRITICAL
        
        Args:
            severity_score: Severity (0-100)
            urgency_score: Urgency (0-100)
            affected_population: Population affected
            
        Returns:
            Priority data with score, level, and formula explanation
        """
        
        # Base calculation (80% weight)
        base_score = (severity_score * 0.4) + (urgency_score * 0.4)
        
        # Population bonus (20% weight, capped)
        population_bonus = 0
        if affected_population and affected_population > 0:
            import math
            # Logarithmic scale: 10 people = 4, 100 = 8, 1000 = 12, 10000 = 16, 100000 = 20
            population_bonus = min(20, math.log10(affected_population) * 4)
        
        # Final score
        priority_score = base_score + population_bonus
        priority_score = max(0, min(100, priority_score))  # Clamp to 0-100
        
        # Map to priority level
        if priority_score >= 80:
            priority_level = PriorityLevel.CRITICAL
        elif priority_score >= 60:
            priority_level = PriorityLevel.HIGH
        elif priority_score >= 30:
            priority_level = PriorityLevel.MEDIUM
        else:
            priority_level = PriorityLevel.LOW
        
        # Formula explanation
        formula = f"Priority = (Severity×0.4) + (Urgency×0.4) + Population_Bonus"
        if affected_population:
            formula += f" = ({severity_score}×0.4) + ({urgency_score}×0.4) + {population_bonus:.1f} = {priority_score:.1f}"
        else:
            formula += f" = ({severity_score}×0.4) + ({urgency_score}×0.4) + 0 = {priority_score:.1f}"
        
        return {
            "score": round(priority_score, 2),
            "level": priority_level,
            "formula": formula
        }
    
    def _store_analysis_results(
        self,
        challenge: Challenge,
        ai_result: AIAnalysisResult,
        priority_data: Dict[str, Any],
        embedding_vector: List[float],
        duplicate_candidates: List[DuplicateCandidate]
    ):
        """Store AI analysis results in database."""
        
        try:
            # Delete existing AI analysis if exists (for retry scenarios)
            existing_analysis = self.db.query(ChallengeAIAnalysis).filter(
                ChallengeAIAnalysis.challenge_id == challenge.id
            ).first()
            if existing_analysis:
                self.db.delete(existing_analysis)
            
            # Create AI analysis record
            ai_analysis = ChallengeAIAnalysis(
                challenge_id=challenge.id,
                model_name=self.provider.model if hasattr(self.provider, 'model') else 'mock',
                model_version='1.0',
                summary=ai_result.summary,
                primary_domain=ai_result.classification.primary_domain,
                severity_score=float(ai_result.severity.severity_score),
                urgency_score=float(ai_result.urgency.urgency_score),
                affected_population_estimate=ai_result.affected_population_estimate,
                extracted_skills=[
                    {"name": s.name, "confidence": s.confidence}
                    for s in ai_result.skills
                ],
                recommended_solution_types=[
                    {"type": s.type, "confidence": s.confidence}
                    for s in ai_result.solution_types
                ],
                confidence_score=ai_result.confidence_score
            )
            self.db.add(ai_analysis)
            
            # Store embedding
            # Delete existing embeddings if any
            self.db.query(ChallengeEmbedding).filter(
                ChallengeEmbedding.challenge_id == challenge.id
            ).delete()
            
            embedding = ChallengeEmbedding(
                challenge_id=challenge.id,
                embedding=embedding_vector,
                model_name=self.provider.embedding_model if hasattr(self.provider, 'embedding_model') else 'mock'
            )
            self.db.add(embedding)
            
            # Store duplicate candidates
            # Delete existing duplicates for this challenge
            self.db.query(ChallengeDuplicate).filter(
                ChallengeDuplicate.challenge_id == challenge.id
            ).delete()
            
            for candidate in duplicate_candidates:
                # Ensure no self-duplicates and normalized ordering
                if str(challenge.id) != candidate.challenge_id:
                    duplicate = ChallengeDuplicate(
                        challenge_id=challenge.id,
                        similar_challenge_id=UUID(candidate.challenge_id),
                        similarity_score=candidate.similarity_score,
                        status=DuplicateStatus.PENDING_REVIEW
                    )
                    self.db.add(duplicate)
            
            # Update challenge priority and status
            challenge.priority_score = priority_data["score"]
            challenge.priority_level = priority_data["level"]
            challenge.status = ChallengeStatus.PENDING_REVIEW
            
            # Commit transaction
            self.db.commit()
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to store analysis results: {e}")
    
    def _create_audit_log(
        self,
        challenge_id: UUID,
        user_id: UUID,
        action: str,
        details: Dict[str, Any]
    ):
        """Create audit log entry."""
        
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type="CHALLENGE",
                entity_id=challenge_id,
                new_value=details
            )
            self.db.add(audit_log)
            self.db.commit()
        except Exception:
            # Don't fail the whole operation if audit logging fails
            self.db.rollback()
