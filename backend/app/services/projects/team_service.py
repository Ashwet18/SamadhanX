"""
Project team management service.
"""

from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.project import Project, ProjectMember
from app.models.user import User
from app.models.enums import ProjectMemberRole, UserRole
from app.models.platform import AuditLog


class TeamService:
    """Service for managing project team members."""
    
    def __init__(self, db: Session):
        """
        Initialize team service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def add_member(
        self,
        project_id: UUID,
        user_id: UUID,
        role: ProjectMemberRole,
        current_user: User
    ) -> ProjectMember:
        """
        Add a member to project team.
        
        Args:
            project_id: Project ID
            user_id: User ID to add
            role: Team role
            current_user: User adding the member
            
        Returns:
            Created project member
            
        Raises:
            ValueError: If validation fails
        """
        
        # Validate project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Validate user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Authorization check
        if not self._can_manage_team(project, current_user):
            raise ValueError("Not authorized to manage project team")
        
        # Validate role matches user role
        if role == ProjectMemberRole.FACULTY and user.role != UserRole.FACULTY:
            raise ValueError("User must have FACULTY role to be added as faculty")
        if role == ProjectMemberRole.STUDENT and user.role != UserRole.STUDENT:
            raise ValueError("User must have STUDENT role to be added as student")
        
        try:
            # Create member
            member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                role=role,
                joined_at=datetime.utcnow()
            )
            
            self.db.add(member)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="TEAM_MEMBER_ADDED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={
                    "member_user_id": str(user_id),
                    "member_name": user.full_name,
                    "role": role.value
                }
            )
            
            self.db.commit()
            self.db.refresh(member)
            
            return member
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User is already a member of this project")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to add team member: {e}")
    
    def remove_member(
        self,
        project_id: UUID,
        member_id: UUID,
        current_user: User
    ):
        """
        Remove a member from project team.
        
        Args:
            project_id: Project ID
            member_id: Member ID to remove
            current_user: User removing the member
            
        Raises:
            ValueError: If validation fails
        """
        
        # Validate project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        if not self._can_manage_team(project, current_user):
            raise ValueError("Not authorized to manage project team")
        
        # Get member
        member = self.db.query(ProjectMember).filter(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id
        ).first()
        
        if not member:
            raise ValueError(f"Team member {member_id} not found in this project")
        
        try:
            # Create audit log before deletion
            self._create_audit_log(
                user_id=current_user.id,
                action="TEAM_MEMBER_REMOVED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={
                    "member_user_id": str(member.user_id),
                    "member_name": member.user.full_name if member.user else "Unknown",
                    "role": member.role.value
                }
            )
            
            self.db.delete(member)
            self.db.commit()
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to remove team member: {e}")
    
    def list_members(self, project_id: UUID, current_user: User) -> List[Dict[str, Any]]:
        """
        List all team members for a project.
        
        Args:
            project_id: Project ID
            current_user: Current user
            
        Returns:
            List of team members with details
        """
        
        # Validate project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check (can view if can access project)
        from app.services.projects.project_service import ProjectService
        service = ProjectService(self.db)
        if not service._can_access_project(project, current_user):
            raise ValueError("Not authorized to view project team")
        
        # Get members
        members = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id
        ).all()
        
        result = []
        for member in members:
            result.append({
                "id": str(member.id),
                "user_id": str(member.user_id),
                "name": member.user.full_name if member.user else "Unknown",
                "email": member.user.email if member.user else None,
                "role": member.role.value,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None
            })
        
        return result
    
    def _can_manage_team(self, project: Project, user: User) -> bool:
        """Check if user can manage project team."""
        
        # Government and admin can manage
        if user.role in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            return True
        
        # University admin and faculty from same university can manage
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
