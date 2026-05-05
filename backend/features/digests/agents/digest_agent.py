from typing import Optional, Union, List, Dict, Any
import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class DigestResult(BaseModel):
    title: str
    summary: str


SYSTEM_PROMPT = """Respond in JSON format. You summarize AI-related content into short digests.

Return a JSON object with:
- 'title': A clean, professional title.
- 'summary': A 3-5 sentence summary covering key points and relevance.

Be direct, skip the fluff, and keep it technically accurate."""


class DigestAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        # We use Llama 3.1 70B for high-quality technical summarization of research papers and transcripts.
        self.model = "llama-3.1-70b-versatile" 

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestResult]:
        if not content or not content.strip():
            return None

        # trim content so we don't blow up the context window
        content = content[:12000]

        prompt = f"""Summarize this {article_type} content:

Title: {title}

Content:
{content}"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={
                    "type": "json_object",
                },
            )
            data = json.loads(resp.choices[0].message.content)
            return DigestResult.model_validate(data)
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None
