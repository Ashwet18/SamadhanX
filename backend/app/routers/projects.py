"""
Project lifecycle management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date

from app.db.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectDashboardResponse,
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse,
    ProjectProposalCreate,
    ProjectProposalUpdate,
    ProjectProposalResponse,
    ProjectMilestoneCreate,
    ProjectMilestoneUpdate,
    ProjectMilestoneResponse,
    ImpactMetricCreate,
    ImpactMetricUpdate,
    ImpactMetricResponse,
    ProjectStatusUpdate,
    ProposalActionRequest,
    ImpactActionRequest
)
from app.schemas.base import MessageResponse
from app.services.projects.project_service import ProjectService
from app.services.projects.team_service import TeamService
from app.services.projects.proposal_service import ProposalService
from app.services.projects.milestone_service import MilestoneService
from app.services.projects.impact_service import ImpactService
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.enums import ProjectStatus, UserRole


router = APIRouter(prefix="/api/v1", tags=["Projects"])


# ==================== PROJECT CRUD ====================

@router.post(
    "/challenges/{challenge_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project from accepted assignment"
)
def create_project(
    challenge_id: UUID,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project from an ACCEPTED challenge assignment.
    
    **Requirements:**
    - User must have an ACCEPTED assignment for this challenge
    - No active project can exist for this assignment
    - Generates unique project code: PRJ-JH-YYYY-XXXXX
    """
    try:
        service = ProjectService(db)
        project = service.create_project(
            challenge_id=challenge_id,
            current_user=current_user,
            name=project_data.name,
            description=project_data.description,
            objective=project_data.objective,
            expected_start_date=project_data.expected_start_date,
            expected_end_date=project_data.expected_end_date
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects",
    response_model=ProjectListResponse,
    summary="List projects with filtering"
)
def list_projects(
    status_filter: Optional[ProjectStatus] = Query(None, alias="status"),
    university_id: Optional[UUID] = Query(None),
    challenge_id: Optional[UUID] = Query(None),
    department_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List projects with pagination and filtering.
    
    **Authorization:**
    - Government/Admin: Can view projects across universities (with optional university_id filter)
    - University users: Only projects from their university
    - Faculty/Students: Only projects they have access to
    """
    try:
        service = ProjectService(db)
        projects, total = service.list_projects(
            current_user=current_user,
            status_filter=status_filter,
            university_id=university_id,
            challenge_id=challenge_id,
            department_id=department_id,
            page=page,
            page_size=page_size
        )
        return ProjectListResponse(
            projects=projects,
            total=total,
            page=page,
            page_size=page_size
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects/{project_id}",
    response_model=ProjectDashboardResponse,
    summary="Get project dashboard"
)
def get_project_dashboard(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive project dashboard with aggregates.
    
    **Includes:**
    - Project details
    - Challenge reference
    - University and department info
    - Lifecycle status
    - Team count
    - Milestone progress
    - Impact summary
    """
    try:
        service = ProjectService(db)
        dashboard = service.get_project_dashboard(
            project_id=project_id,
            current_user=current_user
        )
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Update project details"
)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project details.
    
    **Requirements:**
    - Must be project team member or university admin
    """
    try:
        service = ProjectService(db)
        project = service.update_project(
            project_id=project_id,
            current_user=current_user,
            **project_data.dict(exclude_unset=True)
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/status",
    response_model=ProjectResponse,
    summary="Update project status (lifecycle)"
)
def update_project_status(
    project_id: UUID,
    status_update: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project status using lifecycle state machine.
    
    **State Machine Validation:**
    - Only valid transitions are allowed
    - Uses lifecycle.is_valid_transition()
    - Cannot set arbitrary status directly
    """
    try:
        service = ProjectService(db)
        project = service.update_project_status(
            project_id=project_id,
            current_user=current_user,
            new_status=status_update.status,
            reason=status_update.reason
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== TEAM MANAGEMENT ====================

@router.post(
    "/projects/{project_id}/team",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add team member"
)
def add_team_member(
    project_id: UUID,
    member_data: ProjectMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a team member to the project.
    
    **Requirements:**
    - Must be project lead or university admin
    - User must belong to project's university
    """
    try:
        service = TeamService(db)
        member = service.add_team_member(
            project_id=project_id,
            current_user=current_user,
            user_id=member_data.user_id,
            role=member_data.role
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects/{project_id}/team",
    response_model=List[ProjectMemberResponse],
    summary="Get project team"
)
def get_project_team(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all team members for a project."""
    try:
        service = TeamService(db)
        members = service.get_project_team(project_id=project_id, current_user=current_user)
        return members
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/projects/{project_id}/team/{member_id}",
    response_model=ProjectMemberResponse,
    summary="Update team member"
)
def update_team_member(
    project_id: UUID,
    member_id: UUID,
    member_data: ProjectMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team member role."""
    try:
        service = TeamService(db)
        member = service.update_team_member(
            member_id=member_id,
            current_user=current_user,
            role=member_data.role
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/projects/{project_id}/team/{member_id}",
    response_model=MessageResponse,
    summary="Remove team member"
)
def remove_team_member(
    project_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a team member from the project."""
    try:
        service = TeamService(db)
        service.remove_team_member(member_id=member_id, current_user=current_user)
        return MessageResponse(message="Team member removed successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== PROPOSAL WORKFLOW ====================

@router.post(
    "/projects/{project_id}/proposal",
    response_model=ProjectProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project proposal"
)
def create_proposal(
    project_id: UUID,
    proposal_data: ProjectProposalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a project proposal (or update existing draft)."""
    try:
        service = ProposalService(db)
        proposal = service.create_or_update_proposal(
            project_id=project_id,
            current_user=current_user,
            **proposal_data.dict()
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects/{project_id}/proposal",
    response_model=ProjectProposalResponse,
    summary="Get project proposal"
)
def get_proposal(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the project proposal."""
    try:
        service = ProposalService(db)
        proposal = service.get_proposal(project_id=project_id, current_user=current_user)
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/projects/{project_id}/proposal",
    response_model=ProjectProposalResponse,
    summary="Update project proposal"
)
def update_proposal(
    project_id: UUID,
    proposal_data: ProjectProposalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project proposal (DRAFT only)."""
    try:
        service = ProposalService(db)
        proposal = service.update_proposal(
            project_id=project_id,
            current_user=current_user,
            **proposal_data.dict(exclude_unset=True)
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/proposal/submit",
    response_model=ProjectProposalResponse,
    summary="Submit proposal for review"
)
def submit_proposal(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit proposal for government review."""
    try:
        service = ProposalService(db)
        proposal = service.submit_proposal(project_id=project_id, current_user=current_user)
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/proposal/approve",
    response_model=ProjectProposalResponse,
    summary="Approve proposal (Government only)"
)
def approve_proposal(
    project_id: UUID,
    action_data: ProposalActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve project proposal (Government only)."""
    try:
        service = ProposalService(db)
        proposal = service.approve_proposal(
            project_id=project_id,
            current_user=current_user,
            comments=action_data.comments
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/proposal/request-revision",
    response_model=ProjectProposalResponse,
    summary="Request proposal revision (Government only)"
)
def request_proposal_revision(
    project_id: UUID,
    action_data: ProposalActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request revisions to proposal (Government only)."""
    if not action_data.comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are required when requesting revisions"
        )
    
    try:
        service = ProposalService(db)
        proposal = service.request_revision(
            project_id=project_id,
            current_user=current_user,
            comments=action_data.comments
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/proposal/reject",
    response_model=ProjectProposalResponse,
    summary="Reject proposal (Government only)"
)
def reject_proposal(
    project_id: UUID,
    action_data: ProposalActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject project proposal (Government only)."""
    if not action_data.comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are required when rejecting"
        )
    
    try:
        service = ProposalService(db)
        proposal = service.reject_proposal(
            project_id=project_id,
            current_user=current_user,
            comments=action_data.comments
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== MILESTONE MANAGEMENT ====================

@router.post(
    "/projects/{project_id}/milestones",
    response_model=ProjectMilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create milestone"
)
def create_milestone(
    project_id: UUID,
    milestone_data: ProjectMilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a project milestone."""
    try:
        service = MilestoneService(db)
        milestone = service.create_milestone(
            project_id=project_id,
            current_user=current_user,
            **milestone_data.dict()
        )
        return milestone
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects/{project_id}/milestones",
    response_model=List[ProjectMilestoneResponse],
    summary="Get project milestones"
)
def get_project_milestones(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all milestones for a project."""
    try:
        service = MilestoneService(db)
        milestones = service.get_project_milestones(project_id=project_id, current_user=current_user)
        return milestones
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/projects/{project_id}/milestones/{milestone_id}",
    response_model=ProjectMilestoneResponse,
    summary="Update milestone"
)
def update_milestone(
    project_id: UUID,
    milestone_id: UUID,
    milestone_data: ProjectMilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a milestone."""
    try:
        service = MilestoneService(db)
        milestone = service.update_milestone(
            milestone_id=milestone_id,
            current_user=current_user,
            **milestone_data.dict(exclude_unset=True)
        )
        return milestone
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/milestones/{milestone_id}/complete",
    response_model=ProjectMilestoneResponse,
    summary="Complete milestone"
)
def complete_milestone(
    project_id: UUID,
    milestone_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark milestone as completed."""
    try:
        service = MilestoneService(db)
        milestone = service.complete_milestone(milestone_id=milestone_id, current_user=current_user)
        return milestone
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== IMPACT MEASUREMENT ====================

@router.post(
    "/projects/{project_id}/impact",
    response_model=ImpactMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create/update impact measurement"
)
def create_or_update_impact(
    project_id: UUID,
    impact_data: ImpactMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update impact measurement."""
    try:
        service = ImpactService(db)
        impact = service.create_or_update_impact(
            project_id=project_id,
            current_user=current_user,
            **impact_data.dict()
        )
        return impact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects/{project_id}/impact",
    response_model=List[ImpactMetricResponse],
    summary="Get project impact measurements"
)
def get_project_impact(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all impact measurements for a project."""
    try:
        service = ImpactService(db)
        impacts = service.get_project_impact(project_id=project_id, current_user=current_user)
        return impacts
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/projects/{project_id}/impact/{impact_id}",
    response_model=ImpactMetricResponse,
    summary="Update impact measurement"
)
def update_impact(
    project_id: UUID,
    impact_id: UUID,
    impact_data: ImpactMetricUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update impact measurement (re-create with updated data)."""
    try:
        service = ImpactService(db)
        # Get existing impact to retrieve metric_name
        from app.models.platform import ImpactMetric
        existing = db.query(ImpactMetric).filter(ImpactMetric.id == impact_id).first()
        if not existing:
            raise ValueError("Impact metric not found")
        
        # Update using create_or_update_impact
        impact = service.create_or_update_impact(
            project_id=project_id,
            current_user=current_user,
            metric_name=existing.metric_name,
            **impact_data.dict(exclude_unset=True)
        )
        return impact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/impact/{impact_id}/submit",
    response_model=ImpactMetricResponse,
    summary="Submit impact for verification"
)
def submit_impact(
    project_id: UUID,
    impact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit impact measurement for government verification."""
    try:
        service = ImpactService(db)
        impact = service.submit_impact(impact_id=impact_id, current_user=current_user)
        return impact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/impact/{impact_id}/verify",
    response_model=ImpactMetricResponse,
    summary="Verify impact (Government only)"
)
def verify_impact(
    project_id: UUID,
    impact_id: UUID,
    action_data: ImpactActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify impact measurement (Government only)."""
    try:
        service = ImpactService(db)
        impact = service.verify_impact(
            impact_id=impact_id,
            current_user=current_user,
            comments=action_data.comments
        )
        return impact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/projects/{project_id}/impact/{impact_id}/request-revision",
    response_model=ImpactMetricResponse,
    summary="Request impact revision (Government only)"
)
def request_impact_revision(
    project_id: UUID,
    impact_id: UUID,
    action_data: ImpactActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request revisions to impact measurement (Government only)."""
    if not action_data.comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are required when requesting revisions"
        )
    
    try:
        service = ImpactService(db)
        impact = service.request_revision(
            impact_id=impact_id,
            current_user=current_user,
            comments=action_data.comments
        )
        return impact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
