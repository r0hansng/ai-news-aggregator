from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import users, signals, digests, orchestration
from app.database.connection import engine
from app.database.models import Base

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
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["Signals"])
app.include_router(digests.router, prefix="/api/v1/digests", tags=["Digests"])
app.include_router(orchestration.router, prefix="/api/v1/orchestrate", tags=["Orchestration"])

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
