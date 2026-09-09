"""
Partnership lifecycle state machine.

Manages valid partnership status transitions and enforces business rules.
"""

from typing import Dict, Set
from app.models.enums import PartnershipStatus


class PartnershipLifecycleManager:
    """Manages partnership status transitions."""
    
    # Define valid transitions
    VALID_TRANSITIONS: Dict[PartnershipStatus, Set[PartnershipStatus]] = {
        PartnershipStatus.RECOMMENDED: {
            PartnershipStatus.REQUESTED,
            PartnershipStatus.CANCELLED
        },
        PartnershipStatus.REQUESTED: {
            PartnershipStatus.UNDER_REVIEW,
            PartnershipStatus.DECLINED,
            PartnershipStatus.CANCELLED
        },
        PartnershipStatus.UNDER_REVIEW: {
            PartnershipStatus.ACCEPTED,
            PartnershipStatus.DECLINED,
            PartnershipStatus.CANCELLED
        },
        PartnershipStatus.ACCEPTED: {
            PartnershipStatus.ACTIVE,
            PartnershipStatus.CANCELLED
        },
        PartnershipStatus.DECLINED: set(),  # Terminal state
        PartnershipStatus.ACTIVE: {
            PartnershipStatus.COMPLETED,
            PartnershipStatus.CANCELLED
        },
        PartnershipStatus.COMPLETED: set(),  # Terminal state
        PartnershipStatus.CANCELLED: set()  # Terminal state
    }
    
    # Terminal states (cannot transition from these)
    TERMINAL_STATES = {
        PartnershipStatus.DECLINED,
        PartnershipStatus.COMPLETED,
        PartnershipStatus.CANCELLED
    }
    
    def is_valid_transition(
        self,
        current_status: PartnershipStatus,
        new_status: PartnershipStatus
    ) -> bool:
        """
        Check if a status transition is valid.
        
        Args:
            current_status: Current partnership status
            new_status: Desired new status
            
        Returns:
            True if transition is valid, False otherwise
        """
        if current_status not in self.VALID_TRANSITIONS:
            return False
        
        return new_status in self.VALID_TRANSITIONS[current_status]
    
    def get_valid_next_states(self, current_status: PartnershipStatus) -> Set[PartnershipStatus]:
        """
        Get all valid next states from current status.
        
        Args:
            current_status: Current partnership status
            
        Returns:
            Set of valid next statuses
        """
        return self.VALID_TRANSITIONS.get(current_status, set())
    
    def is_terminal_state(self, status: PartnershipStatus) -> bool:
        """
        Check if a status is terminal (no transitions possible).
        
        Args:
            status: Partnership status to check
            
        Returns:
            True if terminal state, False otherwise
        """
        return status in self.TERMINAL_STATES
    
    def get_lifecycle_description(self) -> Dict[str, str]:
        """
        Get human-readable lifecycle descriptions.
        
        Returns:
            Dict mapping status to description
        """
        return {
            "RECOMMENDED": "Industry partner recommended by matching algorithm",
            "REQUESTED": "Partnership request sent to industry partner",
            "UNDER_REVIEW": "Industry partner reviewing partnership request",
            "ACCEPTED": "Industry partner accepted partnership request",
            "DECLINED": "Industry partner declined partnership request (terminal)",
            "ACTIVE": "Partnership is active and ongoing",
            "COMPLETED": "Partnership successfully completed (terminal)",
            "CANCELLED": "Partnership cancelled (terminal)"
        }
