from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repository import Repository
from app.agent.curator_agent import CuratorAgent
from app.schemas.digest import DigestFeedResponse, DigestItem
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from typing import List

router = APIRouter()

@router.get("/latest", response_model=DigestFeedResponse)
def get_latest_digests(
    x_user_id: str = Header(..., description="Unique ID of the user"),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Fetch the latest AI-ranked digests tailored to the user's expertise and interests.
    """
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    # 1. Fetch all available digests from the DB
    all_digests = repo.get_all_digests()
    if not all_digests:
        return {"items": [], "count": 0}
        
    # 2. Transform DB objects to dicts for the agent
    digest_dicts = [
        {
            "id": d.id,
            "title": d.title,
            "summary": d.summary,
            "article_type": d.article_type,
            "url": d.url
        }
        for d in all_digests
    ]
    
    # 3. Construct user profile for the curator
    user_profile = {
        "name": user.name,
        "background": user.background,
        "expertise_level": user.expertise_level,
        "interests": user.interests,
        "preferences": user.preferences
    }
    
    # 4. Use AI Curator to rank the digests
    curator = CuratorAgent(user_profile)
    ranked_results = curator.rank_digests(digest_dicts)
    
    # 5. Merge rankings with original digest data
    final_items = []
    # Create a map for quick lookup
    ranking_map = {r.digest_id: r for r in ranked_results}
    
    for d in all_digests:
        item = DigestItem(
            id=d.id,
            title=d.title,
            summary=d.summary,
            article_type=d.article_type,
            url=d.url,
            published_at=d.created_at
        )
        
        # Attach AI ranking if available
        if d.id in ranking_map:
            rank_data = ranking_map[d.id]
            item.relevance_score = rank_data.relevance_score
            item.rank = rank_data.rank
            item.reasoning = rank_data.reasoning
            
        final_items.append(item)
    
    # Sort by rank (if rank exists) then by score, then by date
    final_items.sort(key=lambda x: (x.rank or 999, -(x.relevance_score or 0)))
    
    # Apply limit
    paginated_items = final_items[:limit]
    
    return {
        "items": paginated_items,
        "count": len(paginated_items)
    }

@router.post("/{id}/feedback", response_model=FeedbackResponse)
def submit_digest_feedback(
    id: str,
    feedback_in: FeedbackCreate,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a specific digest. This helps calibrate the AI curator's future rankings.
    """
    repo = Repository(db)
    user = repo.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    return repo.create_feedback(
        user_id=x_user_id,
        digest_id=id,
        rating=feedback_in.rating,
        comment=feedback_in.comment
    )
