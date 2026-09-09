"""
Industry collaboration schemas for request/response validation.
"""

from pydantic import Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from app.schemas.base import BaseSchema, PaginatedResponse
from app.models.enums import (
    PartnershipType,
    PartnershipStatus,
    ContributionType,
    ContributionStatus,
    IndustryType,
    VerificationStatus,
    AvailabilityStatus
)


# ==================== INDUSTRY MATCH SCHEMAS ====================

class IndustryMatchComponentScores(BaseSchema):
    """Component scores for industry matching."""
    
    expertise: float = Field(..., ge=0, le=100)
    domain_fit: float = Field(..., ge=0, le=100)
    technical_capability: float = Field(..., ge=0, le=100)
    resources: float = Field(..., ge=0, le=100)
    geographic: float = Field(..., ge=0, le=100)
    partnership_history: float = Field(..., ge=0, le=100)
    availability: float = Field(..., ge=0, le=100)


class IndustryMatchResponse(BaseSchema):
    """Schema for industry match result."""
    
    industry_id: UUID
    industry_name: str
    industry_type: IndustryType
    overall_score: float = Field(..., ge=0, le=100)
    component_scores: IndustryMatchComponentScores
    evidence: List[str]
    explanation: str
    matched_at: Optional[datetime] = None


class IndustryMatchListResponse(BaseSchema):
    """Schema for list of industry matches."""
    
    project_id: UUID
    matches: List[IndustryMatchResponse]
    total_matches: int


# ==================== PARTNERSHIP SCHEMAS ====================

class PartnershipCreate(BaseSchema):
    """Schema for creating a partnership request."""
    
    industry_id: UUID = Field(..., description="Industry partner ID")
    partnership_type: PartnershipType = Field(..., description="Type of partnership")
    objectives: Optional[str] = Field(None, max_length=2000, description="Partnership objectives")
    requested_support: Optional[str] = Field(None, max_length=2000, description="Requested support description")
    expected_contribution: Optional[str] = Field(None, max_length=2000, description="Expected contribution")
    proposed_duration: Optional[int] = Field(None, ge=1, le=60, description="Duration in months")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class PartnershipAccept(BaseSchema):
    """Schema for accepting a partnership."""
    
    notes: Optional[str] = Field(None, max_length=1000, description="Acceptance notes")


class PartnershipDecline(BaseSchema):
    """Schema for declining a partnership."""
    
    reason: str = Field(..., min_length=10, max_length=1000, description="Decline reason")


class PartnershipCancel(BaseSchema):
    """Schema for cancelling a partnership."""
    
    reason: str = Field(..., min_length=10, max_length=1000, description="Cancellation reason")


class PartnershipActivate(BaseSchema):
    """Schema for activating a partnership."""
    
    start_date: Optional[date] = Field(None, description="Partnership start date")


class PartnershipComplete(BaseSchema):
    """Schema for completing a partnership."""
    
    end_date: Optional[date] = Field(None, description="Partnership end date")
    notes: Optional[str] = Field(None, max_length=1000, description="Completion notes")


class PartnershipResponse(BaseSchema):
    """Schema for partnership response."""
    
    id: UUID
    project_id: UUID
    industry_id: UUID
    partnership_type: PartnershipType
    objectives: Optional[str]
    requested_support: Optional[str]
    expected_contribution: Optional[str]
    proposed_duration: Optional[int]
    notes: Optional[str]
    status: PartnershipStatus
    requested_by: Optional[UUID]
    requested_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    decline_reason: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class PartnershipDetailResponse(BaseSchema):
    """Schema for detailed partnership response."""
    
    partnership: PartnershipResponse
    project: Optional[Dict[str, Any]] = None
    industry: Optional[Dict[str, Any]] = None
    university: Optional[Dict[str, Any]] = None
    contribution_count: int = 0
    delivered_contribution_count: int = 0


class PartnershipListResponse(PaginatedResponse):
    """Schema for paginated partnership list response."""
    
    partnerships: List[PartnershipResponse]


# ==================== CONTRIBUTION SCHEMAS ====================

class ContributionCreate(BaseSchema):
    """Schema for creating a contribution."""
    
    contribution_type: ContributionType = Field(..., description="Type of contribution")
    description: str = Field(..., min_length=10, max_length=2000, description="Contribution description")
    estimated_value: Optional[Decimal] = Field(None, ge=0, description="Optional estimated value")
    currency: str = Field(default="INR", max_length=10, description="Currency code")


class ContributionUpdate(BaseSchema):
    """Schema for updating a contribution."""
    
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    evidence_reference: Optional[str] = Field(None, max_length=500)


class ContributionCommit(BaseSchema):
    """Schema for committing a contribution."""
    
    committed_date: Optional[date] = Field(None, description="Commitment date")


class ContributionDeliver(BaseSchema):
    """Schema for delivering a contribution."""
    
    delivered_date: Optional[date] = Field(None, description="Delivery date")
    evidence_reference: Optional[str] = Field(None, max_length=500, description="Evidence reference")


class ContributionCancel(BaseSchema):
    """Schema for cancelling a contribution."""
    
    reason: str = Field(..., min_length=10, max_length=500, description="Cancellation reason")


class ContributionResponse(BaseSchema):
    """Schema for contribution response."""
    
    id: UUID
    partnership_id: UUID
    contribution_type: ContributionType
    description: str
    estimated_value: Optional[Decimal]
    currency: str
    status: ContributionStatus
    committed_date: Optional[date]
    delivered_date: Optional[date]
    evidence_reference: Optional[str]
    created_at: datetime
    updated_at: datetime


# ==================== INDUSTRY DASHBOARD SCHEMAS ====================

class IndustryPartnershipSummary(BaseSchema):
    """Summary of partnerships for industry dashboard."""
    
    total_partnerships: int = 0
    pending_requests: int = 0
    under_review: int = 0
    accepted: int = 0
    active: int = 0
    completed: int = 0
    declined: int = 0
    cancelled: int = 0


class IndustryDashboardResponse(BaseSchema):
    """Schema for industry dashboard."""
    
    industry_id: UUID
    industry_name: str
    partnership_summary: IndustryPartnershipSummary
    recent_requests: List[PartnershipResponse]
    active_partnerships: List[PartnershipResponse]
    supported_project_count: int


class IndustryProjectResponse(BaseSchema):
    """Schema for industry-supported projects."""
    
    project_id: UUID
    project_code: str
    project_name: str
    university_name: str
    partnership_type: PartnershipType
    partnership_status: PartnershipStatus
    partnership_start_date: Optional[date]


# ==================== INDUSTRY PARTNER SCHEMAS ====================

class IndustryPartnerResponse(BaseSchema):
    """Schema for industry partner response."""
    
    id: UUID
    organization_name: str
    type: IndustryType
    description: Optional[str]
    website: Optional[str]
    district: Optional[str]
    state: str
    capabilities: Optional[str]
    sectors: Optional[str]
    resources: Optional[str]
    availability_status: AvailabilityStatus
    verification_status: VerificationStatus
    created_at: datetime


class IndustryExpertiseResponse(BaseSchema):
    """Schema for industry expertise."""
    
    expertise_id: UUID
    expertise_name: str
    proficiency_score: float
