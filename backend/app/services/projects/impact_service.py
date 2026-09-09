"""
Project impact measurement service.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.project import Project
from app.models.platform import ImpactMetric
from app.models.user import User
from app.models.enums import VerificationStatus, UserRole
from app.models.platform import AuditLog, Notification


class ImpactService:
    """Service for managing project impact measurements."""
    
    def __init__(self, db: Session):
        """
        Initialize impact service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_or_update_impact(
        self,
        project_id: UUID,
        current_user: User,
        metric_name: str,
        beneficiaries_count: Optional[int] = None,
        geographic_area: Optional[str] = None,
        deployment_date: Optional[date] = None,
        baseline_value: Optional[float] = None,
        target_value: Optional[float] = None,
        actual_value: Optional[float] = None,
        unit: Optional[str] = None,
        impact_description: Optional[str] = None,
        evidence_reference: Optional[str] = None,
        sustainability_status: Optional[str] = None
    ) -> ImpactMetric:
        """
        Create or update impact measurement.
        
        Args:
            project_id: Project ID
            current_user: Current user
            metric_name: Name of the metric being measured
            (other fields): Impact measurement data
            
        Returns:
            Created or updated impact metric
        """
        
        # Validate project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        if not self._can_edit_impact(project, current_user):
            raise ValueError("Not authorized to edit project impact")
        
        try:
            # Check for existing metric
            impact = self.db.query(ImpactMetric).filter(
                ImpactMetric.project_id == project_id,
                ImpactMetric.metric_name == metric_name
            ).first()
            
            if impact:
                # Update existing (only if PENDING or REJECTED)
                if impact.verification_status not in [VerificationStatus.PENDING, VerificationStatus.REJECTED]:
                    raise ValueError(
                        f"Cannot edit impact with status: {impact.verification_status.value}"
                    )
                is_new = False
            else:
                # Create new
                impact = ImpactMetric(
                    project_id=project_id,
                    metric_name=metric_name
                )
                is_new = True
            
            # Update fields
            impact.beneficiaries_count = beneficiaries_count
            impact.geographic_area = geographic_area
            impact.deployment_date = deployment_date
            impact.baseline_value = baseline_value
            impact.target_value = target_value
            impact.actual_value = actual_value
            impact.unit = unit
            impact.impact_description = impact_description
            impact.evidence_reference = evidence_reference
            impact.sustainability_status = sustainability_status
            impact.verification_status = VerificationStatus.PENDING
            impact.submitted_by = current_user.id
            impact.measured_at = datetime.utcnow()
            
            if is_new:
                self.db.add(impact)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="IMPACT_UPDATED" if not is_new else "IMPACT_CREATED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"metric_name": metric_name}
            )
            
            self.db.commit()
            self.db.refresh(impact)
            
            return impact
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to save impact measurement: {e}")
    
    def submit_impact(
        self,
        impact_id: UUID,
        current_user: User
    ) -> ImpactMetric:
        """
        Submit impact for verification.
        
        Args:
            impact_id: Impact metric ID
            current_user: Current user
            
        Returns:
            Updated impact metric
        """
        
        impact = self.db.query(ImpactMetric).filter(ImpactMetric.id == impact_id).first()
        if not impact:
            raise ValueError(f"Impact metric {impact_id} not found")
        
        # Authorization check
        project = impact.project
        if not self._can_edit_impact(project, current_user):
            raise ValueError("Not authorized to submit impact")
        
        if impact.verification_status != VerificationStatus.PENDING:
            raise ValueError(f"Can only submit PENDING impact. Current status: {impact.verification_status.value}")
        
        try:
            # Note: We keep status as PENDING, but record submission
            # Government will change to VERIFIED or REJECTED
            impact.submitted_by = current_user.id
            impact.measured_at = datetime.utcnow()
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="IMPACT_SUBMITTED",
                entity_type="PROJECT",
                entity_id=project.id,
                details={"metric_name": impact.metric_name, "impact_id": str(impact_id)}
            )
            
            # Notify government
            self._create_notification(
                user_role=UserRole.GOVERNMENT_OFFICER,
                notification_type="IMPACT_SUBMITTED",
                title="Impact Measurement Submitted",
                message=f"Project '{project.name}' ({project.project_code}) has submitted impact measurements for review.",
                reference_type="PROJECT",
                reference_id=project.id
            )
            
            self.db.commit()
            self.db.refresh(impact)
            
            return impact
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to submit impact: {e}")
    
    def verify_impact(
        self,
        impact_id: UUID,
        current_user: User,
        comments: Optional[str] = None
    ) -> ImpactMetric:
        """
        Verify impact measurement (Government only).
        
        Args:
            impact_id: Impact metric ID
            current_user: Current user (must be government)
            comments: Optional verification comments
            
        Returns:
            Updated impact metric
        """
        
        if current_user.role not in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            raise ValueError("Only government officers can verify impact")
        
        impact = self.db.query(ImpactMetric).filter(ImpactMetric.id == impact_id).first()
        if not impact:
            raise ValueError(f"Impact metric {impact_id} not found")
        
        if impact.verification_status not in [VerificationStatus.PENDING, VerificationStatus.REJECTED]:
            raise ValueError(f"Can only verify PENDING/REJECTED impact. Current status: {impact.verification_status.value}")
        
        try:
            impact.verification_status = VerificationStatus.VERIFIED
            impact.verified_by = current_user.id
            impact.verified_at = datetime.utcnow()
            impact.review_comments = comments
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="IMPACT_VERIFIED",
                entity_type="PROJECT",
                entity_id=impact.project_id,
                details={"metric_name": impact.metric_name, "impact_id": str(impact_id)}
            )
            
            # Notify project team
            self._notify_project_team(
                project=impact.project,
                notification_type="IMPACT_VERIFIED",
                title="Impact Measurement Verified",
                message=f"Impact measurement for '{impact.metric_name}' has been verified by government."
            )
            
            self.db.commit()
            self.db.refresh(impact)
            
            return impact
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to verify impact: {e}")
    
    def request_revision(
        self,
        impact_id: UUID,
        current_user: User,
        comments: str
    ) -> ImpactMetric:
        """
        Request revisions to impact measurement (Government only).
        
        Args:
            impact_id: Impact metric ID
            current_user: Current user (must be government)
            comments: Required revision comments
            
        Returns:
            Updated impact metric
        """
        
        if current_user.role not in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            raise ValueError("Only government officers can request revisions")
        
        if not comments:
            raise ValueError("Comments are required when requesting revisions")
        
        impact = self.db.query(ImpactMetric).filter(ImpactMetric.id == impact_id).first()
        if not impact:
            raise ValueError(f"Impact metric {impact_id} not found")
        
        try:
            impact.verification_status = VerificationStatus.REJECTED
            impact.verified_by = current_user.id
            impact.verified_at = datetime.utcnow()
            impact.review_comments = comments
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="IMPACT_REVISION_REQUESTED",
                entity_type="PROJECT",
                entity_id=impact.project_id,
                details={"metric_name": impact.metric_name, "comments": comments}
            )
            
            # Notify project team
            self._notify_project_team(
                project=impact.project,
                notification_type="IMPACT_REVISION_REQUESTED",
                title="Impact Measurement Revision Requested",
                message=f"Government requested revisions to impact measurement: {comments[:100]}"
            )
            
            self.db.commit()
            self.db.refresh(impact)
            
            return impact
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to request revision: {e}")
    
    def get_project_impact(self, project_id: UUID, current_user: User) -> list:
        """
        Get all impact measurements for a project.
        
        Args:
            project_id: Project ID
            current_user: Current user
            
        Returns:
            List of impact measurements
        """
        
        # Validate project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        from app.services.projects.project_service import ProjectService
        service = ProjectService(self.db)
        if not service._can_access_project(project, current_user):
            raise ValueError("Not authorized to view project impact")
        
        # Get impact measurements
        impacts = self.db.query(ImpactMetric).filter(
            ImpactMetric.project_id == project_id
        ).all()
        
        return impacts
    
    def _can_edit_impact(self, project: Project, user: User) -> bool:
        """Check if user can edit impact measurements."""
        
        # University team can edit
        if user.role in [UserRole.UNIVERSITY_ADMIN, UserRole.FACULTY]:
            from app.services.projects.project_service import ProjectService
            service = ProjectService(self.db)
            user_university = service._get_user_university(user)
            return user_university and user_university == project.university_id
        
        return False
    
    def _create_audit_log(self, user_id: UUID, action: str, entity_type: str, entity_id: UUID, details: Dict[str, Any]):
        """Create audit log entry."""
        try:
            audit_log = AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id, new_value=details)
            self.db.add(audit_log)
        except Exception:
            pass
    
    def _create_notification(self, user_role: UserRole, notification_type: str, title: str, message: str, reference_type: str, reference_id: UUID):
        """Create notification for role."""
        try:
            users = self.db.query(User).filter(User.role == user_role).all()
            for user in users:
                notification = Notification(user_id=user.id, type=notification_type, title=title, message=message, reference_type=reference_type, reference_id=reference_id, is_read=False)
                self.db.add(notification)
        except Exception:
            pass
    
    def _notify_project_team(self, project: Project, notification_type: str, title: str, message: str):
        """Notify project team members."""
        try:
            from app.models.project import ProjectMember
            members = self.db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
            for member in members:
                notification = Notification(user_id=member.user_id, type=notification_type, title=title, message=message, reference_type="PROJECT", reference_id=project.id, is_read=False)
                self.db.add(notification)
        except Exception:
            pass
