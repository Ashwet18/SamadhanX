"""
Project milestone management service.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.project import Project, ProjectMilestone
from app.models.user import User
from app.models.enums import MilestoneStatus, UserRole
from app.models.platform import AuditLog


class MilestoneService:
    """Service for managing project milestones."""
    
    def __init__(self, db: Session):
        """
        Initialize milestone service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_milestone(
        self,
        project_id: UUID,
        current_user: User,
        name: str,
        description: Optional[str] = None,
        sequence_number: int = 1,
        owner_id: Optional[UUID] = None,
        planned_start: Optional[date] = None,
        planned_end: Optional[date] = None
    ) -> ProjectMilestone:
        """
        Create a new milestone.
        
        Args:
            project_id: Project ID
            current_user: Current user
            name: Milestone name
            description: Milestone description
            sequence_number: Sequence/order number
            owner_id: Owner user ID
            planned_start: Planned start date
            planned_end: Planned end date
            
        Returns:
            Created milestone
        """
        
        # Validate project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        if not self._can_manage_milestones(project, current_user):
            raise ValueError("Not authorized to manage project milestones")
        
        try:
            milestone = ProjectMilestone(
                project_id=project_id,
                name=name,
                description=description,
                sequence_number=sequence_number,
                owner_id=owner_id,
                planned_start=planned_start,
                planned_end=planned_end,
                status=MilestoneStatus.PENDING,
                completion_percentage=0
            )
            
            self.db.add(milestone)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="MILESTONE_CREATED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"milestone_name": name, "sequence": sequence_number}
            )
            
            self.db.commit()
            self.db.refresh(milestone)
            
            return milestone
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create milestone: {e}")
    
    def update_milestone(
        self,
        milestone_id: UUID,
        current_user: User,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[MilestoneStatus] = None,
        completion_percentage: Optional[int] = None,
        evidence: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ProjectMilestone:
        """
        Update milestone details.
        
        Args:
            milestone_id: Milestone ID
            current_user: Current user
            (other fields): Updated values
            
        Returns:
            Updated milestone
        """
        
        milestone = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.id == milestone_id
        ).first()
        
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        # Authorization check
        if not self._can_manage_milestones(milestone.project, current_user):
            raise ValueError("Not authorized to update milestone")
        
        try:
            # Update fields
            if name is not None:
                milestone.name = name
            if description is not None:
                milestone.description = description
            if status is not None:
                milestone.status = status
                # Set actual dates
                if status == MilestoneStatus.IN_PROGRESS and not milestone.actual_start:
                    milestone.actual_start = date.today()
                if status == MilestoneStatus.COMPLETED:
                    milestone.actual_end = date.today()
                    milestone.completion_percentage = 100
            if completion_percentage is not None:
                milestone.completion_percentage = max(0, min(100, completion_percentage))
            if evidence is not None:
                milestone.evidence = evidence
            if notes is not None:
                milestone.notes = notes
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="MILESTONE_UPDATED",
                entity_type="PROJECT",
                entity_id=milestone.project_id,
                details={
                    "milestone_id": str(milestone_id),
                    "milestone_name": milestone.name,
                    "status": status.value if status else None
                }
            )
            
            self.db.commit()
            self.db.refresh(milestone)
            
            return milestone
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update milestone: {e}")
    
    def complete_milestone(
        self,
        milestone_id: UUID,
        current_user: User,
        evidence: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ProjectMilestone:
        """
        Mark milestone as completed.
        
        Args:
            milestone_id: Milestone ID
            current_user: Current user
            evidence: Completion evidence
            notes: Completion notes
            
        Returns:
            Updated milestone
        """
        
        milestone = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.id == milestone_id
        ).first()
        
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        # Authorization check
        if not self._can_manage_milestones(milestone.project, current_user):
            raise ValueError("Not authorized to complete milestone")
        
        if milestone.status == MilestoneStatus.COMPLETED:
            raise ValueError("Milestone is already completed")
        
        try:
            milestone.status = MilestoneStatus.COMPLETED
            milestone.completion_percentage = 100
            milestone.actual_end = date.today()
            
            if evidence:
                milestone.evidence = evidence
            if notes:
                milestone.notes = notes
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="MILESTONE_COMPLETED",
                entity_type="PROJECT",
                entity_id=milestone.project_id,
                details={
                    "milestone_id": str(milestone_id),
                    "milestone_name": milestone.name
                }
            )
            
            self.db.commit()
            self.db.refresh(milestone)
            
            return milestone
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to complete milestone: {e}")
    
    def list_milestones(
        self,
        project_id: UUID,
        current_user: User
    ) -> List[Dict[str, Any]]:
        """
        List all milestones for a project.
        
        Args:
            project_id: Project ID
            current_user: Current user
            
        Returns:
            List of milestones
        """
        
        # Validate project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        from app.services.projects.project_service import ProjectService
        service = ProjectService(self.db)
        if not service._can_access_project(project, current_user):
            raise ValueError("Not authorized to view project milestones")
        
        # Get milestones
        milestones = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id
        ).order_by(ProjectMilestone.sequence_number).all()
        
        result = []
        for milestone in milestones:
            result.append({
                "id": str(milestone.id),
                "name": milestone.name,
                "description": milestone.description,
                "sequence_number": milestone.sequence_number,
                "status": milestone.status.value,
                "completion_percentage": milestone.completion_percentage,
                "planned_start": milestone.planned_start.isoformat() if milestone.planned_start else None,
                "planned_end": milestone.planned_end.isoformat() if milestone.planned_end else None,
                "actual_start": milestone.actual_start.isoformat() if milestone.actual_start else None,
                "actual_end": milestone.actual_end.isoformat() if milestone.actual_end else None,
                "owner_id": str(milestone.owner_id) if milestone.owner_id else None,
                "evidence": milestone.evidence,
                "notes": milestone.notes,
                "created_at": milestone.created_at.isoformat() if milestone.created_at else None
            })
        
        return result
    
    def _can_manage_milestones(self, project: Project, user: User) -> bool:
        """Check if user can manage milestones."""
        
        # Government and admin can manage
        if user.role in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            return True
        
        # University team can manage
        if user.role in [UserRole.UNIVERSITY_ADMIN, UserRole.FACULTY]:
            from app.services.projects.project_service import ProjectService
            service = ProjectService(self.db)
            user_university = service._get_user_university(user)
            return user_university and user_university == project.university_id
        
        return False
    
    def _create_audit_log(
        self,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID,
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
