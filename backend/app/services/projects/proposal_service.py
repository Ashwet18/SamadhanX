"""
Project proposal management service.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.project import Project, ProjectProposal
from app.models.user import User
from app.models.enums import ProposalStatus, ProjectStatus, UserRole
from app.models.platform import AuditLog, Notification


class ProposalService:
    """Service for managing project proposals."""
    
    def __init__(self, db: Session):
        """
        Initialize proposal service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_or_update_proposal(
        self,
        project_id: UUID,
        current_user: User,
        title: str,
        problem_statement: str,
        proposed_solution: str,
        methodology: Optional[str] = None,
        technology_stack: Optional[str] = None,
        innovation: Optional[str] = None,
        expected_outcomes: Optional[str] = None,
        beneficiaries: Optional[str] = None,
        estimated_budget: Optional[float] = None,
        required_resources: Optional[str] = None,
        implementation_plan: Optional[str] = None,
        risks: Optional[str] = None,
        sustainability_plan: Optional[str] = None
    ) -> ProjectProposal:
        """
        Create or update project proposal.
        
        Args:
            project_id: Project ID
            current_user: Current user
            (other fields): Proposal content
            
        Returns:
            Created or updated proposal
        """
        
        # Validate project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        if not self._can_edit_proposal(project, current_user):
            raise ValueError("Not authorized to edit proposal")
        
        try:
            # Check for existing proposal
            proposal = self.db.query(ProjectProposal).filter(
                ProjectProposal.project_id == project_id
            ).first()
            
            if proposal:
                # Update existing (only if DRAFT or REVISION_REQUIRED)
                if proposal.status not in [ProposalStatus.DRAFT, ProposalStatus.REVISION_REQUIRED]:
                    raise ValueError(
                        f"Cannot edit proposal with status: {proposal.status.value}"
                    )
                
                is_new = False
            else:
                # Create new
                proposal = ProjectProposal(project_id=project_id)
                is_new = True
            
            # Update fields
            proposal.title = title
            proposal.problem_statement = problem_statement
            proposal.proposed_solution = proposed_solution
            proposal.methodology = methodology
            proposal.technology_stack = technology_stack
            proposal.innovation = innovation
            proposal.expected_outcomes = expected_outcomes
            proposal.beneficiaries = beneficiaries
            proposal.estimated_budget = estimated_budget
            proposal.required_resources = required_resources
            proposal.implementation_plan = implementation_plan
            proposal.risks = risks
            proposal.sustainability_plan = sustainability_plan
            proposal.status = ProposalStatus.DRAFT
            
            if is_new:
                self.db.add(proposal)
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROPOSAL_UPDATED" if not is_new else "PROPOSAL_CREATED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"title": title, "status": ProposalStatus.DRAFT.value}
            )
            
            self.db.commit()
            self.db.refresh(proposal)
            
            return proposal
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to save proposal: {e}")
    
    def submit_proposal(
        self,
        project_id: UUID,
        current_user: User
    ) -> ProjectProposal:
        """
        Submit proposal for review.
        
        Args:
            project_id: Project ID
            current_user: Current user
            
        Returns:
            Updated proposal
        """
        
        proposal = self._get_proposal(project_id)
        
        # Validate status
        if proposal.status != ProposalStatus.DRAFT:
            raise ValueError(f"Can only submit DRAFT proposals. Current status: {proposal.status.value}")
        
        # Authorization check
        project = proposal.project
        if not self._can_edit_proposal(project, current_user):
            raise ValueError("Not authorized to submit proposal")
        
        try:
            proposal.status = ProposalStatus.SUBMITTED
            proposal.submitted_by = current_user.id
            proposal.submitted_at = datetime.utcnow()
            
            # Update project status
            if project.status == ProjectStatus.PLANNING:
                project.status = ProjectStatus.PROPOSAL
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROPOSAL_SUBMITTED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"title": proposal.title}
            )
            
            # Notify government
            self._create_notification(
                user_role=UserRole.GOVERNMENT_OFFICER,
                notification_type="PROPOSAL_SUBMITTED",
                title="Proposal Submitted for Review",
                message=f"Project '{project.name}' ({project.project_code}) has submitted a solution proposal for review.",
                reference_type="PROJECT",
                reference_id=project_id
            )
            
            self.db.commit()
            self.db.refresh(proposal)
            
            return proposal
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to submit proposal: {e}")
    
    def approve_proposal(
        self,
        project_id: UUID,
        current_user: User,
        comments: Optional[str] = None
    ) -> ProjectProposal:
        """
        Approve proposal (Government only).
        
        Args:
            project_id: Project ID
            current_user: Current user (must be government)
            comments: Optional review comments
            
        Returns:
            Updated proposal
        """
        
        if current_user.role not in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            raise ValueError("Only government officers can approve proposals")
        
        proposal = self._get_proposal(project_id)
        
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Can only approve SUBMITTED proposals. Current status: {proposal.status.value}")
        
        try:
            proposal.status = ProposalStatus.APPROVED
            proposal.reviewed_by = current_user.id
            proposal.reviewed_at = datetime.utcnow()
            proposal.review_comments = comments
            
            # Update project status
            project = proposal.project
            if project.status == ProjectStatus.PROPOSAL:
                project.status = ProjectStatus.APPROVED
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROPOSAL_APPROVED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"title": proposal.title, "comments": comments}
            )
            
            # Notify university
            self._notify_university(
                project=project,
                notification_type="PROPOSAL_APPROVED",
                title="Proposal Approved",
                message=f"Your solution proposal for project '{project.name}' has been approved by the government."
            )
            
            self.db.commit()
            self.db.refresh(proposal)
            
            return proposal
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to approve proposal: {e}")
    
    def request_revision(
        self,
        project_id: UUID,
        current_user: User,
        comments: str
    ) -> ProjectProposal:
        """
        Request revisions to proposal (Government only).
        
        Args:
            project_id: Project ID
            current_user: Current user (must be government)
            comments: Required revision comments
            
        Returns:
            Updated proposal
        """
        
        if current_user.role not in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            raise ValueError("Only government officers can request revisions")
        
        if not comments:
            raise ValueError("Comments are required when requesting revisions")
        
        proposal = self._get_proposal(project_id)
        
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Can only review SUBMITTED proposals. Current status: {proposal.status.value}")
        
        try:
            proposal.status = ProposalStatus.REVISION_REQUIRED
            proposal.reviewed_by = current_user.id
            proposal.reviewed_at = datetime.utcnow()
            proposal.review_comments = comments
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROPOSAL_REVISION_REQUESTED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"title": proposal.title, "comments": comments}
            )
            
            # Notify university
            self._notify_university(
                project=proposal.project,
                notification_type="PROPOSAL_REVISION_REQUESTED",
                title="Proposal Revision Requested",
                message=f"Government has requested revisions to your proposal for project '{proposal.project.name}'. Comments: {comments[:100]}"
            )
            
            self.db.commit()
            self.db.refresh(proposal)
            
            return proposal
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to request revision: {e}")
    
    def reject_proposal(
        self,
        project_id: UUID,
        current_user: User,
        comments: str
    ) -> ProjectProposal:
        """
        Reject proposal (Government only).
        
        Args:
            project_id: Project ID
            current_user: Current user (must be government)
            comments: Required rejection reason
            
        Returns:
            Updated proposal
        """
        
        if current_user.role not in [UserRole.GOVERNMENT_OFFICER, UserRole.PLATFORM_ADMIN]:
            raise ValueError("Only government officers can reject proposals")
        
        if not comments:
            raise ValueError("Comments are required when rejecting proposals")
        
        proposal = self._get_proposal(project_id)
        
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Can only review SUBMITTED proposals. Current status: {proposal.status.value}")
        
        try:
            proposal.status = ProposalStatus.REJECTED
            proposal.reviewed_by = current_user.id
            proposal.reviewed_at = datetime.utcnow()
            proposal.review_comments = comments
            
            # Create audit log
            self._create_audit_log(
                user_id=current_user.id,
                action="PROPOSAL_REJECTED",
                entity_type="PROJECT",
                entity_id=project_id,
                details={"title": proposal.title, "comments": comments}
            )
            
            # Notify university
            self._notify_university(
                project=proposal.project,
                notification_type="PROPOSAL_REJECTED",
                title="Proposal Rejected",
                message=f"Your proposal for project '{proposal.project.name}' has been rejected. Reason: {comments[:100]}"
            )
            
            self.db.commit()
            self.db.refresh(proposal)
            
            return proposal
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to reject proposal: {e}")
    
    def get_proposal(self, project_id: UUID, current_user: User) -> Optional[ProjectProposal]:
        """Get proposal with authorization check."""
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Authorization check
        from app.services.projects.project_service import ProjectService
        service = ProjectService(self.db)
        if not service._can_access_project(project, current_user):
            raise ValueError("Not authorized to view proposal")
        
        return self.db.query(ProjectProposal).filter(
            ProjectProposal.project_id == project_id
        ).first()
    
    def _get_proposal(self, project_id: UUID) -> ProjectProposal:
        """Get proposal or raise error."""
        
        proposal = self.db.query(ProjectProposal).filter(
            ProjectProposal.project_id == project_id
        ).first()
        
        if not proposal:
            raise ValueError(f"No proposal found for project {project_id}")
        
        return proposal
    
    def _can_edit_proposal(self, project: Project, user: User) -> bool:
        """Check if user can edit proposal."""
        
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
    
    def _notify_university(self, project: Project, notification_type: str, title: str, message: str):
        """Notify university team members."""
        try:
            from app.models.project import ProjectMember
            members = self.db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
            for member in members:
                notification = Notification(user_id=member.user_id, type=notification_type, title=title, message=message, reference_type="PROJECT", reference_id=project.id, is_read=False)
                self.db.add(notification)
        except Exception:
            pass
