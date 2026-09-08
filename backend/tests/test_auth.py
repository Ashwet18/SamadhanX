"""
Tests for authentication and authorization.
"""

import pytest
from fastapi import status
from sqlalchemy import select

from app.models import User, Role, UserRoleAssociation
from app.models.enums import UserRole, AccountStatus
from app.core.security import security


def test_register_citizen_success(client, db_session):
    """Test successful user registration as citizen."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "citizen@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "citizen@test.com"
    assert data["name"] == "Test Citizen"
    assert "CITIZEN" in data["roles"]
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client, db_session):
    """Test rejection of duplicate email registration."""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "duplicate@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    # Second registration with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Another User",
            "email": "duplicate@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already registered" in response.json()["detail"].lower()


def test_register_weak_password(client, db_session):
    """Test rejection of weak password."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "weak@test.com",
            "password": "weak",
            "role": "CITIZEN"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_no_special_char_password(client, db_session):
    """Test rejection of password without special character."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "nospecial@test.com",
            "password": "Password123",
            "role": "CITIZEN"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_password_is_hashed(client, db_session):
    """Test that password is properly hashed in database."""
    plain_password = "SecurePass123!"
    
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "hashed@test.com",
            "password": plain_password,
            "role": "CITIZEN"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    user_id = response.json()["id"]
    
    # Verify password is hashed in database
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    assert user.password_hash != plain_password
    assert user.password_hash.startswith("$2b$")  # bcrypt hash
    assert security.verify_password(plain_password, user.password_hash)
    
    db.close()


def test_login_success(client, db_session):
    """Test successful login with correct credentials."""
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "login@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@test.com",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "login@test.com"


def test_login_incorrect_password(client, db_session):
    """Test login rejection with incorrect password."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "wrongpass@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@test.com",
            "password": "WrongPassword123!"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client, db_session):
    """Test login rejection for nonexistent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_me_with_valid_token(client, db_session):
    """Test accessing /me with valid token."""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "validtoken@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "validtoken@test.com",
            "password": "SecurePass123!"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Access /me
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "validtoken@test.com"
    assert "CITIZEN" in data["roles"]


def test_access_me_without_token(client, db_session):
    """Test rejection of /me without token."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_me_with_invalid_token(client, db_session):
    """Test rejection of /me with invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_citizen_role_recognized(client, db_session):
    """Test that citizen role is properly recognized."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Citizen User",
            "email": "citizenrole@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "CITIZEN" in data["roles"]
    assert data["is_citizen"] == True


def test_faculty_role_recognized(client, db_session):
    """Test that faculty role is properly recognized."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Faculty User",
            "email": "facultyrole@test.com",
            "password": "SecurePass123!",
            "role": "FACULTY"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "FACULTY" in data["roles"]


def test_privileged_role_cannot_be_self_assigned(client, db_session):
    """Test that privileged roles cannot be self-assigned during registration."""
    # Try to register as PLATFORM_ADMIN
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Hacker",
            "email": "hacker@test.com",
            "password": "SecurePass123!",
            "role": "PLATFORM_ADMIN"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Try to register as GOVERNMENT_OFFICER
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Hacker",
            "email": "hacker2@test.com",
            "password": "SecurePass123!",
            "role": "GOVERNMENT_OFFICER"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Try to register as UNIVERSITY_ADMIN
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Hacker",
            "email": "hacker3@test.com",
            "password": "SecurePass123!",
            "role": "UNIVERSITY_ADMIN"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_seeded_user_can_authenticate(client, db_session):
    """Test that seeded users can authenticate with Password@123."""
    # This test assumes seed script has been run
    # If seed data doesn't exist, this test will be skipped
    
    from app.db.database import SessionLocal
    db = SessionLocal()
    
    # Check if a seeded user exists
    seeded_user = db.query(User).filter(User.email.like("%@example.com")).first()
    
    if not seeded_user:
        pytest.skip("No seeded users found - seed script not run")
    
    # Try to login with seeded credentials
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": seeded_user.email,
            "password": "Password@123"
        }
    )
    
    db.close()
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == seeded_user.email


def test_jwt_contains_required_fields(client, db_session):
    """Test that JWT token contains required fields."""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "jwtfields@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "jwtfields@test.com",
            "password": "SecurePass123!"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Decode token to check fields
    payload = security.decode_token(token)
    
    assert "sub" in payload
    assert "exp" in payload
    assert "iat" in payload
    assert "type" in payload
    assert payload["type"] == "access"
    
    # Check if user info is in token
    sub_data = payload["sub"]
    if isinstance(sub_data, dict):
        assert "email" in sub_data
        assert "roles" in sub_data


def test_expired_token_rejected(client, db_session):
    """Test that expired token is rejected."""
    from datetime import timedelta
    from app.models import User
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    
    # Create a user
    user = User(
        name="Test User",
        email="expired@test.com",
        password_hash=security.hash_password("SecurePass123!"),
        account_status=AccountStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    
    # Create an expired token (expires in past)
    expired_token = security.create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(seconds=-10)  # Expired 10 seconds ago
    )
    
    db.close()
    
    # Try to access /me with expired token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_inactive_user_cannot_login(client, db_session):
    """Test that inactive user cannot login."""
    from app.db.database import SessionLocal
    
    # Register user
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "inactive@test.com",
            "password": "SecurePass123!",
            "role": "CITIZEN"
        }
    )
    
    user_id = register_response.json()["id"]
    
    # Set user to inactive
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    user.account_status = AccountStatus.INACTIVE
    db.commit()
    db.close()
    
    # Try to login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@test.com",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "inactive" in response.json()["detail"].lower()


def test_health_endpoint_still_works(client, db_session):
    """Test that existing /health endpoint still works."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
