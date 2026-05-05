from typing import Optional, Union, List, Dict, Any
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


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
    interests: list[str] = []
    youtube_channels: list[Any] = []
    preferences: dict[str, str] = {"digestFrequency": "Daily", "format": "Summary"}
    email_updates_enabled: bool = False

class UserResponse(UserBase):
    id: UUID
    title: Optional[str]
    background: Optional[str]
    expertise_level: str
    interests: list[str] = []
    youtube_channels: list[Any] = []
    preferences: dict[str, str] = {}
    email_updates_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    background: Optional[str] = None
    expertise_level: Optional[str] = None
    interests: list[str] | None = None
    youtube_channels: list[Any] | None = None
    preferences: dict[str, str] | None = None

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
