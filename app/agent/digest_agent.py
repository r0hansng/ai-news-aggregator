import os
import json
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class DigestResult(BaseModel):
    title: str = Field(description="A clear, concise title for the digest (can match or refine the original)")
    summary: str = Field(description="A 3-5 sentence summary of the key points, insights, and takeaways from the article or video")


DIGEST_PROMPT = """You are an expert AI content summarizer specializing in creating concise, insightful digests for AI professionals.

Your role is to analyze AI-related articles, blog posts, and video transcripts and produce a clear, actionable digest.

Guidelines:
- Write a crisp title that captures the essence of the content
- Summarize the key points, findings, and takeaways in 3-5 sentences
- Highlight what's novel, important, or practically useful
- Maintain technical accuracy while keeping it accessible
- Focus on what an AI professional would find most valuable

Content types you will process:
- youtube: Video transcripts from AI channels
- openai: OpenAI blog posts and announcements
- anthropic: Anthropic blog posts and research updates"""


class DigestAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def generate_digest(
        self,
        title: str,
        content: str,
        article_type: str
    ) -> Optional[DigestResult]:
        if not content or not content.strip():
            return None

        # Truncate very long content to avoid token limits
        max_chars = 12000
        truncated_content = content[:max_chars] + ("..." if len(content) > max_chars else "")

        user_prompt = f"""Please create a digest for the following {article_type} content:

Title: {title}

Content:
{truncated_content}

Generate a clear title and a 3-5 sentence summary capturing the key insights."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DIGEST_PROMPT},
                    {"role": "user", "content": user_prompt},
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

            raw = response.choices[0].message.content
            data = json.loads(raw)
            return DigestResult.model_validate(data)
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None