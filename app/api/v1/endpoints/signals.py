from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repository import Repository
from app.schemas.signal import SignalResponse, TopicAdd, YouTubeAdd
from typing import Optional

router = APIRouter()

@router.get("/", response_model=SignalResponse)
def get_user_signals(
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Fetch all active technical interests and YouTube signals for the user.
    """
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    
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
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Check if topic already exists to avoid duplicates
    if topic_in.topic in user.interests:
        return user
        
    new_interests = list(user.interests) + [topic_in.topic]
    return repo.update_user_signals(x_user_id, interests=new_interests)

@router.post("/youtube", response_model=SignalResponse)
def add_youtube_channel(
    channel_in: YouTubeAdd,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Connect a new YouTube channel for the AI assistant to monitor.
    """
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    if channel_in.channel_id in user.youtube_channels:
        return user
        
    new_channels = list(user.youtube_channels) + [channel_in.channel_id]
    return repo.update_user_signals(x_user_id, youtube_channels=new_channels)

@router.delete("/youtube/{channel_id}", response_model=SignalResponse)
def remove_youtube_channel(
    channel_id: str,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Disconnect a YouTube channel from the monitoring list.
    """
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    new_channels = [c for c in user.youtube_channels if c != channel_id]
    return repo.update_user_signals(x_user_id, youtube_channels=new_channels)
