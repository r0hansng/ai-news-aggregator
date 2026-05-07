"""
Signal Domain Models
====================

This module defines the primary entities for 'Signals' (raw technical news items).
We maintain separate tables for each source (YouTube, OpenAI, Anthropic) 
to accommodate source-specific metadata (e.g., transcripts for videos, 
markdown for blog posts).

Rationale:
Storing raw signals separately from curated digests allows us to perform
historical analysis and model retraining on the complete ingestion stream.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from backend.infra.database.base import Base


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    description = Column(Text)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OpenAIArticle(Base):
    __tablename__ = "openai_articles"

    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnthropicArticle(Base):
    __tablename__ = "anthropic_articles"

    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
