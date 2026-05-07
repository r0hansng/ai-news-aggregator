"""
YouTube Ingestion Engine
========================

This module provides specialized scrapers for YouTube content.
It uses RSS feeds for high-speed discovery and the YouTube Transcript API
for deep technical extraction.

Design Decision:
----------------
We use RSS feeds (`/feeds/videos.xml`) instead of the official YouTube Data API
v3 for most operations to avoid strict quota limits and API key management
complexity for basic video discovery.
"""

import logging
import os
from datetime import datetime, timedelta, timezone

from typing import Dict, List, Optional
import feedparser
from pydantic import BaseModel

logger = logging.getLogger(__name__)
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig


class Transcript(BaseModel):
    text: str


class ChannelVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: Optional[str] = None


class YouTubeScraper:
    def __init__(self):
        proxy_config = None
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")

        if proxy_username and proxy_password:
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_username, proxy_password=proxy_password
            )

        self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)

    def _get_rss_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def _extract_video_id(self, video_url: str) -> str:
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
        if "youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[1].split("?")[0]
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        return video_url

    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        """
        Fetch transcript with language fallback.
        Priority: English -> Any available -> None.
        """
        try:
            # List all available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try English first, then any manual transcript, then any generated transcript
            try:
                transcript = transcript_list.find_transcript(['en'])
            except NoTranscriptFound:
                # Fallback to the first available transcript if English isn't found
                transcript = next(iter(transcript_list))

            data = transcript.fetch()
            text = " ".join([snippet['text'] for snippet in data])
            return Transcript(text=text)
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.warning(f"No transcript available for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript for {video_id}: {e}")
            return None

    def get_latest_videos(self, channel_id: str, hours: int = 24) -> List[ChannelVideo]:
        """Discovery via RSS (No API quota cost)"""
        try:
            feed = feedparser.parse(self._get_rss_url(channel_id))
            if not feed.entries:
                return []

            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            videos = []

            for entry in feed.entries:
                if "/shorts/" in entry.link:
                    continue
                published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                if published_time >= cutoff_time:
                    video_id = self._extract_video_id(entry.link)
                    videos.append(
                        ChannelVideo(
                            title=entry.title,
                            url=entry.link,
                            video_id=video_id,
                            published_at=published_time,
                            description=entry.get("summary", ""),
                        )
                    )
            return videos
        except Exception as e:
            logger.error(f"RSS fetch failed for {channel_id}: {e}")
            return []

    def resolve_channel_id(self, query: str) -> Optional[Dict]:
        """
        Resolves a channel handle (@handle) or name.
        Uses high-speed regex on channel pages with fallback to Google search simulation.
        """
        import re
        import requests

        query = query.strip()

        # Direct ID match
        if re.match(r"^UC[a-zA-Z0-9_-]{22}$", query):
            return {"channel_id": query, "display_name": query, "handle": query}

        handle = query if query.startswith("@") else f"@{query}"
        url = f"https://www.youtube.com/{handle}"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 200:
                channel_id = None
                # Regex patterns for various YT page formats
                match = re.search(r"\"channelId\":\"(UC[a-zA-Z0-9_-]{22})\"", response.text)
                if not match:
                    match = re.search(r"\"externalId\":\"(UC[a-zA-Z0-9_-]{22})\"", response.text)
                
                if match:
                    channel_id = match.group(1)
                
                if channel_id:
                    title_match = re.search(r"<title>(.*?)(?: - YouTube)?</title>", response.text)
                    display_name = title_match.group(1).strip() if title_match else handle
                    return {
                        "channel_id": channel_id,
                        "display_name": display_name,
                        "handle": handle,
                    }
        except Exception as e:
            logger.error(f"Error resolving channel {query}: {e}")

        return None


if __name__ == "__main__":
    scraper = YouTubeScraper()
    transcript: Transcript = scraper.get_transcript("jqd6_bbjhS8")
    print(transcript.text)
    channel_videos: List[ChannelVideo] = scraper.scrape_channel(
        "UCn8ujwUInbJkBhffxqAPBVQ", hours=200
    )
