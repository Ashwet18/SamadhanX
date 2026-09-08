"""
Base service class with common functionality.

Provides common patterns for service layer implementation.
"""

from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID

from app.db.database import Base
from app.models.base import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    """
    Base service class providing common CRUD operations.
    
    Args:
        ModelType: SQLAlchemy model class
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize service with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get_by_id(self, db: Session, id: UUID) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            db: Database session
            id: Record UUID
            
        Returns:
            Model instance or None if not found
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_id_or_404(self, db: Session, id: UUID) -> ModelType:
        """
        Get a record by ID or raise 404.
        
        Args:
            db: Database session
            id: Record UUID
            
        Returns:
            Model instance
            
        Raises:
            HTTPException: 404 if record not found
        """
        obj = self.get_by_id(db, id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return obj
    
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            
        Returns:
            List of model instances
        """
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching filters.
        
        Args:
            db: Database session
            filters: Optional filters to apply
            
        Returns:
            Number of matching records
        """
        query = db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    def create(self, db: Session, obj_data: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_data: Data for creating the record
            
        Returns:
            Created model instance
            
        Raises:
            HTTPException: 400 if creation fails due to integrity constraints
        """
        try:
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create record due to constraint violation"
            )
    
    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_data: Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.
        
        Args:
            db: Database session
            db_obj: Existing model instance
            obj_data: Data for updating the record
            
        Returns:
            Updated model instance
        """
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: UUID) -> bool:
        """
        Delete a record by ID.
        
        Args:
            db: Database session
            id: Record UUID
            
        Returns:
            True if record was deleted, False if not found
        """
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def soft_delete(self, db: Session, id: UUID) -> bool:
        """
        Soft delete a record by ID (if model supports soft delete).
        
        Args:
            db: Database session
            id: Record UUID
            
        Returns:
            True if record was soft deleted, False if not found
        """
        obj = self.get_by_id(db, id)
        if obj and hasattr(obj, 'soft_delete'):
            obj.soft_delete()
            db.add(obj)
            db.commit()
            return True
        return False