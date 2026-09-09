"""
University matching engine for challenge assignments.
"""

from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.challenge import Challenge, ChallengeAIAnalysis, ChallengeAssignment
from app.models.university import University, UniversityExpertise, Expertise
from app.models.enums import ChallengeStatus, AssignmentStatus
from app.models.platform import AuditLog
from app.services.matching.config import MatchingConfig, DEFAULT_MATCHING_CONFIG
from app.services.matching.scorer import UniversityScorer
from app.services.matching.schemas import (
    MatchingResult,
    UniversityMatch,
    ComponentScores,
    MatchingEvidence,
    ExpertiseMatch,
    FacultyMatch,
    FacilityMatch,
    IndustryConnection
)


class UniversityMatchingEngine:
    """Engine for matching challenges to universities."""
    
    def __init__(self, db: Session, config: MatchingConfig = None):
        """
        Initialize matching engine.
        
        Args:
            db: Database session
            config: Matching configuration (uses default if not provided)
        """
        self.db = db
        self.config = config or DEFAULT_MATCHING_CONFIG
        self.scorer = UniversityScorer(db, self.config)
        
        # Validate config
        if not self.config.weights.validate_sum():
            raise ValueError("Matching weights must sum to 1.0")
    
    def match_challenge(self, challenge_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Match a validated challenge to suitable universities.
        
        Args:
            challenge_id: Challenge ID to match
            user_id: User ID triggering the match
            
        Returns:
            Matching results dictionary
            
        Raises:
            ValueError: If challenge is not in valid state
            RuntimeError: If matching fails
        """
        
        # Create audit log
        self._create_audit_log(
            challenge_id=challenge_id,
            user_id=user_id,
            action="MATCHING_STARTED",
            details={"status": "started"}
        )
        
        try:
            # Load and validate challenge
            challenge = self._load_and_validate_challenge(challenge_id)
            
            # Load AI analysis
            ai_analysis = challenge.ai_analysis
            if not ai_analysis:
                raise ValueError(
                    f"Challenge {challenge_id} has no AI analysis. "
                    "Run AI analysis before matching."
                )
            
            # Extract requirements
            required_skills = ai_analysis.extracted_skills or []
            primary_domain = ai_analysis.primary_domain or "Unknown"
            
            # Get candidate universities
            candidates = self._get_candidate_universities(required_skills)
            
            if not candidates:
                # No candidates found
                self._create_audit_log(
                    challenge_id=challenge_id,
                    user_id=user_id,
                    action="MATCHING_COMPLETED",
                    details={
                        "status": "completed",
                        "candidates_found": 0,
                        "note": "No suitable universities found"
                    }
                )
                
                return {
                    "challenge_id": str(challenge_id),
                    "challenge_code": challenge.challenge_code,
                    "required_expertise": [s["name"] for s in required_skills],
                    "primary_domain": primary_domain,
                    "matching_status": "completed",
                    "ranked_universities": [],
                    "total_candidates": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Score each candidate
            scored_universities = []
            for university in candidates:
                match_result = self._score_university(
                    university=university,
                    challenge=challenge,
                    required_skills=required_skills,
                    primary_domain=primary_domain
                )
                scored_universities.append(match_result)
            
            # Rank universities by score
            scored_universities.sort(key=lambda x: x["score"], reverse=True)
            
            # Limit results
            top_universities = scored_universities[:self.config.max_recommendations]
            
            # Store recommendations
            self._store_recommendations(
                challenge=challenge,
                universities=top_universities,
                user_id=user_id
            )
            
            # Create audit log
            self._create_audit_log(
                challenge_id=challenge_id,
                user_id=user_id,
                action="MATCHING_COMPLETED",
                details={
                    "status": "completed",
                    "candidates_evaluated": len(scored_universities),
                    "recommendations_stored": len(top_universities)
                }
            )
            
            # Build response
            return {
                "challenge_id": str(challenge_id),
                "challenge_code": challenge.challenge_code,
                "required_expertise": [s["name"] for s in required_skills],
                "primary_domain": primary_domain,
                "matching_status": "completed",
                "ranked_universities": top_universities,
                "total_candidates": len(scored_universities),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Create audit log for failure
            self._create_audit_log(
                challenge_id=challenge_id,
                user_id=user_id,
                action="MATCHING_FAILED",
                details={
                    "status": "failed",
                    "error": str(e)
                }
            )
            
            raise RuntimeError(f"Matching failed: {e}")
    
    def _load_and_validate_challenge(self, challenge_id: UUID) -> Challenge:
        """Load and validate challenge status."""
        
        challenge = self.db.query(Challenge).filter(
            Challenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        # Check status
        if challenge.status != ChallengeStatus.VALIDATED:
            raise ValueError(
                f"Challenge must be VALIDATED before matching. "
                f"Current status: {challenge.status.value}"
            )
        
        return challenge
    
    def _get_candidate_universities(
        self,
        required_skills: List[Dict[str, Any]]
    ) -> List[University]:
        """
        Get candidate universities for matching.
        
        Args:
            required_skills: Required skills from AI analysis
            
        Returns:
            List of candidate universities
        """
        if not required_skills:
            # No skills specified - return all verified universities
            return self.db.query(University).filter(
                University.verification_status == "VERIFIED"
            ).all()
        
        # Get expertise IDs for required skills
        skill_names = [s["name"] for s in required_skills]
        expertise_records = self.db.query(Expertise).filter(
            Expertise.name.in_(skill_names)
        ).all()
        expertise_ids = [e.id for e in expertise_records]
        
        if not expertise_ids:
            # No matching expertise found - return all universities
            return self.db.query(University).all()
        
        # Get universities with relevant expertise
        universities = self.db.query(University).join(UniversityExpertise).filter(
            UniversityExpertise.expertise_id.in_(expertise_ids),
            UniversityExpertise.proficiency_score >= self.config.min_expertise_match
        ).distinct().all()
        
        # Also include universities without explicit expertise match
        # to avoid overly aggressive filtering
        all_universities = self.db.query(University).all()
        
        # Combine and deduplicate
        candidate_ids = set([u.id for u in universities])
        for u in all_universities:
            candidate_ids.add(u.id)
        
        return [u for u in all_universities if u.id in candidate_ids]
    
    def _score_university(
        self,
        university: University,
        challenge: Challenge,
        required_skills: List[Dict[str, Any]],
        primary_domain: str
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a university.
        
        Args:
            university: University to score
            challenge: Challenge being matched
            required_skills: Required skills
            primary_domain: Primary challenge domain
            
        Returns:
            Scoring dictionary with all components
        """
        
        # Score each component
        expertise_score, expertise_evidence = self.scorer.score_expertise(
            university, required_skills
        )
        
        faculty_score, faculty_evidence = self.scorer.score_faculty(
            university, required_skills
        )
        
        infrastructure_score, infrastructure_evidence = self.scorer.score_infrastructure(
            university, required_skills
        )
        
        location_score, location_reason = self.scorer.score_location(
            university, challenge.district, challenge.state or "Jharkhand"
        )
        
        industry_score, industry_evidence = self.scorer.score_industry_connections(
            university, required_skills
        )
        
        projects_score, projects_note = self.scorer.score_previous_projects(
            university, primary_domain
        )
        
        # Calculate weighted final score
        weights = self.config.weights
        final_score = (
            expertise_score * weights.expertise +
            faculty_score * weights.faculty +
            infrastructure_score * weights.infrastructure +
            projects_score * weights.previous_projects +
            location_score * weights.location +
            industry_score * weights.industry
        )
        
        # Round to 2 decimal places
        final_score = round(final_score, 2)
        
        # Generate explanation
        reason = self._generate_explanation(
            university_name=university.name,
            final_score=final_score,
            expertise_score=expertise_score,
            faculty_score=faculty_score,
            infrastructure_score=infrastructure_score,
            location_reason=location_reason,
            has_industry=len(industry_evidence) > 0
        )
        
        return {
            "university_id": str(university.id),
            "university_name": university.name,
            "university_code": university.code,
            "score": final_score,
            "components": {
                "expertise": round(expertise_score, 2),
                "faculty": round(faculty_score, 2),
                "infrastructure": round(infrastructure_score, 2),
                "previous_projects": round(projects_score, 2),
                "location": round(location_score, 2),
                "industry": round(industry_score, 2)
            },
            "evidence": {
                "matched_expertise": expertise_evidence,
                "matched_faculty": faculty_evidence,
                "matched_facilities": infrastructure_evidence,
                "industry_connections": industry_evidence,
                "location_reason": location_reason,
                "previous_projects_note": projects_note
            },
            "reason": reason
        }
    
    def _generate_explanation(
        self,
        university_name: str,
        final_score: float,
        expertise_score: float,
        faculty_score: float,
        infrastructure_score: float,
        location_reason: str,
        has_industry: bool
    ) -> str:
        """Generate human-readable explanation."""
        
        strengths = []
        
        if expertise_score >= 80:
            strengths.append("strong expertise match")
        elif expertise_score >= 60:
            strengths.append("good expertise capabilities")
        
        if faculty_score >= 80:
            strengths.append("available qualified faculty")
        elif faculty_score >= 60:
            strengths.append("relevant faculty resources")
        
        if infrastructure_score >= 70:
            strengths.append("relevant laboratory infrastructure")
        
        if "same district" in location_reason.lower():
            strengths.append("local presence")
        elif "same state" in location_reason.lower():
            strengths.append("in-state location")
        
        if has_industry:
            strengths.append("industry collaboration capability")
        
        if not strengths:
            strengths.append("partial capability match")
        
        explanation = (
            f"{university_name} scored {final_score}/100. "
            f"Key factors: {', '.join(strengths)}. "
            f"Location: {location_reason}."
        )
        
        return explanation
    
    def _store_recommendations(
        self,
        challenge: Challenge,
        universities: List[Dict[str, Any]],
        user_id: UUID
    ):
        """
        Store university recommendations in database.
        
        Args:
            challenge: Challenge being matched
            universities: Scored universities
            user_id: User triggering match
        """
        
        try:
            for rank, univ_data in enumerate(universities, start=1):
                university_id = UUID(univ_data["university_id"])
                
                # Check if assignment already exists
                existing = self.db.query(ChallengeAssignment).filter(
                    ChallengeAssignment.challenge_id == challenge.id,
                    ChallengeAssignment.university_id == university_id
                ).first()
                
                if existing:
                    # Update only if status is RECOMMENDED
                    # Protect INVITED, ACCEPTED, DECLINED
                    if existing.status == AssignmentStatus.RECOMMENDED:
                        existing.assignment_score = int(univ_data["score"])
                        existing.reason = univ_data["reason"]
                        existing.assigned_by = user_id
                else:
                    # Create new assignment
                    assignment = ChallengeAssignment(
                        challenge_id=challenge.id,
                        university_id=university_id,
                        assignment_score=int(univ_data["score"]),
                        reason=univ_data["reason"],
                        status=AssignmentStatus.RECOMMENDED,
                        assigned_by=user_id
                    )
                    self.db.add(assignment)
            
            self.db.commit()
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to store recommendations: {e}")
    
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
