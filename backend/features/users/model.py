"""
User Identity & Preference Models
=================================

This module defines the models for identity management and persona tracking.
It stores technical backgrounds, interests, and granular preferences used
by the AI Curator Agent to personalize the news feed.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, String, Text

from backend.infra.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    title = Column(String)
    background = Column(Text)
    expertise_level = Column(String)
    interests = Column(JSON, nullable=False, default=list)
    preferences = Column(JSON, nullable=False, default=dict)
    youtube_channels = Column(JSON, nullable=False, default=list)
    hashed_password = Column(String, nullable=True)  # Temporarily nullable for existing users
    email_updates_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    digest_id = Column(String, nullable=False)
    rating = Column(String, nullable=False)  # relevant, irrelevant, etc.
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
