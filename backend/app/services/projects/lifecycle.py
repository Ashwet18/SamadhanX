"""
Project lifecycle state machine and transitions.
"""

from typing import Dict, Set
from app.models.enums import ProjectStatus


class ProjectLifecycleManager:
    """Manages valid project status transitions."""
    
    # Valid state transitions
    VALID_TRANSITIONS: Dict[ProjectStatus, Set[ProjectStatus]] = {
        ProjectStatus.PLANNING: {
            ProjectStatus.TEAM_FORMATION,
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.TEAM_FORMATION: {
            ProjectStatus.PROPOSAL,
            ProjectStatus.PLANNING,  # Can go back
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.PROPOSAL: {
            ProjectStatus.APPROVED,
            ProjectStatus.TEAM_FORMATION,  # Can go back
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.APPROVED: {
            ProjectStatus.PROTOTYPE,
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.PROTOTYPE: {
            ProjectStatus.TESTING,
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.TESTING: {
            ProjectStatus.PILOT,
            ProjectStatus.PROTOTYPE,  # Can go back
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.PILOT: {
            ProjectStatus.DEPLOYED,
            ProjectStatus.TESTING,  # Can go back
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.DEPLOYED: {
            ProjectStatus.COMPLETED,
            ProjectStatus.ON_HOLD,
            ProjectStatus.CANCELLED
        },
        ProjectStatus.ON_HOLD: {
            # Can return to any previous active state
            # This is handled specially in is_valid_transition
        },
        ProjectStatus.COMPLETED: set(),  # Terminal state
        ProjectStatus.CANCELLED: set()   # Terminal state
    }
    
    @classmethod
    def is_valid_transition(
        cls,
        current_status: ProjectStatus,
        new_status: ProjectStatus,
        previous_status: ProjectStatus = None
    ) -> bool:
        """
        Check if status transition is valid.
        
        Args:
            current_status: Current project status
            new_status: Desired new status
            previous_status: Status before ON_HOLD (optional)
            
        Returns:
            True if transition is valid
        """
        
        # Special case: ON_HOLD can return to appropriate active states
        if current_status == ProjectStatus.ON_HOLD and previous_status:
            # Can return to the status it was in before going ON_HOLD
            return new_status == previous_status or new_status in [
                ProjectStatus.PLANNING,
                ProjectStatus.TEAM_FORMATION,
                ProjectStatus.PROPOSAL,
                ProjectStatus.APPROVED,
                ProjectStatus.PROTOTYPE,
                ProjectStatus.TESTING,
                ProjectStatus.PILOT,
                ProjectStatus.DEPLOYED
            ]
        
        # Normal transitions
        allowed_transitions = cls.VALID_TRANSITIONS.get(current_status, set())
        return new_status in allowed_transitions
    
    @classmethod
    def get_next_states(cls, current_status: ProjectStatus) -> Set[ProjectStatus]:
        """
        Get allowed next states from current status.
        
        Args:
            current_status: Current project status
            
        Returns:
            Set of allowed next statuses
        """
        return cls.VALID_TRANSITIONS.get(current_status, set())
    
    @classmethod
    def can_be_edited(cls, status: ProjectStatus) -> bool:
        """
        Check if project can be edited in current status.
        
        Args:
            status: Project status
            
        Returns:
            True if project details can be edited
        """
        return status in [
            ProjectStatus.PLANNING,
            ProjectStatus.TEAM_FORMATION,
            ProjectStatus.PROPOSAL
        ]
    
    @classmethod
    def requires_proposal(cls, status: ProjectStatus) -> bool:
        """
        Check if status requires an approved proposal.
        
        Args:
            status: Project status
            
        Returns:
            True if proposal must be approved
        """
        return status in [
            ProjectStatus.APPROVED,
            ProjectStatus.PROTOTYPE,
            ProjectStatus.TESTING,
            ProjectStatus.PILOT,
            ProjectStatus.DEPLOYED,
            ProjectStatus.COMPLETED
        ]
    
    @classmethod
    def is_terminal(cls, status: ProjectStatus) -> bool:
        """
        Check if status is terminal (no further transitions).
        
        Args:
            status: Project status
            
        Returns:
            True if status is terminal
        """
        return status in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]
