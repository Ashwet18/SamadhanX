"""
University matching routes for challenge assignments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.schemas.base import MessageResponse
from app.services.matching import UniversityMatchingEngine
from app.models.challenge import Challenge, ChallengeAssignment
from app.models.platform import Notification
from app.models.user import User
from app.models.enums import ChallengeStatus, AssignmentStatus
from app.core.dependencies import (
    get_current_user,
    require_admin_or_government
)


router = APIRouter(prefix="/api/v1", tags=["Matching"])


@router.post(
    "/challenges/{challenge_id}/match",
    summary="Match challenge to universities",
    description="Run university matching algorithm for a VALIDATED challenge. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def match_challenge(
    challenge_id: UUID,
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Match a validated challenge to suitable universities.
    
    **Requirements:**
    - Challenge must be VALIDATED
    - AI analysis must exist
    - User must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Process:**
    1. Load challenge and AI analysis
    2. Extract required expertise
    3. Find candidate universities
    4. Score each candidate across 6 factors
    5. Rank by weighted score
    6. Store top recommendations
    
    **Scoring Factors:**
    - Expertise Match (40%)
    - Faculty Availability (20%)
    - Infrastructure (15%)
    - Previous Projects (10%)
    - Location (10%)
    - Industry Connections (5%)
    
    **Returns:**
    - Ranked list of universities with scores
    - Component score breakdown
    - Explainable evidence for each match
    """
    
    try:
        engine = UniversityMatchingEngine(db)
        result = engine.match_challenge(challenge_id, current_user.id)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {str(e)}"
        )


@router.get(
    "/challenges/{challenge_id}/matches",
    summary="Get university matches",
    description="Get ranked university recommendations for a challenge. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_challenge_matches(
    challenge_id: UUID,
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Get university matches for a challenge.
    
    **Requirements:**
    - User must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Returns:**
    - List of university assignments with scores and status
    - Ranked by assignment score
    - Includes explainable reasoning
    """
    
    # Check challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge {challenge_id} not found"
        )
    
    # Get assignments
    assignments = db.query(ChallengeAssignment).filter(
        ChallengeAssignment.challenge_id == challenge_id
    ).order_by(ChallengeAssignment.assignment_score.desc()).all()
    
    # Build response
    matches = []
    for rank, assignment in enumerate(assignments, start=1):
        matches.append({
            "rank": rank,
            "university": {
                "id": str(assignment.university.id),
                "name": assignment.university.name,
                "code": assignment.university.code,
                "district": assignment.university.district,
                "state": assignment.university.state
            },
            "score": assignment.assignment_score,
            "reason": assignment.reason,
            "assignment_status": assignment.status.value,
            "assigned_by": str(assignment.assigned_by) if assignment.assigned_by else None,
            "created_at": assignment.created_at.isoformat() if assignment.created_at else None
        })
    
    return {
        "challenge_id": str(challenge_id),
        "challenge_code": challenge.challenge_code,
        "challenge_status": challenge.status.value,
        "matches": matches,
        "total": len(matches)
    }


@router.post(
    "/challenges/{challenge_id}/matches/{university_id}/invite",
    summary="Invite university to challenge",
    description="Invite a university to work on a challenge. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def invite_university(
    challenge_id: UUID,
    university_id: UUID,
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Invite a university to work on a challenge.
    
    **Requirements:**
    - Challenge must be VALIDATED
    - Assignment must exist (from matching)
    - User must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Actions:**
    - Updates assignment status to INVITED
    - Creates notification for university administrators
    - Updates challenge status to UNIVERSITY_INVITED (if first invitation)
    
    **Returns:**
    - Success message
    """
    
    # Check challenge
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge {challenge_id} not found"
        )
    
    if challenge.status != ChallengeStatus.VALIDATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Challenge must be VALIDATED to invite universities. Current status: {challenge.status.value}"
        )
    
    # Check assignment
    assignment = db.query(ChallengeAssignment).filter(
        ChallengeAssignment.challenge_id == challenge_id,
        ChallengeAssignment.university_id == university_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No assignment found for university {university_id}. Run matching first."
        )
    
    # Update assignment status
    assignment.status = AssignmentStatus.INVITED
    
    # Update challenge status if first invitation
    if challenge.status == ChallengeStatus.VALIDATED:
        challenge.status = ChallengeStatus.UNIVERSITY_INVITED
    
    # Create notification for university administrators
    # Get university admin users
    from app.models.user import User as UserModel
    from app.models.enums import UserRole
    
    university_admins = db.query(UserModel).filter(
        UserModel.role == UserRole.UNIVERSITY_ADMIN
        # TODO: Filter by specific university when user-university link exists
    ).all()
    
    for admin in university_admins:
        notification = Notification(
            user_id=admin.id,
            type="CHALLENGE_INVITATION",
            title="New Challenge Opportunity",
            message=f"Your university has been invited to work on challenge: {challenge.title} ({challenge.challenge_code}). "
                   f"Matching score: {assignment.assignment_score}/100.",
            reference_type="CHALLENGE",
            reference_id=challenge_id,
            is_read=False
        )
        db.add(notification)
    
    db.commit()
    
    return MessageResponse(
        message=f"University {assignment.university.name} invited successfully",
        success=True
    )


@router.post(
    "/challenges/{challenge_id}/matches/{university_id}/accept",
    summary="Accept challenge invitation",
    description="Accept a challenge invitation. Requires UNIVERSITY_ADMIN role."
)
def accept_invitation(
    challenge_id: UUID,
    university_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a challenge invitation.
    
    **Requirements:**
    - User must be UNIVERSITY_ADMIN
    - Assignment must be INVITED or RECOMMENDED
    
    **Actions:**
    - Updates assignment status to ACCEPTED
    - Updates challenge status to ACCEPTED (if appropriate)
    - Creates notification for government
    
    **Returns:**
    - Success message
    """
    
    # Check authorization
    from app.models.enums import UserRole
    if current_user.role != UserRole.UNIVERSITY_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only UNIVERSITY_ADMIN can accept invitations"
        )
    
    # Check assignment
    assignment = db.query(ChallengeAssignment).filter(
        ChallengeAssignment.challenge_id == challenge_id,
        ChallengeAssignment.university_id == university_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check status
    if assignment.status not in [AssignmentStatus.INVITED, AssignmentStatus.RECOMMENDED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept assignment with status: {assignment.status.value}"
        )
    
    # Update assignment
    assignment.status = AssignmentStatus.ACCEPTED
    
    # Update challenge status
    challenge = assignment.challenge
    if challenge.status == ChallengeStatus.UNIVERSITY_INVITED:
        challenge.status = ChallengeStatus.ACCEPTED
    
    db.commit()
    
    return MessageResponse(
        message=f"Challenge invitation accepted successfully",
        success=True
    )


@router.post(
    "/challenges/{challenge_id}/matches/{university_id}/decline",
    summary="Decline challenge invitation",
    description="Decline a challenge invitation. Requires UNIVERSITY_ADMIN role."
)
def decline_invitation(
    challenge_id: UUID,
    university_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decline a challenge invitation.
    
    **Requirements:**
    - User must be UNIVERSITY_ADMIN
    - Assignment must be INVITED or RECOMMENDED
    
    **Actions:**
    - Updates assignment status to DECLINED
    
    **Returns:**
    - Success message
    """
    
    # Check authorization
    from app.models.enums import UserRole
    if current_user.role != UserRole.UNIVERSITY_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only UNIVERSITY_ADMIN can decline invitations"
        )
    
    # Check assignment
    assignment = db.query(ChallengeAssignment).filter(
        ChallengeAssignment.challenge_id == challenge_id,
        ChallengeAssignment.university_id == university_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check status
    if assignment.status not in [AssignmentStatus.INVITED, AssignmentStatus.RECOMMENDED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot decline assignment with status: {assignment.status.value}"
        )
    
    # Update assignment
    assignment.status = AssignmentStatus.DECLINED
    
    db.commit()
    
    return MessageResponse(
        message=f"Challenge invitation declined",
        success=True
    )


@router.get(
    "/universities/{university_id}/recommended-challenges",
    summary="Get recommended challenges for university",
    description="Get challenges recommended or invited to a university. Requires UNIVERSITY_ADMIN or FACULTY role."
)
def get_university_challenges(
    university_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get challenges recommended or invited to a university.
    
    **Requirements:**
    - User must be UNIVERSITY_ADMIN or FACULTY
    
    **Returns:**
    - List of challenges with assignment details
    - Filtered by RECOMMENDED, INVITED, or ACCEPTED status
    """
    
    # Check authorization
    from app.models.enums import UserRole
    if current_user.role not in [UserRole.UNIVERSITY_ADMIN, UserRole.FACULTY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only UNIVERSITY_ADMIN or FACULTY can view university challenges"
        )
    
    # Get assignments
    assignments = db.query(ChallengeAssignment).filter(
        ChallengeAssignment.university_id == university_id,
        ChallengeAssignment.status.in_([
            AssignmentStatus.RECOMMENDED,
            AssignmentStatus.INVITED,
            AssignmentStatus.ACCEPTED
        ])
    ).order_by(ChallengeAssignment.assignment_score.desc()).all()
    
    # Build response
    challenges = []
    for assignment in assignments:
        challenge = assignment.challenge
        
        challenges.append({
            "challenge_id": str(challenge.id),
            "challenge_code": challenge.challenge_code,
            "title": challenge.title,
            "description": challenge.description,
            "district": challenge.district,
            "status": challenge.status.value,
            "priority_level": challenge.priority_level.value if challenge.priority_level else None,
            "assignment_score": assignment.assignment_score,
            "assignment_status": assignment.status.value,
            "reason": assignment.reason,
            "created_at": challenge.created_at.isoformat() if challenge.created_at else None
        })
    
    return {
        "university_id": str(university_id),
        "challenges": challenges,
        "total": len(challenges)
    }
