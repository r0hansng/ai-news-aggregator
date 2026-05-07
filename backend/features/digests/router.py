"""
Digest Delivery Router
======================

This module provides the core API for the user's news feed. It orchestrates
the retrieval of digests and invokes the AI Curator Agent for real-time
semantic ranking based on the user's active session.
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.features.digests.agents.curator_agent import CuratorAgent
from backend.features.digests.repository import DigestRepository
from backend.features.users.repository import UserRepository
from backend.infra.database.connection import get_db
from backend.infra.gatekeeper import gk

from .feedback_schema import FeedbackCreate, FeedbackResponse
from .schema import DigestFeedResponse, DigestItem
from backend.infra.cache.redis import cache

router = APIRouter()


@router.get("/latest", response_model=DigestFeedResponse)
def get_latest_digests(
    x_user_id: str = Header(..., description="Unique ID of the user"),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Fetch the latest AI-ranked digests tailored to the user's expertise and interests.
    """
    # Check cache first
    cache_key = f"feed:{x_user_id}:{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    user_repo = UserRepository(db)
    digest_repo = DigestRepository(db)
    user = user_repo.get_user_by_id(x_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    # 1. Fetch all available digests from the DB
    all_digests = digest_repo.get_all_digests()
    if not all_digests:
        return {"items": [], "count": 0}

    # 2. Transform DB objects to dicts for the agent
    digest_dicts = [
        {
            "id": d.id,
            "title": d.title,
            "summary": d.summary,
            "article_type": d.article_type,
            "url": d.url,
        }
        for d in all_digests
    ]

    # 3. Construct user profile for the curator
    user_profile = {
        "name": user.name,
        "background": user.background,
        "expertise_level": user.expertise_level,
        "interests": user.interests,
        "preferences": user.preferences,
    }

    # 4. Use AI Curator to rank the digests (if enabled by Gatekeeper)
    ranked_results = []
    if gk.is_enabled("ENABLE_AGENTIC_DIGESTS"):
        curator = CuratorAgent(user_profile)
        ranked_results = curator.rank_digests(digest_dicts)
    else:
        # Fallback to simple sorting if AI curation is disabled
        pass

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
            published_at=d.created_at,
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

    response = {"items": paginated_items, "count": len(paginated_items)}
    
    # Cache the response for 60 seconds (matches polling)
    cache.set(cache_key, response, expire=60)

    return response


@router.post("/{id}/feedback", response_model=FeedbackResponse)
def submit_digest_feedback(
    id: str,
    feedback_in: FeedbackCreate,
    x_user_id: str = Header(..., description="Unique ID of the user"),
    db: Session = Depends(get_db),
):
    """
    Submit feedback for a specific digest. This helps calibrate the AI curator's future rankings.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Invalidate user's feed cache on feedback
    # We delete all limit variations for this user
    # Simplified: just delete the most common ones or use pattern matching if needed
    cache.delete(f"feed:{x_user_id}:10")
    cache.delete(f"feed:{x_user_id}:15")
    cache.delete(f"feed:{x_user_id}:20")

    return user_repo.create_feedback(
        user_id=x_user_id, digest_id=id, rating=feedback_in.rating, comment=feedback_in.comment
    )
