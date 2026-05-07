"""
Digest Domain Models
====================

This module defines the 'Digest' entity, which represents a curated, 
AI-ranked, and summarized technical news item tailored for a specific user.

Rationale:
Digests are the final output of our semantic pipeline. They link back to
the original signals but contain unique AI-generated summaries and 
relevance rankings.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from backend.infra.database.base import Base


class Digest(Base):
    __tablename__ = "digests"

    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)
    article_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
