from typing import Optional, Union, List, Dict, Any

from pydantic import BaseModel, Field


class SignalUpdate(BaseModel):
    interests: list[str] = Field(default_factory=list)
    youtube_channels: list[str] = Field(default_factory=list)

class TopicAdd(BaseModel):
    topic: str = Field(..., min_length=1)

class YouTubeAdd(BaseModel):
    channel_id: str = Field(..., min_length=1)

class SignalResponse(BaseModel):
    interests: list[str]
    youtube_channels: list[str]

    class Config:
        from_attributes = True
