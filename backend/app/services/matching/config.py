"""
Matching engine configuration and weights.
"""

from typing import Dict
from pydantic import BaseModel, Field


class MatchingWeights(BaseModel):
    """
    Configurable weights for university matching factors.
    
    All weights must sum to 1.0 (100%).
    """
    
    expertise: float = Field(0.40, ge=0.0, le=1.0, description="Expertise match weight")
    faculty: float = Field(0.20, ge=0.0, le=1.0, description="Faculty availability weight")
    infrastructure: float = Field(0.15, ge=0.0, le=1.0, description="Infrastructure/facilities weight")
    previous_projects: float = Field(0.10, ge=0.0, le=1.0, description="Previous project relevance weight")
    location: float = Field(0.10, ge=0.0, le=1.0, description="Geographic location weight")
    industry: float = Field(0.05, ge=0.0, le=1.0, description="Industry connections weight")
    
    def validate_sum(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = (
            self.expertise +
            self.faculty +
            self.infrastructure +
            self.previous_projects +
            self.location +
            self.industry
        )
        return abs(total - 1.0) < 0.001  # Allow small floating point errors
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "expertise": self.expertise,
            "faculty": self.faculty,
            "infrastructure": self.infrastructure,
            "previous_projects": self.previous_projects,
            "location": self.location,
            "industry": self.industry
        }


class MatchingConfig(BaseModel):
    """Matching engine configuration."""
    
    weights: MatchingWeights = Field(default_factory=MatchingWeights)
    
    # Scoring fallbacks for missing data
    neutral_score: float = Field(50.0, description="Neutral score when data is missing")
    
    # Location scoring
    same_district_score: float = Field(100.0, description="Score for same district")
    same_state_score: float = Field(70.0, description="Score for same state")
    different_state_score: float = Field(30.0, description="Score for different state")
    
    # Faculty availability scoring
    available_score: float = Field(100.0, description="Score for AVAILABLE faculty")
    limited_score: float = Field(60.0, description="Score for LIMITED faculty")
    unavailable_score: float = Field(0.0, description="Score for UNAVAILABLE faculty")
    
    # Minimum thresholds
    min_expertise_match: float = Field(0.3, description="Minimum expertise match to consider")
    
    # Result limits
    max_recommendations: int = Field(10, description="Maximum universities to recommend")
    
    # Facility matching
    facility_exact_match_bonus: float = Field(20.0, description="Bonus for exact facility name match")
    facility_partial_match_score: float = Field(10.0, description="Score for partial facility match")


# Default configuration
DEFAULT_MATCHING_CONFIG = MatchingConfig()
