from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repository import Repository
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserResponseWithTokens, Token, TokenRefresh
from app.core import security
import uuid

router = APIRouter()

@router.post("/onboard", response_model=UserResponseWithTokens, status_code=status.HTTP_201_CREATED)
def onboard_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Onboard a new user and return their profile with auth tokens.
    """
    repo = Repository(db)
    
    # Check if user already exists
    existing_user = repo.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already registered."
        )
    
    # Generate a unique ID for the new user
    user_id = str(uuid.uuid4())
    
    # Create the user in the database
    new_user = repo.create_user(
        user_id=user_id,
        name=user_in.name,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        title=user_in.title,
        background=user_in.background,
        expertise_level=user_in.expertise_level,
        interests=user_in.interests,
        preferences=user_in.preferences,
        youtube_channels=user_in.youtube_channels
    )
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user profile."
        )
    
    # Create tokens
    access_token = security.create_access_token(user_id)
    refresh_token = security.create_refresh_token(user_id)
    
    return {
        "user": new_user,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }

@router.post("/login", response_model=UserResponseWithTokens)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user by email and password, then return their profile data with tokens.
    """
    repo = Repository(db)
    user = repo.get_user_by_email(login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please onboard first."
        )
    
    # Verify password
    if not user.hashed_password or not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    
    return {
        "user": user,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Create new pair of tokens (Resetting the window)
    new_access_token = security.create_access_token(user_id)
    new_refresh_token = security.create_refresh_token(user_id)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db)):
    """
    Get the profile of the currently logged in user.
    """
    # In a real app, we'd use security.get_current_user
    repo = Repository(db)
    users = repo.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No user found")
    return users[0]
@router.post("/preferences/email", response_model=UserResponse)
def update_email_preference(enabled: bool, db: Session = Depends(get_db)):
    """
    Update the user's preference for receiving email updates.
    """
    # In a real app, we would get the user_id from the authenticated token
    # For now, we'll assume the user is the only one in the system or we'd pass an ID
    # But let's try to find a user to update
    repo = Repository(db)
    users = repo.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No user found")
    
    user = users[0] # Just update the first user for demo purposes
    updated_user = repo.update_user_email_preferences(user.id, enabled)
    return updated_user

@router.post("/send-digest", status_code=status.HTTP_200_OK)
async def trigger_digest_email(db: Session = Depends(get_db)):
    """
    Manually trigger a digest email for the user.
    """
    from app.core.email import send_digest_email
    repo = Repository(db)
    users = repo.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No user found")
    
    user = users[0]
    if not user.email_updates_enabled:
        return {"message": "Email updates are disabled for this user."}
    
    digests = repo.get_recent_digests(hours=24)
    if not digests:
        return {"message": "No recent digests found to send."}
    
    await send_digest_email(user.email, user.name, digests)
    return {"message": f"Digest email sent to {user.email}"}
