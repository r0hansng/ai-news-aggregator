"""
Database Seeding Utility
========================

This script provides a one-click mechanism to bootstrap the local development
environment with high-integrity 'Golden Data'. 

Seed targets:
- Schema: Verifies and creates tables.
- Admin User: Creates a default advanced persona to test the AI Curator.

Rationale:
A 'Big Tech' environment should be reproducible in minutes. This script 
ensures that every engineer starts with the same high-quality test data.
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.features.users.repository import UserRepository
from backend.infra.database.base import Base
from backend.infra.database.connection import engine


def seed_database():

    Base.metadata.create_all(engine)
    print("Database tables created/verified.")

    user_repo = UserRepository()

    admin_email = "admin@local.dev"
    if user_repo.get_user_by_email(admin_email):
        print(f"User {admin_email} already exists in the database.")
        return

    user_id = uuid.uuid4().hex

    youtube_channels = [
        "UCawZsQWqfGSbCI5yjkdVkTA"  # Matthew Berman
    ]

    admin_user = user_repo.create_user(
        user_id=user_id,
        name="Admin",
        email=admin_email,
        title="AI System Administrator",
        background="System administrator and AI enthusiast testing the production readiness of the AI News Aggregator.",
        expertise_level="Advanced",
        interests=[
            "Large Language Models (LLMs) and their applications",
            "Retrieval-Augmented Generation (RAG) systems",
            "AI agent architectures and frameworks",
            "Production AI systems and MLOps",
            "Real-world AI applications and case studies",
            "AI infrastructure and scaling challenges",
        ],
        preferences={
            "prefer_practical": True,
            "prefer_technical_depth": True,
            "prefer_research_breakthroughs": True,
            "prefer_production_focus": True,
            "avoid_marketing_hype": True,
        },
        youtube_channels=youtube_channels,
    )

    if admin_user:
        print(f"Successfully created user: {admin_user.name} ({admin_user.email})")
    else:
        print("Failed to create user.")


if __name__ == "__main__":
    seed_database()
