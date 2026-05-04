import os
import json
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DigestResult(BaseModel):
    title: str
    summary: str


SYSTEM_PROMPT = """You summarize AI-related content (YouTube videos, blog posts) into short digests for busy professionals.

Write a clean title and a 3-5 sentence summary that covers the key points and why it matters.
Be direct, skip the fluff, and keep it technically accurate."""


class DigestAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

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
                    "type": "json_schema",
                    "json_schema": {
                        "name": "digest_result",
                        "schema": DigestResult.model_json_schema(),
                    },
                },
            )
            data = json.loads(resp.choices[0].message.content)
            return DigestResult.model_validate(data)
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None