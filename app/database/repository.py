from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import YouTubeVideo, OpenAIArticle, AnthropicArticle, Digest, User, UserFeedback
from .connection import get_session


class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
        
    def create_user(self, user_id: str, name: str, email: str, hashed_password: str = None, title: str = "", background: str = "", expertise_level: str = "Beginner", interests: list = None, preferences: dict = None, youtube_channels: list = None) -> Optional[User]:
        existing = self.session.query(User).filter_by(email=email).first()
        if existing:
            return None
            
        user = User(
            id=user_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            title=title,
            background=background,
            expertise_level=expertise_level,
            interests=interests or [],
            preferences=preferences or {},
            youtube_channels=youtube_channels or []
        )
        self.session.add(user)
        self.session.commit()
        return user
        
    def get_all_users(self) -> List[User]:
        return self.session.query(User).all()
        
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()
        
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()
        
    def update_user_signals(self, user_id: str, interests: List[str] = None, youtube_channels: List[str] = None) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if interests is not None:
            user.interests = interests
        if youtube_channels is not None:
            user.youtube_channels = youtube_channels
            
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def update_user_email_preferences(self, user_id: str, enabled: bool) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.email_updates_enabled = enabled
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def create_youtube_video(self, video_id: str, title: str, url: str, channel_id: str, 
                            published_at: datetime, description: str = "", transcript: Optional[str] = None) -> Optional[YouTubeVideo]:
        existing = self.session.query(YouTubeVideo).filter_by(video_id=video_id).first()
        if existing:
            return None
        video = YouTubeVideo(
            video_id=video_id,
            title=title,
            url=url,
            channel_id=channel_id,
            published_at=published_at,
            description=description,
            transcript=transcript
        )
        self.session.add(video)
        self.session.commit()
        return video
    
    def create_openai_article(self, guid: str, title: str, url: str, published_at: datetime,
                              description: str = "", category: Optional[str] = None) -> Optional[OpenAIArticle]:
        existing = self.session.query(OpenAIArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = OpenAIArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def create_anthropic_article(self, guid: str, title: str, url: str, published_at: datetime,
                                description: str = "", category: Optional[str] = None) -> Optional[AnthropicArticle]:
        existing = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if existing:
            return None
        article = AnthropicArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def bulk_create_youtube_videos(self, videos: List[dict]) -> int:
        new_videos = []
        for v in videos:
            existing = self.session.query(YouTubeVideo).filter_by(video_id=v["video_id"]).first()
            if not existing:
                new_videos.append(YouTubeVideo(
                    video_id=v["video_id"],
                    title=v["title"],
                    url=v["url"],
                    channel_id=v.get("channel_id", ""),
                    published_at=v["published_at"],
                    description=v.get("description", ""),
                    transcript=v.get("transcript")
                ))
        if new_videos:
            self.session.add_all(new_videos)
            self.session.commit()
        return len(new_videos)
    
    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(OpenAIArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(OpenAIArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def bulk_create_anthropic_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(AnthropicArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(AnthropicArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_anthropic_articles_without_markdown(self, limit: Optional[int] = None) -> List[AnthropicArticle]:
        query = self.session.query(AnthropicArticle).filter(AnthropicArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_anthropic_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False
    
    def get_youtube_videos_without_transcript(self, limit: Optional[int] = None) -> List[YouTubeVideo]:
        query = self.session.query(YouTubeVideo).filter(YouTubeVideo.transcript.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update_youtube_video_transcript(self, video_id: str, transcript: str) -> bool:
        video = self.session.query(YouTubeVideo).filter_by(video_id=video_id).first()
        if video:
            video.transcript = transcript
            self.session.commit()
            return True
        return False
    
    def get_articles_without_digest(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        articles = []
        seen_ids = set()
        
        digests = self.session.query(Digest).all()
        for d in digests:
            seen_ids.add(f"{d.article_type}:{d.article_id}")
        
        youtube_videos = self.session.query(YouTubeVideo).filter(
            YouTubeVideo.transcript.isnot(None),
            YouTubeVideo.transcript != "__UNAVAILABLE__"
        ).all()
        for video in youtube_videos:
            key = f"youtube:{video.video_id}"
            if key not in seen_ids:
                articles.append({
                    "type": "youtube",
                    "id": video.video_id,
                    "title": video.title,
                    "url": video.url,
                    "content": video.transcript or video.description or "",
                    "published_at": video.published_at
                })
        
        openai_articles = self.session.query(OpenAIArticle).all()
        for article in openai_articles:
            key = f"openai:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "openai",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.description or "",
                    "published_at": article.published_at
                })
        
        anthropic_articles = self.session.query(AnthropicArticle).filter(
            AnthropicArticle.markdown.isnot(None)
        ).all()
        for article in anthropic_articles:
            key = f"anthropic:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "anthropic",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })
        
        if limit:
            articles = articles[:limit]
        
        return articles
    
    def create_digest(self, article_type: str, article_id: str, url: str, title: str, summary: str, published_at: Optional[datetime] = None) -> Optional[Digest]:
        digest_id = f"{article_type}:{article_id}"
        existing = self.session.query(Digest).filter_by(id=digest_id).first()
        if existing:
            return None
        
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)
        
        digest = Digest(
            id=digest_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at
        )
        self.session.add(digest)
        self.session.commit()
        return digest
    
    def get_recent_digests(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        digests = self.session.query(Digest).filter(
            Digest.created_at >= cutoff_time
        ).order_by(Digest.created_at.desc()).all()
        
        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "article_id": d.article_id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at
            }
            for d in digests
        ]

    def get_all_digests(self) -> List[Digest]:
        return self.session.query(Digest).order_by(Digest.created_at.desc()).all()

    def create_feedback(self, user_id: str, digest_id: str, rating: str, comment: str = None) -> UserFeedback:
        import uuid
        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            user_id=user_id,
            digest_id=digest_id,
            rating=rating,
            comment=comment
        )
        self.session.add(feedback)
        self.session.commit()
        return feedback
