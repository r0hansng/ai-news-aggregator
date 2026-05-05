from typing import Optional, Union, List, Dict, Any
from typing import Optional, Union, List, Dict
from sqlalchemy.orm import Session

from backend.infra.database.connection import get_session

from .model import User, UserFeedback


class UserRepository:
    """
    Handles all persistent storage operations for User profiles and Feedback.
    
    This repository encapsulates SQLAlchemy sessions to ensure that business logic
    remains decoupled from the underlying database implementation.
    """
    def __init__(self, session: Optional[Session] = None):
        """
        Initializes the repository with a session.
        If no session is provided, it defaults to the global get_session() utility.
        """
        self.session = session or get_session()

    def create_user(self, user_id: str, name: str, email: str, hashed_password: str = None, title: str = "", background: str = "", expertise_level: str = "Beginner", interests: list = None, preferences: dict = None, youtube_channels: list = None) -> Optional[User]:
        """
        Creates a new user record in the system.
        
        Args:
            user_id: Pre-generated UUID for the user.
            name: Full name.
            email: Primary contact and login identifier (Unique).
            hashed_password: Argon2 hash of the user's password.
            title: Professional title (used by AI for curation).
            background: Technical background (used by AI for curation).
            expertise_level: Beginner, Intermediate, or Advanced.
            interests: List of technical topics to track.
            preferences: JSON blob of delivery and AI tuning preferences.
            youtube_channels: List of YouTube channel IDs to monitor.
            
        Returns:
            The created User object or None if the email already exists.
        """
        existing = self.session.query(User).filter_by(email=email).first()
        if existing:
            return None

        user = User(
            id=user_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            title=title,
            background=background,
            expertise_level=expertise_level,
            interests=interests or [],
            preferences=preferences or {},
            youtube_channels=youtube_channels or []
        )
        self.session.add(user)
        self.session.commit()
        return user

    def get_all_users(self) -> list[User]:
        return self.session.query(User).all()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

    def update_user_signals(self, user_id: str, interests: list[str] = None, youtube_channels: list[str] = None) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if interests is not None:
            user.interests = interests
        if youtube_channels is not None:
            user.youtube_channels = youtube_channels

        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user_email_preferences(self, user_id: str, enabled: bool) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.email_updates_enabled = enabled
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user_profile(self, user_id: str, **fields) -> Optional[User]:
        """Partial update for user profile fields. Only updates provided fields."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        allowed = {"name", "title", "background", "expertise_level", "interests", "youtube_channels", "preferences"}
        for key, value in fields.items():
            if key in allowed and value is not None:
                setattr(user, key, value)

        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    def create_feedback(self, user_id: str, digest_id: str, rating: str, comment: str = None) -> UserFeedback:
        import uuid
        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            user_id=user_id,
            digest_id=digest_id,
            rating=rating,
            comment=comment
        )
        self.session.add(feedback)
        self.session.commit()
        return feedback
