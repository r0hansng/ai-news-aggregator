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
    password: str
    title: Optional[str] = None
    background: Optional[str] = None
    expertise_level: str = "Beginner"
    interests: List[str] = []
    youtube_channels: List[str] = []
    preferences: Dict[str, str] = {"digestFrequency": "Daily", "format": "Summary"}
    email_updates_enabled: bool = False

class UserResponse(UserBase):
    id: UUID
    title: Optional[str]
    expertise_level: str
    email_updates_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponseWithTokens(BaseModel):
    user: UserResponse
    tokens: Token

class TokenRefresh(BaseModel):
    refresh_token: str
