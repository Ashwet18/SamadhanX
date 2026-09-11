"""
Tests for category API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.challenge import Category


def test_list_categories_returns_200(client: TestClient):
    """Test that GET /api/v1/categories returns 200."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200


def test_list_categories_returns_array(client: TestClient):
    """Test that categories endpoint returns an array."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_list_categories_contains_seeded_data(client: TestClient, db_session: Session):
    """Test that response contains actual database categories."""
    # Get actual categories from database
    db_categories = db_session.query(Category).all()
    
    # Get categories from API
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    api_categories = response.json()
    
    # Should return array even if empty
    assert isinstance(api_categories, list)
    
    # If database has categories, API should return them
    assert len(api_categories) == len(db_categories)


def test_category_response_shape(client: TestClient):
    """Test that category response has correct shape."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data) > 0:
        category = data[0]
        
        # Check required fields
        assert "id" in category
        assert "name" in category
        
        # Check optional fields exist (can be None)
        assert "description" in category
        assert "parent_id" in category
        
        # Validate field types
        assert isinstance(category["id"], str)  # UUID as string
        assert isinstance(category["name"], str)
        
        if category["description"] is not None:
            assert isinstance(category["description"], str)
        
        if category["parent_id"] is not None:
            assert isinstance(category["parent_id"], str)


def test_categories_include_hierarchical_data(client: TestClient):
    """Test that both parent and subcategories are returned."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data) > 0:
        # Check for top-level categories (parent_id is None)
        top_level = [cat for cat in data if cat["parent_id"] is None]
        assert len(top_level) > 0, "Should have at least one top-level category"
        
        # Check if any subcategories exist (parent_id is not None)
        subcategories = [cat for cat in data if cat["parent_id"] is not None]
        # Subcategories may or may not exist depending on seed data


def test_categories_ordered_alphabetically(client: TestClient):
    """Test that categories are returned in alphabetical order by name."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data) > 1:
        names = [cat["name"] for cat in data]
        assert names == sorted(names), f"Categories should be ordered alphabetically: {names}"


def test_category_ids_are_valid_uuids(client: TestClient):
    """Test that category IDs are valid UUID format."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data) > 0:
        import uuid
        
        for category in data:
            # Attempt to parse UUID - will raise ValueError if invalid
            try:
                uuid.UUID(category["id"])
            except ValueError:
                pytest.fail(f"Category ID '{category['id']}' is not a valid UUID")


def test_empty_database_returns_empty_array(client: TestClient, db_session: Session):
    """Test that endpoint handles empty database gracefully."""
    # Delete all categories (in a transaction that will be rolled back)
    db_session.query(Category).delete()
    db_session.commit()
    
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_categories_endpoint_does_not_require_authentication(client: TestClient):
    """Test that categories can be fetched without authentication."""
    # Make request without Authorization header
    response = client.get("/api/v1/categories")
    
    # Should not return 401 Unauthorized
    assert response.status_code == 200


def test_category_names_match_seed_data(client: TestClient):
    """Test that category names match expected seed data if database is seeded."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    
    # Test only applies if categories exist
    if len(data) == 0:
        pytest.skip("No categories in test database - test requires seeded data")
    
    category_names = [cat["name"] for cat in data]
    
    # Expected primary categories from seed.py
    expected_primary = [
        "Education",
        "Healthcare",
        "Agriculture",
        "Water Management",
        "Sanitation",
        "Environment",
        "Energy",
        "Urban Infrastructure",
        "Accessibility",
        "Public Administration",
        "Rural Livelihoods",
        "Disaster Management",
    ]
    
    # Check that expected primary categories exist
    for expected in expected_primary:
        assert expected in category_names, f"Expected category '{expected}' not found in {category_names}"
