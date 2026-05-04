from typing import Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.youtube import YouTubeScraper
from app.database.repository import Repository


TRANSCRIPT_UNAVAILABLE_MARKER = "__UNAVAILABLE__"


def process_youtube_channels(channel_ids: list[str], hours: int = 24):
    scraper = YouTubeScraper()
    repo = Repository()
    
    total_new = 0
    for channel_id in channel_ids:
        print(f"Scraping channel: {channel_id}")
        videos = scraper.scrape_channel(channel_id, hours=hours)
        if videos:
            count = repo.bulk_create_youtube_videos([v.model_dump() for v in videos])
            total_new += count
            print(f"Added {count} new videos from {channel_id}")
            
    return total_new

def process_youtube_transcripts(limit: Optional[int] = None) -> dict:
    scraper = YouTubeScraper()
    repo = Repository()
    
    videos = repo.get_youtube_videos_without_transcript(limit=limit)
    processed = 0
    unavailable = 0
    failed = 0
    
    for video in videos:
        try:
            transcript_result = scraper.get_transcript(video.video_id)
            if transcript_result:
                repo.update_youtube_video_transcript(video.video_id, transcript_result.text)
                processed += 1
            else:
                repo.update_youtube_video_transcript(video.video_id, TRANSCRIPT_UNAVAILABLE_MARKER)
                unavailable += 1
        except Exception as e:
            repo.update_youtube_video_transcript(video.video_id, TRANSCRIPT_UNAVAILABLE_MARKER)
            unavailable += 1
            print(f"Error processing video {video.video_id}: {e}")
    
    return {
        "total": len(videos),
        "processed": processed,
        "unavailable": unavailable,
        "failed": failed
    }


if __name__ == "__main__":
    result = process_youtube_transcripts()
    print(f"Total videos: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Unavailable: {result['unavailable']}")
    print(f"Failed: {result['failed']}")
