"""
Base Pydantic schemas for common patterns.

Provides base classes and common response schemas.
"""

from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow creation from ORM objects
        validate_assignment=True,  # Validate on assignment
        use_enum_values=True,  # Use enum values instead of names
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )


class ResponseSchema(BaseSchema):
    """Base response schema with common fields."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseSchema):
    """Simple message response."""
    
    message: str
    success: bool = True
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
    success: bool = False


# Generic type for paginated responses
T = TypeVar('T')


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response schema."""
    
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response with calculated fields."""
        total_pages = (total + page_size - 1) // page_size
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class HealthCheckResponse(BaseSchema):
    """Health check response schema."""
    
    status: str
    version: str
    environment: str
    timestamp: datetime
    services: Optional[dict] = None