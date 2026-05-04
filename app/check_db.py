from app.database.connection import get_session
from app.database.models import YouTubeVideo, OpenAIArticle, AnthropicArticle, Digest, User

session = get_session()

print("=== DB Status ===")
print(f"Users: {session.query(User).count()}")
print(f"YouTube Videos: {session.query(YouTubeVideo).count()}")
print(f"OpenAI Articles: {session.query(OpenAIArticle).count()}")
print(f"Anthropic Articles: {session.query(AnthropicArticle).count()}")
print(f"Digests: {session.query(Digest).count()}")

if session.query(YouTubeVideo).count() > 0:
    print("\nSample Video:")
    v = session.query(YouTubeVideo).first()
    print(f"- {v.title} (ID: {v.video_id})")

session.close()
