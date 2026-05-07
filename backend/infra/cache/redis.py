"""
Redis Caching Infrastructure
============================

Provides a high-performance caching layer for the AI News Aggregator.
Used for feed response caching, session management, and task de-duplication.

Design Rationale:
- Latency: <1ms for cache hits (vs 100ms+ for DB/LLM).
- Scaling: Handles high-concurrency read/write ops (crucial for 10k users).
- Fallback: Gracefully handles Redis disconnection (falls back to DB).
"""

import json
import logging
import os
from typing import Optional, Any

import redis

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        try:
            self.client = redis.Redis(
                host=host, 
                port=port, 
                decode_responses=True,
                socket_timeout=2
            )
            self.client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600):
        if not self.client:
            return
        try:
            self.client.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.warning(f"Redis SET error for key {key}: {e}")

    def delete(self, key: str):
        if not self.client:
            return
        try:
            self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE error for key {key}: {e}")

# Singleton instance for global use
cache = RedisCache()
