"""
Tests for challenge submission and management.
"""

import pytest
from fastapi import status
from io import BytesIO

from app.models.enums import ChallengeStatus, UserRole


def test_citizen_can_create_challenge(client, db_session):
    """Test that a citizen can create a challenge."""
    # Register and login as citizen
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "citizen.challenge@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "citizen.challenge@test.com",
            "password": "SecurePass123!"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Create a category first
    from app.models.challenge import Category
    category = Category(name="Test Category", description="Test")
    db_session.add(category)
    db_session.commit()
    
    # Create challenge
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Need clean water supply",
            "description": "Our village lacks clean drinking water. We need a sustainable solution for 500 families.",
            "district": "Ranchi",
            "block": "Kanke",
            "village": "Test Village",
            "latitude": 23.3441,
            "longitude": 85.3096,
            "affected_population": 2500,
            "category_ids": [str(category.id)]
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Need clean water supply"
    assert data["status"] == "SUBMITTED"
    assert "CH-JH-" in data["challenge_code"]
    assert len(data["categories"]) == 1


def test_unauthenticated_cannot_create_challenge(client, db_session):
    """Test that unauthenticated users cannot create challenges."""
    response = client.post(
        "/api/v1/challenges",
        json={
            "title": "Test Challenge",
            "description": "This should fail without authentication",
            "district": "Ranchi",
            "category_ids": []
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_non_citizen_cannot_create_challenge(client, db_session):
    """Test that non-citizens cannot create challenges."""
    # Register as faculty (not citizen)
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Faculty Member",
            "email": "faculty@test.com",
            "password": "SecurePass123!",
            "role": "FACULTY"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "faculty@test.com",
            "password": "SecurePass123!"
        }
    )
    
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Challenge",
            "description": "This should fail - faculty is not citizen",
            "district": "Ranchi",
            "category_ids": []
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_required_fields_validated(client, db_session):
    """Test that required fields are validated."""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "validation@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "validation@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    # Missing title
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Test description that is long enough",
            "district": "Ranchi",
            "category_ids": []
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_title_too_short_rejected(client, db_session):
    """Test that short titles are rejected."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "shorttitle@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "shorttitle@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Short",  # Less than 10 characters
            "description": "This is a long enough description for the challenge",
            "district": "Ranchi",
            "category_ids": []
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_description_too_short_rejected(client, db_session):
    """Test that short descriptions are rejected."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "shortdesc@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "shortdesc@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Valid Challenge Title",
            "description": "Too short",  # Less than 30 characters
            "district": "Ranchi",
            "category_ids": []
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_latitude_rejected(client, db_session):
    """Test that invalid latitude is rejected."""
    # Setup user and token
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "lattest@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "lattest@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    # Invalid latitude (> 90)
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Valid Challenge Title",
            "description": "This is a valid description that is long enough",
            "district": "Ranchi",
            "latitude": 95.0,  # Invalid
            "longitude": 85.0,
            "category_ids": [str(category.id)]
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_latitude_without_longitude_rejected(client, db_session):
    """Test that providing only latitude is rejected."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "coordtest@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "coordtest@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    # Only latitude, no longitude
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Valid Challenge Title",
            "description": "This is a valid description that is long enough",
            "district": "Ranchi",
            "latitude": 23.0,
            "category_ids": [str(category.id)]
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_category_rejected(client, db_session):
    """Test that invalid category IDs are rejected."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "cattest@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "cattest@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    # Use non-existent category UUID
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Valid Challenge Title",
            "description": "This is a valid description that is long enough",
            "district": "Ranchi",
            "category_ids": ["550e8400-e29b-41d4-a716-446655440000"]  # Non-existent
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_challenge_code_generated(client, db_session):
    """Test that challenge code is automatically generated."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "codetest@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "codetest@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Challenge With Code",
            "description": "This challenge should get an automatic code",
            "district": "Ranchi",
            "category_ids": [str(category.id)]
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "challenge_code" in data
    assert data["challenge_code"].startswith("CH-JH-")


def test_initial_status_is_submitted(client, db_session):
    """Test that new challenges start with SUBMITTED status."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "statustest@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "statustest@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Status Challenge",
            "description": "Testing initial status of challenge",
            "district": "Ranchi",
            "category_ids": [str(category.id)]
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "SUBMITTED"


def test_citizen_can_view_own_challenges(client, db_session):
    """Test that citizens can view their own challenges."""
    # Setup and create challenge
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "viewown@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "viewown@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    create_response = client.post(
        "/api/v1/challenges",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "My Own Challenge",
            "description": "This is my personal challenge submission",
            "district": "Ranchi",
            "category_ids": [str(category.id)]
        }
    )
    
    challenge_id = create_response.json()["id"]
    
    # View own challenge
    response = client.get(
        f"/api/v1/challenges/{challenge_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "My Own Challenge"


def test_citizen_can_list_my_challenges(client, db_session):
    """Test the /my endpoint for listing own challenges."""
    # Setup
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "listmy@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "listmy@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    # Create challenges
    for i in range(3):
        client.post(
            "/api/v1/challenges",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"Challenge {i+1}",
                "description": f"Description for challenge {i+1} with enough text",
                "district": "Ranchi",
                "category_ids": [str(category.id)]
            }
        )
    
    # List my challenges
    response = client.get(
        "/api/v1/challenges/my",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


def test_pagination_works(client, db_session):
    """Test that pagination works correctly."""
    # Create multiple challenges and test pagination
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "pagination@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "pagination@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    from app.models.challenge import Category
    category = Category(name="Test", description="Test")
    db_session.add(category)
    db_session.commit()
    
    # Create 5 challenges
    for i in range(5):
        client.post(
            "/api/v1/challenges",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"Challenge {i+1}",
                "description": f"Pagination test challenge number {i+1}",
                "district": "Ranchi",
                "category_ids": [str(category.id)]
            }
        )
    
    # Test page 1 with page_size=2
    response = client.get(
        "/api/v1/challenges/my?page=1&page_size=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3
    assert data["has_next"] == True
    assert data["has_previous"] == False


def test_government_can_access_review_queue(client, db_session):
    """Test that government officers can access review queue."""
    # Create government officer manually (can't self-register)
    from app.models.user import User, Role, UserRoleAssociation, GovernmentOfficer
    from app.models.enums import AccountStatus, UserRole
    from app.core.security import security
    
    user = User(
        name="Government Officer",
        email="govt@test.com",
        password_hash=security.hash_password("SecurePass123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.flush()
    
    role = Role(name=UserRole.GOVERNMENT_OFFICER, description="Govt")
    db_session.add(role)
    db_session.flush()
    
    user_role = UserRoleAssociation(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    
    govt = GovernmentOfficer(
        user_id=user.id,
        employee_id="GOV001",
        department="Test Dept",
        designation="Officer"
    )
    db_session.add(govt)
    db_session.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "govt@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    # Access review queue
    response = client.get(
        "/api/v1/challenges/review-queue",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "page" in data


def test_citizen_cannot_access_review_queue(client, db_session):
    """Test that citizens cannot access review queue."""
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "noreview@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "noreview@test.com", "password": "SecurePass123!"}
    )
    
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/v1/challenges/review-queue",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_health_endpoint_still_works(client, db_session):
    """Test that /health endpoint still works."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
