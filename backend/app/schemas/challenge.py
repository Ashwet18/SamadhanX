"""
Challenge schemas for request/response validation.
"""

from pydantic import Field, field_validator, model_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema, PaginatedResponse
from app.models.enums import ChallengeStatus, PriorityLevel, MediaType


class CategoryResponse(BaseSchema):
    """Schema for category response."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class ChallengeCreate(BaseSchema):
    """Schema for creating a challenge."""
    
    title: str = Field(..., min_length=10, max_length=500, description="Challenge title")
    description: str = Field(..., min_length=30, max_length=5000, description="Detailed description")
    district: str = Field(..., min_length=2, max_length=100, description="District name")
    block: Optional[str] = Field(None, max_length=100, description="Block name")
    village: Optional[str] = Field(None, max_length=100, description="Village name")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    affected_population: Optional[int] = Field(None, ge=0, le=10000000, description="Estimated affected population")
    category_ids: List[UUID] = Field(..., min_length=1, description="At least one category ID")
    
    @field_validator('title', 'description', 'district', 'block', 'village')
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace and reject blank strings."""
        if v is None:
            return v
        
        stripped = v.strip()
        if not stripped:
            raise ValueError('Field cannot be blank or whitespace only')
        
        return stripped
    
    @model_validator(mode='after')
    def validate_coordinates(self):
        """Validate that both coordinates are provided together."""
        lat = self.latitude
        lon = self.longitude
        
        # If one is provided, both must be provided
        if (lat is not None and lon is None) or (lat is None and lon is not None):
            raise ValueError('Both latitude and longitude must be provided together')
        
        return self


class ChallengeUpdate(BaseSchema):
    """Schema for updating a challenge."""
    
    title: Optional[str] = Field(None, min_length=10, max_length=500)
    description: Optional[str] = Field(None, min_length=30, max_length=5000)
    district: Optional[str] = Field(None, min_length=2, max_length=100)
    block: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    affected_population: Optional[int] = Field(None, ge=0, le=10000000)
    category_ids: Optional[List[UUID]] = Field(None, min_length=1)
    
    @field_validator('title', 'description', 'district', 'block', 'village')
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace and reject blank strings."""
        if v is None:
            return v
        
        stripped = v.strip()
        if not stripped:
            raise ValueError('Field cannot be blank or whitespace only')
        
        return stripped


class ChallengeMediaResponse(BaseSchema):
    """Schema for media file response."""
    
    id: UUID
    media_type: MediaType
    file_url: str
    file_name: str
    mime_type: Optional[str]
    file_size: Optional[int]
    created_at: datetime


class ChallengeResponse(BaseSchema):
    """Schema for challenge response."""
    
    id: UUID
    challenge_code: str
    title: str
    description: str
    status: ChallengeStatus
    priority_score: Optional[float] = None
    priority_level: Optional[PriorityLevel] = None
    district: str
    block: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    affected_population: Optional[int] = None
    categories: List[CategoryResponse] = []
    media: List[ChallengeMediaResponse] = []
    created_at: datetime
    updated_at: datetime
    
    # Submitter info (optional, depends on access level)
    submitted_by: Optional[UUID] = None
    submitter_name: Optional[str] = None


class ChallengeListItem(BaseSchema):
    """Schema for challenge in list view (lighter than full response)."""
    
    id: UUID
    challenge_code: str
    title: str
    status: ChallengeStatus
    priority_level: Optional[PriorityLevel] = None
    district: str
    affected_population: Optional[int] = None
    category_count: int = 0
    media_count: int = 0
    created_at: datetime


class ChallengeListResponse(BaseSchema):
    """Schema for paginated challenge list response."""
    
    items: List[ChallengeListItem]
    page: int
    page_size: int
    total: int
    pages: int
    has_next: bool
    has_previous: bool


class ChallengeFilterParams(BaseSchema):
    """Schema for challenge filtering parameters."""
    
    status: Optional[ChallengeStatus] = None
    district: Optional[str] = None
    category_id: Optional[UUID] = None
    priority_level: Optional[PriorityLevel] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
