from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repository import Repository
from app.services.process_youtube import process_youtube_channels
from app.services.process_digest import process_digests
from app.services.process_curator import curate_digests
from app.services.scrape_articles import scrape_all_articles
import uuid

router = APIRouter()

def run_pipeline(user_id: str, db_session: Session):
    """
    Background worker function to run the full scraping and curation pipeline.
    """
    repo = Repository(db_session)
    user = repo.get_user_by_id(user_id)
    if not user:
        return
        
    # 1. Scrape YouTube Channels (Initial pull 500 hours to get data)
    if user.youtube_channels:
        process_youtube_channels(user.youtube_channels, hours=500)
        
    # 2. Scrape News Articles
    scrape_all_articles(hours=500)
        
    # 3. Generate Digests for any new content found
    process_digests()
    
    # 4. Final Curation for this user
    user_profile = {
        "name": user.name,
        "background": user.background,
        "expertise_level": user.expertise_level,
        "interests": user.interests,
        "preferences": user.preferences
    }
    curate_digests(hours=500, user_profile=user_profile)

@router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def trigger_pipeline_refresh(
    background_tasks: BackgroundTasks,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a full refresh of the AI assistant's signals and news feed.
    This process runs in the background and may take a few minutes.
    """
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    # Offload to background task
    background_tasks.add_task(run_pipeline, x_user_id, db)
    
    return {
        "message": "Orchestration pipeline triggered successfully.",
        "user_id": x_user_id,
        "status": "processing"
    }
