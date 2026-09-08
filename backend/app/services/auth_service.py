"""
Authentication service for user management and authentication.
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.models.user import User, Role, UserRoleAssociation, Citizen, GovernmentOfficer
from app.models.enums import UserRole, AccountStatus
from app.schemas.auth import UserRegister, UserLogin, UserResponse, LoginResponse
from app.core.security import security
from app.core.config import settings


class AuthService:
    """Service for authentication and user management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserRegister) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists or other validation fails
        """
        # Check if email already exists
        existing_user = self.db.execute(
            select(User).where(User.email == user_data.email)
        ).scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = security.hash_password(user_data.password)
        
        # Create user
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=password_hash,
            account_status=AccountStatus.ACTIVE
        )
        
        self.db.add(user)
        self.db.flush()
        
        # Get or create role
        role = self.db.execute(
            select(Role).where(Role.name == user_data.role)
        ).scalar_one_or_none()
        
        if not role:
            role = Role(name=user_data.role, description=f"{user_data.role.value} role")
            self.db.add(role)
            self.db.flush()
        
        # Assign role to user
        user_role = UserRoleAssociation(user_id=user.id, role_id=role.id)
        self.db.add(user_role)
        
        # Create profile based on role
        if user_data.role == UserRole.CITIZEN:
            citizen = Citizen(user_id=user.id)
            self.db.add(citizen)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, login_data: UserLogin) -> LoginResponse:
        """
        Authenticate user and return token with user info.
        
        Args:
            login_data: Login credentials
            
        Returns:
            Login response with token and user info
            
        Raises:
            HTTPException: If authentication fails
        """
        # Fetch user with roles
        user = self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRoleAssociation.role))
            .where(User.email == login_data.email)
        ).scalar_one_or_none()
        
        # Generic error message to avoid revealing whether email exists
        auth_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        if not user:
            raise auth_error
        
        # Verify password
        if not security.verify_password(login_data.password, user.password_hash):
            raise auth_error
        
        # Check account status
        if user.account_status != AccountStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user.account_status.value.lower()}. Please contact support."
            )
        
        # Get user roles
        role_names = [ur.role.name.value for ur in user.roles]
        
        # Create JWT token with user info
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "roles": role_names
        }
        
        access_token = security.create_access_token(
            subject=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Build user response
        user_response = self._build_user_response(user)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID with roles loaded.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        user = self.db.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(UserRoleAssociation.role),
                selectinload(User.citizen_profile),
                selectinload(User.government_profile),
                selectinload(User.faculty_profile),
                selectinload(User.student_profile)
            )
            .where(User.id == user_id)
        ).scalar_one_or_none()
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email with roles loaded.
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        user = self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRoleAssociation.role))
            .where(User.email == email)
        ).scalar_one_or_none()
        
        return user
    
    def get_current_user_response(self, user: User) -> UserResponse:
        """
        Build UserResponse from User model.
        
        Args:
            user: User model
            
        Returns:
            UserResponse schema
        """
        return self._build_user_response(user)
    
    def _build_user_response(self, user: User) -> UserResponse:
        """
        Build UserResponse from User model.
        
        Args:
            user: User model
            
        Returns:
            UserResponse
        """
        # Get role names
        role_names = [ur.role.name.value for ur in user.roles]
        
        # Check profile types
        is_citizen = user.citizen_profile is not None
        is_government_officer = user.government_profile is not None
        is_faculty = user.faculty_profile is not None
        is_student = user.student_profile is not None
        
        # Get government officer details if applicable
        government_employee_id = None
        government_department = None
        government_designation = None
        
        if user.government_profile:
            government_employee_id = user.government_profile.employee_id
            government_department = user.government_profile.department
            government_designation = user.government_profile.designation
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            account_status=user.account_status,
            roles=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_citizen=is_citizen,
            is_government_officer=is_government_officer,
            is_faculty=is_faculty,
            is_student=is_student,
            government_employee_id=government_employee_id,
            government_department=government_department,
            government_designation=government_designation
        )
    
    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.
        
        Args:
            user: Current user
            current_password: Current password
            new_password: New password
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not security.verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash and set new password
        user.password_hash = security.hash_password(new_password)
        self.db.commit()
