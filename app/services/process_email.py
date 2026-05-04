import logging
from dotenv import load_dotenv

load_dotenv()

from app.agent.email_agent import EmailAgent, ArticleDetail, EmailDigest
from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import USER_PROFILE
from app.database.repository import Repository
from app.services.email import send_email, digest_to_html

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_email_digest(hours: int = 24, top_n: int = 10) -> EmailDigest:
    repo = Repository()
    digests = repo.get_recent_digests(hours=hours)

    if not digests:
        logger.warning(f"No digests found from the last {hours} hours")
        raise ValueError("No digests available")

    logger.info(f"Ranking {len(digests)} digests")
    curator = CuratorAgent(USER_PROFILE)
    ranked = curator.rank_digests(digests)

    if not ranked:
        raise ValueError("Failed to rank articles")

    # build a lookup so we can join the ranking back to full article data
    digest_map = {d["id"]: d for d in digests}

    article_details = []
    for a in ranked:
        d = digest_map.get(a.digest_id, {})
        article_details.append(ArticleDetail(
            digest_id=a.digest_id,
            rank=a.rank,
            relevance_score=a.relevance_score,
            reasoning=a.reasoning,
            title=d.get("title", ""),
            summary=d.get("summary", ""),
            url=d.get("url", ""),
            article_type=d.get("article_type", ""),
        ))

    logger.info(f"Building email with top {top_n} articles")
    email_agent = EmailAgent(USER_PROFILE)
    digest = email_agent.build_digest(
        ranked_articles=article_details,
        total_ranked=len(ranked),
        limit=top_n
    )

    logger.info(digest.intro.greeting)
    logger.info(digest.intro.introduction)

    return digest


def send_digest_email(hours: int = 24, top_n: int = 10) -> dict:
    try:
        digest = generate_email_digest(hours=hours, top_n=top_n)

        subject = f"Daily AI News Digest - {digest.intro.greeting.split('for ')[-1] if 'for ' in digest.intro.greeting else 'Today'}"
        send_email(
            subject=subject,
            body_text=digest.to_markdown(),
            body_html=digest_to_html(digest)
        )

        logger.info("Email sent!")
        return {"success": True, "subject": subject, "articles_count": len(digest.articles)}

    except ValueError as e:
        logger.error(f"Error sending email: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = send_digest_email(hours=24, top_n=10)
    if result["success"]:
        print(f"Sent! Subject: {result['subject']} | Articles: {result['articles_count']}")
    else:
        print(f"Failed: {result['error']}")
