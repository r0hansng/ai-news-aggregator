"""
Database Health & Integrity Check
=================================

This module provides a lightweight diagnostic tool to verify the current 
state of the database. It counts records across all primary entities
and prints a sample to verify schema accessibility.

Rationale:
In production debugging, having a 'pre-flight' check script saves time
when diagnosing environment-specific connectivity or schema issues.
"""

from backend.features.users.model import User
from backend.infra.database.connection import get_session
from backend.infra.database.models import AnthropicArticle, Digest, OpenAIArticle, YouTubeVideo

session = get_session()

print("=== DB Status ===")
print(f"Users: {session.query(User).count()}")
print(f"YouTube Videos: {session.query(YouTubeVideo).count()}")
print(f"OpenAI Articles: {session.query(OpenAIArticle).count()}")
print(f"Anthropic Articles: {session.query(AnthropicArticle).count()}")
print(f"Digests: {session.query(Digest).count()}")

if session.query(YouTubeVideo).count() > 0:
    print("\nSample Video:")
    v = session.query(YouTubeVideo).first()
    print(f"- {v.title} (ID: {v.video_id})")

session.close()
