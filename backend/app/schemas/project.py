"""
Project lifecycle schemas for request/response validation.
"""

from pydantic import Field, field_validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date

from app.schemas.base import BaseSchema, PaginatedResponse
from app.models.enums import (
    ProjectStatus,
    ProposalStatus,
    MilestoneStatus,
    ProjectMemberRole,
    VerificationStatus
)


# ==================== PROJECT SCHEMAS ====================

class ProjectCreate(BaseSchema):
    """Schema for creating a project."""
    
    name: str = Field(..., min_length=5, max_length=200, description="Project name")
    description: str = Field(..., min_length=20, max_length=2000, description="Project description")
    objective: Optional[str] = Field(None, max_length=1000, description="Project objective")
    expected_start_date: Optional[date] = Field(None, description="Expected start date")
    expected_end_date: Optional[date] = Field(None, description="Expected end date")


class ProjectUpdate(BaseSchema):
    """Schema for updating a project."""
    
    name: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    objective: Optional[str] = Field(None, max_length=1000)
    expected_start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None


class ProjectStatusUpdate(BaseSchema):
    """Schema for updating project status."""
    
    status: ProjectStatus = Field(..., description="New project status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class ProjectResponse(BaseSchema):
    """Schema for project response."""
    
    id: UUID
    challenge_id: UUID
    university_id: UUID
    department_id: Optional[UUID]
    project_code: str
    name: str
    description: str
    objective: Optional[str]
    status: ProjectStatus
    expected_start_date: Optional[date]
    expected_end_date: Optional[date]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(PaginatedResponse):
    """Schema for paginated project list response."""
    
    projects: List[ProjectResponse]


class ProjectDashboardResponse(BaseSchema):
    """Schema for comprehensive project dashboard."""
    
    project: ProjectResponse
    challenge: Optional[Dict[str, Any]] = None
    university: Optional[Dict[str, Any]] = None
    department: Optional[Dict[str, Any]] = None
    team_count: int = 0
    milestone_count: int = 0
    completed_milestones: int = 0
    completion_percentage: float = 0.0
    current_milestone: Optional[Dict[str, Any]] = None
    next_milestone: Optional[Dict[str, Any]] = None
    latest_activity: Optional[datetime] = None
    impact_summary: Optional[Dict[str, Any]] = None


# ==================== TEAM SCHEMAS ====================

class ProjectMemberCreate(BaseSchema):
    """Schema for adding a team member."""
    
    user_id: UUID = Field(..., description="User ID to add")
    role: ProjectMemberRole = Field(..., description="Member role")


class ProjectMemberUpdate(BaseSchema):
    """Schema for updating a team member."""
    
    role: ProjectMemberRole = Field(..., description="New member role")


class ProjectMemberResponse(BaseSchema):
    """Schema for team member response."""
    
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectMemberRole
    joined_at: datetime
    user: Optional[Dict[str, Any]] = None


# ==================== PROPOSAL SCHEMAS ====================

class ProjectProposalCreate(BaseSchema):
    """Schema for creating a proposal."""
    
    title: str = Field(..., min_length=10, max_length=300, description="Proposal title")
    summary: str = Field(..., min_length=50, max_length=2000, description="Executive summary")
    problem_statement: str = Field(..., min_length=50, max_length=3000, description="Problem statement")
    proposed_solution: str = Field(..., min_length=100, max_length=5000, description="Proposed solution")
    innovation: Optional[str] = Field(None, max_length=2000, description="Innovation aspect")
    expected_outcomes: Optional[str] = Field(None, max_length=2000, description="Expected outcomes")
    beneficiaries: Optional[str] = Field(None, max_length=1000, description="Target beneficiaries")
    required_resources: Optional[str] = Field(None, max_length=2000, description="Required resources")
    implementation_plan: Optional[str] = Field(None, max_length=3000, description="Implementation plan")
    risks: Optional[str] = Field(None, max_length=2000, description="Risk assessment")
    sustainability_plan: Optional[str] = Field(None, max_length=2000, description="Sustainability plan")
    methodology: Optional[str] = Field(None, max_length=3000, description="Methodology")
    timeline: Optional[str] = Field(None, max_length=1000, description="Project timeline")
    budget_estimate: Optional[float] = Field(None, ge=0, description="Estimated budget")


class ProjectProposalUpdate(BaseSchema):
    """Schema for updating a proposal."""
    
    title: Optional[str] = Field(None, min_length=10, max_length=300)
    summary: Optional[str] = Field(None, min_length=50, max_length=2000)
    problem_statement: Optional[str] = Field(None, min_length=50, max_length=3000)
    proposed_solution: Optional[str] = Field(None, min_length=100, max_length=5000)
    innovation: Optional[str] = Field(None, max_length=2000)
    expected_outcomes: Optional[str] = Field(None, max_length=2000)
    beneficiaries: Optional[str] = Field(None, max_length=1000)
    required_resources: Optional[str] = Field(None, max_length=2000)
    implementation_plan: Optional[str] = Field(None, max_length=3000)
    risks: Optional[str] = Field(None, max_length=2000)
    sustainability_plan: Optional[str] = Field(None, max_length=2000)
    methodology: Optional[str] = Field(None, max_length=3000)
    timeline: Optional[str] = Field(None, max_length=1000)
    budget_estimate: Optional[float] = Field(None, ge=0)


class ProposalActionRequest(BaseSchema):
    """Schema for proposal actions (approve/reject/revise)."""
    
    comments: Optional[str] = Field(None, max_length=2000, description="Action comments")


class ProjectProposalResponse(BaseSchema):
    """Schema for proposal response."""
    
    id: UUID
    project_id: UUID
    title: str
    summary: str
    problem_statement: str
    proposed_solution: str
    innovation: Optional[str]
    expected_outcomes: Optional[str]
    beneficiaries: Optional[str]
    required_resources: Optional[str]
    implementation_plan: Optional[str]
    risks: Optional[str]
    sustainability_plan: Optional[str]
    methodology: Optional[str]
    timeline: Optional[str]
    budget_estimate: Optional[float]
    status: ProposalStatus
    submitted_by: Optional[UUID]
    submitted_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    review_comments: Optional[str]
    created_at: datetime
    updated_at: datetime


# ==================== MILESTONE SCHEMAS ====================

class ProjectMilestoneCreate(BaseSchema):
    """Schema for creating a milestone."""
    
    title: str = Field(..., min_length=5, max_length=200, description="Milestone title")
    description: Optional[str] = Field(None, max_length=1000, description="Milestone description")
    sequence_number: int = Field(..., ge=1, description="Milestone sequence number")
    planned_start_date: Optional[date] = Field(None, description="Planned start date")
    planned_end_date: Optional[date] = Field(None, description="Planned end date")


class ProjectMilestoneUpdate(BaseSchema):
    """Schema for updating a milestone."""
    
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    sequence_number: Optional[int] = Field(None, ge=1)
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    evidence: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


class ProjectMilestoneResponse(BaseSchema):
    """Schema for milestone response."""
    
    id: UUID
    project_id: UUID
    title: str
    description: Optional[str]
    sequence_number: int
    status: MilestoneStatus
    planned_start_date: Optional[date]
    planned_end_date: Optional[date]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    evidence: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# ==================== IMPACT SCHEMAS ====================

class ImpactMetricCreate(BaseSchema):
    """Schema for creating impact measurement."""
    
    metric_name: str = Field(..., min_length=3, max_length=200, description="Metric name")
    beneficiaries_count: Optional[int] = Field(None, ge=0, description="Number of beneficiaries")
    geographic_area: Optional[str] = Field(None, max_length=200, description="Geographic coverage area")
    deployment_date: Optional[date] = Field(None, description="Solution deployment date")
    baseline_value: Optional[float] = Field(None, description="Baseline (before) value")
    target_value: Optional[float] = Field(None, description="Target value")
    actual_value: Optional[float] = Field(None, description="Actual (after) value")
    unit: Optional[str] = Field(None, max_length=50, description="Measurement unit")
    impact_description: Optional[str] = Field(None, max_length=2000, description="Impact description")
    evidence_reference: Optional[str] = Field(None, max_length=500, description="Evidence file reference")
    sustainability_status: Optional[str] = Field(None, max_length=100, description="Sustainability status")


class ImpactMetricUpdate(BaseSchema):
    """Schema for updating impact measurement."""
    
    beneficiaries_count: Optional[int] = Field(None, ge=0)
    geographic_area: Optional[str] = Field(None, max_length=200)
    deployment_date: Optional[date] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    actual_value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    impact_description: Optional[str] = Field(None, max_length=2000)
    evidence_reference: Optional[str] = Field(None, max_length=500)
    sustainability_status: Optional[str] = Field(None, max_length=100)


class ImpactActionRequest(BaseSchema):
    """Schema for impact actions (verify/revise)."""
    
    comments: Optional[str] = Field(None, max_length=2000, description="Action comments")


class ImpactMetricResponse(BaseSchema):
    """Schema for impact metric response."""
    
    id: UUID
    project_id: UUID
    metric_name: str
    beneficiaries_count: Optional[int]
    geographic_area: Optional[str]
    deployment_date: Optional[date]
    baseline_value: Optional[float]
    target_value: Optional[float]
    actual_value: Optional[float]
    unit: Optional[str]
    impact_description: Optional[str]
    evidence_reference: Optional[str]
    sustainability_status: Optional[str]
    verification_status: VerificationStatus
    measured_at: Optional[datetime]
    submitted_by: Optional[UUID]
    verified_by: Optional[UUID]
    verified_at: Optional[datetime]
    review_comments: Optional[str]
    created_at: datetime
    updated_at: datetime
