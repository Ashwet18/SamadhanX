"""
Industry collaboration services.
"""

from app.services.industry_matching import IndustryMatchingEngine, IndustryMatchingConfig
from app.services.industry.partnership_service import PartnershipService
from app.services.industry.partnership_lifecycle import PartnershipLifecycleManager

__all__ = [
    "IndustryMatchingEngine",
    "IndustryMatchingConfig",
    "PartnershipService",
    "PartnershipLifecycleManager",
]
