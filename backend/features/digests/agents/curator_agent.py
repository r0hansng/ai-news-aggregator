"""
Curator Agent Module
====================

This module defines the intelligence layer for semantic signal ranking.
It interfaces with high-performance LLM providers (Groq) to evaluate
content relevance based on complex user personas.

Internal Dependencies:
- OpenAI: Used as the SDK for LLM communication.
- Pydantic: Used for structured response validation and type safety.
"""
from __future__ import annotations
import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

load_dotenv()


class RankedArticle(BaseModel):
    """
    Data contract for a single ranked signal.

    Attributes:
        digest_id: Unique identifier for the source signal.
        relevance_score: A normalized float (0-10) indicating AI-perceived relevance.
        rank: The ordinal position of the article in the current batch.
        reasoning: High-level justification for the assigned score (used for debugging/UI).
    """
    digest_id: str
    relevance_score: float
    rank: int
    reasoning: str


class RankedDigestList(BaseModel):
    articles: List[RankedArticle]


SYSTEM_PROMPT = """Respond in JSON format. You rank AI news articles based on how relevant they are to a specific user's background and interests.

Return a JSON object with an 'articles' key containing a list of objects.
Each object MUST have:
- 'digest_id': The ID provided in the input.
- 'relevance_score': 0-10 float.
- 'rank': Unique integer (1 = best).
- 'reasoning': A short sentence explaining the score.

Score each article 0-10 and be honest — not everything is a 9."""


class CuratorAgent:
    """
    The intelligence layer of the application.

    This agent uses a Large Language Model (LLM) to perform 'Semantic Ranking'.
    Instead of keyword matching, it evaluates how a news item aligns with a user's
    specific professional background and technical expertise level.

    Design Pattern: Zero-Shot Chain-of-Thought Ranking.
    """

    def __init__(self, user_profile: dict):
        """
        Initializes the agent with a user's persona.

        The user_profile is treated as a 'System Prompt Extension', anchoring the
        model's perspective to the specific needs of that professional.
        """
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        # We use Llama 3.3 70B via Groq for sub-second inference latency, which is
        # critical for real-time ranking of the user's feed.
        self.model = "llama-3.3-70b-versatile"
        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        Constructs a high-context persona for the LLM.

        Rationale: By injecting the user's expertise level (Beginner vs Advanced),
        we instruct the model to penalize basic tutorials for Advanced users
        and prioritize deep-dive research papers.
        """
        p = self.user_profile
        interests = "\n".join(f"- {i}" for i in p["interests"])
        prefs = "\n".join(f"- {k}: {v}" for k, v in p["preferences"].items())

        return f"""{SYSTEM_PROMPT}

User Persona: {p["name"]}
Technical Background: {p["background"]}
Expertise Level: {p["expertise_level"]} (PRIORITIZE DEPTH ACCORDINGLY)

Technical Interests:
{interests}

Signal Filtering Preferences:
{prefs}"""

    def rank_digests(self, digests: List[Dict]) -> List[RankedArticle]:
        """
        Executes the semantic ranking process with robust error recovery.
        Uses batching to handle large signal sets without exceeding context limits.
        """
        if not digests:
            return []

        # Constants for Batching (Prevent LLM context overflow/timeout)
        BATCH_SIZE = 15
        all_ranked_articles = []

        for i in range(0, len(digests), BATCH_SIZE):
            batch = digests[i : i + BATCH_SIZE]
            ranked_batch = self._rank_batch(batch)
            all_ranked_articles.extend(ranked_batch)

        return all_ranked_articles

    def _rank_batch(self, batch: List[Dict], retries: int = 2) -> List[RankedArticle]:
        """Rank a specific batch of signals with retry mechanism."""
        articles_text = "\n\n".join(
            [
                f"ID: {d['id']}\nTitle: {d['title']}\nSummary: {d['summary']}\nType: {d['article_type']}"
                for d in batch
            ]
        )

        prompt = f"""Rank these {len(batch)} signals for the user above:

{articles_text}

Provide relevance_score (0-10) and unique rank (1 = best)."""

        for attempt in range(retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2, # Lower temperature for ranking stability
                    response_format={"type": "json_object"},
                    timeout=15.0 # Strict timeout for 10k user scalability
                )
                
                content = resp.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from LLM")

                data = json.loads(content)
                return RankedDigestList.model_validate(data).articles

            except Exception as e:
                if attempt == retries:
                    logger.error(f"Final failure ranking batch: {e}")
                    # Fallback: Return low-score ranking for the batch to prevent UI crash
                    return [
                        RankedArticle(
                            digest_id=d['id'], 
                            relevance_score=1.0, 
                            rank=99, 
                            reasoning="Ranking service degraded, falling back to discovery order."
                        )
                        for d in batch
                    ]
                logger.warning(f"Retry {attempt + 1} for ranking batch due to: {e}")
        
        return []
