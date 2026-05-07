"""
Global Configuration Module
===========================

This module centralizes static configurations and fallback values for the
AI News Aggregator backend. 

Key Components:
- Source IDs: Hardcoded identifiers for seed sources (YouTube, etc.)
- Environment defaults: (Reserved for future extension)

Rationale: Centralizing these IDs ensures that we can update source targets
without diving into the ingestion logic.
"""

# Default YouTube Channel IDs to scrape if the user has not specified any.
# Examples: Anthropic (UCawZsQWqfGSbCI5yjkdVkTA)
YOUTUBE_CHANNELS = [
    "UCawZsQWqfGSbCI5yjkdVkTA",
]
