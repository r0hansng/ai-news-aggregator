"""
User Management & Authentication Router
=======================================

This module provides the core identity API for the AI News Aggregator. 
It handles onboarding, session management (JWT), and profile personalization.
"""

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.features.digests.repository import DigestRepository
from backend.features.users.repository import UserRepository
from backend.features.users.schema import (
    Token,
    TokenRefresh,
    UserCreate,
    UserLogin,
    UserResponse,
    UserResponseWithTokens,
    UserUpdate,
)
from backend.infra import security
from backend.infra.database.connection import get_db

router = APIRouter()


@router.post("/onboard", response_model=UserResponseWithTokens, status_code=status.HTTP_201_CREATED)
def onboard_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Onboard a new user and return their profile with auth tokens.
    """
    user_repo = UserRepository(db)

    # Check if user already exists
    existing_user = user_repo.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already registered.",
        )

    # Generate a unique ID for the new user
    user_id = str(uuid.uuid4())

    # Create the user in the database
    new_user = user_repo.create_user(
        user_id=user_id,
        name=user_in.name,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        title=user_in.title,
        background=user_in.background,
        expertise_level=user_in.expertise_level,
        interests=user_in.interests,
        preferences=user_in.preferences,
        youtube_channels=user_in.youtube_channels,
    )

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user profile.",
        )

    # Create tokens
    access_token = security.create_access_token(user_id)
    refresh_token = security.create_refresh_token(user_id)

    return {
        "user": new_user,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
    }


@router.post("/login", response_model=UserResponseWithTokens)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user by email and password, then return their profile data with tokens.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(login_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Please onboard first."
        )

    # Verify password
    if not user.hashed_password or not security.verify_password(
        login_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    return {
        "user": user,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
    }


@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh):
    """
    Exchange a valid refresh token for a new access and refresh token.
    This effectively resets the inactivity window to 1 week.
    """
    payload = security.decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    user_id = payload.get("sub")

    # Create new pair of tokens (Resetting the window)
    new_access_token = security.create_access_token(user_id)
    new_refresh_token = security.create_refresh_token(user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(
    x_user_id: str = Header(..., description="Unique ID of the user"), db: Session = Depends(get_db)
):
    """
    Get the profile of the currently logged in user.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    update_data: UserUpdate,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db),
):
    """
    Partially update the current user's profile, signals, and delivery preferences.
    """
    user_repo = UserRepository(db)
    user = user_repo.update_user_profile(x_user_id, **update_data.model_dump(exclude_none=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    x_user_id: str = Header(..., description="Unique ID of the user"), db: Session = Depends(get_db)
):
    """
    Delete the current user account and all associated data.
    """
    user_repo = UserRepository(db)
    success = user_repo.delete_user(x_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@router.post("/preferences/email", response_model=UserResponse)
def update_email_preference(
    enabled: bool,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db),
):
    """
    Update the user's preference for receiving email updates.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = user_repo.update_user_email_preferences(x_user_id, enabled)
    return updated_user


@router.post("/send-digest", status_code=status.HTTP_200_OK)
def trigger_digest_email(
    x_user_id: str = Header(..., description="Unique ID of the user"), db: Session = Depends(get_db)
):
    """
    Manually trigger a digest email for the user.
    """
    from backend.features.digests.process_email import generate_email_digest_for_user
    from backend.infra.email.email import digest_to_html, send_email

    user_repo = UserRepository(db)
    digest_repo = DigestRepository(db)
    user = user_repo.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.email_updates_enabled:
        return {"message": "Email updates are disabled for this user."}

    # Get last 7 days of digests to ensure we have enough for a top 10 list
    digests = digest_repo.get_recent_digests(hours=168)
    if not digests:
        return {"message": "No recent digests found to send."}

    digest_content = generate_email_digest_for_user(user, digests, top_n=10)
    if not digest_content:
        return {"message": "Failed to generate digest."}

    subject = f"Your Top 10 AI Signals - {digest_content.intro.greeting.split('for ')[-1] if 'for ' in digest_content.intro.greeting else 'Today'}"

    send_email(
        subject=subject,
        body_text=digest_content.to_markdown(),
        body_html=digest_to_html(digest_content),
        recipients=[user.email],
    )

    return {"message": f"Digest email sent to {user.email}"}
