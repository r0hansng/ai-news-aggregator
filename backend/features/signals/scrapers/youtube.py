from typing import Optional, Union, List, Dict, Any
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict

import feedparser
from pydantic import BaseModel
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
                proxy_username=proxy_username,
                proxy_password=proxy_password
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
        try:
            transcript = self.transcript_api.fetch(video_id)
            text = " ".join([snippet.text for snippet in transcript.snippets])
            return Transcript(text=text)
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None

    def get_latest_videos(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
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
                videos.append(ChannelVideo(
                    title=entry.title,
                    url=entry.link,
                    video_id=video_id,
                    published_at=published_time,
                    description=entry.get("summary", "")
                ))

        return videos

    def scrape_channel(self, channel_id: str, hours: int = 150) -> list[ChannelVideo]:
        videos = self.get_latest_videos(channel_id, hours)
        result = []
        for video in videos:
            transcript = self.get_transcript(video.video_id)
            result.append(video.model_copy(update={"transcript": transcript.text if transcript else None}))
        return result

    def resolve_channel_id(self, query: str) -> Optional[dict]:
        """
        Resolves a channel handle (@handle) or name to a dictionary with channel_id and display_name.
        """
        import re

        import requests

        query = query.strip()


        if re.match(r'^UC[a-zA-Z0-9_-]{22}$', query):
            return {"channel_id": query, "display_name": query, "handle": query}


        handle = query if query.startswith('@') else f"@{query}"
        url = f"https://www.youtube.com/{handle}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                channel_id = None

                # Look for the channelId in the meta tags or scripts
                match = re.search(r'\"channelId\":\"(UC[a-zA-Z0-9_-]{22})\"', response.text)
                if match:
                    channel_id = match.group(1)
                else:
                    # Fallback: check meta property="og:url"
                    match = re.search(r'meta property=\"og:url\" content=\"https://www\.youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})\"', response.text)
                    if match:
                        channel_id = match.group(1)

                if channel_id:
                    # Extract display name from <title> tag
                    title_match = re.search(r'<title>(.*?)(?: - YouTube)?</title>', response.text)
                    display_name = title_match.group(1).strip() if title_match else handle

                    return {
                        "channel_id": channel_id,
                        "display_name": display_name,
                        "handle": handle
                    }
        except Exception as e:
            print(f"Error resolving channel {query}: {e}")

        return None



if __name__ == "__main__":
    scraper = YouTubeScraper()
    transcript: Transcript = scraper.get_transcript("jqd6_bbjhS8")
    print(transcript.text)
    channel_videos: list[ChannelVideo] = scraper.scrape_channel("UCn8ujwUInbJkBhffxqAPBVQ", hours=200)
