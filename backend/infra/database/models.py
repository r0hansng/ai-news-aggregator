"""
Central Database Model Registry
===============================

This module aggregates all domain models from across the codebase into a single
registry. This is critical for SQLAlchemy's `Base.metadata` to correctly 
identify all tables during migrations or schema creation.

Usage:
    Import this module in the database initialization scripts to ensure
    all models are registered before calling `Base.metadata.create_all()`.
"""

from backend.features.digests.model import Digest
from backend.features.signals.model import AnthropicArticle, OpenAIArticle, YouTubeVideo

# This file acts as a central registry for SQLAlchemy models.
# By importing models here, we ensure they are registered with Base.metadata
# and can be imported from backend.infra.database.models for convenience.
from backend.features.users.model import User, UserFeedback
from backend.infra.database.base import Base

# Define what is exported when doing 'from backend.infra.database.models import *'
__all__ = [
    "Base",
    "User",
    "UserFeedback",
    "YouTubeVideo",
    "OpenAIArticle",
    "AnthropicArticle",
    "Digest",
]
