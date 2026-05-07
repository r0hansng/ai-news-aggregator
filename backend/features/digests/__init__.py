from typing import Any, Dict, List, Optional, Union

"""
Digests Feature Module
======================

This module is the "Brain" of the application. It transforms raw signals into
personalized, AI-curated news summaries.

Key Functions:
1. LLM Ranking: Using Agentic workflows to score news relevance based on user profiles.
2. Summary Generation: Synthesizing transcripts and articles into readable digests.
3. Email Orchestration: Building and delivering the final top-10 newsletter.
4. Feedback Loop: Storing user feedback to calibrate future rankings.

Architecture:
- `agents/`: AI agents powered by Anthropic/OpenAI/Groq for curation.
- `orchestration_router.py`: The control plane for triggering full-system refreshes.
- `repository.py`: Management of curated Digest items.
- `router.py`: API for fetching the personalized feed and submitting feedback.
"""
