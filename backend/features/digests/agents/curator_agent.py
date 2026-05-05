from typing import Optional, Union, List, Dict, Any
import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class RankedArticle(BaseModel):
    digest_id: str
    relevance_score: float
    rank: int
    reasoning: str


class RankedDigestList(BaseModel):
    articles: list[RankedArticle]


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

    def rank_digests(self, digests: list[dict]) -> list[RankedArticle]:
        """
        Executes the semantic ranking process.
        
        This method performs 'Batch Ranking' to minimize LLM tokens and latency.
        It uses JSON Schema enforcement to guarantee that the agent's output
        is perfectly structured for the UI layer.
        """
        if not digests:
            return []

        # Rationale: We provide the article ID and Summary to the LLM so it can
        # weigh the 'Density of Insight' against the user's interests.
        articles_text = "\n\n".join([
            f"ID: {d['id']}\nTitle: {d['title']}\nSummary: {d['summary']}\nType: {d['article_type']}"
            for d in digests
        ])

        prompt = f"""Rank these {len(digests)} articles for the user above:

{articles_text}

Give each a relevance_score (0-10) and a unique rank (1 = best)."""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={
                    "type": "json_object",
                },
            )
            data = json.loads(resp.choices[0].message.content)
            return RankedDigestList.model_validate(data).articles
        except Exception as e:
            print(f"Error ranking digests: {e}")
            return []
