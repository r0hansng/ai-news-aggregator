import os
import logging
from typing import List, Optional
from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Email Configuration
class EmailConfig:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "mock_user")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "mock_pass")
    MAIL_FROM = os.getenv("MAIL_FROM", "updates@ai-news.aggregator")
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
    VALIDATE_CERTS=EmailConfig.VALIDATE_CERTS
)

async def send_digest_email(email: str, name: str, digests: List[dict]):
    """
    Send the latest AI digest to the user via email.
    In development/mock mode, this logs the content.
    """
    subject = f"Your Daily AI News Digest, {name}!"
    
    # Simple HTML template for the digest
    digest_html = f"""
    <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee;">
                <h1 style="color: #1a1a1a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">AI News Aggregator</h1>
                <p>Hello {name}, here are the latest updates based on your interests:</p>
    """
    
    for digest in digests:
        digest_html += f"""
                <div style="margin-bottom: 25px; padding: 15px; background-color: #f9fafb; border-radius: 8px;">
                    <h2 style="margin-top: 0; color: #2563eb;">{digest['title']}</h2>
                    <p style="font-size: 14px; color: #6b7280;">Source: {digest['article_type'].upper()}</p>
                    <div style="margin-top: 10px;">
                        {digest['summary']}
                    </div>
                    <a href="{digest['url']}" style="display: inline-block; margin-top: 10px; color: #3b82f6; text-decoration: none; font-weight: bold;">Read Full Article →</a>
                </div>
        """
        
    digest_html += """
                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #9ca3af; text-align: center;">
                    You're receiving this because you enabled email updates in your AI News Aggregator preferences.<br>
                    To unsubscribe, change your settings in the app.
                </p>
            </div>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=digest_html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    
    # For now, let's just log it unless we have real credentials
    if EmailConfig.MAIL_USERNAME == "mock_user":
        logger.info(f"MOCK EMAIL SENT TO {email}")
        # We can also write to a local file for the user to inspect
        with open("last_email_sent.html", "w") as f:
            f.write(digest_html)
    else:
        try:
            await fm.send_message(message)
            logger.info(f"Email sent successfully to {email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise e
