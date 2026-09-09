"""
Pytest configuration and fixtures for database tests.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import app
from app.models import *
from app.core.config import settings

# Use PostgreSQL for testing (supports UUID and Vector types)
# Falls back to settings.DATABASE_URL if TEST_DATABASE_URL not set
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", settings.DATABASE_URL)


@pytest.fixture(scope="function")
def engine():
    """Create a test database engine."""
    # PostgreSQL doesn't need connect_args (check_same_thread is SQLite-specific)
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Override get_db dependency to use test session
    def override_get_db():
        try:
            yield session
        finally:
            pass  # Don't close session here
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client."""
    return TestClient(app)
