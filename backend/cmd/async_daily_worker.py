"""
Asynchronous Daily Orchestration Pipeline
==========================================

This module uses Celery to orchestrate the daily signal pipeline.
It leverages distributed task execution to handle high volume (10k+ users)
and prevent long-running tasks from blocking the system.
"""

import sys
import logging
from celery import chain, group
from backend.features.signals.tasks import scrape_youtube_channels_task, process_transcripts_task, scrape_anthropic_research_task
from backend.features.digests.tasks import synthesize_digests_task, rank_digests_for_all_task, deliver_emails_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_async_pipeline(hours=24, top_n=10):
    logger.info("Triggering Asynchronous Daily Pipeline")

    # Define the DAG using Celery Chain
    # 1. Scrape tasks in parallel (group)
    # 2. Process transcripts
    # 3. Synthesize digests
    # 4. Rank for all users
    # 5. Deliver emails
    
    # Note: We hardcode some channel IDs or fetch them from DB in a real scenario
    sample_channels = ["UCn8ujwUInbJkBhffxqAPBVQ", "UCnVvS9_X9Y6X7X8X9X0X1X2"] 

    pipeline = chain(
        group(
            scrape_youtube_channels_task.s(sample_channels, hours),
            scrape_anthropic_research_task.s()
        ),
        process_transcripts_task.s(limit=50),
        synthesize_digests_task.s(),
        rank_digests_for_all_task.s(),
        deliver_emails_task.s(top_n=top_n)
    )

    result = pipeline.apply_async()
    logger.info(f"Pipeline triggered! Task ID: {result.id}")
    return result

if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 168
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run_async_pipeline(hours=hours, top_n=top_n)
