from typing import Optional, Union, List, Dict, Any
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from backend.features.digests.agents.curator_agent import CuratorAgent
from backend.features.digests.agents.email_agent import ArticleDetail, EmailAgent, EmailDigest
from backend.features.digests.repository import DigestRepository
from backend.features.users.repository import UserRepository
from backend.infra.email.email import digest_to_html, send_email

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_email_digest_for_user(user, digests, top_n: int = 10) -> EmailDigest:
    logger.info(f"Ranking {len(digests)} digests for user {user.name}")

    user_profile = {
        "name": user.name,
        "title": user.title,
        "background": user.background,
        "expertise_level": user.expertise_level,
        "interests": user.interests,
        "preferences": user.preferences
    }

    curator = CuratorAgent(user_profile)
    ranked = curator.rank_digests(digests)

    if not ranked:
        return None

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

    logger.info(f"Building email with top {top_n} articles for {user.name}")
    email_agent = EmailAgent(user_profile)
    digest = email_agent.build_digest(
        ranked_articles=article_details,
        total_ranked=len(ranked),
        limit=top_n
    )

    return digest


async def send_digest_emails(hours: int = 24, top_n: int = 10) -> dict:
    user_repo = UserRepository()
    digest_repo = DigestRepository()
    users = user_repo.get_all_users()
    digests = digest_repo.get_recent_digests(hours=hours)

    if not users:
        logger.warning("No users found in the database.")
        return {"success": False, "error": "No users available"}

    if not digests:
        logger.warning(f"No digests found from the last {hours} hours")
        return {"success": False, "error": "No digests available"}

    app_env = os.getenv("APP_ENV", "development").lower()
    my_email = os.getenv("MY_EMAIL")

    success_count = 0
    failed_count = 0

    for user in users:
        try:
            digest = generate_email_digest_for_user(user, digests, top_n=top_n)
            if not digest:
                logger.warning(f"Failed to generate digest for {user.name}")
                failed_count += 1
                continue

            subject = f"Daily AI News Digest - {digest.intro.greeting.split('for ')[-1] if 'for ' in digest.intro.greeting else 'Today'}"


            recipient = user.email
            logger.info(f"Sending email for {user.name} to {recipient}")

            await send_email(
                subject=f"[{user.name}] {subject}",
                body_text=digest.to_markdown(),
                body_html=digest_to_html(digest),
                recipients=[recipient]
            )
            success_count += 1
            logger.info(f"Email sent for {user.name}!")

        except Exception as e:
            logger.error(f"Error sending email for {user.name}: {e}")
            failed_count += 1

    return {
        "success": success_count > 0,
        "success_count": success_count,
        "failed_count": failed_count
    }


if __name__ == "__main__":
    result = send_digest_emails(hours=24, top_n=10)
    print(f"Result: {result}")
