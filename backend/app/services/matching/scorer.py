"""
Scoring functions for university matching.
"""

from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.university import (
    University,
    UniversityExpertise,
    Faculty,
    FacultyExpertise,
    Facility,
    Expertise
)
from app.models.industry import IndustryPartner, IndustryExpertise
from app.models.enums import AvailabilityStatus
from app.services.matching.config import MatchingConfig


class UniversityScorer:
    """Calculates individual scoring components for university matching."""
    
    def __init__(self, db: Session, config: MatchingConfig):
        """
        Initialize scorer.
        
        Args:
            db: Database session
            config: Matching configuration
        """
        self.db = db
        self.config = config
    
    def score_expertise(
        self,
        university: University,
        required_skills: List[Dict[str, float]]
    ) -> Tuple[float, List[Dict]]:
        """
        Score university expertise match.
        
        Args:
            university: University to score
            required_skills: List of {name: str, confidence: float}
            
        Returns:
            Tuple of (score, evidence)
        """
        if not required_skills:
            return self.config.neutral_score, []
        
        # Get university expertise
        university_expertise = self.db.query(UniversityExpertise).filter(
            UniversityExpertise.university_id == university.id
        ).join(Expertise).all()
        
        # Create expertise map
        expertise_map = {
            ue.expertise.name.lower(): ue.proficiency_score
            for ue in university_expertise
        }
        
        # Calculate weighted match for each required skill
        total_weight = 0.0
        total_score = 0.0
        matched_expertise = []
        
        for skill in required_skills:
            skill_name = skill.get("name", "").lower()
            skill_confidence = skill.get("confidence", 1.0)
            
            if skill_name in expertise_map:
                proficiency = expertise_map[skill_name]
                
                # Score = proficiency * 100, weighted by skill confidence
                skill_score = proficiency * 100
                total_score += skill_score * skill_confidence
                total_weight += skill_confidence
                
                matched_expertise.append({
                    "name": skill["name"],
                    "proficiency": proficiency,
                    "required_confidence": skill_confidence
                })
        
        # Calculate final score
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            # No matching expertise found
            final_score = 0.0
        
        return final_score, matched_expertise
    
    def score_faculty(
        self,
        university: University,
        required_skills: List[Dict[str, float]]
    ) -> Tuple[float, List[Dict]]:
        """
        Score faculty availability and relevance.
        
        Args:
            university: University to score
            required_skills: List of required skills
            
        Returns:
            Tuple of (score, evidence)
        """
        if not required_skills:
            return self.config.neutral_score, []
        
        # Get required expertise IDs
        required_names = [s["name"].lower() for s in required_skills]
        expertise_records = self.db.query(Expertise).filter(
            Expertise.name.in_([s["name"] for s in required_skills])
        ).all()
        expertise_ids = [e.id for e in expertise_records]
        
        if not expertise_ids:
            return self.config.neutral_score, []
        
        # Get relevant faculty with matching expertise
        relevant_faculty = self.db.query(Faculty).filter(
            Faculty.university_id == university.id
        ).join(FacultyExpertise).filter(
            FacultyExpertise.expertise_id.in_(expertise_ids)
        ).distinct().all()
        
        if not relevant_faculty:
            return 0.0, []
        
        # Calculate availability score
        availability_scores = {
            AvailabilityStatus.AVAILABLE: self.config.available_score,
            AvailabilityStatus.LIMITED: self.config.limited_score,
            AvailabilityStatus.UNAVAILABLE: self.config.unavailable_score
        }
        
        total_score = 0.0
        matched_faculty = []
        
        for faculty in relevant_faculty:
            score = availability_scores.get(
                faculty.availability_status,
                self.config.neutral_score
            )
            total_score += score
            
            # Get faculty expertise
            faculty_expertise = self.db.query(FacultyExpertise).filter(
                FacultyExpertise.faculty_id == faculty.id,
                FacultyExpertise.expertise_id.in_(expertise_ids)
            ).join(Expertise).all()
            
            matched_faculty.append({
                "faculty_id": str(faculty.id),
                "name": faculty.user.full_name if faculty.user else "Unknown",
                "designation": faculty.designation,
                "availability": faculty.availability_status.value,
                "expertise": [fe.expertise.name for fe in faculty_expertise]
            })
        
        # Average score across relevant faculty
        final_score = total_score / len(relevant_faculty) if relevant_faculty else 0.0
        
        return final_score, matched_faculty
    
    def score_infrastructure(
        self,
        university: University,
        required_skills: List[Dict[str, float]]
    ) -> Tuple[float, List[Dict]]:
        """
        Score infrastructure and facility match.
        
        Args:
            university: University to score
            required_skills: Required skills (used to infer facility needs)
            
        Returns:
            Tuple of (score, evidence)
        """
        if not required_skills:
            return self.config.neutral_score, []
        
        # Get all facilities
        facilities = self.db.query(Facility).filter(
            Facility.university_id == university.id
        ).all()
        
        if not facilities:
            return 0.0, []
        
        # Map skills to expected facility keywords
        facility_keywords = self._get_facility_keywords(required_skills)
        
        # Score facilities
        matched_facilities = []
        total_match_score = 0.0
        
        for facility in facilities:
            # Check for keyword matches
            facility_text = f"{facility.name} {facility.type or ''} {facility.description or ''}".lower()
            
            match_score = 0.0
            match_reasons = []
            
            for keyword in facility_keywords:
                if keyword.lower() in facility_text:
                    match_score += self.config.facility_partial_match_score
                    match_reasons.append(keyword)
            
            if match_score > 0:
                total_match_score += match_score
                
                matched_facilities.append({
                    "facility_id": str(facility.id),
                    "name": facility.name,
                    "type": facility.type,
                    "availability": facility.availability_status.value,
                    "match_reason": f"Matches: {', '.join(match_reasons)}"
                })
        
        # Normalize score to 0-100
        if matched_facilities:
            # Cap at 100
            final_score = min(100.0, total_match_score)
        else:
            final_score = 0.0
        
        return final_score, matched_facilities
    
    def score_location(
        self,
        university: University,
        challenge_district: Optional[str],
        challenge_state: str = "Jharkhand"
    ) -> Tuple[float, str]:
        """
        Score geographic location match.
        
        Args:
            university: University to score
            challenge_district: Challenge district
            challenge_state: Challenge state
            
        Returns:
            Tuple of (score, reason)
        """
        if not challenge_district:
            return self.config.neutral_score, "Challenge location not specified"
        
        university_district = university.district
        university_state = university.state or "Jharkhand"
        
        # Same district
        if university_district and university_district.lower() == challenge_district.lower():
            return self.config.same_district_score, f"Same district: {challenge_district}"
        
        # Same state (Jharkhand)
        if university_state.lower() == challenge_state.lower():
            return self.config.same_state_score, f"Same state: {challenge_state}"
        
        # Different state
        return self.config.different_state_score, f"Different state: {university_state}"
    
    def score_industry_connections(
        self,
        university: University,
        required_skills: List[Dict[str, float]]
    ) -> Tuple[float, List[Dict]]:
        """
        Score industry partner connections.
        
        For MVP: Check if industry partners exist with relevant expertise.
        Note: Partnerships are project-specific, so we check general industry
        expertise availability in the region/ecosystem.
        
        Args:
            university: University to score
            required_skills: Required skills
            
        Returns:
            Tuple of (score, evidence)
        """
        if not required_skills:
            return self.config.neutral_score, []
        
        # Get required expertise names
        required_names = [s["name"].lower() for s in required_skills]
        
        # Get industry partners with relevant expertise
        # Filter by region if possible (same state as university)
        industry_expertise = self.db.query(IndustryExpertise).join(
            Expertise
        ).filter(
            Expertise.name.in_([s["name"] for s in required_skills])
        ).join(IndustryPartner).filter(
            IndustryPartner.state == (university.state or "Jharkhand")
        ).all()
        
        if not industry_expertise:
            # Try without region filter
            industry_expertise = self.db.query(IndustryExpertise).join(
                Expertise
            ).filter(
                Expertise.name.in_([s["name"] for s in required_skills])
            ).join(IndustryPartner).all()
        
        if not industry_expertise:
            return self.config.neutral_score, []
        
        # Calculate score based on relevant connections
        matched_industries = []
        seen_industries = set()
        
        for ie in industry_expertise:
            if ie.industry_id not in seen_industries:
                seen_industries.add(ie.industry_id)
                
                # Get all relevant expertise for this industry
                all_expertise = self.db.query(IndustryExpertise).filter(
                    IndustryExpertise.industry_id == ie.industry_id
                ).join(Expertise).all()
                
                relevant_expertise = [
                    e.expertise.name for e in all_expertise
                    if e.expertise.name.lower() in required_names
                ]
                
                matched_industries.append({
                    "industry_id": str(ie.industry_id),
                    "organization_name": ie.industry.organization_name,
                    "type": ie.industry.type.value,
                    "relevant_expertise": relevant_expertise
                })
        
        # Score: 60-100 based on number of relevant connections available
        if matched_industries:
            # 1 connection = 70, 2+ = 80, 3+ = 90, 5+ = 100
            count = len(matched_industries)
            if count >= 5:
                score = 100.0
            elif count >= 3:
                score = 90.0
            elif count >= 2:
                score = 80.0
            else:
                score = 70.0
        else:
            score = self.config.neutral_score
        
        return score, matched_industries
    
    def score_previous_projects(
        self,
        university: University,
        challenge_domain: str
    ) -> Tuple[float, str]:
        """
        Score previous project relevance.
        
        Args:
            university: University to score
            challenge_domain: Challenge primary domain
            
        Returns:
            Tuple of (score, note)
        """
        # For MVP, use neutral score with explanation
        # TODO: Implement when project history data is available
        return (
            self.config.neutral_score,
            "Insufficient historical project data for scoring. This factor will be enhanced when project completion history becomes available."
        )
    
    def _get_facility_keywords(self, required_skills: List[Dict[str, float]]) -> List[str]:
        """
        Map required skills to facility keywords.
        
        Args:
            required_skills: Required skills
            
        Returns:
            List of facility keywords
        """
        keyword_map = {
            "iot": ["iot", "internet of things", "sensor", "embedded"],
            "ai/ml": ["ai", "artificial intelligence", "machine learning", "ml", "data science"],
            "gis": ["gis", "geographic", "geospatial", "remote sensing", "mapping"],
            "computer vision": ["computer vision", "image processing", "vision"],
            "embedded systems": ["embedded", "microcontroller", "electronics"],
            "water engineering": ["water", "hydraulics", "environmental"],
            "civil engineering": ["civil", "structural", "construction"],
            "agricultural engineering": ["agricultural", "farming", "agri"],
            "environmental science": ["environmental", "ecology", "pollution"],
            "renewable energy": ["solar", "wind", "renewable", "energy"],
            "electronics": ["electronics", "circuit", "electrical"],
            "robotics": ["robotics", "robot", "automation"],
            "biotechnology": ["bio", "biotechnology", "genetics"],
            "web development": ["computer", "software", "programming"],
            "mobile development": ["mobile", "app", "software"]
        }
        
        keywords = []
        for skill in required_skills:
            skill_name = skill["name"].lower()
            if skill_name in keyword_map:
                keywords.extend(keyword_map[skill_name])
            else:
                # Use the skill name itself
                keywords.append(skill_name)
        
        return list(set(keywords))  # Remove duplicates
