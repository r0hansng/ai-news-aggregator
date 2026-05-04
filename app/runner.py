from .scrapers.youtube import YouTubeScraper
from .scrapers.openai import OpenAIScraper
from .scrapers.anthropic import AnthropicScraper
from .database.repository import Repository

def run_scrapers(hours=24):
    youtube_scraper = YouTubeScraper()
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    repo = Repository()
    
    youtube_videos = []
    video_dicts = []
    
    users = repo.get_all_users()
    channels_to_scrape = set()
    for u in users:
        if u.youtube_channels:
            channels_to_scrape.update(u.youtube_channels)
            
    # Fallback if no users have channels configured
    if not channels_to_scrape:
        from .config import YOUTUBE_CHANNELS
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
        repo.bulk_create_youtube_videos(video_dicts)
    
    if openai_articles:
        repo.bulk_create_openai_articles([{
            "guid": a.guid,
            "title": a.title,
            "url": a.url,
            "published_at": a.published_at,
            "description": a.description,
            "category": a.category
        } for a in openai_articles])
    
    if anthropic_articles:
        repo.bulk_create_anthropic_articles([{
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

