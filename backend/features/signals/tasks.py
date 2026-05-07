"""
Signal Processing Tasks
=======================

Background tasks for scraping and normalizing technical signals.
"""

from backend.infra.tasks.celery_app import app
from backend.features.signals.process_youtube import process_youtube_channels, process_youtube_transcripts
from backend.features.signals.process_anthropic import process_anthropic_research
from typing import List
import logging

logger = logging.getLogger(__name__)

@app.task(name="tasks.scrape_youtube_channels", bind=True, max_retries=3)
def scrape_youtube_channels_task(self, channel_ids: List[str], hours: int = 24):
    """Distributed task to scrape YouTube metadata."""
    try:
        return process_youtube_channels(channel_ids, hours)
    except Exception as exc:
        logger.error(f"YouTube scrape failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(name="tasks.process_transcripts", bind=True)
def process_transcripts_task(self, limit: int = 10):
    """Distributed task to extract transcripts (heavy IO/CPU)."""
    return process_youtube_transcripts(limit=limit)

@app.task(name="tasks.scrape_anthropic_research")
def scrape_anthropic_research_task():
    """Distributed task for research ingestion."""
    return process_anthropic_research()
