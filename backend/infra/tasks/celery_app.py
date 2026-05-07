"""
Celery Task Queue Orchestration
===============================

This module initializes the Celery application, which serves as the 
backbone for distributed background processing in the AI News Aggregator.

Design Rationale:
- Broker: Redis (provides low-latency task handovers).
- Backend: Redis (stores task results).
- Parallelism: Allows scaling scraping and LLM ranking independently.
"""

import os
from celery import Celery

# Load configuration from environment
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Initialize Celery
app = Celery(
    "ai_news_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "backend.features.signals.tasks",
        "backend.features.digests.tasks"
    ]
)

# Configuration for Production Scale (10k users)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Prevent a single slow LLM task from blocking the worker
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Jitter to prevent thundering herd on scheduled tasks
    task_soft_time_limit=300,
    task_time_limit=600,
)

if __name__ == "__main__":
    app.start()
