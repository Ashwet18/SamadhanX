"""
Category routes for listing available challenge categories.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.challenge import Category
from app.schemas.challenge import CategoryResponse


router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.get(
    "",
    response_model=List[CategoryResponse],
    summary="List all categories",
    description="Get all available challenge categories. Returns top-level and subcategories."
)
def list_categories(db: Session = Depends(get_db)):
    """
    List all available challenge categories.
    
    Categories are hierarchical with optional parent_id:
    - Top-level categories have parent_id = None
    - Subcategories reference their parent via parent_id
    
    Returns:
        List of all categories with id, name, description, and parent_id
        
    Note:
        This endpoint is read-only and used for populating category selectors.
        Categories are seeded during database initialization.
    """
    # Fetch all categories from database
    categories = db.query(Category).order_by(Category.name).all()
    
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            parent_id=cat.parent_id
        )
        for cat in categories
    ]
