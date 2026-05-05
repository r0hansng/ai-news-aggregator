from backend.infra.database.base import Base

# This file acts as a central registry for SQLAlchemy models.
# By importing models here, we ensure they are registered with Base.metadata
# and can be imported from backend.infra.database.models for convenience.

from backend.features.users.model import User, UserFeedback
from backend.features.signals.model import YouTubeVideo, OpenAIArticle, AnthropicArticle
from backend.features.digests.model import Digest

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
