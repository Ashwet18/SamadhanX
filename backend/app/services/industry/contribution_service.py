"""
Partnership contribution tracking service.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

from app.models.partnership import Partnership, Contribution
from app.models.user import User
from app.models.platform import AuditLog
from app.models.enums import (
    ContributionType,
    ContributionStatus,
    PartnershipStatus,
    UserRole
)


class ContributionService:
    """Service for partnership contribution management."""
    
    def __init__(self, db: Session):
        """
        Initialize contribution service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_contribution(
        self,
        partnership_id: UUID,
        current_user: User,
        contribution_type: ContributionType,
        description: str,
        estimated_value: Optional[Decimal] = None,
        currency: str = "INR"
    ) -> Contribution:
        """
        Create a new contribution record.
        
        Args:
            partnership_id: Partnership ID
            current_user: User creating contribution
            contribution_type: Type of contribution
            description: Contribution description
            estimated_value: Optional estimated value
            currency: Currency code
            
        Returns:
            Created contribution
        """
        
        # Validate partnership
        partnership = self._get_partnership(partnership_id)
        
        # Verify partnership is in active state
        if partnership.status not in [
            PartnershipStatus.ACCEPTED,
            PartnershipStatus.ACTIVE
        ]:
            raise ValueError(
                f"Can only add contributions to accepted/active partnerships. "
                f"Current status: {partnership.status.value}"
            )
        
        # Authorization check
        if not self._can_manage_contributions(partnership, current_user):
            raise PermissionError("Not authorized to create contributions for this partnership")
        
        try:
            contribution = Contribution(
                partnership_id=partnership_id,
                contribution_type=contribution_type,
                description=description,
                estimated_value=estimated_value,
                currency=currency,
                status=ContributionStatus.PLANNED
            )
            
            self.db.add(contribution)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="CONTRIBUTION_CREATED",
                entity_type="CONTRIBUTION",
                entity_id=None,
                details={
                    "partnership_id": str(partnership_id),
                    "contribution_type": contribution_type.value,
                    "description": description[:100]
                }
            )
            
            self.db.commit()
            self.db.refresh(contribution)
            
            return contribution
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create contribution: {e}")
    
    def update_contribution(
        self,
        contribution_id: UUID,
        current_user: User,
        **updates
    ) -> Contribution:
        """
        Update contribution details.
        
        Args:
            contribution_id: Contribution ID
            current_user: Current user
            **updates: Fields to update
            
        Returns:
            Updated contribution
        """
        
        contribution = self._get_contribution(contribution_id)
        partnership = contribution.partnership
        
        # Can only update PLANNED or COMMITTED contributions
        if contribution.status not in [ContributionStatus.PLANNED, ContributionStatus.COMMITTED]:
            raise ValueError(
                f"Can only update PLANNED or COMMITTED contributions. "
                f"Current status: {contribution.status.value}"
            )
        
        # Authorization
        if not self._can_manage_contributions(partnership, current_user):
            raise PermissionError("Not authorized to update this contribution")
        
        try:
            allowed_fields = ['description', 'estimated_value', 'currency', 'evidence_reference']
            for field, value in updates.items():
                if field in allowed_fields and value is not None:
                    setattr(contribution, field, value)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="CONTRIBUTION_UPDATED",
                entity_type="CONTRIBUTION",
                entity_id=contribution_id,
                details=updates
            )
            
            self.db.commit()
            self.db.refresh(contribution)
            
            return contribution
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update contribution: {e}")
    
    def commit_contribution(
        self,
        contribution_id: UUID,
        current_user: User,
        committed_date: Optional[date] = None
    ) -> Contribution:
        """
        Mark contribution as committed.
        
        Args:
            contribution_id: Contribution ID
            current_user: User committing
            committed_date: Optional commitment date
            
        Returns:
            Updated contribution
        """
        
        contribution = self._get_contribution(contribution_id)
        partnership = contribution.partnership
        
        # Can only commit PLANNED contributions
        if contribution.status != ContributionStatus.PLANNED:
            raise ValueError(
                f"Can only commit PLANNED contributions. "
                f"Current status: {contribution.status.value}"
            )
        
        # Authorization: industry users only
        if not self._is_industry_user_for_partnership(partnership, current_user):
            raise PermissionError("Only industry partner can commit contributions")
        
        try:
            contribution.status = ContributionStatus.COMMITTED
            contribution.committed_date = committed_date or date.today()
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="CONTRIBUTION_COMMITTED",
                entity_type="CONTRIBUTION",
                entity_id=contribution_id,
                details={"committed_date": str(contribution.committed_date)}
            )
            
            self.db.commit()
            self.db.refresh(contribution)
            
            return contribution
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to commit contribution: {e}")
    
    def deliver_contribution(
        self,
        contribution_id: UUID,
        current_user: User,
        delivered_date: Optional[date] = None,
        evidence_reference: Optional[str] = None
    ) -> Contribution:
        """
        Mark contribution as delivered.
        
        Args:
            contribution_id: Contribution ID
            current_user: User marking as delivered
            delivered_date: Optional delivery date
            evidence_reference: Optional evidence reference
            
        Returns:
            Updated contribution
        """
        
        contribution = self._get_contribution(contribution_id)
        partnership = contribution.partnership
        
        # Can deliver from COMMITTED or IN_PROGRESS
        if contribution.status not in [ContributionStatus.COMMITTED, ContributionStatus.IN_PROGRESS]:
            raise ValueError(
                f"Can only deliver COMMITTED or IN_PROGRESS contributions. "
                f"Current status: {contribution.status.value}"
            )
        
        # Authorization
        if not self._can_manage_contributions(partnership, current_user):
            raise PermissionError("Not authorized to deliver this contribution")
        
        try:
            contribution.status = ContributionStatus.DELIVERED
            contribution.delivered_date = delivered_date or date.today()
            if evidence_reference:
                contribution.evidence_reference = evidence_reference
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="CONTRIBUTION_DELIVERED",
                entity_type="CONTRIBUTION",
                entity_id=contribution_id,
                details={"delivered_date": str(contribution.delivered_date)}
            )
            
            self.db.commit()
            self.db.refresh(contribution)
            
            return contribution
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to deliver contribution: {e}")
    
    def cancel_contribution(
        self,
        contribution_id: UUID,
        current_user: User,
        reason: str
    ) -> Contribution:
        """
        Cancel a contribution.
        
        Args:
            contribution_id: Contribution ID
            current_user: User cancelling
            reason: Cancellation reason
            
        Returns:
            Updated contribution
        """
        
        if not reason:
            raise ValueError("Cancellation reason is required")
        
        contribution = self._get_contribution(contribution_id)
        partnership = contribution.partnership
        
        # Can cancel if not delivered
        if contribution.status == ContributionStatus.DELIVERED:
            raise ValueError("Cannot cancel delivered contributions")
        
        # Authorization
        if not self._can_manage_contributions(partnership, current_user):
            raise PermissionError("Not authorized to cancel this contribution")
        
        try:
            old_status = contribution.status
            contribution.status = ContributionStatus.CANCELLED
            
            # Store reason in description
            contribution.description += f"\n\nCancelled: {reason}"
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="CONTRIBUTION_CANCELLED",
                entity_type="CONTRIBUTION",
                entity_id=contribution_id,
                details={"old_status": old_status.value, "reason": reason}
            )
            
            self.db.commit()
            self.db.refresh(contribution)
            
            return contribution
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to cancel contribution: {e}")
    
    def get_partnership_contributions(
        self,
        partnership_id: UUID,
        current_user: User
    ) -> List[Contribution]:
        """
        Get all contributions for a partnership.
        
        Args:
            partnership_id: Partnership ID
            current_user: Current user
            
        Returns:
            List of contributions
        """
        
        partnership = self._get_partnership(partnership_id)
        
        # Authorization
        from app.services.industry.partnership_service import PartnershipService
        service = PartnershipService(self.db)
        if not service._can_view_partnership(partnership, current_user):
            raise PermissionError("Not authorized to view this partnership's contributions")
        
        contributions = self.db.query(Contribution).filter(
            Contribution.partnership_id == partnership_id
        ).order_by(Contribution.created_at).all()
        
        return contributions
    
    def _get_partnership(self, partnership_id: UUID) -> Partnership:
        """Get partnership or raise error."""
        partnership = self.db.query(Partnership).filter(
            Partnership.id == partnership_id
        ).first()
        
        if not partnership:
            raise ValueError(f"Partnership {partnership_id} not found")
        
        return partnership
    
    def _get_contribution(self, contribution_id: UUID) -> Contribution:
        """Get contribution or raise error."""
        contribution = self.db.query(Contribution).filter(
            Contribution.id == contribution_id
        ).first()
        
        if not contribution:
            raise ValueError(f"Contribution {contribution_id} not found")
        
        return contribution
    
    def _can_manage_contributions(self, partnership: Partnership, user: User) -> bool:
        """Check if user can manage contributions."""
        user_roles = {ur.role.name for ur in user.roles}
        
        # Admin can manage
        if UserRole.PLATFORM_ADMIN in user_roles:
            return True
        
        # Industry user for this partnership
        if self._is_industry_user_for_partnership(partnership, user):
            return True
        
        # University admin/faculty for project's university
        if UserRole.UNIVERSITY_ADMIN in user_roles or UserRole.FACULTY in user_roles:
            if user.faculty_profile and user.faculty_profile.university_id == partnership.project.university_id:
                return True
        
        return False
    
    def _is_industry_user_for_partnership(self, partnership: Partnership, user: User) -> bool:
        """Check if user is industry user for this partnership."""
        # Check if user has INDUSTRY role
        user_roles = {ur.role.name for ur in user.roles}
        if UserRole.INDUSTRY not in user_roles and UserRole.CSR not in user_roles and UserRole.PLATFORM_ADMIN not in user_roles:
            return False
        
        if UserRole.PLATFORM_ADMIN in user_roles:
            return True
        
        # Check if user belongs to the partnership's industry
        if hasattr(user, 'industry_profile') and user.industry_profile:
            return user.industry_profile.industry_id == partnership.industry_id
        
        return False
    
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
