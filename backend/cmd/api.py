"""
Main API Entry Point
====================

This script initializes the FastAPI application, registers all domain-driven
feature routers, and configures global middleware (CORS, logging).

Design Philosophy:
------------------
- Separation of Concerns: The app instance is created here, but business logic
  resides strictly within the `features/` directory.
- Schema Discovery: We explicitly import all routers to ensure OpenAPI docs
  are correctly generated at `/docs`.

Note on Migrations:
-------------------
In this development environment, we use `Base.metadata.create_all()` for simplicity.
In a high-scale production system, this would be handled by Alembic to manage
stateful schema changes safely.
"""
import os
import logging
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Global Rate Limiter (Protection for 10k users scale)
limiter = Limiter(key_func=get_remote_address)

# Initialize Sentry for production error tracking (10k users support)
# In production, SENTRY_DSN should be set in environment.
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1, # Sample 10% of transactions for performance
        profiles_sample_rate=0.1,
    )

# Setup Production Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from backend.features.digests.orchestration_router import router as orchestration_router
from backend.features.digests.router import router as digests_router
from backend.features.signals.router import router as signals_router
from backend.features.users.router import router as users_router

app = FastAPI(
    title="AI News Aggregator API",
    description="Production-grade API for personalized AI technical news curation.",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS for the Next.js frontend
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", ""),
]

# Clean up empty strings and ensure production URLs are supported
origins = [o for o in origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(signals_router, prefix="/api/v1/signals", tags=["Signals"])
app.include_router(digests_router, prefix="/api/v1/digests", tags=["Digests"])
app.include_router(orchestration_router, prefix="/api/v1/orchestrate", tags=["Orchestration"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI News Aggregator API", "docs": "/docs", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "now"}
