import os
import json
from datetime import datetime
from typing import List, Optional
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class EmailIntro(BaseModel):
    greeting: str
    introduction: str


class ArticleDetail(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: Optional[str] = None


class EmailDigest(BaseModel):
    intro: EmailIntro
    articles: List[ArticleDetail]
    total_ranked: int
    top_n: int

    def to_markdown(self) -> str:
        out = f"{self.intro.greeting}\n\n{self.intro.introduction}\n\n---\n\n"
        for a in self.articles:
            out += f"## {a.title}\n\n{a.summary}\n\n[Read more →]({a.url})\n\n---\n\n"
        return out


SYSTEM_PROMPT = """Write a short, warm intro for a daily AI news digest email.
Greet the user by name, mention today's date, and briefly tease what's in the top articles.
2-3 sentences max. Keep it friendly, not corporate."""


class EmailAgent:
    def __init__(self, user_profile: dict):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.user = user_profile

    def _make_intro(self, articles: List) -> EmailIntro:
        if not articles:
            today = datetime.now().strftime("%B %d, %Y")
            return EmailIntro(
                greeting=f"Hey {self.user['name']}, here's your AI digest for {today}.",
                introduction="Nothing new to report today."
            )

        top = articles[:10]
        today = datetime.now().strftime("%B %d, %Y")
        titles = "\n".join([
            f"{i+1}. {a.title if hasattr(a, 'title') else a.get('title', '')} ({a.relevance_score if hasattr(a, 'relevance_score') else a.get('relevance_score', 0):.1f}/10)"
            for i, a in enumerate(top)
        ])

        prompt = f"""Write an intro for {self.user['name']}'s digest on {today}.

Top articles:
{titles}"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "email_intro",
                        "schema": EmailIntro.model_json_schema(),
                    },
                },
            )
            data = json.loads(resp.choices[0].message.content)
            intro = EmailIntro.model_validate(data)

            # make sure greeting starts properly
            if not intro.greeting.lower().startswith("hey"):
                intro.greeting = f"Hey {self.user['name']}, here's your AI digest for {today}."

            return intro
        except Exception as e:
            print(f"Error generating email intro: {e}")
            today = datetime.now().strftime("%B %d, %Y")
            return EmailIntro(
                greeting=f"Hey {self.user['name']}, here's your AI digest for {today}.",
                introduction="Here are your top AI stories for today."
            )

    def build_digest(self, ranked_articles: List[ArticleDetail], total_ranked: int, limit: int = 10) -> EmailDigest:
        top = ranked_articles[:limit]
        intro = self._make_intro(top)
        return EmailDigest(intro=intro, articles=top, total_ranked=total_ranked, top_n=limit)
