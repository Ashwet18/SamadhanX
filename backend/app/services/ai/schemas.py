"""
Pydantic schemas for AI analysis results.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SkillExtractionResult(BaseModel):
    """Extracted skill with confidence."""
    
    name: str = Field(..., description="Skill name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class SolutionRecommendation(BaseModel):
    """Recommended solution type with confidence."""
    
    type: str = Field(..., description="Solution type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ClassificationResult(BaseModel):
    """Challenge classification result."""
    
    primary_domain: str = Field(..., description="Primary domain/category")
    secondary_domains: List[str] = Field(default_factory=list, description="Secondary domains")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    classification_reason: str = Field(..., description="Explanation of classification")


class SeverityResult(BaseModel):
    """Severity analysis result."""
    
    severity_score: int = Field(..., ge=0, le=100, description="Severity score (0-100)")
    severity_reason: str = Field(..., description="Explanation of severity assessment")


class UrgencyResult(BaseModel):
    """Urgency analysis result."""
    
    urgency_score: int = Field(..., ge=0, le=100, description="Urgency score (0-100)")
    urgency_reason: str = Field(..., description="Explanation of urgency assessment")


class AIAnalysisResult(BaseModel):
    """Complete AI analysis result."""
    
    summary: str = Field(..., description="Concise English summary")
    detected_language: Optional[str] = Field(None, description="Detected input language")
    classification: ClassificationResult
    severity: SeverityResult
    urgency: UrgencyResult
    skills: List[SkillExtractionResult] = Field(default_factory=list)
    solution_types: List[SolutionRecommendation] = Field(default_factory=list)
    affected_population_estimate: Optional[int] = Field(None, description="Population estimate if derivable")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall analysis confidence")


class DuplicateCandidate(BaseModel):
    """Potential duplicate challenge."""
    
    challenge_id: str = Field(..., description="Similar challenge ID")
    challenge_code: str = Field(..., description="Similar challenge code")
    title: str = Field(..., description="Similar challenge title")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")
