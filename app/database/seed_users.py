import sys
from pathlib import Path
import uuid

# Ensure the root directory is on the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.connection import engine
from app.database.models import Base
from app.database.repository import Repository

def seed_database():
    # Make sure tables exist (this is safe to run multiple times)
    Base.metadata.create_all(engine)
    print("Database tables created/verified.")

    repo = Repository()
    
    # Check if admin already exists
    admin_email = "admin@local.dev"
    if repo.get_user_by_email(admin_email):
        print(f"User {admin_email} already exists in the database.")
        return

    # Seed the admin user
    user_id = uuid.uuid4().hex
    
    # Default youtube channels for the admin (from config)
    youtube_channels = [
        "UCawZsQWqfGSbCI5yjkdVkTA"  # Matthew Berman
    ]
    
    admin_user = repo.create_user(
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
            "AI infrastructure and scaling challenges"
        ],
        preferences={
            "prefer_practical": True,
            "prefer_technical_depth": True,
            "prefer_research_breakthroughs": True,
            "prefer_production_focus": True,
            "avoid_marketing_hype": True
        },
        youtube_channels=youtube_channels
    )
    
    if admin_user:
        print(f"Successfully created user: {admin_user.name} ({admin_user.email})")
    else:
        print("Failed to create user.")

if __name__ == "__main__":
    seed_database()
