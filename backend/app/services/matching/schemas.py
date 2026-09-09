"""
Schemas for university matching results.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class ExpertiseMatch(BaseModel):
    """Matched expertise with proficiency."""
    
    name: str = Field(..., description="Expertise name")
    proficiency: float = Field(..., ge=0.0, le=1.0, description="University proficiency score")
    required_confidence: Optional[float] = Field(None, description="Challenge requirement confidence")


class FacultyMatch(BaseModel):
    """Matched faculty member."""
    
    faculty_id: UUID = Field(..., description="Faculty ID")
    name: str = Field(..., description="Faculty name")
    designation: str = Field(..., description="Faculty designation")
    availability: str = Field(..., description="Availability status")
    expertise: List[str] = Field(default_factory=list, description="Relevant expertise")


class FacilityMatch(BaseModel):
    """Matched facility/laboratory."""
    
    facility_id: UUID = Field(..., description="Facility ID")
    name: str = Field(..., description="Facility name")
    type: Optional[str] = Field(None, description="Facility type")
    availability: str = Field(..., description="Availability status")
    match_reason: str = Field(..., description="Why this facility matches")


class IndustryConnection(BaseModel):
    """Industry partner connection."""
    
    industry_id: UUID = Field(..., description="Industry partner ID")
    organization_name: str = Field(..., description="Organization name")
    type: str = Field(..., description="Industry type")
    relevant_expertise: List[str] = Field(default_factory=list, description="Relevant expertise")


class MatchingEvidence(BaseModel):
    """Evidence supporting university match."""
    
    matched_expertise: List[ExpertiseMatch] = Field(default_factory=list)
    matched_faculty: List[FacultyMatch] = Field(default_factory=list)
    matched_facilities: List[FacilityMatch] = Field(default_factory=list)
    industry_connections: List[IndustryConnection] = Field(default_factory=list)
    location_reason: str = Field(..., description="Location match explanation")
    previous_projects_note: str = Field(..., description="Previous projects note")


class ComponentScores(BaseModel):
    """Breakdown of matching component scores."""
    
    expertise: float = Field(..., ge=0.0, le=100.0, description="Expertise match score")
    faculty: float = Field(..., ge=0.0, le=100.0, description="Faculty availability score")
    infrastructure: float = Field(..., ge=0.0, le=100.0, description="Infrastructure score")
    previous_projects: float = Field(..., ge=0.0, le=100.0, description="Previous projects score")
    location: float = Field(..., ge=0.0, le=100.0, description="Location score")
    industry: float = Field(..., ge=0.0, le=100.0, description="Industry connections score")


class UniversityMatch(BaseModel):
    """University match result."""
    
    rank: int = Field(..., description="Ranking position")
    university_id: UUID = Field(..., description="University ID")
    university_name: str = Field(..., description="University name")
    university_code: str = Field(..., description="University code")
    score: float = Field(..., ge=0.0, le=100.0, description="Final matching score")
    components: ComponentScores = Field(..., description="Component score breakdown")
    evidence: MatchingEvidence = Field(..., description="Matching evidence")
    reason: str = Field(..., description="Human-readable explanation")
    assignment_status: Optional[str] = Field(None, description="Current assignment status")


class MatchingResult(BaseModel):
    """Complete matching result for a challenge."""
    
    challenge_id: UUID = Field(..., description="Challenge ID")
    challenge_code: str = Field(..., description="Challenge code")
    required_expertise: List[str] = Field(default_factory=list, description="Required skills")
    primary_domain: str = Field(..., description="Primary challenge domain")
    matching_status: str = Field(..., description="Matching status")
    ranked_universities: List[UniversityMatch] = Field(default_factory=list)
    total_candidates: int = Field(..., description="Total universities evaluated")
    timestamp: str = Field(..., description="Matching timestamp")
