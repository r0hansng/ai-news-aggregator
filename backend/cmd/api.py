from typing import Optional, Union, List, Dict, Any
"""
API Server Entry Point
======================

This script initializes and runs the FastAPI application. It orchestrates the 
inclusion of all feature routers and sets up global middleware (CORS).

Execution:
    $ uvicorn app.cmd.api:app --reload

Deployment:
    The Dockerfile uses this file as the primary CMD to serve the production API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.features.users.router import router as users_router
from backend.features.signals.router import router as signals_router
from backend.features.digests.router import router as digests_router
from backend.features.digests.orchestration_router import router as orchestration_router
from backend.infra.database.connection import engine
from backend.infra.database.base import Base
from backend.infra.database.models import User # Ensure models are registered

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI News Aggregator API",
    description="Production-grade API for personalized AI technical news curation.",
    version="1.0.0"
)

# Configure CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    return {
        "message": "Welcome to the AI News Aggregator API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "now"}
