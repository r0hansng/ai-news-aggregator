from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    rating: str = Field(..., example="relevant", description="The rating for the digest (e.g., relevant, irrelevant, too_basic, too_advanced)")
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    digest_id: str
    rating: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
