"""
Database configuration and session management.

Sets up SQLAlchemy engine, session factory, and database utilities.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=True if settings.DEBUG else False,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Utility class for database operations."""
    
    @staticmethod
    def create_tables():
        """Create all tables defined by models."""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables():
        """Drop all tables. Use with caution!"""
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return SessionLocal()


# Global database manager instance
db_manager = DatabaseManager()