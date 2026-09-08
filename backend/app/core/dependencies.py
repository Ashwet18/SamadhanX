"""
FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Set
from uuid import UUID

from app.db.database import get_db
from app.core.security import security
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.enums import UserRole, AccountStatus


# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = security.decode_token(token)
        
        # Extract user data
        token_data = payload.get("sub")
        if not token_data:
            raise credentials_exception
        
        # Handle both old format (string user_id) and new format (dict with user info)
        if isinstance(token_data, dict):
            user_id_str = token_data.get("sub")
        else:
            user_id_str = token_data
        
        if not user_id_str:
            raise credentials_exception
        
        try:
            user_id = UUID(user_id_str)
        except (ValueError, AttributeError):
            raise credentials_exception
        
    except Exception:
        raise credentials_exception
    
    # Fetch user from database
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    
    # Check account status
    if user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.account_status.value.lower()}"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user with status check).
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current active user
    """
    return current_user


class RoleChecker:
    """
    Dependency class for checking user roles.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(RoleChecker([UserRole.PLATFORM_ADMIN]))])
        async def admin_only():
            ...
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Check if user has any of the allowed roles.
        
        Args:
            current_user: Current user
            
        Returns:
            Current user if authorized
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_roles = {ur.role.name for ur in current_user.roles}
        allowed_roles_set = set(self.allowed_roles)
        
        if not user_roles.intersection(allowed_roles_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user


class RequireAllRoles:
    """
    Dependency class for checking if user has ALL specified roles.
    
    Usage:
        @app.get("/special", dependencies=[Depends(RequireAllRoles([UserRole.FACULTY, UserRole.RESEARCHER]))])
        async def special_endpoint():
            ...
    """
    
    def __init__(self, required_roles: List[UserRole]):
        self.required_roles = set(required_roles)
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Check if user has all required roles.
        
        Args:
            current_user: Current user
            
        Returns:
            Current user if authorized
            
        Raises:
            HTTPException: If user doesn't have all required roles
        """
        user_roles = {ur.role.name for ur in current_user.roles}
        
        if not self.required_roles.issubset(user_roles):
            missing_roles = self.required_roles - user_roles
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required roles: {', '.join(r.value for r in missing_roles)}"
            )
        
        return current_user


def require_role(*roles: UserRole):
    """
    Create a dependency that requires any of the specified roles.
    
    Args:
        *roles: One or more required roles
        
    Returns:
        Dependency function
        
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role(UserRole.PLATFORM_ADMIN))])
        async def admin_only():
            ...
    """
    return RoleChecker(list(roles))


def require_any_role(*roles: UserRole):
    """
    Create a dependency that requires any of the specified roles (alias for require_role).
    
    Args:
        *roles: One or more required roles
        
    Returns:
        Dependency function
    """
    return RoleChecker(list(roles))


def require_all_roles(*roles: UserRole):
    """
    Create a dependency that requires all of the specified roles.
    
    Args:
        *roles: Required roles (user must have all)
        
    Returns:
        Dependency function
        
    Usage:
        @app.get("/special", dependencies=[Depends(require_all_roles(UserRole.FACULTY, UserRole.RESEARCHER))])
        async def special_endpoint():
            ...
    """
    return RequireAllRoles(list(roles))


# Convenience dependencies for common role checks
require_citizen = require_role(UserRole.CITIZEN)
require_government = require_role(UserRole.GOVERNMENT_OFFICER)
require_university_admin = require_role(UserRole.UNIVERSITY_ADMIN)
require_faculty = require_role(UserRole.FACULTY)
require_student = require_role(UserRole.STUDENT)
require_industry = require_role(UserRole.INDUSTRY)
require_platform_admin = require_role(UserRole.PLATFORM_ADMIN)

# Combined role dependencies
require_admin_or_government = require_any_role(
    UserRole.PLATFORM_ADMIN,
    UserRole.GOVERNMENT_OFFICER
)

require_university_staff = require_any_role(
    UserRole.UNIVERSITY_ADMIN,
    UserRole.FACULTY
)

require_university_member = require_any_role(
    UserRole.UNIVERSITY_ADMIN,
    UserRole.FACULTY,
    UserRole.STUDENT
)
