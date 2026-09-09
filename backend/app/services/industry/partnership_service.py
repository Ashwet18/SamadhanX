"""
Partnership management service.

Handles partnership creation, lifecycle management, and authorization.
"""

from typing import Dict, Any, Optional, List, Tuple
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from app.models.partnership import Partnership
from app.models.project import Project
from app.models.industry import IndustryPartner
from app.models.user import User
from app.models.platform import AuditLog, Notification
from app.models.enums import (
    PartnershipStatus,
    PartnershipType,
    UserRole,
    ProjectStatus,
    VerificationStatus
)
from app.services.industry.partnership_lifecycle import PartnershipLifecycleManager


class PartnershipService:
    """Service for partnership management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize partnership service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.lifecycle_manager = PartnershipLifecycleManager()
    
    def create_partnership_request(
        self,
        project_id: UUID,
        industry_id: UUID,
        current_user: User,
        partnership_type: PartnershipType,
        objectives: Optional[str] = None,
        requested_support: Optional[str] = None,
        expected_contribution: Optional[str] = None,
        proposed_duration: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Partnership:
        """
        Create a new partnership request.
        
        Args:
            project_id: Project ID
            industry_id: Industry partner ID
            current_user: User creating the request
            partnership_type: Type of partnership
            objectives: Partnership objectives
            requested_support: Requested support description
            expected_contribution: Expected contribution from industry
            proposed_duration: Duration in months
            notes: Additional notes
            
        Returns:
            Created partnership
            
        Raises:
            ValueError: If validation fails
            PermissionError: If not authorized
            RuntimeError: If creation fails
        """
        
        # Validate project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Validate project status
        if project.status not in [
            ProjectStatus.APPROVED,
            ProjectStatus.PROTOTYPE,
            ProjectStatus.TESTING,
            ProjectStatus.PILOT,
            ProjectStatus.DEPLOYED
        ]:
            raise ValueError(
                f"Project must be in active development state to request partnerships. "
                f"Current status: {project.status.value}"
            )
        
        # Validate industry partner exists
        industry = self.db.query(IndustryPartner).filter(
            IndustryPartner.id == industry_id
        ).first()
        if not industry:
            raise ValueError(f"Industry partner {industry_id} not found")
        
        # Verify industry is verified
        if industry.verification_status != VerificationStatus.VERIFIED:
            raise ValueError("Can only create partnerships with verified industry partners")
        
        # Authorization check
        if not self._can_create_partnership(project, current_user):
            raise PermissionError("Not authorized to create partnerships for this project")
        
        # Check for duplicate active partnership
        existing = self.db.query(Partnership).filter(
            Partnership.project_id == project_id,
            Partnership.industry_id == industry_id,
            Partnership.partnership_type == partnership_type,
            Partnership.status.in_([
                PartnershipStatus.REQUESTED,
                PartnershipStatus.UNDER_REVIEW,
                PartnershipStatus.ACCEPTED,
                PartnershipStatus.ACTIVE
            ])
        ).first()
        
        if existing:
            raise ValueError(
                f"An active {partnership_type.value} partnership already exists "
                f"with this industry partner (status: {existing.status.value})"
            )
        
        try:
            # Create partnership
            partnership = Partnership(
                project_id=project_id,
                industry_id=industry_id,
                partnership_type=partnership_type,
                objectives=objectives,
                requested_support=requested_support,
                expected_contribution=expected_contribution,
                proposed_duration=proposed_duration,
                notes=notes,
                status=PartnershipStatus.REQUESTED,
                requested_by=current_user.id,
                requested_at=datetime.utcnow()
            )
            
            self.db.add(partnership)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PARTNERSHIP_REQUESTED",
                entity_type="PARTNERSHIP",
                entity_id=None,  # Will be set after commit
                details={
                    "project_id": str(project_id),
                    "industry_id": str(industry_id),
                    "partnership_type": partnership_type.value
                }
            )
            
            # Notify industry partner
            self._notify_industry(
                industry_id=industry_id,
                notification_type="PARTNERSHIP_REQUESTED",
                title="New Partnership Request",
                message=f"Project '{project.name}' ({project.project_code}) has requested a {partnership_type.value} partnership.",
                reference_type="PARTNERSHIP",
                reference_id=None  # Will be set after commit
            )
            
            self.db.commit()
            self.db.refresh(partnership)
            
            return partnership
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create partnership request: {e}")
    
    def accept_partnership(
        self,
        partnership_id: UUID,
        current_user: User,
        notes: Optional[str] = None
    ) -> Partnership:
        """
        Accept a partnership request (industry only).
        
        Args:
            partnership_id: Partnership ID
            current_user: Industry user accepting
            notes: Optional acceptance notes
            
        Returns:
            Updated partnership
        """
        
        partnership = self._get_partnership(partnership_id)
        
        # Verify current status allows acceptance
        if not self.lifecycle_manager.is_valid_transition(
            partnership.status,
            PartnershipStatus.ACCEPTED
        ):
            raise ValueError(
                f"Cannot accept partnership with status {partnership.status.value}"
            )
        
        # Authorization: must be industry user from the partner organization
        if not self._is_industry_user_for_partnership(partnership, current_user):
            raise PermissionError("Only industry partner users can accept partnerships")
        
        try:
            partnership.status = PartnershipStatus.ACCEPTED
            partnership.reviewed_by = current_user.id
            partnership.reviewed_at = datetime.utcnow()
            if notes:
                partnership.notes = (partnership.notes or "") + f"\n\nAcceptance notes: {notes}"
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PARTNERSHIP_ACCEPTED",
                entity_type="PARTNERSHIP",
                entity_id=partnership_id,
                details={"notes": notes}
            )
            
            # Notify project team
            self._notify_project_team(
                project_id=partnership.project_id,
                notification_type="PARTNERSHIP_ACCEPTED",
                title="Partnership Accepted",
                message=f"{partnership.industry.organization_name} accepted your {partnership.partnership_type.value} partnership request."
            )
            
            self.db.commit()
            self.db.refresh(partnership)
            
            return partnership
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to accept partnership: {e}")
    
    def decline_partnership(
        self,
        partnership_id: UUID,
        current_user: User,
        reason: str
    ) -> Partnership:
        """
        Decline a partnership request (industry only).
        
        Args:
            partnership_id: Partnership ID
            current_user: Industry user declining
            reason: Required decline reason
            
        Returns:
            Updated partnership
        """
        
        if not reason:
            raise ValueError("Decline reason is required")
        
        partnership = self._get_partnership(partnership_id)
        
        # Verify current status allows decline
        if not self.lifecycle_manager.is_valid_transition(
            partnership.status,
            PartnershipStatus.DECLINED
        ):
            raise ValueError(
                f"Cannot decline partnership with status {partnership.status.value}"
            )
        
        # Authorization
        if not self._is_industry_user_for_partnership(partnership, current_user):
            raise PermissionError("Only industry partner users can decline partnerships")
        
        try:
            partnership.status = PartnershipStatus.DECLINED
            partnership.reviewed_by = current_user.id
            partnership.reviewed_at = datetime.utcnow()
            partnership.decline_reason = reason
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PARTNERSHIP_DECLINED",
                entity_type="PARTNERSHIP",
                entity_id=partnership_id,
                details={"reason": reason}
            )
            
            # Notify project team
            self._notify_project_team(
                project_id=partnership.project_id,
                notification_type="PARTNERSHIP_DECLINED",
                title="Partnership Declined",
                message=f"{partnership.industry.organization_name} declined your partnership request: {reason[:100]}"
            )
            
            self.db.commit()
            self.db.refresh(partnership)
            
            return partnership
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to decline partnership: {e}")
    
    def activate_partnership(
        self,
        partnership_id: UUID,
        current_user: User,
        start_date: Optional[date] = None
    ) -> Partnership:
        """
        Activate an accepted partnership.
        
        Args:
            partnership_id: Partnership ID
            current_user: User activating
            start_date: Optional start date
            
        Returns:
            Updated partnership
        """
        
        partnership = self._get_partnership(partnership_id)
        
        # Verify transition is valid
        if not self.lifecycle_manager.is_valid_transition(
            partnership.status,
            PartnershipStatus.ACTIVE
        ):
            raise ValueError(
                f"Cannot activate partnership with status {partnership.status.value}"
            )
        
        # Authorization: university or industry can activate
        if not (self._can_manage_partnership(partnership, current_user) or
                self._is_industry_user_for_partnership(partnership, current_user)):
            raise PermissionError("Not authorized to activate this partnership")
        
        try:
            partnership.status = PartnershipStatus.ACTIVE
            partnership.start_date = start_date or date.today()
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PARTNERSHIP_ACTIVATED",
                entity_type="PARTNERSHIP",
                entity_id=partnership_id,
                details={"start_date": str(partnership.start_date)}
            )
            
            # Notify both parties
            self._notify_project_team(
                project_id=partnership.project_id,
                notification_type="PARTNERSHIP_ACTIVATED",
                title="Partnership Activated",
                message=f"Partnership with {partnership.industry.organization_name} is now active."
            )
            
            self.db.commit()
            self.db.refresh(partnership)
            
            return partnership
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to activate partnership: {e}")
    
    def complete_partnership(
        self,
        partnership_id: UUID,
        current_user: User,
        end_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Partnership:
        """
        Mark partnership as completed.
        
        Args:
            partnership_id: Partnership ID
            current_user: User completing
            end_date: Optional end date
            notes: Optional completion notes
            
        Returns:
            Updated partnership
        """
        
        partnership = self._get_partnership(partnership_id)
        
        # Verify transition is valid
        if not self.lifecycle_manager.is_valid_transition(
            partnership.status,
            PartnershipStatus.COMPLETED
        ):
            raise ValueError(
                f"Cannot complete partnership with status {partnership.status.value}"
            )
        
        # Authorization
        if not (self._can_manage_partnership(partnership, current_user) or
                self._is_industry_user_for_partnership(partnership, current_user)):
            raise PermissionError("Not authorized to complete this partnership")
        
        try:
            partnership.status = PartnershipStatus.COMPLETED
            partnership.end_date = end_date or date.today()
            if notes:
                partnership.notes = (partnership.notes or "") + f"\n\nCompletion notes: {notes}"
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PARTNERSHIP_COMPLETED",
                entity_type="PARTNERSHIP",
                entity_id=partnership_id,
                details={"end_date": str(partnership.end_date)}
            )
            
            # Notify both parties
            self._notify_project_team(
                project_id=partnership.project_id,
                notification_type="PARTNERSHIP_COMPLETED",
                title="Partnership Completed",
                message=f"Partnership with {partnership.industry.organization_name} has been completed."
            )
            
            self._notify_industry(
                industry_id=partnership.industry_id,
                notification_type="PARTNERSHIP_COMPLETED",
                title="Partnership Completed",
                message=f"Partnership with project {partnership.project.project_code} has been completed.",
                reference_type="PARTNERSHIP",
                reference_id=partnership_id
            )
            
            self.db.commit()
            self.db.refresh(partnership)
            
            return partnership
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to complete partnership: {e}")
    
    def cancel_partnership(
        self,
        partnership_id: UUID,
        current_user: User,
        reason: str
    ) -> Partnership:
        """
        Cancel a partnership.
        
        Args:
            partnership_id: Partnership ID
            current_user: User cancelling
            reason: Required cancellation reason
            
        Returns:
            Updated partnership
        """
        
        if not reason:
            raise ValueError("Cancellation reason is required")
        
        partnership = self._get_partnership(partnership_id)
        
        # Verify transition is valid
        if not self.lifecycle_manager.is_valid_transition(
            partnership.status,
            PartnershipStatus.CANCELLED
        ):
            raise ValueError(
                f"Cannot cancel partnership with status {partnership.status.value}"
            )
        
        # Authorization
        if not (self._can_manage_partnership(partnership, current_user) or
                self._is_industry_user_for_partnership(partnership, current_user)):
            raise PermissionError("Not authorized to cancel this partnership")
        
        try:
            old_status = partnership.status
            partnership.status = PartnershipStatus.CANCELLED
            partnership.decline_reason = reason  # Reuse decline_reason field
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PARTNERSHIP_CANCELLED",
                entity_type="PARTNERSHIP",
                entity_id=partnership_id,
                details={"old_status": old_status.value, "reason": reason}
            )
            
            # Notify both parties
            self._notify_project_team(
                project_id=partnership.project_id,
                notification_type="PARTNERSHIP_CANCELLED",
                title="Partnership Cancelled",
                message=f"Partnership with {partnership.industry.organization_name} has been cancelled: {reason[:100]}"
            )
            
            self._notify_industry(
                industry_id=partnership.industry_id,
                notification_type="PARTNERSHIP_CANCELLED",
                title="Partnership Cancelled",
                message=f"Partnership with project {partnership.project.project_code} has been cancelled.",
                reference_type="PARTNERSHIP",
                reference_id=partnership_id
            )
            
            self.db.commit()
            self.db.refresh(partnership)
            
            return partnership
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to cancel partnership: {e}")
    
    def get_partnership(
        self,
        partnership_id: UUID,
        current_user: User
    ) -> Partnership:
        """
        Get partnership by ID with authorization check.
        
        Args:
            partnership_id: Partnership ID
            current_user: Current user
            
        Returns:
            Partnership
        """
        
        partnership = self._get_partnership(partnership_id)
        
        # Authorization check
        if not self._can_view_partnership(partnership, current_user):
            raise PermissionError("Not authorized to view this partnership")
        
        return partnership
    
    def list_partnerships(
        self,
        current_user: User,
        project_id: Optional[UUID] = None,
        industry_id: Optional[UUID] = None,
        university_id: Optional[UUID] = None,
        status: Optional[PartnershipStatus] = None,
        partnership_type: Optional[PartnershipType] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Partnership], int]:
        """
        List partnerships with filtering and pagination.
        
        Args:
            current_user: Current user
            project_id: Filter by project
            industry_id: Filter by industry
            university_id: Filter by university
            status: Filter by status
            partnership_type: Filter by type
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (partnerships list, total count)
        """
        
        query = self.db.query(Partnership)
        
        # Authorization-based filtering
        user_roles = {ur.role.name for ur in current_user.roles}
        
        if UserRole.INDUSTRY in user_roles or UserRole.CSR in user_roles:
            # Industry users see only their own organization's partnerships
            industry_partner_id = self._get_user_industry(current_user)
            if not industry_partner_id:
                return [], 0
            query = query.filter(Partnership.industry_id == industry_partner_id)
        
        elif UserRole.UNIVERSITY_ADMIN in user_roles or UserRole.FACULTY in user_roles:
            # University users see only their university's projects
            user_university_id = self._get_user_university(current_user)
            if not user_university_id:
                return [], 0
            
            # Join with projects to filter by university
            from app.models.project import Project as ProjectModel
            query = query.join(ProjectModel).filter(
                ProjectModel.university_id == user_university_id
            )
        
        elif UserRole.STUDENT in user_roles:
            # Students see partnerships for projects they're members of
            from app.models.project import ProjectMember
            query = query.join(ProjectMember, Partnership.project_id == ProjectMember.project_id).filter(
                ProjectMember.user_id == current_user.id
            )
        
        elif UserRole.GOVERNMENT_OFFICER not in user_roles and UserRole.PLATFORM_ADMIN not in user_roles:
            # Citizens and others have no access
            return [], 0
        
        # Apply filters
        if project_id:
            query = query.filter(Partnership.project_id == project_id)
        if industry_id:
            query = query.filter(Partnership.industry_id == industry_id)
        if university_id:
            from app.models.project import Project as ProjectModel
            query = query.join(ProjectModel).filter(ProjectModel.university_id == university_id)
        if status:
            query = query.filter(Partnership.status == status)
        if partnership_type:
            query = query.filter(Partnership.partnership_type == partnership_type)
        
        # Count total
        total = query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        partnerships = query.order_by(Partnership.created_at.desc()).offset(offset).limit(page_size).all()
        
        return partnerships, total
    
    def _get_partnership(self, partnership_id: UUID) -> Partnership:
        """Get partnership or raise error."""
        partnership = self.db.query(Partnership).filter(
            Partnership.id == partnership_id
        ).first()
        
        if not partnership:
            raise ValueError(f"Partnership {partnership_id} not found")
        
        return partnership
    
    def _can_create_partnership(self, project: Project, user: User) -> bool:
        """Check if user can create partnerships for project."""
        user_roles = {ur.role.name for ur in user.roles}
        
        # Government and admin can create for any project
        if UserRole.GOVERNMENT_OFFICER in user_roles or UserRole.PLATFORM_ADMIN in user_roles:
            return True
        
        # University users can create for their university's projects
        if UserRole.UNIVERSITY_ADMIN in user_roles or UserRole.FACULTY in user_roles:
            user_university = self._get_user_university(user)
            return user_university and user_university == project.university_id
        
        return False
    
    def _can_manage_partnership(self, partnership: Partnership, user: User) -> bool:
        """Check if user can manage partnership (activate, complete, cancel)."""
        user_roles = {ur.role.name for ur in user.roles}
        
        # Government and admin can manage any
        if UserRole.GOVERNMENT_OFFICER in user_roles or UserRole.PLATFORM_ADMIN in user_roles:
            return True
        
        # University users can manage their university's partnerships
        if UserRole.UNIVERSITY_ADMIN in user_roles or UserRole.FACULTY in user_roles:
            user_university = self._get_user_university(user)
            project = partnership.project
            return user_university and user_university == project.university_id
        
        return False
    
    def _can_view_partnership(self, partnership: Partnership, user: User) -> bool:
        """Check if user can view partnership."""
        user_roles = {ur.role.name for ur in user.roles}
        
        # Government and admin can view all
        if UserRole.GOVERNMENT_OFFICER in user_roles or UserRole.PLATFORM_ADMIN in user_roles:
            return True
        
        # Industry users can view their own
        if UserRole.INDUSTRY in user_roles or UserRole.CSR in user_roles:
            user_industry = self._get_user_industry(user)
            return user_industry and user_industry == partnership.industry_id
        
        # University users can view their university's
        if UserRole.UNIVERSITY_ADMIN in user_roles or UserRole.FACULTY in user_roles:
            user_university = self._get_user_university(user)
            project = partnership.project
            return user_university and user_university == project.university_id
        
        # Students can view if they're on the project team
        if UserRole.STUDENT in user_roles:
            from app.models.project import ProjectMember
            member = self.db.query(ProjectMember).filter(
                ProjectMember.project_id == partnership.project_id,
                ProjectMember.user_id == user.id
            ).first()
            return member is not None
        
        return False
    
    def _is_industry_user_for_partnership(self, partnership: Partnership, user: User) -> bool:
        """Check if user is an industry user for this partnership's industry."""
        # Check if user has industry-related role
        user_roles = {ur.role.name for ur in user.roles}
        if UserRole.INDUSTRY not in user_roles and UserRole.CSR not in user_roles and UserRole.PLATFORM_ADMIN not in user_roles:
            return False
        
        if UserRole.PLATFORM_ADMIN in user_roles:
            return True
        
        user_industry = self._get_user_industry(user)
        return user_industry and user_industry == partnership.industry_id
    
    def _get_user_university(self, user: User) -> Optional[UUID]:
        """Get user's university ID."""
        if user.role == UserRole.FACULTY and user.faculty_profile:
            return user.faculty_profile.university_id
        if user.role == UserRole.STUDENT and user.student_profile:
            return user.student_profile.university_id
        return None
    
    def _get_user_industry(self, user: User) -> Optional[UUID]:
        """Get user's industry partner ID."""
        if hasattr(user, 'industry_profile') and user.industry_profile:
            return user.industry_profile.industry_id
        return None
    
    def _create_audit_log(
        self,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: Optional[UUID],
        details: Dict[str, Any]
    ):
        """Create audit log entry."""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                new_value=details
            )
            self.db.add(audit_log)
        except Exception:
            pass
    
    def _notify_project_team(
        self,
        project_id: UUID,
        notification_type: str,
        title: str,
        message: str
    ):
        """Notify project team members."""
        try:
            from app.models.project import ProjectMember
            members = self.db.query(ProjectMember).filter(
                ProjectMember.project_id == project_id
            ).all()
            
            for member in members:
                notification = Notification(
                    user_id=member.user_id,
                    type=notification_type,
                    title=title,
                    message=message,
                    reference_type="PARTNERSHIP",
                    reference_id=project_id,
                    is_read=False
                )
                self.db.add(notification)
        except Exception:
            pass
    
    def _notify_industry(
        self,
        industry_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        reference_type: str,
        reference_id: Optional[UUID]
    ):
        """Notify industry partner users."""
        try:
            # TODO: Get industry users when user-industry relationship exists
            # For now, notify all users with INDUSTRY role
            industry_users = self.db.query(User).filter(
                User.role == UserRole.INDUSTRY
            ).all()
            
            for user in industry_users:
                notification = Notification(
                    user_id=user.id,
                    type=notification_type,
                    title=title,
                    message=message,
                    reference_type=reference_type,
                    reference_id=reference_id,
                    is_read=False
                )
                self.db.add(notification)
        except Exception:
            pass
