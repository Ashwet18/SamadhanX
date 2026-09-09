"""
University matching services for challenge assignments.
"""

from .engine import UniversityMatchingEngine
from .config import MatchingWeights, MatchingConfig, DEFAULT_MATCHING_CONFIG
from .schemas import (
    MatchingResult,
    UniversityMatch,
    ComponentScores,
    MatchingEvidence,
    ExpertiseMatch,
    FacultyMatch,
    FacilityMatch
)

__all__ = [
    "UniversityMatchingEngine",
    "MatchingWeights",
    "MatchingConfig",
    "DEFAULT_MATCHING_CONFIG",
    "MatchingResult",
    "UniversityMatch",
    "ComponentScores",
    "MatchingEvidence",
    "ExpertiseMatch",
    "FacultyMatch",
    "FacilityMatch",
]
