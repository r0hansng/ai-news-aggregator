from typing import Optional, Union, List, Dict, Any
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.infra.database.connection import get_db
from backend.features.signals.scrapers.youtube import YouTubeScraper
from backend.features.users.repository import UserRepository
from .schema import SignalResponse, TopicAdd, YouTubeAdd

router = APIRouter()

@router.get("/resolve-youtube", response_model=dict)
def resolve_youtube_channel(
    handle: str,
    x_user_id: Optional[str] = Header(None, description="Unique ID of the user")
):
    """
    Resolves a YouTube handle or name to a Channel ID.
    """
    scraper = YouTubeScraper()
    result = scraper.resolve_channel_id(handle)

    if not result or not result.get("channel_id"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not resolve channel for: {handle}"
        )

    return result

@router.get("/", response_model=SignalResponse)
def get_user_signals(
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Fetch all active technical interests and YouTube signals for the user.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    return user

@router.post("/interests", response_model=SignalResponse)
def add_interest(
    topic_in: TopicAdd,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Add a new technical topic to the user's tracking list.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Check if topic already exists to avoid duplicates
    if topic_in.topic in user.interests:
        return user

    new_interests = list(user.interests) + [topic_in.topic]
    return user_repo.update_user_signals(x_user_id, interests=new_interests)

@router.post("/youtube", response_model=SignalResponse)
def add_youtube_channel(
    channel_in: YouTubeAdd,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Connect a new YouTube channel for the AI assistant to monitor.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    if channel_in.channel_id in user.youtube_channels:
        return user

    new_channels = list(user.youtube_channels) + [channel_in.channel_id]
    return user_repo.update_user_signals(x_user_id, youtube_channels=new_channels)

@router.delete("/youtube/{channel_id}", response_model=SignalResponse)
def remove_youtube_channel(
    channel_id: str,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Disconnect a YouTube channel from the monitoring list.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    new_channels = [c for c in user.youtube_channels if c != channel_id]
    return user_repo.update_user_signals(x_user_id, youtube_channels=new_channels)
