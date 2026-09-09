"""
Industry collaboration and partnership routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.db.database import get_db
from app.schemas.industry import (
    IndustryMatchListResponse,
    PartnershipCreate,
    PartnershipResponse,
    PartnershipDetailResponse,
    PartnershipListResponse,
    PartnershipAccept,
    PartnershipDecline,
    PartnershipCancel,
    PartnershipActivate,
    PartnershipComplete,
    ContributionCreate,
    ContributionUpdate,
    ContributionResponse,
    ContributionCommit,
    ContributionDeliver,
    ContributionCancel,
    IndustryDashboardResponse
)
from app.schemas.base import MessageResponse
from app.services.industry_matching import IndustryMatchingEngine
from app.services.industry.partnership_service import PartnershipService
from app.services.industry.contribution_service import ContributionService
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.enums import PartnershipStatus, PartnershipType, UserRole
from app.models.partnership import Partnership


router = APIRouter(prefix="/api/v1", tags=["Industry Collaboration"])


# ==================== INDUSTRY MATCHING ====================

@router.post(
    "/projects/{project_id}/industry-match",
    response_model=IndustryMatchListResponse,
    summary="Trigger industry matching for project"
)
def match_industries_for_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find and rank suitable industry partners for a project.
    
    **Authorization:**
    - Government Officer
    - Platform Admin
    - University Admin (own university only)
    - Faculty (own university only)
    """
    try:
        engine = IndustryMatchingEngine(db)
        matches = engine.match_industries_for_project(project_id, save_results=True)
        
        return IndustryMatchListResponse(
            project_id=project_id,
            matches=[
                {
                    "industry_id": m["industry_id"],
                    "industry_name": m["industry"].organization_name,
                    "industry_type": m["industry"].type,
                    "overall_score": m["overall_score"],
                    "component_scores": m["component_scores"],
                    "evidence": m["evidence"],
                    "explanation": m["explanation"],
                    "matched_at": None
                }
                for m in matches
            ],
            total_matches=len(matches)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/projects/{project_id}/industry-matches",
    response_model=IndustryMatchListResponse,
    summary="Get saved industry matches for project"
)
def get_project_industry_matches(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve saved industry matching results.
    
    **Authorization:** Same as match trigger
    """
    try:
        engine = IndustryMatchingEngine(db)
        matches = engine.get_saved_matches(project_id)
        
        return IndustryMatchListResponse(
            project_id=project_id,
            matches=[
                {
                    "industry_id": m["industry_id"],
                    "industry_name": m["industry"].organization_name,
                    "industry_type": m["industry"].type,
                    "overall_score": m["overall_score"],
                    "component_scores": m["component_scores"],
                    "evidence": m["evidence"],
                    "explanation": m["explanation"],
                    "matched_at": m.get("matched_at")
                }
                for m in matches
            ],
            total_matches=len(matches)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ==================== PARTNERSHIP MANAGEMENT ====================

@router.post(
    "/projects/{project_id}/partnerships",
    response_model=PartnershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create partnership request"
)
def create_partnership_request(
    project_id: UUID,
    partnership_data: PartnershipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new partnership request to an industry partner.
    
    **Authorization:**
    - Government Officer
    - University Admin (own university)
    - Faculty (own university)
    """
    try:
        service = PartnershipService(db)
        partnership = service.create_partnership_request(
            project_id=project_id,
            industry_id=partnership_data.industry_id,
            current_user=current_user,
            partnership_type=partnership_data.partnership_type,
            objectives=partnership_data.objectives,
            requested_support=partnership_data.requested_support,
            expected_contribution=partnership_data.expected_contribution,
            proposed_duration=partnership_data.proposed_duration,
            notes=partnership_data.notes
        )
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/partnerships",
    response_model=PartnershipListResponse,
    summary="List partnerships"
)
def list_partnerships(
    project_id: Optional[UUID] = Query(None),
    industry_id: Optional[UUID] = Query(None),
    university_id: Optional[UUID] = Query(None),
    status_filter: Optional[PartnershipStatus] = Query(None, alias="status"),
    partnership_type: Optional[PartnershipType] = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List partnerships with filtering and pagination.
    
    **Authorization:**
    - Government/Admin: All partnerships
    - University users: Own university's partnerships
    - Industry users: Own organization's partnerships
    """
    try:
        service = PartnershipService(db)
        partnerships, total = service.list_partnerships(
            current_user=current_user,
            project_id=project_id,
            industry_id=industry_id,
            university_id=university_id,
            status=status_filter,
            partnership_type=partnership_type,
            page=page,
            page_size=page_size
        )
        
        return PartnershipListResponse(
            partnerships=partnerships,
            total=total,
            page=page,
            page_size=page_size
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/partnerships/{partnership_id}",
    response_model=PartnershipResponse,
    summary="Get partnership details"
)
def get_partnership(
    partnership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get partnership by ID."""
    try:
        service = PartnershipService(db)
        partnership = service.get_partnership(partnership_id, current_user)
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/accept",
    response_model=PartnershipResponse,
    summary="Accept partnership (Industry only)"
)
def accept_partnership(
    partnership_id: UUID,
    accept_data: PartnershipAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a partnership request.
    
    **Authorization:** Industry partner users only
    """
    try:
        service = PartnershipService(db)
        partnership = service.accept_partnership(
            partnership_id=partnership_id,
            current_user=current_user,
            notes=accept_data.notes
        )
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/decline",
    response_model=PartnershipResponse,
    summary="Decline partnership (Industry only)"
)
def decline_partnership(
    partnership_id: UUID,
    decline_data: PartnershipDecline,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decline a partnership request.
    
    **Authorization:** Industry partner users only
    """
    try:
        service = PartnershipService(db)
        partnership = service.decline_partnership(
            partnership_id=partnership_id,
            current_user=current_user,
            reason=decline_data.reason
        )
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/activate",
    response_model=PartnershipResponse,
    summary="Activate partnership"
)
def activate_partnership(
    partnership_id: UUID,
    activate_data: PartnershipActivate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activate an accepted partnership.
    
    **Authorization:** University or industry users
    """
    try:
        service = PartnershipService(db)
        partnership = service.activate_partnership(
            partnership_id=partnership_id,
            current_user=current_user,
            start_date=activate_data.start_date
        )
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/complete",
    response_model=PartnershipResponse,
    summary="Complete partnership"
)
def complete_partnership(
    partnership_id: UUID,
    complete_data: PartnershipComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark partnership as completed.
    
    **Authorization:** University or industry users
    """
    try:
        service = PartnershipService(db)
        partnership = service.complete_partnership(
            partnership_id=partnership_id,
            current_user=current_user,
            end_date=complete_data.end_date,
            notes=complete_data.notes
        )
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/cancel",
    response_model=PartnershipResponse,
    summary="Cancel partnership"
)
def cancel_partnership(
    partnership_id: UUID,
    cancel_data: PartnershipCancel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a partnership.
    
    **Authorization:** University or industry users
    """
    try:
        service = PartnershipService(db)
        partnership = service.cancel_partnership(
            partnership_id=partnership_id,
            current_user=current_user,
            reason=cancel_data.reason
        )
        return partnership
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== CONTRIBUTIONS ====================

@router.post(
    "/partnerships/{partnership_id}/contributions",
    response_model=ContributionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create contribution"
)
def create_contribution(
    partnership_id: UUID,
    contribution_data: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a partnership contribution record."""
    try:
        service = ContributionService(db)
        contribution = service.create_contribution(
            partnership_id=partnership_id,
            current_user=current_user,
            contribution_type=contribution_data.contribution_type,
            description=contribution_data.description,
            estimated_value=contribution_data.estimated_value,
            currency=contribution_data.currency
        )
        return contribution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/partnerships/{partnership_id}/contributions",
    response_model=List[ContributionResponse],
    summary="Get partnership contributions"
)
def get_partnership_contributions(
    partnership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all contributions for a partnership."""
    try:
        service = ContributionService(db)
        contributions = service.get_partnership_contributions(partnership_id, current_user)
        return contributions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/partnerships/{partnership_id}/contributions/{contribution_id}",
    response_model=ContributionResponse,
    summary="Update contribution"
)
def update_contribution(
    partnership_id: UUID,
    contribution_id: UUID,
    contribution_data: ContributionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update contribution details."""
    try:
        service = ContributionService(db)
        contribution = service.update_contribution(
            contribution_id=contribution_id,
            current_user=current_user,
            **contribution_data.dict(exclude_unset=True)
        )
        return contribution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/contributions/{contribution_id}/commit",
    response_model=ContributionResponse,
    summary="Commit contribution (Industry only)"
)
def commit_contribution(
    partnership_id: UUID,
    contribution_id: UUID,
    commit_data: ContributionCommit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark contribution as committed."""
    try:
        service = ContributionService(db)
        contribution = service.commit_contribution(
            contribution_id=contribution_id,
            current_user=current_user,
            committed_date=commit_data.committed_date
        )
        return contribution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/contributions/{contribution_id}/deliver",
    response_model=ContributionResponse,
    summary="Deliver contribution"
)
def deliver_contribution(
    partnership_id: UUID,
    contribution_id: UUID,
    deliver_data: ContributionDeliver,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark contribution as delivered."""
    try:
        service = ContributionService(db)
        contribution = service.deliver_contribution(
            contribution_id=contribution_id,
            current_user=current_user,
            delivered_date=deliver_data.delivered_date,
            evidence_reference=deliver_data.evidence_reference
        )
        return contribution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/partnerships/{partnership_id}/contributions/{contribution_id}/cancel",
    response_model=ContributionResponse,
    summary="Cancel contribution"
)
def cancel_contribution(
    partnership_id: UUID,
    contribution_id: UUID,
    cancel_data: ContributionCancel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a contribution."""
    try:
        service = ContributionService(db)
        contribution = service.cancel_contribution(
            contribution_id=contribution_id,
            current_user=current_user,
            reason=cancel_data.reason
        )
        return contribution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ==================== INDUSTRY DASHBOARD ====================

@router.get(
    "/industry/partnerships",
    response_model=List[PartnershipResponse],
    summary="Get industry partnerships dashboard"
)
def get_industry_partnerships(
    status_filter: Optional[PartnershipStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get partnerships for authenticated industry user's organization.
    
    **Authorization:** Industry users only (own organization)
    """
    # Verify user is industry
    user_roles = {ur.role.name for ur in current_user.roles}
    if UserRole.INDUSTRY not in user_roles and UserRole.CSR not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only industry users can access industry dashboard"
        )
    
    # Get industry_id from user profile
    if not hasattr(current_user, 'industry_profile') or not current_user.industry_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an industry organization"
        )
    
    industry_id = current_user.industry_profile.industry_id
    
    try:
        service = PartnershipService(db)
        partnerships, total = service.list_partnerships(
            current_user=current_user,
            industry_id=industry_id,
            status=status_filter,
            page=page,
            page_size=page_size
        )
        
        return partnerships
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/industry/projects",
    response_model=List[Dict[str, Any]],
    summary="Get industry-supported projects"
)
def get_industry_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get projects supported by authenticated industry user's organization.
    
    **Authorization:** Industry users only (own organization)
    """
    # Verify user is industry
    user_roles = {ur.role.name for ur in current_user.roles}
    if UserRole.INDUSTRY not in user_roles and UserRole.CSR not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only industry users can access industry dashboard"
        )
    
    # Get industry_id from user profile
    if not hasattr(current_user, 'industry_profile') or not current_user.industry_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an industry organization"
        )
    
    industry_id = current_user.industry_profile.industry_id
    
    try:
        # Get partnerships for this industry
        partnerships = db.query(Partnership).filter(
            Partnership.industry_id == industry_id,
            Partnership.status.in_([
                PartnershipStatus.ACCEPTED,
                PartnershipStatus.ACTIVE,
                PartnershipStatus.COMPLETED
            ])
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Build project summary
        projects = []
        for partnership in partnerships:
            project = partnership.project
            university = project.university if project.university else None
            challenge = project.challenge if project.challenge else None
            
            projects.append({
                "project_id": str(project.id),
                "project_code": project.project_code,
                "project_name": project.name,
                "university_name": university.name if university else "Unknown",
                "challenge_title": challenge.title if challenge else "Unknown",
                "project_status": project.status.value,
                "partnership_type": partnership.partnership_type.value,
                "partnership_status": partnership.status.value,
                "partnership_start_date": partnership.start_date.isoformat() if partnership.start_date else None,
                "partnership_end_date": partnership.end_date.isoformat() if partnership.end_date else None
            })
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
