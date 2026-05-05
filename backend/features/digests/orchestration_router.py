from typing import Optional, Union, List, Dict, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.infra.database.connection import get_db
from backend.features.users.repository import UserRepository
from backend.features.digests.process_curator import curate_digests
from backend.features.digests.process_digest import process_digests
from backend.features.signals.process_youtube import process_youtube_channels
from backend.features.signals.scrape_articles import scrape_all_articles
from pydantic import BaseModel

class RefreshResponse(BaseModel):
    message: str
    user_id: str
    status: str

router = APIRouter()

def run_pipeline(user_id: str, db_session: Session):
    """
    Background worker function to run the full scraping and curation pipeline.
    """
    user_repo = UserRepository(db_session)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        return

    if user.youtube_channels:
        channel_ids = [ch["id"] if isinstance(ch, dict) else ch for ch in user.youtube_channels if (isinstance(ch, dict) and ch.get("id")) or isinstance(ch, str)]
        process_youtube_channels(channel_ids, hours=500)

    scrape_all_articles(hours=500)

    process_digests()

    user_profile = {
        "name": user.name,
        "background": user.background,
        "expertise_level": user.expertise_level,
        "interests": user.interests,
        "preferences": user.preferences
    }
    curate_digests(hours=500, user_profile=user_profile)

@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_pipeline_refresh(
    background_tasks: BackgroundTasks,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a full refresh of the AI assistant's signals and news feed.
    This process runs in the background and may take a few minutes.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    background_tasks.add_task(run_pipeline, x_user_id, db)

    return {
        "message": "Orchestration pipeline triggered successfully.",
        "user_id": x_user_id,
        "status": "processing"
    }
