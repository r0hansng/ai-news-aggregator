from typing import Optional, Union, List, Dict, Any
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union, List, Dict

from sqlalchemy.orm import Session

from backend.infra.database.connection import get_session

from .model import Digest


class DigestRepository:
    """
    Manages the lifecycle of AI-generated News Digests.
    
    This repository is responsible for storing and retrieving curated summaries 
    created by the LLM Agents. It uses a composite ID string (`type:original_id`) 
     to ensure cross-module uniqueness without complex foreign key relationships.
    """
    def __init__(self, session: Optional[Session] = None):
        """
        Initializes the repository with a session.
        """
        self.session = session or get_session()

    def create_digest(self, article_type: str, article_id: str, url: str, title: str, summary: str, published_at: Optional[datetime] = None) -> Optional[Digest]:
        digest_id = f"{article_type}:{article_id}"
        existing = self.session.query(Digest).filter_by(id=digest_id).first()
        if existing:
            return None

        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)

        digest = Digest(
            id=digest_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at
        )
        self.session.add(digest)
        self.session.commit()
        return digest

    def get_recent_digests(self, hours: int = 24) -> list[dict[str, Any]]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        digests = self.session.query(Digest).filter(
            Digest.created_at >= cutoff_time
        ).order_by(Digest.created_at.desc()).all()

        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "article_id": d.article_id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at
            }
            for d in digests
        ]

    def get_all_digests(self) -> list[Digest]:
        return self.session.query(Digest).order_by(Digest.created_at.desc()).all()
