from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

class UserPreferences(BaseModel):
    digest_frequency: str = Field(..., example="Daily")
    format: str = Field(..., example="Summary")

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    title: Optional[str] = None
    background: Optional[str] = None
    expertise_level: str = "Beginner"
    interests: List[str] = []
    youtube_channels: List[str] = []
    preferences: Dict[str, str] = {"digestFrequency": "Daily", "format": "Summary"}

class UserResponse(UserBase):
    id: UUID
    title: Optional[str]
    expertise_level: str
    created_at: datetime

    class Config:
        from_attributes = True
