"""
Pydantic schemas for request/response validation.

Contains all schema definitions for API input/output validation.
"""

from .base import BaseSchema, ResponseSchema, PaginatedResponse, MessageResponse
from .auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenPayload,
    UserResponse,
    LoginResponse,
    PasswordChange
)
from .challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeListItem,
    ChallengeListResponse,
    CategoryResponse,
    ChallengeMediaResponse,
    ChallengeFilterParams
)

# TODO: Import schema modules as they are created
# from .university import UniversityCreate, UniversityResponse
# from .project import ProjectCreate, ProjectResponse

__all__ = [
    # Base schemas
    "BaseSchema",
    "ResponseSchema", 
    "PaginatedResponse",
    "MessageResponse",
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenPayload",
    "UserResponse",
    "LoginResponse",
    "PasswordChange",
    # Challenge schemas
    "ChallengeCreate",
    "ChallengeUpdate",
    "ChallengeResponse",
    "ChallengeListItem",
    "ChallengeListResponse",
    "CategoryResponse",
    "ChallengeMediaResponse",
    "ChallengeFilterParams",
    # TODO: Add schema classes as they are created
]