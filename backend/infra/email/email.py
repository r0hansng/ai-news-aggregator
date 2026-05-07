"""
Email Delivery Infrastructure
=============================

This module provides the core delivery engine for the AI News Aggregator.
It handles HTML template rendering and SMTP transmission via FastAPI-Mail.

Design Pattern: Template-as-Code
--------------------------------
To maintain sub-second performance and avoid complex template management,
we use Python f-strings for HTML generation. In a larger production 
environment, this would be swapped for Jinja2 or a headless CMS.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

load_dotenv()


logger = logging.getLogger(__name__)


class EmailConfig:
    MAIL_USERNAME = os.getenv("MY_EMAIL", "mock_user")
    MAIL_PASSWORD = os.getenv("APP_PASSWORD", "mock_pass")
    MAIL_FROM = os.getenv("MY_EMAIL", "updates@ai-news.aggregator")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "AI News Aggregator")
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = False
    USE_CREDENTIALS = True
    VALIDATE_CERTS = True


conf = ConnectionConfig(
    MAIL_USERNAME=EmailConfig.MAIL_USERNAME,
    MAIL_PASSWORD=EmailConfig.MAIL_PASSWORD,
    MAIL_FROM=EmailConfig.MAIL_FROM,
    MAIL_PORT=EmailConfig.MAIL_PORT,
    MAIL_SERVER=EmailConfig.MAIL_SERVER,
    MAIL_FROM_NAME=EmailConfig.MAIL_FROM_NAME,
    MAIL_STARTTLS=EmailConfig.MAIL_STARTTLS,
    MAIL_SSL_TLS=EmailConfig.MAIL_SSL_TLS,
    USE_CREDENTIALS=EmailConfig.USE_CREDENTIALS,
    VALIDATE_CERTS=EmailConfig.VALIDATE_CERTS,
)


def digest_to_html(digest: Any) -> str:
    """
    Converts an EmailDigest Pydantic model into a clean HTML newsletter.

    This function acts as the 'Template Engine' for the curation system.
    """
    html = f"""
    <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a1a1a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">AI News Aggregator</h1>
            <p style="font-size: 18px; font-weight: bold; color: #3b82f6;">{digest.intro.greeting}</p>
            <p>{digest.intro.introduction}</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    """

    for article in digest.articles:
        html += f"""
            <div style="margin-bottom: 30px; padding: 15px; background-color: #f9fafb; border-radius: 8px;">
                <h2 style="margin-top: 0; color: #2563eb; font-size: 20px;">{article.title}</h2>
                <p style="font-size: 13px; color: #6b7280; text-transform: uppercase;">Source: {article.article_type} | Relevance: {article.relevance_score}/10</p>
                <div style="margin: 10px 0;">{article.summary}</div>
                <p style="font-style: italic; font-size: 14px; color: #4b5563;">Why you'll like it: {article.reasoning}</p>
                <a href="{article.url}" style="display: inline-block; background-color: #3b82f6; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 14px;">Read Full Article →</a>
            </div>
        """

    html += """
            <p style="font-size: 12px; color: #9ca3af; text-align: center; margin-top: 30px;">
                You're receiving this because you enabled email updates.<br>
                To unsubscribe, change your settings in the AI News Aggregator app.
            </p>
        </body>
    </html>
    """
    return html


async def send_email(subject: str, body_text: str, body_html: str, recipients: list[str]):
    """
    Transmits an email using the FastMail client.

    In development mode (mock_user), it writes the HTML to a local file for inspection.
    """
    message = MessageSchema(
        subject=subject, recipients=recipients, body=body_html, subtype=MessageType.html
    )

    fm = FastMail(conf)

    if EmailConfig.MAIL_USERNAME == "mock_user" or os.getenv("APP_ENV") == "development":
        logger.info(f"MOCK EMAIL SENT TO {recipients}")
        with open("last_email_sent.html", "w") as f:
            f.write(body_html)
    else:
        try:
            await fm.send_message(message)
            logger.info(f"Email sent successfully to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise e
