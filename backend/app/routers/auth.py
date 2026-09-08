"""
Authentication and authorization routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    LoginResponse,
    UserResponse,
    PasswordChange
)
from app.schemas.base import MessageResponse
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account. Restricted roles (PLATFORM_ADMIN, GOVERNMENT_OFFICER, UNIVERSITY_ADMIN) cannot be self-registered."
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **name**: Full name (2-200 characters)
    - **email**: Valid email address (must be unique)
    - **phone**: Phone number (optional)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit, special char)
    - **role**: User role (CITIZEN, STUDENT, FACULTY, INDUSTRY, MENTOR, CSR, RESEARCHER)
    
    Returns the created user information (without password).
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return auth_service.get_current_user_response(user)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login to get access token",
    description="Authenticate with email and password to receive a JWT access token."
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    - **email**: User email address
    - **password**: User password
    
    Returns:
    - **access_token**: JWT token for authentication
    - **token_type**: "bearer"
    - **user**: User information including roles
    
    Use the access_token in subsequent requests with header:
    `Authorization: Bearer <access_token>`
    """
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)


@router.post(
    "/login/form",
    response_model=LoginResponse,
    summary="Login with OAuth2 form (for Swagger UI)",
    description="Alternative login endpoint compatible with OAuth2PasswordRequestForm for Swagger UI testing."
)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login using OAuth2 password flow (for Swagger UI compatibility).
    
    This endpoint accepts form data instead of JSON and is compatible with
    the OAuth2PasswordBearer scheme used by FastAPI's automatic documentation.
    
    - **username**: User email address (OAuth2 calls it username)
    - **password**: User password
    
    Returns the same response as /login endpoint.
    """
    # Convert form data to login schema
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user."
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    
    Returns:
    - User profile information
    - User roles
    - Account status
    - Profile type indicators (is_citizen, is_faculty, etc.)
    - Government officer details (if applicable)
    """
    auth_service = AuthService(db)
    return auth_service.get_current_user_response(current_user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change user password",
    description="Change the password for the currently authenticated user."
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    
    Requires valid JWT token in Authorization header.
    
    - **current_password**: Current password for verification
    - **new_password**: New strong password
    
    Returns success message if password changed successfully.
    """
    auth_service = AuthService(db)
    auth_service.change_password(
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    return MessageResponse(
        message="Password changed successfully",
        success=True
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (client-side only)",
    description="Logout endpoint for documentation purposes. JWT tokens are stateless, so logout happens client-side by discarding the token."
)
def logout():
    """
    Logout current user.
    
    **Note**: Since JWT tokens are stateless, logout is handled client-side.
    The client should:
    1. Remove the access_token from storage (localStorage, sessionStorage, cookies)
    2. Remove the Authorization header from future requests
    
    The server does not invalidate tokens (they expire after ACCESS_TOKEN_EXPIRE_MINUTES).
    
    For production systems, consider implementing:
    - Token blacklisting with Redis
    - Refresh token rotation
    - Short-lived access tokens
    """
    return MessageResponse(
        message="Logout successful. Please remove the token from client storage.",
        success=True
    )
