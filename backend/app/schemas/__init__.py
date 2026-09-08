"""
Pydantic schemas for request/response validation.

Contains all schema definitions for API input/output validation.
"""

from .base import BaseSchema, ResponseSchema, PaginatedResponse

# TODO: Import schema modules as they are created
# from .user import UserCreate, UserUpdate, UserResponse, LoginRequest, TokenResponse
# from .challenge import ChallengeCreate, ChallengeUpdate, ChallengeResponse
# from .university import UniversityCreate, UniversityResponse
# from .project import ProjectCreate, ProjectResponse

__all__ = [
    "BaseSchema",
    "ResponseSchema", 
    "PaginatedResponse",
    # TODO: Add schema classes as they are created
]