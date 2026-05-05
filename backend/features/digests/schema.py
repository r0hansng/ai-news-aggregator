from typing import Optional, Union, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class DigestItem(BaseModel):
    id: str
    title: str
    summary: str
    article_type: str
    url: str
    published_at: Optional[datetime]
    relevance_score: float | None = None
    rank: Optional[int] = None
    reasoning: Optional[str] = None

    class Config:
        from_attributes = True

class DigestFeedResponse(BaseModel):
    items: list[DigestItem]
    count: int
