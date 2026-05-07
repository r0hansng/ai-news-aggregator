"""
Digest Generation Tasks
=======================

Background tasks for AI curation and delivery.
"""

from backend.infra.tasks.celery_app import app
from backend.features.digests.process_digest import synthesize_digests
from backend.features.digests.process_curator import rank_all_users
from backend.features.digests.process_email import dispatch_emails
import logging

logger = logging.getLogger(__name__)

@app.task(name="tasks.synthesize_digests")
def synthesize_digests_task():
    """Synthesize raw signals into structured digests."""
    return synthesize_digests()

@app.task(name="tasks.rank_digests_for_all", bind=True, max_retries=2)
def rank_digests_for_all_task(self):
    """
    Heavy LLM task: Rank all active users.
    For 10k users, this is distributed across workers.
    """
    try:
        return rank_all_users()
    except Exception as exc:
        logger.error(f"Global ranking failed: {exc}")
        raise self.retry(exc=exc, countdown=120)

@app.task(name="tasks.deliver_emails")
def deliver_emails_task(top_n: int = 10):
    """Dispatch curated digests to users."""
    return dispatch_emails(top_n=top_n)
