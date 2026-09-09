"""
Industry matching engine for projects.

Deterministic, explainable matching algorithm that recommends
suitable industry partners for projects based on multiple factors.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from app.models.project import Project
from app.models.challenge import Challenge
from app.models.industry import IndustryPartner, IndustryExpertise, IndustryMatch
from app.models.partnership import Partnership
from app.models.university import Faculty, Expertise
from app.models.enums import PartnershipStatus, AvailabilityStatus, VerificationStatus, ProjectStatus


class IndustryMatchingConfig:
    """Configurable weights for industry matching scoring."""
    
    # Default weights (must sum to 1.0)
    EXPERTISE_WEIGHT = 0.40
    DOMAIN_FIT_WEIGHT = 0.20
    TECHNICAL_CAPABILITY_WEIGHT = 0.15
    RESOURCES_WEIGHT = 0.10
    GEOGRAPHIC_WEIGHT = 0.05
    PARTNERSHIP_HISTORY_WEIGHT = 0.05
    AVAILABILITY_WEIGHT = 0.05
    
    # Minimum score threshold for recommendations
    MIN_RECOMMENDATION_SCORE = 50.0
    
    # Maximum number of recommendations
    MAX_RECOMMENDATIONS = 10
    
    @classmethod
    def get_weights(cls) -> Dict[str, float]:
        """Get all weights as a dictionary."""
        return {
            "expertise": cls.EXPERTISE_WEIGHT,
            "domain_fit": cls.DOMAIN_FIT_WEIGHT,
            "technical_capability": cls.TECHNICAL_CAPABILITY_WEIGHT,
            "resources": cls.RESOURCES_WEIGHT,
            "geographic": cls.GEOGRAPHIC_WEIGHT,
            "partnership_history": cls.PARTNERSHIP_HISTORY_WEIGHT,
            "availability": cls.AVAILABILITY_WEIGHT
        }
    
    @classmethod
    def validate_weights(cls):
        """Validate that weights sum to 1.0."""
        total = sum(cls.get_weights().values())
        assert abs(total - 1.0) < 0.001, f"Weights must sum to 1.0, got {total}"


class IndustryMatchingEngine:
    """Engine for matching industry partners to projects."""
    
    def __init__(self, db: Session, config: Optional[IndustryMatchingConfig] = None):
        """
        Initialize matching engine.
        
        Args:
            db: Database session
            config: Optional configuration (uses defaults if not provided)
        """
        self.db = db
        self.config = config or IndustryMatchingConfig()
        self.config.validate_weights()
    
    def match_industries_for_project(
        self,
        project_id: UUID,
        save_results: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find and rank industry partners for a project.
        
        Args:
            project_id: Project ID
            save_results: Whether to save results to database
            
        Returns:
            List of matched industries with scores and explanations
        """
        
        # Get project with challenge
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        challenge = self.db.query(Challenge).filter(Challenge.id == project.challenge_id).first()
        if not challenge:
            raise ValueError(f"Challenge {project.challenge_id} not found")
        
        # Get all verified industry partners
        industries = self.db.query(IndustryPartner).filter(
            IndustryPartner.verification_status == VerificationStatus.VERIFIED
        ).all()
        
        # Score each industry
        matches = []
        for industry in industries:
            scores = self._score_industry(project, challenge, industry)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(scores)
            
            if overall_score >= self.config.MIN_RECOMMENDATION_SCORE:
                # Generate evidence and explanation
                evidence = self._generate_evidence(scores, industry, project, challenge)
                explanation = self._generate_explanation(scores, industry, project, challenge)
                
                match_data = {
                    "industry_id": industry.id,
                    "industry": industry,
                    "overall_score": round(overall_score, 2),
                    "component_scores": {
                        "expertise": round(scores["expertise"], 2),
                        "domain_fit": round(scores["domain_fit"], 2),
                        "technical_capability": round(scores["technical_capability"], 2),
                        "resources": round(scores["resources"], 2),
                        "geographic": round(scores["geographic"], 2),
                        "partnership_history": round(scores["partnership_history"], 2),
                        "availability": round(scores["availability"], 2)
                    },
                    "evidence": evidence,
                    "explanation": explanation
                }
                
                matches.append(match_data)
        
        # Sort by score descending
        matches.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Limit to max recommendations
        matches = matches[:self.config.MAX_RECOMMENDATIONS]
        
        # Save results if requested
        if save_results and matches:
            self._save_matches(project_id, matches)
        
        return matches
    
    def _score_industry(
        self,
        project: Project,
        challenge: Challenge,
        industry: IndustryPartner
    ) -> Dict[str, float]:
        """
        Score an industry partner across all dimensions.
        
        Returns dict with raw scores (0-100) for each component.
        """
        
        scores = {}
        
        # 1. Expertise match (0-100)
        scores["expertise"] = self._score_expertise_match(project, challenge, industry)
        
        # 2. Domain fit (0-100)
        scores["domain_fit"] = self._score_domain_fit(challenge, industry)
        
        # 3. Technical capability (0-100)
        scores["technical_capability"] = self._score_technical_capability(project, industry)
        
        # 4. Resources/infrastructure (0-100)
        scores["resources"] = self._score_resources(industry)
        
        # 5. Geographic relevance (0-100)
        scores["geographic"] = self._score_geographic(challenge, industry)
        
        # 6. Partnership history (0-100)
        scores["partnership_history"] = self._score_partnership_history(industry)
        
        # 7. Availability (0-100)
        scores["availability"] = self._score_availability(industry)
        
        return scores
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        weights = self.config.get_weights()
        
        overall = (
            scores["expertise"] * weights["expertise"] +
            scores["domain_fit"] * weights["domain_fit"] +
            scores["technical_capability"] * weights["technical_capability"] +
            scores["resources"] * weights["resources"] +
            scores["geographic"] * weights["geographic"] +
            scores["partnership_history"] * weights["partnership_history"] +
            scores["availability"] * weights["availability"]
        )
        
        return overall
    
    def _score_expertise_match(
        self,
        project: Project,
        challenge: Challenge,
        industry: IndustryPartner
    ) -> float:
        """
        Score expertise alignment between project needs and industry expertise.
        
        Uses challenge AI analysis skills if available, otherwise falls back to
        challenge categories.
        """
        
        # Get industry expertise
        industry_expertise = self.db.query(IndustryExpertise).filter(
            IndustryExpertise.industry_id == industry.id
        ).all()
        
        if not industry_expertise:
            return 50.0  # Neutral score for missing data
        
        # Get challenge AI analysis if available
        from app.models.challenge import ChallengeAIAnalysis
        ai_analysis = self.db.query(ChallengeAIAnalysis).filter(
            ChallengeAIAnalysis.challenge_id == challenge.id
        ).first()
        
        if ai_analysis and ai_analysis.extracted_skills:
            # Match against extracted skills
            required_skills = [s.lower() for s in ai_analysis.extracted_skills]
            
            # Get expertise names
            expertise_names = []
            for ie in industry_expertise:
                exp = ie.expertise
                if exp:
                    expertise_names.append(exp.name.lower())
            
            if not required_skills:
                return 50.0
            
            # Calculate overlap
            matches = sum(1 for skill in required_skills if any(skill in exp or exp in skill for exp in expertise_names))
            overlap_ratio = matches / len(required_skills)
            
            # Weight by proficiency
            avg_proficiency = sum(ie.proficiency_score for ie in industry_expertise) / len(industry_expertise)
            
            score = (overlap_ratio * 0.7 + avg_proficiency * 0.3) * 100
            return min(100.0, score)
        
        # Fallback: use challenge categories
        if not challenge.categories:
            return 50.0
        
        # Simple keyword matching
        category_names = [cat.name.lower() for cat in challenge.categories]
        expertise_names = [ie.expertise.name.lower() for ie in industry_expertise if ie.expertise]
        
        matches = sum(1 for cat in category_names if any(cat in exp or exp in cat for exp in expertise_names))
        if category_names:
            score = (matches / len(category_names)) * 100
            return min(100.0, score)
        
        return 50.0
    
    def _score_domain_fit(self, challenge: Challenge, industry: IndustryPartner) -> float:
        """Score how well the industry's domain aligns with challenge domain."""
        
        if not industry.sectors:
            return 50.0  # Neutral for missing data
        
        # Get challenge domain from AI analysis
        from app.models.challenge import ChallengeAIAnalysis
        ai_analysis = self.db.query(ChallengeAIAnalysis).filter(
            ChallengeAIAnalysis.challenge_id == challenge.id
        ).first()
        
        if not ai_analysis or not ai_analysis.predicted_category:
            return 50.0
        
        challenge_domain = ai_analysis.predicted_category.lower()
        industry_sectors = industry.sectors.lower()
        
        # Simple keyword matching
        if challenge_domain in industry_sectors or any(word in industry_sectors for word in challenge_domain.split()):
            return 80.0
        
        return 40.0
    
    def _score_technical_capability(self, project: Project, industry: IndustryPartner) -> float:
        """Score technical capability based on capabilities description."""
        
        if not industry.capabilities:
            return 50.0  # Neutral for missing data
        
        # If capabilities are described, give a positive score
        capabilities_length = len(industry.capabilities)
        
        if capabilities_length > 500:
            return 85.0
        elif capabilities_length > 200:
            return 70.0
        elif capabilities_length > 50:
            return 60.0
        else:
            return 50.0
    
    def _score_resources(self, industry: IndustryPartner) -> float:
        """Score available resources and infrastructure."""
        
        if not industry.resources:
            return 50.0  # Neutral for missing data
        
        # If resources are described, give a positive score
        resources_length = len(industry.resources)
        
        if resources_length > 300:
            return 80.0
        elif resources_length > 100:
            return 65.0
        elif resources_length > 30:
            return 55.0
        else:
            return 50.0
    
    def _score_geographic(self, challenge: Challenge, industry: IndustryPartner) -> float:
        """Score geographic proximity/relevance."""
        
        if not industry.district or not challenge.district:
            return 50.0  # Neutral for missing data
        
        # Same district = high score
        if industry.district.lower() == challenge.district.lower():
            return 90.0
        
        # Same state (Jharkhand)
        if industry.state == "Jharkhand":
            return 60.0
        
        return 30.0
    
    def _score_partnership_history(self, industry: IndustryPartner) -> float:
        """Score based on previous partnership success."""
        
        # Get completed partnerships
        completed_partnerships = self.db.query(Partnership).filter(
            Partnership.industry_id == industry.id,
            Partnership.status == PartnershipStatus.COMPLETED
        ).count()
        
        # Get active partnerships
        active_partnerships = self.db.query(Partnership).filter(
            Partnership.industry_id == industry.id,
            Partnership.status == PartnershipStatus.ACTIVE
        ).count()
        
        total = completed_partnerships + active_partnerships
        
        if total == 0:
            return 50.0  # Neutral for no history
        
        # Score based on partnership count
        if total >= 10:
            return 90.0
        elif total >= 5:
            return 75.0
        elif total >= 2:
            return 65.0
        else:
            return 55.0
    
    def _score_availability(self, industry: IndustryPartner) -> float:
        """Score based on current availability status."""
        
        if industry.availability_status == AvailabilityStatus.AVAILABLE:
            return 90.0
        elif industry.availability_status == AvailabilityStatus.LIMITED:
            return 60.0
        else:  # UNAVAILABLE
            return 20.0
    
    def _generate_evidence(
        self,
        scores: Dict[str, float],
        industry: IndustryPartner,
        project: Project,
        challenge: Challenge
    ) -> List[str]:
        """Generate evidence list for the match."""
        
        evidence = []
        
        # Expertise evidence
        if scores["expertise"] >= 70:
            expertise_count = self.db.query(IndustryExpertise).filter(
                IndustryExpertise.industry_id == industry.id
            ).count()
            evidence.append(f"Strong expertise alignment ({expertise_count} relevant areas)")
        
        # Domain evidence
        if scores["domain_fit"] >= 70:
            evidence.append(f"Relevant sector experience: {industry.sectors[:100] if industry.sectors else 'General'}")
        
        # Technical capability
        if scores["technical_capability"] >= 70:
            evidence.append("Strong technical capabilities")
        
        # Resources
        if scores["resources"] >= 70:
            evidence.append("Relevant technical resources available")
        
        # Geographic
        if scores["geographic"] >= 80:
            evidence.append(f"Located in {industry.district}, Jharkhand")
        
        # Partnership history
        completed = self.db.query(Partnership).filter(
            Partnership.industry_id == industry.id,
            Partnership.status == PartnershipStatus.COMPLETED
        ).count()
        if completed > 0:
            evidence.append(f"Successfully completed {completed} previous partnership(s)")
        
        # Availability
        if industry.availability_status == AvailabilityStatus.AVAILABLE:
            evidence.append("Currently available for partnerships")
        
        return evidence
    
    def _generate_explanation(
        self,
        scores: Dict[str, float],
        industry: IndustryPartner,
        project: Project,
        challenge: Challenge
    ) -> str:
        """Generate human-readable explanation for the match."""
        
        # Find strongest factors
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_factors = [name for name, score in sorted_scores[:3] if score >= 60]
        
        if not top_factors:
            return f"Moderate match for {project.name}. Further evaluation recommended."
        
        factor_descriptions = {
            "expertise": "strong expertise alignment",
            "domain_fit": "relevant domain experience",
            "technical_capability": "robust technical capabilities",
            "resources": "appropriate resource availability",
            "geographic": "favorable geographic proximity",
            "partnership_history": "proven partnership track record",
            "availability": "current availability"
        }
        
        reasons = [factor_descriptions.get(f, f) for f in top_factors]
        
        if len(reasons) == 1:
            reason_text = reasons[0]
        elif len(reasons) == 2:
            reason_text = f"{reasons[0]} and {reasons[1]}"
        else:
            reason_text = f"{', '.join(reasons[:-1])}, and {reasons[-1]}"
        
        return f"Strong match for {project.name} with {reason_text}."
    
    def _save_matches(self, project_id: UUID, matches: List[Dict[str, Any]]):
        """Save matching results to database."""
        
        # Delete old matches for this project
        self.db.query(IndustryMatch).filter(
            IndustryMatch.project_id == project_id
        ).delete()
        
        # Save new matches
        for match in matches:
            industry_match = IndustryMatch(
                project_id=project_id,
                industry_id=match["industry_id"],
                overall_score=match["overall_score"],
                expertise_score=match["component_scores"]["expertise"],
                domain_score=match["component_scores"]["domain_fit"],
                capability_score=match["component_scores"]["technical_capability"],
                resource_score=match["component_scores"]["resources"],
                geographic_score=match["component_scores"]["geographic"],
                partnership_history_score=match["component_scores"]["partnership_history"],
                availability_score=match["component_scores"]["availability"],
                evidence=json.dumps(match["evidence"]),
                explanation=match["explanation"],
                matched_at=datetime.utcnow()
            )
            self.db.add(industry_match)
        
        self.db.commit()
    
    def get_saved_matches(self, project_id: UUID) -> List[Dict[str, Any]]:
        """Retrieve saved industry matches for a project."""
        
        matches = self.db.query(IndustryMatch).filter(
            IndustryMatch.project_id == project_id
        ).order_by(IndustryMatch.overall_score.desc()).all()
        
        result = []
        for match in matches:
            result.append({
                "industry_id": match.industry_id,
                "industry": match.industry,
                "overall_score": match.overall_score,
                "component_scores": {
                    "expertise": match.expertise_score,
                    "domain_fit": match.domain_score,
                    "technical_capability": match.capability_score,
                    "resources": match.resource_score,
                    "geographic": match.geographic_score,
                    "partnership_history": match.partnership_history_score,
                    "availability": match.availability_score
                },
                "evidence": json.loads(match.evidence) if match.evidence else [],
                "explanation": match.explanation,
                "matched_at": match.matched_at
            })
        
        return result
