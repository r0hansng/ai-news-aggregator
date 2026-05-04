from pydantic import BaseModel, Field
from typing import List

class SignalUpdate(BaseModel):
    interests: List[str] = Field(default_factory=list)
    youtube_channels: List[str] = Field(default_factory=list)

class TopicAdd(BaseModel):
    topic: str = Field(..., min_length=1)

class YouTubeAdd(BaseModel):
    channel_id: str = Field(..., min_length=1)

class SignalResponse(BaseModel):
    interests: List[str]
    youtube_channels: List[str]
    
    class Config:
        from_attributes = True
