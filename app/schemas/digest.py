from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DigestItem(BaseModel):
    id: str
    title: str
    summary: str
    article_type: str
    url: str
    published_at: Optional[datetime]
    relevance_score: Optional[float] = None
    rank: Optional[int] = None
    reasoning: Optional[str] = None

    class Config:
        from_attributes = True

class DigestFeedResponse(BaseModel):
    items: List[DigestItem]
    count: int
