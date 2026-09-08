"""
Authentication and authorization schemas.
"""

from pydantic import EmailStr, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema
from app.models.enums import UserRole, AccountStatus


class UserRegister(BaseSchema):
    """Schema for user registration."""
    
    name: str = Field(..., min_length=2, max_length=200, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=15, description="Phone number")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    role: UserRole = Field(default=UserRole.CITIZEN, description="User role")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )
        
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role_registration(cls, v):
        """Prevent self-registration as privileged roles."""
        restricted_roles = {
            UserRole.PLATFORM_ADMIN,
            UserRole.GOVERNMENT_OFFICER,
            UserRole.UNIVERSITY_ADMIN
        }
        
        if v in restricted_roles:
            raise ValueError(
                f'Cannot self-register as {v.value}. '
                'Contact administrator for privileged account creation.'
            )
        
        return v


class UserLogin(BaseSchema):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class Token(BaseSchema):
    """Schema for JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenPayload(BaseSchema):
    """Schema for JWT token payload."""
    
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    roles: List[str] = Field(..., description="User roles")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    type: str = Field(default="access", description="Token type")


class UserResponse(BaseSchema):
    """Schema for user response (without sensitive data)."""
    
    id: UUID
    name: str
    email: str
    phone: Optional[str]
    account_status: AccountStatus
    roles: List[str] = Field(default_factory=list, description="User role names")
    created_at: datetime
    updated_at: datetime
    
    # Profile extensions
    is_citizen: bool = Field(default=False)
    is_government_officer: bool = Field(default=False)
    is_faculty: bool = Field(default=False)
    is_student: bool = Field(default=False)
    
    # Government officer details (if applicable)
    government_employee_id: Optional[str] = None
    government_department: Optional[str] = None
    government_designation: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginResponse(BaseSchema):
    """Schema for login response with token and user info."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")


class PasswordChange(BaseSchema):
    """Schema for password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )
        
        return v
