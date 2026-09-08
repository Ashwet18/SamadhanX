"""
Challenge service for business logic and data operations.
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_
from fastapi import HTTPException, status, UploadFile
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import random

from app.models.challenge import Challenge, Category, ChallengeCategory, ChallengeMedia
from app.models.platform import AuditLog
from app.models.user import User
from app.models.enums import ChallengeStatus, PriorityLevel, MediaType, UserRole
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeListItem,
    ChallengeListResponse,
    CategoryResponse,
    ChallengeMediaResponse
)
from app.services.storage_service import storage_service


class ChallengeService:
    """Service for challenge management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_challenge_code(self) -> str:
        """
        Generate unique challenge code.
        
        Format: CH-JH-YYYY-XXXXX
        Example: CH-JH-2026-00001
        
        Returns:
            Unique challenge code
        """
        year = datetime.now().year
        
        # Find the highest existing code for this year
        prefix = f"CH-JH-{year}-"
        
        highest = self.db.execute(
            select(Challenge.challenge_code)
            .where(Challenge.challenge_code.like(f"{prefix}%"))
            .order_by(Challenge.challenge_code.desc())
        ).scalar()
        
        if highest:
            # Extract number and increment
            number_part = highest.split('-')[-1]
            next_number = int(number_part) + 1
        else:
            # Start from 1
            next_number = 1
        
        # Generate code with padding
        challenge_code = f"{prefix}{next_number:05d}"
        
        # Verify uniqueness (should be guaranteed by DB constraint)
        existing = self.db.execute(
            select(Challenge).where(Challenge.challenge_code == challenge_code)
        ).scalar_one_or_none()
        
        if existing:
            # Collision detected, add random suffix
            challenge_code = f"{prefix}{next_number:05d}-{random.randint(10, 99)}"
        
        return challenge_code
    
    def create_challenge(
        self,
        challenge_data: ChallengeCreate,
        current_user: User
    ) -> Challenge:
        """
        Create a new challenge.
        
        Args:
            challenge_data: Challenge creation data
            current_user: Authenticated user (must be CITIZEN)
            
        Returns:
            Created challenge
            
        Raises:
            HTTPException: If validation fails or categories don't exist
        """
        # Verify categories exist
        categories = self.db.execute(
            select(Category).where(Category.id.in_(challenge_data.category_ids))
        ).scalars().all()
        
        if len(categories) != len(challenge_data.category_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more category IDs are invalid"
            )
        
        # Generate challenge code
        challenge_code = self.generate_challenge_code()
        
        # Create challenge
        challenge = Challenge(
            challenge_code=challenge_code,
            submitted_by=current_user.id,
            title=challenge_data.title,
            description=challenge_data.description,
            status=ChallengeStatus.SUBMITTED,
            district=challenge_data.district,
            block=challenge_data.block,
            village=challenge_data.village,
            latitude=challenge_data.latitude,
            longitude=challenge_data.longitude,
            affected_population=challenge_data.affected_population
        )
        
        self.db.add(challenge)
        self.db.flush()
        
        # Add category relationships
        for category in categories:
            challenge_category = ChallengeCategory(
                challenge_id=challenge.id,
                category_id=category.id
            )
            self.db.add(challenge_category)
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action="CHALLENGE_CREATED",
            entity_type="Challenge",
            entity_id=challenge.id,
            new_value={
                "challenge_code": challenge_code,
                "title": challenge_data.title,
                "district": challenge_data.district,
                "status": ChallengeStatus.SUBMITTED.value
            }
        )
        self.db.add(audit_log)
        
        self.db.commit()
        self.db.refresh(challenge)
        
        return challenge
    
    def get_challenge(
        self,
        challenge_id: UUID,
        current_user: Optional[User] = None
    ) -> Challenge:
        """
        Get challenge by ID with relationships loaded.
        
        Args:
            challenge_id: Challenge ID
            current_user: Optional current user for access control
            
        Returns:
            Challenge
            
        Raises:
            HTTPException: If challenge not found
        """
        challenge = self.db.execute(
            select(Challenge)
            .options(
                selectinload(Challenge.categories).selectinload(ChallengeCategory.category),
                selectinload(Challenge.media),
                selectinload(Challenge.submitted_by_user)
            )
            .where(Challenge.id == challenge_id)
        ).scalar_one_or_none()
        
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
        
        return challenge
    
    def list_challenges(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ChallengeStatus] = None,
        district: Optional[str] = None,
        category_id: Optional[UUID] = None,
        priority_level: Optional[PriorityLevel] = None
    ) -> ChallengeListResponse:
        """
        List challenges with filtering and pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            status: Filter by status
            district: Filter by district
            category_id: Filter by category
            priority_level: Filter by priority
            
        Returns:
            Paginated challenge list
        """
        # Build query
        query = select(Challenge)
        
        # Apply filters
        if status:
            query = query.where(Challenge.status == status)
        
        if district:
            query = query.where(Challenge.district == district)
        
        if category_id:
            query = query.join(Challenge.categories).where(
                ChallengeCategory.category_id == category_id
            )
        
        if priority_level:
            query = query.where(Challenge.priority_level == priority_level)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        query = query.order_by(Challenge.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        challenges = self.db.execute(query).scalars().all()
        
        # Build response items
        items = []
        for challenge in challenges:
            # Count categories and media
            category_count = len(challenge.categories)
            media_count = len(challenge.media)
            
            items.append(ChallengeListItem(
                id=challenge.id,
                challenge_code=challenge.challenge_code,
                title=challenge.title,
                status=challenge.status,
                priority_level=challenge.priority_level,
                district=challenge.district,
                affected_population=challenge.affected_population,
                category_count=category_count,
                media_count=media_count,
                created_at=challenge.created_at
            ))
        
        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size
        
        return ChallengeListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def get_my_challenges(
        self,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ChallengeStatus] = None
    ) -> ChallengeListResponse:
        """
        Get challenges submitted by current user.
        
        Args:
            current_user: Current user
            page: Page number
            page_size: Items per page
            status: Optional status filter
            
        Returns:
            Paginated challenge list
        """
        query = select(Challenge).where(Challenge.submitted_by == current_user.id)
        
        if status:
            query = query.where(Challenge.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        query = query.order_by(Challenge.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        challenges = self.db.execute(query).scalars().all()
        
        items = []
        for challenge in challenges:
            items.append(ChallengeListItem(
                id=challenge.id,
                challenge_code=challenge.challenge_code,
                title=challenge.title,
                status=challenge.status,
                priority_level=challenge.priority_level,
                district=challenge.district,
                affected_population=challenge.affected_population,
                category_count=len(challenge.categories),
                media_count=len(challenge.media),
                created_at=challenge.created_at
            ))
        
        total_pages = (total + page_size - 1) // page_size
        
        return ChallengeListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def get_review_queue(
        self,
        page: int = 1,
        page_size: int = 20,
        district: Optional[str] = None,
        category_id: Optional[UUID] = None
    ) -> ChallengeListResponse:
        """
        Get challenges in review queue for government officers.
        
        Args:
            page: Page number
            page_size: Items per page
            district: Optional district filter
            category_id: Optional category filter
            
        Returns:
            Paginated challenge list
        """
        # Challenges in review are SUBMITTED or PENDING_REVIEW
        query = select(Challenge).where(
            or_(
                Challenge.status == ChallengeStatus.SUBMITTED,
                Challenge.status == ChallengeStatus.PENDING_REVIEW
            )
        )
        
        if district:
            query = query.where(Challenge.district == district)
        
        if category_id:
            query = query.join(Challenge.categories).where(
                ChallengeCategory.category_id == category_id
            )
        
        # Get total
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        query = query.order_by(Challenge.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        challenges = self.db.execute(query).scalars().all()
        
        items = []
        for challenge in challenges:
            items.append(ChallengeListItem(
                id=challenge.id,
                challenge_code=challenge.challenge_code,
                title=challenge.title,
                status=challenge.status,
                priority_level=challenge.priority_level,
                district=challenge.district,
                affected_population=challenge.affected_population,
                category_count=len(challenge.categories),
                media_count=len(challenge.media),
                created_at=challenge.created_at
            ))
        
        total_pages = (total + page_size - 1) // page_size
        
        return ChallengeListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def update_challenge(
        self,
        challenge_id: UUID,
        update_data: ChallengeUpdate,
        current_user: User
    ) -> Challenge:
        """
        Update challenge.
        
        Args:
            challenge_id: Challenge ID
            update_data: Update data
            current_user: Current user (must be owner)
            
        Returns:
            Updated challenge
            
        Raises:
            HTTPException: If not authorized or status doesn't allow editing
        """
        challenge = self.get_challenge(challenge_id)
        
        # Check ownership
        if challenge.submitted_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own challenges"
            )
        
        # Check if status allows editing
        if challenge.status not in [ChallengeStatus.DRAFT, ChallengeStatus.SUBMITTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot edit challenge in status {challenge.status.value}"
            )
        
        # Store old values for audit
        old_value = {
            "title": challenge.title,
            "description": challenge.description,
            "district": challenge.district
        }
        
        # Update fields
        if update_data.title is not None:
            challenge.title = update_data.title
        if update_data.description is not None:
            challenge.description = update_data.description
        if update_data.district is not None:
            challenge.district = update_data.district
        if update_data.block is not None:
            challenge.block = update_data.block
        if update_data.village is not None:
            challenge.village = update_data.village
        if update_data.latitude is not None:
            challenge.latitude = update_data.latitude
        if update_data.longitude is not None:
            challenge.longitude = update_data.longitude
        if update_data.affected_population is not None:
            challenge.affected_population = update_data.affected_population
        
        # Update categories if provided
        if update_data.category_ids is not None:
            # Verify categories exist
            categories = self.db.execute(
                select(Category).where(Category.id.in_(update_data.category_ids))
            ).scalars().all()
            
            if len(categories) != len(update_data.category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more category IDs are invalid"
                )
            
            # Remove old categories
            self.db.execute(
                select(ChallengeCategory).where(ChallengeCategory.challenge_id == challenge.id)
            )
            for cc in challenge.categories:
                self.db.delete(cc)
            
            # Add new categories
            for category in categories:
                challenge_category = ChallengeCategory(
                    challenge_id=challenge.id,
                    category_id=category.id
                )
                self.db.add(challenge_category)
        
        # Create audit log
        new_value = {
            "title": challenge.title,
            "description": challenge.description,
            "district": challenge.district
        }
        
        audit_log = AuditLog(
            user_id=current_user.id,
            action="CHALLENGE_UPDATED",
            entity_type="Challenge",
            entity_id=challenge.id,
            old_value=old_value,
            new_value=new_value
        )
        self.db.add(audit_log)
        
        self.db.commit()
        self.db.refresh(challenge)
        
        return challenge
    
    def delete_challenge(
        self,
        challenge_id: UUID,
        current_user: User
    ) -> None:
        """
        Delete challenge (only drafts).
        
        Args:
            challenge_id: Challenge ID
            current_user: Current user (must be owner)
            
        Raises:
            HTTPException: If not authorized or status doesn't allow deletion
        """
        challenge = self.get_challenge(challenge_id)
        
        # Check ownership
        if challenge.submitted_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own challenges"
            )
        
        # Only allow deletion of drafts
        if challenge.status != ChallengeStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete draft challenges. Submitted challenges cannot be deleted for audit purposes."
            )
        
        # Create audit log before deletion
        audit_log = AuditLog(
            user_id=current_user.id,
            action="CHALLENGE_DELETED",
            entity_type="Challenge",
            entity_id=challenge.id,
            old_value={
                "challenge_code": challenge.challenge_code,
                "title": challenge.title,
                "status": challenge.status.value
            }
        )
        self.db.add(audit_log)
        
        # Delete challenge (cascade will handle related records)
        self.db.delete(challenge)
        self.db.commit()
    
    async def upload_media(
        self,
        challenge_id: UUID,
        file: UploadFile,
        current_user: User
    ) -> ChallengeMedia:
        """
        Upload media file for challenge.
        
        Args:
            challenge_id: Challenge ID
            file: Uploaded file
            current_user: Current user
            
        Returns:
            Created media record
            
        Raises:
            HTTPException: If not authorized or upload fails
        """
        challenge = self.get_challenge(challenge_id)
        
        # Check authorization (owner or government/admin)
        user_roles = {ur.role.name for ur in current_user.roles}
        is_owner = challenge.submitted_by == current_user.id
        is_authorized = is_owner or bool(
            user_roles.intersection({UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN})
        )
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload media for this challenge"
            )
        
        # Upload file
        file_url, original_filename, mime_type, file_size = await storage_service.upload_file(
            file, folder=f"challenges/{challenge_id}"
        )
        
        # Determine media type
        media_type_str = storage_service.get_media_type_from_mime(mime_type)
        media_type = MediaType[media_type_str]
        
        # Create media record
        media = ChallengeMedia(
            challenge_id=challenge_id,
            media_type=media_type,
            file_url=file_url,
            file_name=original_filename,
            mime_type=mime_type,
            file_size=file_size,
            uploaded_by=current_user.id
        )
        
        self.db.add(media)
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action="MEDIA_UPLOADED",
            entity_type="ChallengeMedia",
            entity_id=media.id,
            new_value={
                "challenge_id": str(challenge_id),
                "file_name": original_filename,
                "media_type": media_type.value
            }
        )
        self.db.add(audit_log)
        
        self.db.commit()
        self.db.refresh(media)
        
        return media
    
    def delete_media(
        self,
        challenge_id: UUID,
        media_id: UUID,
        current_user: User
    ) -> None:
        """
        Delete media file.
        
        Args:
            challenge_id: Challenge ID
            media_id: Media ID
            current_user: Current user
            
        Raises:
            HTTPException: If not authorized or media not found
        """
        challenge = self.get_challenge(challenge_id)
        
        # Get media
        media = self.db.execute(
            select(ChallengeMedia).where(
                ChallengeMedia.id == media_id,
                ChallengeMedia.challenge_id == challenge_id
            )
        ).scalar_one_or_none()
        
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        
        # Check authorization
        user_roles = {ur.role.name for ur in current_user.roles}
        is_owner = challenge.submitted_by == current_user.id
        is_authorized = is_owner or bool(
            user_roles.intersection({UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN})
        )
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this media"
            )
        
        # Delete file from storage
        storage_service.delete_file(media.file_url)
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action="MEDIA_DELETED",
            entity_type="ChallengeMedia",
            entity_id=media.id,
            old_value={
                "challenge_id": str(challenge_id),
                "file_name": media.file_name,
                "file_url": media.file_url
            }
        )
        self.db.add(audit_log)
        
        # Delete media record
        self.db.delete(media)
        self.db.commit()
    
    def build_challenge_response(self, challenge: Challenge) -> ChallengeResponse:
        """
        Build ChallengeResponse from Challenge model.
        
        Args:
            challenge: Challenge model
            
        Returns:
            ChallengeResponse
        """
        # Build categories
        categories = [
            CategoryResponse(
                id=cc.category.id,
                name=cc.category.name,
                description=cc.category.description,
                parent_id=cc.category.parent_id
            )
            for cc in challenge.categories
        ]
        
        # Build media
        media = [
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
        
        # Get submitter name if available
        submitter_name = None
        if challenge.submitted_by_user:
            submitter_name = challenge.submitted_by_user.name
        
        return ChallengeResponse(
            id=challenge.id,
            challenge_code=challenge.challenge_code,
            title=challenge.title,
            description=challenge.description,
            status=challenge.status,
            priority_score=challenge.priority_score,
            priority_level=challenge.priority_level,
            district=challenge.district,
            block=challenge.block,
            village=challenge.village,
            latitude=challenge.latitude,
            longitude=challenge.longitude,
            affected_population=challenge.affected_population,
            categories=categories,
            media=media,
            created_at=challenge.created_at,
            updated_at=challenge.updated_at,
            submitted_by=challenge.submitted_by,
            submitter_name=submitter_name
        )
