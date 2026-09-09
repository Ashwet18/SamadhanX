"""
Main project management service.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.project import Project
from app.models.challenge import Challenge, ChallengeAssignment
from app.models.university import University
from app.models.user import User
from app.models.enums import (
    ChallengeStatus,
    AssignmentStatus,
    ProjectStatus,
    UserRole
)
from app.models.platform import AuditLog, Notification
from app.services.projects.lifecycle import ProjectLifecycleManager


class ProjectService:
    """Service for project management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize project service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.lifecycle_manager = ProjectLifecycleManager()
    
    def create_project(
        self,
        challenge_id: UUID,
        current_user: User,
        name: str,
        description: Optional[str] = None,
        objective: Optional[str] = None,
        department_id: Optional[UUID] = None,
        expected_start_date: Optional[date] = None,
        expected_end_date: Optional[date] = None
    ) -> Project:
        """
        Create a new project from an accepted challenge assignment.
        
        Args:
            challenge_id: Challenge ID
            current_user: User creating the project
            name: Project name
            description: Project description
            objective: Project objective
            department_id: Department ID
            expected_end_date: Expected completion date
            
        Returns:
            Created project
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If creation fails
        """
        
        # Validate challenge exists
        challenge = self.db.query(Challenge).filter(
            Challenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        # Get user's university
        university_id = self._get_user_university(current_user)
        if not university_id:
            raise ValueError("User is not associated with a university")
        
        # Check for ACCEPTED assignment
        assignment = self.db.query(ChallengeAssignment).filter(
            ChallengeAssignment.challenge_id == challenge_id,
            ChallengeAssignment.university_id == university_id,
            ChallengeAssignment.status == AssignmentStatus.ACCEPTED
        ).first()
        
        if not assignment:
            raise ValueError(
                "No ACCEPTED assignment found for this challenge and university. "
                "University must accept the invitation before creating a project."
            )
        
        # Check for duplicate active project
        existing_project = self.db.query(Project).filter(
            Project.challenge_id == challenge_id,
            Project.university_id == university_id,
            Project.status.notin_([ProjectStatus.CANCELLED, ProjectStatus.COMPLETED])
        ).first()
        
        if existing_project:
            raise ValueError(
                f"An active project already exists for this challenge: {existing_project.project_code}"
            )
        
        try:
            # Generate project code
            project_code = self._generate_project_code()
            
            # Create project
            project = Project(
                project_code=project_code,
                challenge_id=challenge_id,
                university_id=university_id,
                department_id=department_id,
                name=name,
                description=description,
                objective=objective,
                status=ProjectStatus.PLANNING,
                start_date=expected_start_date or date.today(),
                expected_end_date=expected_end_date,
                created_by=current_user.id
            )
            
            self.db.add(project)
            
            # Update challenge status
            if challenge.status == ChallengeStatus.ACCEPTED:
                challenge.status = ChallengeStatus.PROJECT_CREATED
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROJECT_CREATED",
                entity_type="PROJECT",
                entity_id=None,  # Will be set after commit
                details={
                    "project_code": project_code,
                    "challenge_id": str(challenge_id),
                    "university_id": str(university_id),
                    "name": name
                }
            )
            
            # Create notification for government
            self._create_notification(
                user_role=UserRole.GOVERNMENT_OFFICER,
                notification_type="PROJECT_CREATED",
                title="New Project Created",
                message=f"Project '{name}' ({project_code}) has been created for challenge {challenge.challenge_code}",
                reference_type="PROJECT",
                reference_id=None  # Will be set after commit
            )
            
            self.db.commit()
            self.db.refresh(project)
            
            return project
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create project: {e}")
    
    def get_project(self, project_id: UUID, current_user: User) -> Project:
        """
        Get project by ID with authorization check.
        
        Args:
            project_id: Project ID
            current_user: Current user
            
        Returns:
            Project
            
        Raises:
            ValueError: If not found or not authorized
        """
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        if not self._can_access_project(project, current_user):
            raise ValueError("Not authorized to access this project")
        
        return project
    
    def list_projects(
        self,
        current_user: User,
        status_filter: Optional[ProjectStatus] = None,
        university_id: Optional[UUID] = None,
        challenge_id: Optional[UUID] = None,
        department_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple:
        """
        List projects with filtering and pagination.
        
        Args:
            current_user: Current user
            status_filter: Filter by status
            university_id: Filter by university
            challenge_id: Filter by challenge
            department_id: Filter by department
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (projects list, total count)
        """
        
        query = self.db.query(Project)
        
        # Authorization-based filtering
        if current_user.role == UserRole.GOVERNMENT_OFFICER or current_user.role == UserRole.PLATFORM_ADMIN:
            # Can see all projects (optionally filtered by university_id)
            if university_id:
                query = query.filter(Project.university_id == university_id)
        elif current_user.role in [UserRole.UNIVERSITY_ADMIN, UserRole.FACULTY]:
            # Can only see own university projects
            user_university_id = self._get_user_university(current_user)
            if user_university_id:
                query = query.filter(Project.university_id == user_university_id)
            else:
                return [], 0
        elif current_user.role == UserRole.STUDENT:
            # Can only see projects they're member of
            from app.models.project import ProjectMember
            query = query.join(ProjectMember).filter(ProjectMember.user_id == current_user.id)
        else:
            # Citizens cannot access projects
            return [], 0
        
        # Apply filters
        if status_filter:
            query = query.filter(Project.status == status_filter)
        if challenge_id:
            query = query.filter(Project.challenge_id == challenge_id)
        if department_id:
            query = query.filter(Project.department_id == department_id)
        
        # Count total
        total = query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        projects = query.order_by(Project.created_at.desc()).offset(offset).limit(page_size).all()
        
        return projects, total
    
    def update_project_status(
        self,
        project_id: UUID,
        new_status: ProjectStatus,
        current_user: User,
        reason: Optional[str] = None
    ) -> Project:
        """
        Update project status with validation.
        
        Args:
            project_id: Project ID
            new_status: New status
            current_user: Current user
            reason: Optional reason
            
        Returns:
            Updated project
            
        Raises:
            ValueError: If transition is invalid
        """
        
        project = self.get_project(project_id, current_user)
        
        # Validate transition
        if not self.lifecycle_manager.is_valid_transition(project.status, new_status):
            raise ValueError(
                f"Invalid status transition from {project.status.value} to {new_status.value}"
            )
        
        # Authorization check
        if not self._can_manage_project(project, current_user):
            raise PermissionError("Not authorized to change project status")
        
        try:
            old_status = project.status
            project.status = new_status
            
            # Set completion date if completed
            if new_status == ProjectStatus.COMPLETED:
                project.actual_end_date = date.today()
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROJECT_STATUS_CHANGED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "reason": reason
                }
            )
            
            self.db.commit()
            self.db.refresh(project)
            
            return project
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update project status: {e}")
    
    def update_project(
        self,
        project_id: UUID,
        current_user: User,
        **updates
    ) -> Project:
        """
        Update project details.
        
        Args:
            project_id: Project ID
            current_user: Current user
            **updates: Fields to update
            
        Returns:
            Updated project
        """
        
        project = self.get_project(project_id, current_user)
        
        # Authorization check
        if not self._can_manage_project(project, current_user):
            raise PermissionError("Not authorized to update project")
        
        try:
            # Update allowed fields
            allowed_fields = ['name', 'description', 'objective', 'expected_start_date', 'expected_end_date', 'actual_start_date', 'actual_end_date']
            for field, value in updates.items():
                if field in allowed_fields and value is not None:
                    setattr(project, field, value)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROJECT_UPDATED",
                entity_type="PROJECT",
                entity_id=project_id,
                details=updates
            )
            
            self.db.commit()
            self.db.refresh(project)
            
            return project
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update project: {e}")
    
    def get_project_dashboard(
        self,
        project_id: UUID,
        current_user: User
    ) -> Dict[str, Any]:
        """
        Get comprehensive project dashboard with aggregates.
        
        Args:
            project_id: Project ID
            current_user: Current user
            
        Returns:
            Dashboard data with project, challenge, university, team, milestones, impact
        """
        
        project = self.get_project(project_id, current_user)
        
        # Get challenge
        challenge = None
        if project.challenge:
            challenge = {
                "id": str(project.challenge.id),
                "challenge_code": project.challenge.challenge_code,
                "title": project.challenge.title,
                "status": project.challenge.status.value
            }
        
        # Get university
        university = None
        if project.university:
            university = {
                "id": str(project.university.id),
                "name": project.university.name,
                "district": project.university.district
            }
        
        # Get department if exists
        department = None
        if project.department_id:
            from app.models.university import Department
            dept = self.db.query(Department).filter(Department.id == project.department_id).first()
            if dept:
                department = {
                    "id": str(dept.id),
                    "name": dept.name
                }
        
        # Get team count
        from app.models.project import ProjectMember
        team_count = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id
        ).count()
        
        # Get milestone stats
        from app.models.project import ProjectMilestone
        from app.models.enums import MilestoneStatus
        
        milestone_count = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id
        ).count()
        
        completed_milestones = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id,
            ProjectMilestone.status == MilestoneStatus.COMPLETED
        ).count()
        
        completion_percentage = (completed_milestones / milestone_count * 100) if milestone_count > 0 else 0.0
        
        # Get current/next milestone
        current_milestone = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id,
            ProjectMilestone.status == MilestoneStatus.IN_PROGRESS
        ).order_by(ProjectMilestone.sequence_number).first()
        
        next_milestone = self.db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id,
            ProjectMilestone.status == MilestoneStatus.PLANNED
        ).order_by(ProjectMilestone.sequence_number).first()
        
        current_milestone_data = None
        if current_milestone:
            current_milestone_data = {
                "id": str(current_milestone.id),
                "title": current_milestone.title,
                "sequence_number": current_milestone.sequence_number,
                "planned_end_date": current_milestone.planned_end_date.isoformat() if current_milestone.planned_end_date else None
            }
        
        next_milestone_data = None
        if next_milestone:
            next_milestone_data = {
                "id": str(next_milestone.id),
                "title": next_milestone.title,
                "sequence_number": next_milestone.sequence_number,
                "planned_start_date": next_milestone.planned_start_date.isoformat() if next_milestone.planned_start_date else None
            }
        
        # Get impact summary
        from app.models.platform import ImpactMetric
        from app.models.enums import VerificationStatus
        
        impact_metrics = self.db.query(ImpactMetric).filter(
            ImpactMetric.project_id == project_id
        ).all()
        
        impact_summary = None
        if impact_metrics:
            verified_count = sum(1 for m in impact_metrics if m.verification_status == VerificationStatus.VERIFIED)
            total_beneficiaries = sum(m.beneficiaries_count or 0 for m in impact_metrics)
            
            impact_summary = {
                "total_metrics": len(impact_metrics),
                "verified_metrics": verified_count,
                "total_beneficiaries": total_beneficiaries,
                "deployment_date": impact_metrics[0].deployment_date.isoformat() if impact_metrics[0].deployment_date else None
            }
        
        # Latest activity
        latest_activity = project.updated_at
        
        return {
            "project": project,
            "challenge": challenge,
            "university": university,
            "department": department,
            "team_count": team_count,
            "milestone_count": milestone_count,
            "completed_milestones": completed_milestones,
            "completion_percentage": round(completion_percentage, 2),
            "current_milestone": current_milestone_data,
            "next_milestone": next_milestone_data,
            "latest_activity": latest_activity,
            "impact_summary": impact_summary
        }
    
    def _generate_project_code(self) -> str:
        """Generate unique project code: PRJ-JH-YYYY-XXXXX"""
        
        year = datetime.now().year
        
        # Get latest project for this year
        latest = self.db.query(Project).filter(
            Project.project_code.like(f"PRJ-JH-{year}-%")
        ).order_by(Project.project_code.desc()).first()
        
        if latest:
            # Extract sequence number and increment
            sequence = int(latest.project_code.split('-')[-1]) + 1
        else:
            sequence = 1
        
        return f"PRJ-JH-{year}-{sequence:05d}"
    
    def _get_user_university(self, user: User) -> Optional[UUID]:
        """Get user's university ID."""
        
        if user.role == UserRole.UNIVERSITY_ADMIN:
            # TODO: Get from user-university mapping when available
            # For now, get from faculty or student profile
            pass
        
        if user.role == UserRole.FACULTY and user.faculty_profile:
            return user.faculty_profile.university_id
        
        if user.role == UserRole.STUDENT and user.student_profile:
            return user.student_profile.university_id
        
        return None
    
    def _can_access_project(self, project: Project, user: User) -> bool:
        """Check if user can access project."""
        
        # Government and admin can access all
        if user.role in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            return True
        
        # University users can access their university's projects
        user_university = self._get_user_university(user)
        if user_university and user_university == project.university_id:
            return True
        
        # Students can access if they're team members
        if user.role == UserRole.STUDENT:
            from app.models.project import ProjectMember
            member = self.db.query(ProjectMember).filter(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == user.id
            ).first()
            return member is not None
        
        return False
    
    def _can_manage_project(self, project: Project, user: User) -> bool:
        """Check if user can manage project (change status, etc)."""
        
        # Government and admin can manage
        if user.role in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            return True
        
        # University admin and faculty from same university can manage
        if user.role in [UserRole.UNIVERSITY_ADMIN, UserRole.FACULTY]:
            user_university = self._get_user_university(user)
            return user_university and user_university == project.university_id
        
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
            # Note: Commit happens in calling function
        except Exception:
            # Don't fail operation if audit logging fails
            pass
    
    def _create_notification(
        self,
        user_role: UserRole,
        notification_type: str,
        title: str,
        message: str,
        reference_type: str,
        reference_id: Optional[UUID]
    ):
        """Create notification for users with specific role."""
        
        try:
            # Get users with role
            users = self.db.query(User).filter(User.role == user_role).all()
            
            for user in users:
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
            # Note: Commit happens in calling function
        except Exception:
            # Don't fail operation if notification creation fails
            pass
