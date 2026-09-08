"""
Challenge routes for citizen challenge submission and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeListResponse,
    ChallengeMediaResponse,
    ChallengeFilterParams
)
from app.schemas.base import MessageResponse
from app.services.challenge_service import ChallengeService
from app.core.dependencies import (
    get_current_user,
    require_citizen,
    require_admin_or_government
)
from app.models.user import User
from app.models.enums import ChallengeStatus, PriorityLevel


router = APIRouter(prefix="/api/v1/challenges", tags=["Challenges"])


@router.post(
    "",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new challenge",
    description="Submit a new societal challenge. Requires CITIZEN role."
)
def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """
    Create a new challenge.
    
    **Requirements:**
    - Must be authenticated as CITIZEN
    - Title: 10-500 characters
    - Description: 30-5000 characters
    - At least one category
    - If GPS coordinates provided, both latitude and longitude required
    
    **Initial Status:** SUBMITTED
    
    **Returns:**
    - Challenge with generated unique code (format: CH-JH-YYYY-XXXXX)
    - Categories linked
    - Ready for government review
    """
    service = ChallengeService(db)
    challenge = service.create_challenge(challenge_data, current_user)
    return service.build_challenge_response(challenge)


@router.get(
    "",
    response_model=ChallengeListResponse,
    summary="List all challenges",
    description="Get paginated list of challenges with optional filters."
)
def list_challenges(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: Optional[ChallengeStatus] = Query(None, description="Filter by status"),
    district: Optional[str] = Query(None, description="Filter by district"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    priority_level: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db)
):
    """
    List challenges with filtering and pagination.
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - status: Filter by challenge status
    - district: Filter by district name
    - category_id: Filter by category UUID
    - priority_level: Filter by priority level
    
    **Returns:**
    - Paginated list with metadata (total, pages, has_next, has_previous)
    """
    service = ChallengeService(db)
    return service.list_challenges(
        page=page,
        page_size=page_size,
        status=status,
        district=district,
        category_id=category_id,
        priority_level=priority_level
    )


@router.get(
    "/my",
    response_model=ChallengeListResponse,
    summary="Get my challenges",
    description="Get challenges submitted by the authenticated citizen."
)
def get_my_challenges(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[ChallengeStatus] = Query(None),
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """
    Get challenges submitted by current user.
    
    **Requirements:**
    - Must be authenticated as CITIZEN
    
    **Query Parameters:**
    - page: Page number
    - page_size: Items per page
    - status: Optional status filter
    
    **Returns:**
    - Only challenges submitted by the authenticated user
    - Paginated with metadata
    """
    service = ChallengeService(db)
    return service.get_my_challenges(
        current_user=current_user,
        page=page,
        page_size=page_size,
        status=status
    )


@router.get(
    "/review-queue",
    response_model=ChallengeListResponse,
    summary="Get challenges in review queue",
    description="Get challenges pending government review. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_review_queue(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    district: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None),
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Get challenges in review queue.
    
    **Requirements:**
    - Must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Returns:**
    - Challenges with status SUBMITTED or PENDING_REVIEW
    - Ordered by creation date (newest first)
    - Paginated with metadata
    
    **Note:** Validation actions not yet implemented in this endpoint.
    """
    service = ChallengeService(db)
    return service.get_review_queue(
        page=page,
        page_size=page_size,
        district=district,
        category_id=category_id
    )


@router.get(
    "/{challenge_id}",
    response_model=ChallengeResponse,
    summary="Get challenge by ID",
    description="Get detailed challenge information including categories and media."
)
def get_challenge(
    challenge_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get challenge by ID.
    
    **Returns:**
    - Complete challenge details
    - Associated categories
    - Uploaded media files
    - Submitter information
    
    **Note:** Currently public. Will be restricted based on challenge visibility in future.
    """
    service = ChallengeService(db)
    challenge = service.get_challenge(challenge_id)
    return service.build_challenge_response(challenge)


@router.patch(
    "/{challenge_id}",
    response_model=ChallengeResponse,
    summary="Update challenge",
    description="Update challenge details. Only owner can edit, and only in DRAFT or SUBMITTED status."
)
def update_challenge(
    challenge_id: UUID,
    update_data: ChallengeUpdate,
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """
    Update challenge.
    
    **Requirements:**
    - Must be the challenge owner
    - Challenge status must be DRAFT or SUBMITTED
    
    **Editable Fields:**
    - title, description, district, block, village
    - latitude, longitude, affected_population
    - categories
    
    **Not Editable:**
    - status, priority_score, priority_level
    - submitted_by, AI analysis results
    
    **Restrictions:**
    - Cannot edit once status reaches PENDING_REVIEW or later
    - Preserves audit trail
    """
    service = ChallengeService(db)
    challenge = service.update_challenge(challenge_id, update_data, current_user)
    return service.build_challenge_response(challenge)


@router.delete(
    "/{challenge_id}",
    response_model=MessageResponse,
    summary="Delete challenge",
    description="Delete challenge. Only drafts can be deleted."
)
def delete_challenge(
    challenge_id: UUID,
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """
    Delete challenge.
    
    **Requirements:**
    - Must be the challenge owner
    - Challenge status must be DRAFT
    
    **Restrictions:**
    - SUBMITTED and later challenges cannot be deleted
    - This preserves audit trail and government review process
    
    **Returns:**
    - Success message
    """
    service = ChallengeService(db)
    service.delete_challenge(challenge_id, current_user)
    
    return MessageResponse(
        message="Challenge deleted successfully",
        success=True
    )


@router.post(
    "/{challenge_id}/media",
    response_model=ChallengeMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload challenge media",
    description="Upload evidence file (image, video, audio, or document) for a challenge."
)
async def upload_media(
    challenge_id: UUID,
    file: UploadFile = File(..., description="Media file to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload media file for challenge.
    
    **Requirements:**
    - Must be challenge owner, GOVERNMENT_OFFICER, or PLATFORM_ADMIN
    
    **Supported Types:**
    - **Images:** JPEG, PNG, WebP (max 10 MB)
    - **Videos:** MP4, WebM (max 50 MB)
    - **Audio:** MP3, WAV, OGG (max 20 MB)
    - **Documents:** PDF (max 10 MB)
    
    **Security:**
    - MIME type validation
    - File size validation
    - Safe filename generation
    - Files never executed
    
    **Returns:**
    - Media record with file URL
    """
    service = ChallengeService(db)
    media = await service.upload_media(challenge_id, file, current_user)
    
    return ChallengeMediaResponse(
        id=media.id,
        media_type=media.media_type,
        file_url=media.file_url,
        file_name=media.file_name,
        mime_type=media.mime_type,
        file_size=media.file_size,
        created_at=media.created_at
    )


@router.get(
    "/{challenge_id}/media",
    response_model=list[ChallengeMediaResponse],
    summary="Get challenge media",
    description="Get all media files associated with a challenge."
)
def get_challenge_media(
    challenge_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all media files for a challenge.
    
    **Returns:**
    - List of media files with URLs
    - File metadata (size, type, upload date)
    """
    service = ChallengeService(db)
    challenge = service.get_challenge(challenge_id)
    
    return [
        ChallengeMediaResponse(
            id=m.id,
            media_type=m.media_type,
            file_url=m.file_url,
            file_name=m.file_name,
            mime_type=m.mime_type,
            file_size=m.file_size,
            created_at=m.created_at
        )
        for m in challenge.media
    ]


@router.delete(
    "/{challenge_id}/media/{media_id}",
    response_model=MessageResponse,
    summary="Delete challenge media",
    description="Delete a media file from a challenge."
)
def delete_media(
    challenge_id: UUID,
    media_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete media file.
    
    **Requirements:**
    - Must be challenge owner, GOVERNMENT_OFFICER, or PLATFORM_ADMIN
    
    **Actions:**
    - Deletes file from storage
    - Removes database record
    - Creates audit log
    
    **Returns:**
    - Success message
    """
    service = ChallengeService(db)
    service.delete_media(challenge_id, media_id, current_user)
    
    return MessageResponse(
        message="Media deleted successfully",
        success=True
    )


@router.post(
    "/{challenge_id}/analyze",
    summary="Analyze challenge with AI",
    description="Run AI analysis pipeline for a challenge. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def analyze_challenge(
    challenge_id: UUID,
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Run AI analysis pipeline for a challenge.
    
    **Requirements:**
    - Must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Pipeline:**
    1. Load challenge
    2. AI analysis (domain, severity, urgency, skills)
    3. Calculate priority score
    4. Generate embedding
    5. Search for semantic duplicates
    6. Store results
    7. Update challenge status to PENDING_REVIEW
    
    **Returns:**
    - Complete analysis results
    - Priority score and level
    - Duplicate candidates with similarity scores
    
    **Note:**
    - AI recommendations require human review
    - Duplicates are marked as PENDING_REVIEW
    - Original challenge is never automatically rejected
    """
    from app.services.ai import ChallengeAIService
    
    try:
        ai_service = ChallengeAIService(db)
        result = ai_service.analyze(challenge_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.get(
    "/{challenge_id}/ai-analysis",
    summary="Get AI analysis results",
    description="Get AI analysis results for a challenge. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_ai_analysis(
    challenge_id: UUID,
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Get AI analysis results for a challenge.
    
    **Requirements:**
    - Must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Returns:**
    - AI analysis summary
    - Classification and domain
    - Severity and urgency scores
    - Extracted skills
    - Solution recommendations
    - Confidence scores
    
    **Note:**
    - Returns 404 if analysis has not been run yet
    """
    from app.models.challenge import ChallengeAIAnalysis
    
    service = ChallengeService(db)
    challenge = service.get_challenge(challenge_id)
    
    if not challenge.ai_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI analysis not found for this challenge"
        )
    
    analysis = challenge.ai_analysis
    
    return {
        "challenge_id": str(challenge.id),
        "challenge_code": challenge.challenge_code,
        "model_name": analysis.model_name,
        "model_version": analysis.model_version,
        "summary": analysis.summary,
        "primary_domain": analysis.primary_domain,
        "severity_score": analysis.severity_score,
        "urgency_score": analysis.urgency_score,
        "affected_population_estimate": analysis.affected_population_estimate,
        "extracted_skills": analysis.extracted_skills,
        "recommended_solution_types": analysis.recommended_solution_types,
        "confidence_score": analysis.confidence_score,
        "analyzed_at": analysis.created_at
    }


@router.get(
    "/{challenge_id}/duplicates",
    summary="Get duplicate candidates",
    description="Get potential duplicate challenges. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_duplicate_candidates(
    challenge_id: UUID,
    current_user: User = Depends(require_admin_or_government),
    db: Session = Depends(get_db)
):
    """
    Get duplicate candidates for a challenge.
    
    **Requirements:**
    - Must be GOVERNMENT_OFFICER or PLATFORM_ADMIN
    
    **Returns:**
    - List of similar challenges
    - Similarity scores (0.0 - 1.0)
    - Status of each duplicate link
    
    **Similarity Levels:**
    - >= 0.90: HIGH_CONFIDENCE
    - 0.80-0.89: POSSIBLE
    - < 0.80: not shown
    
    **Note:**
    - All duplicates initially marked PENDING_REVIEW
    - Government officer must confirm or dismiss
    """
    from app.models.challenge import ChallengeDuplicate, Challenge
    
    service = ChallengeService(db)
    challenge = service.get_challenge(challenge_id)
    
    duplicates = db.query(ChallengeDuplicate).filter(
        ChallengeDuplicate.challenge_id == challenge_id
    ).all()
    
    results = []
    for dup in duplicates:
        similar_challenge = db.query(Challenge).filter(
            Challenge.id == dup.similar_challenge_id
        ).first()
        
        if similar_challenge:
            results.append({
                "duplicate_id": str(dup.id),
                "challenge_id": str(similar_challenge.id),
                "challenge_code": similar_challenge.challenge_code,
                "title": similar_challenge.title,
                "status": similar_challenge.status.value,
                "similarity_score": dup.similarity_score,
                "duplicate_status": dup.status.value,
                "reviewed_by": str(dup.reviewed_by) if dup.reviewed_by else None,
                "created_at": dup.created_at
            })
    
    return {
        "challenge_id": str(challenge_id),
        "challenge_code": challenge.challenge_code,
        "duplicates": results,
        "total": len(results)
    }
