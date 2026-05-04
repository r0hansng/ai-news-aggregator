import os
import json
from typing import List
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class RankedArticle(BaseModel):
    digest_id: str
    relevance_score: float
    rank: int
    reasoning: str


class RankedDigestList(BaseModel):
    articles: List[RankedArticle]


SYSTEM_PROMPT = """You rank AI news articles based on how relevant they are to a specific user's background and interests.

Score each article 0-10 and give it a unique rank (1 = most relevant).
Be honest — not everything is a 9."""


class CuratorAgent:
    def __init__(self, user_profile: dict):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        p = self.user_profile
        interests = "\n".join(f"- {i}" for i in p["interests"])
        prefs = "\n".join(f"- {k}: {v}" for k, v in p["preferences"].items())

        return f"""{SYSTEM_PROMPT}

User: {p["name"]}
Background: {p["background"]}
Level: {p["expertise_level"]}

Interests:
{interests}

Preferences:
{prefs}"""

    def rank_digests(self, digests: List[dict]) -> List[RankedArticle]:
        if not digests:
            return []

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
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ranked_digest_list",
                        "schema": RankedDigestList.model_json_schema(),
                    },
                },
            )
            data = json.loads(resp.choices[0].message.content)
            return RankedDigestList.model_validate(data).articles
        except Exception as e:
            print(f"Error ranking digests: {e}")
            return []