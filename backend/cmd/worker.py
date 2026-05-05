from typing import Optional, Union, List, Dict, Any
"""
Background Ingestion Worker
===========================

This script handles the 'Scraping Phase' of the pipeline. It fetches the latest 
raw data from YouTube, OpenAI, and Anthropic blogs and stores them as signals.

Execution:
    $ python -m app.cmd.worker

Note: This worker is typically triggered by the Daily Pipeline or a Cron job.
"""
from typing import Optional, Union, List, Dict
from backend.features.signals.repository import SignalRepository
from backend.features.signals.scrapers.anthropic import AnthropicScraper
from backend.features.signals.scrapers.openai import OpenAIScraper
from backend.features.signals.scrapers.youtube import YouTubeScraper
from backend.features.users.repository import UserRepository
from backend.config import YOUTUBE_CHANNELS


def run_scrapers(hours=24):
    youtube_scraper = YouTubeScraper()
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    signal_repo = SignalRepository()
    user_repo = UserRepository()

    youtube_videos = []
    video_dicts = []

    users = user_repo.get_all_users()
    channels_to_scrape = set()
    for u in users:
        if u.youtube_channels:
            for ch in u.youtube_channels:
                if isinstance(ch, dict) and ch.get("id"):
                    channels_to_scrape.add(ch["id"])
                elif isinstance(ch, str):
                    channels_to_scrape.add(ch)

    # Fallback if no users have channels configured
    if not channels_to_scrape:
        channels_to_scrape.update(YOUTUBE_CHANNELS)

    for channel_id in channels_to_scrape:
        videos = youtube_scraper.get_latest_videos(channel_id, hours=hours)
        youtube_videos.extend(videos)
        for v in videos:
            video_dicts.append({
                "video_id": v.video_id,
                "title": v.title,
                "url": v.url,
                "channel_id": channel_id,
                "published_at": v.published_at,
                "description": v.description,
                "transcript": v.transcript
            })

    openai_articles = openai_scraper.get_articles(hours=hours)
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)

    if video_dicts:
        signal_repo.bulk_create_youtube_videos(video_dicts)

    if openai_articles:
        signal_repo.bulk_create_openai_articles([{
            "guid": a.guid,
            "title": a.title,
            "url": a.url,
            "published_at": a.published_at,
            "description": a.description,
            "category": a.category
        } for a in openai_articles])

    if anthropic_articles:
        signal_repo.bulk_create_anthropic_articles([{
            "guid": a.guid,
            "title": a.title,
            "url": a.url,
            "published_at": a.published_at,
            "description": a.description,
            "category": a.category
        } for a in anthropic_articles])

    return {
        "youtube": youtube_videos,
        "openai": openai_articles,
        "anthropic": anthropic_articles,
    }

if __name__ == "__main__":
    results = run_scrapers(hours=24)
    print(f"YouTube videos: {len(results['youtube'])}")
    print(f"OpenAI articles: {len(results['openai'])}")
    print(f"Anthropic articles: {len(results['anthropic'])}")

