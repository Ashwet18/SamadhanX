"""
AI services for challenge intelligence.
"""

from .provider import AIProvider, get_ai_provider
from .analyzer import ChallengeAIService
from .duplicate_detector import DuplicateDetector
from .schemas import (
    AIAnalysisResult,
    ClassificationResult,
    SeverityResult,
    UrgencyResult,
    SkillExtractionResult,
    SolutionRecommendation,
    DuplicateCandidate
)

__all__ = [
    "AIProvider",
    "get_ai_provider",
    "ChallengeAIService",
    "DuplicateDetector",
    "AIAnalysisResult",
    "ClassificationResult",
    "SeverityResult",
    "UrgencyResult",
    "SkillExtractionResult",
    "SolutionRecommendation",
    "DuplicateCandidate",
]
