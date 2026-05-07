# Backend Architecture

## Overview

The AI News Aggregator backend is a high-performance, event-driven system built with FastAPI and Python 3.11+. It orchestrates intelligent signal curation, processing, and delivery through a modular architecture following domain-driven design principles.

### System Architecture

```mermaid
graph TD
    subgraph External Sources
        YT[YouTube API]
        OA[OpenAI Blog]
        AN[Anthropic Blog]
    end

    subgraph Ingestion Layer
        WS[Worker Scrapers]
        SR[Signal Repository]
    end

    subgraph Processing Layer
        CA[Curator Agent - Llama 3.3]
        DA[Digest Agent]
        EA[Email Agent]
    end

    subgraph Storage
        DB[(PostgreSQL)]
    end

    External Sources --> WS
    WS --> SR
    SR --> DB
    DB --> CA
    CA --> DA
    DA --> EA
    EA --> Email((User Email))
```

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104+ | Async web framework |
| **Runtime** | Python | 3.11+ | Core application language |
| **Database** | PostgreSQL | 15+ | Persistent data storage |
| **ORM** | SQLAlchemy | 2.0+ | Object-relational mapping |
| **Async Worker** | Celery/APScheduler | Latest | Background job processing |
| **API Docs** | OpenAPI/Swagger | Auto-generated | Interactive API documentation |

## Project Structure

```
backend/
├── cmd/                          # Command-line entry points
│   ├── api.py                   # FastAPI application startup
│   ├── worker.py                # Background job worker
│   ├── daily_worker.py          # Scheduled daily tasks
│   ├── check_db.py              # Database health check
│   └── seed.py                  # Database seeding
│
├── features/                    # Domain-driven features
│   ├── digests/
│   │   ├── model.py             # SQLAlchemy ORM models
│   │   ├── schema.py            # Pydantic request/response schemas
│   │   ├── router.py            # FastAPI route handlers
│   │   ├── repository.py        # Data access layer
│   │   ├── agents/              # AI agents
│   │   │   ├── curator_agent.py    # Ranking and curation logic
│   │   │   ├── digest_agent.py     # Digest generation
│   │   │   └── email_agent.py      # Email composition
│   │   ├── process_curator.py   # Curation orchestration
│   │   ├── process_digest.py    # Digest creation pipeline
│   │   ├── process_email.py     # Email sending pipeline
│   │   ├── feedback_schema.py   # Feedback data structures
│   │   └── orchestration_router.py # Refresh endpoint
│   │
│   ├── signals/
│   │   ├── model.py             # Signal data models
│   │   ├── schema.py            # Signal schemas
│   │   ├── router.py            # Signal endpoints
│   │   ├── repository.py        # Signal data access
│   │   ├── scrapers/            # Content scrapers
│   │   │   ├── youtube.py       # YouTube channel resolver
│   │   │   ├── anthropic.py     # Anthropic blog scraper
│   │   │   └── openai.py        # OpenAI blog scraper
│   │   ├── process_youtube.py   # YouTube processing pipeline
│   │   ├── process_anthropic.py # Anthropic processing
│   │   ├── scrape_articles.py   # Article collection
│   │   └── process_youtube.py   # YouTube processing
│   │
│   └── users/
│       ├── model.py             # User ORM model
│       ├── schema.py            # User schemas
│       ├── router.py            # User endpoints
│       └── repository.py        # User data access
│
├── infra/                       # Infrastructure layer
│   ├── gatekeeper.py            # Request validation and authorization
│   ├── security.py              # Password hashing and JWT tokens
│   ├── database/
│   │   ├── base.py              # Base configurations
│   │   ├── connection.py        # Database connection factory
│   │   ├── models.py            # Shared model definitions
│   │   └── __init__.py          # Package initialization
│   └── email/
│       └── email.py             # SMTP email sending service
│
├── config.py                    # Application configuration
├── __init__.py                  # Package initialization
├── pyproject.toml              # Project metadata and dependencies
└── requirements.txt            # Python dependencies
```

## Data Model

### Entities

```sql
-- User: Subscription and preferences
Users {
  id: UUID PRIMARY KEY
  email: VARCHAR UNIQUE NOT NULL
  password_hash: VARCHAR NOT NULL
  name: VARCHAR
  preferences: JSON
  created_at: TIMESTAMP
}

-- Signal: Raw content from sources
Signals {
  id: UUID PRIMARY KEY
  source_type: ENUM (youtube, anthropic, openai)
  title: VARCHAR
  summary: TEXT
  url: VARCHAR UNIQUE
  content: TEXT
  published_at: TIMESTAMP
  created_at: TIMESTAMP
}

-- Digest: Curated batch of signals
Digests {
  id: UUID PRIMARY KEY
  user_id: UUID FK
  title: VARCHAR
  items: JSON (ranked signals)
  created_at: TIMESTAMP
}

-- Feedback: User signal ratings
Feedback {
  id: UUID PRIMARY KEY
  digest_id: UUID FK
  rating: ENUM (positive, negative)
  comment: TEXT
  created_at: TIMESTAMP
}
```

### Relationships

```
User
  ├── 1:N → Digests
  ├── 1:N → Feedback
  └── 1:N → Interests

Signal
  ├── 1:N → DigestItems
  └── 1:N → Feedback

Digest
  ├── N:1 ← User
  ├── 1:N → DigestItems
  └── 1:N → Feedback
```

## API Specification

### Authentication

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/auth/login` | User authentication |
| POST | `/api/v1/auth/onboard` | User registration |
| POST | `/api/v1/auth/refresh` | Token refresh |
| POST | `/api/v1/auth/logout` | Session termination |

### Digests

| Method | Endpoint | Payload | Response |
|--------|----------|---------|----------|
| GET | `/api/v1/digests/latest?limit=10` | - | `{items: [], count: int}` |
| POST | `/api/v1/digests/{id}/feedback` | `{rating, comment}` | `{status: "ok"}` |

### Signals

| Method | Endpoint | Payload | Response |
|--------|----------|---------|----------|
| GET | `/api/v1/signals/resolve?query=...` | - | `{id, name, handle}` |
| PUT | `/api/v1/signals/sources` | `{interests, channels}` | `{status: "ok"}` |

### Orchestration

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/orchestrate/refresh` | Trigger signal collection |

## Core Workflows

### 1. User Registration (Onboarding)

```
POST /api/v1/auth/onboard
  ├─ Validate email (unique)
  ├─ Hash password with bcrypt
  ├─ Create user record
  ├─ Store preferences (frequency, format)
  └─ Response: { user_id, token }
```

**Time Complexity**: O(1) for validation + O(n) for hashing where n = password length

### 2. Signal Collection Pipeline

```
Scheduled Job (hourly)
  ├─ Scrape YouTube channels
  │  └─ YouTube API → resolve channel_id → fetch uploads
  ├─ Scrape Anthropic blog
  │  └─ HTTP request → parse HTML → extract metadata
  ├─ Scrape OpenAI blog
  │  └─ HTTP request → parse HTML → extract metadata
  └─ Store in Signals table
```

**Error Handling**: Retry 3x with exponential backoff on network errors

### 3. Digest Generation Pipeline

```
Scheduled Job (daily @ 8 AM)
  ├─ For each user:
  │  ├─ Load user interests and preferences
  │  ├─ Query recent signals (last 7 days)
  │  ├─ Filter by relevance (Curator Agent)
  │  ├─ Rank by score (0-100)
  │  ├─ Compose email body (Email Agent)
  │  ├─ Send via SMTP
  │  └─ Create Digest record
  └─ Log delivery status
```

**Processing**: O(n) for n users × O(m) for m signals

### 4. Feedback Processing Pipeline

```
POST /api/v1/digests/{id}/feedback
  ├─ Validate digest ownership
  ├─ Store feedback in database
  ├─ Queue for model retraining
  └─ Response: { status: "ok" }
```

## Agents

### Curator Agent

**Purpose**: Rank signals by relevance to user interests

**Algorithm**:
```python
score = 0
for interest in user_interests:
  if signal_title.contains(interest):
    score += 25
  if signal_summary.contains(interest):
    score += 15
score = min(100, score)  # Cap at 100
```

**Output**: Ranked list of signals with scores

### Digest Agent

**Purpose**: Generate human-readable digest summary

**Input**: Top 5-10 ranked signals

**Output**: Formatted digest with title and descriptions

### Email Agent

**Purpose**: Compose email with digest content

**Template**:
```
Subject: Your Daily News Digest - {date}

Hi {user_name},

Here are today's curated signals based on your interests:

{digest_items}

---
Unsubscribe: {unsubscribe_link}
```

## Security

### Authentication

```
Login Flow:
1. Verify email and password
2. Issue JWT token (24h expiry)
3. Store refresh token in cookie (7d, httpOnly)
4. Return access token in response
```

### Authorization

**Gate Keeper Middleware**:
```python
@require_auth  # Decorator
async def get_digests(request: Request):
    user_id = request.user.id
    # Only return user's own digests
```

### Data Protection

| Method | Applied | Purpose |
|--------|---------|---------|
| **Password Hashing** | bcrypt (12 rounds) | Credential security |
| **JWT Tokens** | HS256 algorithm | API authentication |
| **HTTPS Only** | Production enforced | Transport security |
| **CORS** | Frontend origin whitelisted | Cross-origin protection |

## Performance Optimization

### Database Indexing

```sql
-- Fast user lookups
CREATE INDEX idx_users_email ON users(email);

-- Signal queries by source and date
CREATE INDEX idx_signals_source_date ON signals(source_type, published_at DESC);

-- Digest lookups by user
CREATE INDEX idx_digests_user_created ON digests(user_id, created_at DESC);
```

### Query Optimization

| Technique | Implementation | Impact |
|-----------|-----------------|--------|
| **Pagination** | LIMIT/OFFSET | Reduce memory usage |
| **Lazy Loading** | On-demand relationships | Faster initial queries |
| **Caching** | Redis (optional) | Reduce DB queries |
| **Async Operations** | APScheduler + Celery | Non-blocking processing |

### Latency Targets

| Operation | Target | Current |
|-----------|--------|---------|
| **User Login** | <100ms | ~80ms |
| **Digest Fetch** | <200ms | ~150ms |
| **Feedback Submit** | <100ms | ~60ms |
| **Signal Collection** | N/A | ~5-10s (hourly) |
| **Digest Generation** | N/A | ~2-3s per user |

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker run -d \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15

# Run migrations
alembic upgrade head

# Start API server
make dev

# Start background worker
python -m backend.cmd.worker

# Start scheduled tasks
python -m backend.cmd.daily_worker
```

### Production (Docker)

```bash
# Build image
docker build -f docker/Dockerfile.backend -t ai-news-aggregator-backend .

# Run with environment
docker run -d \
  -e DATABASE_URL=postgresql://... \
  -e GROQ_API_KEY=... \
  -p 8000:8000 \
  ai-news-aggregator-backend
```

## Error Handling

### Standard Response Format

```json
{
  "status": "error",
  "code": "INVALID_EMAIL",
  "message": "Email already registered",
  "detail": "..."
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Digest fetched |
| 400 | Invalid input | Missing email |
| 401 | Unauthorized | Invalid token |
| 403 | Forbidden | Access denied |
| 404 | Not found | User not found |
| 500 | Server error | Database error |

## Monitoring

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Digest generated for user", extra={"user_id": user_id})
logger.error("Failed to send email", exc_info=True)
```

### Health Check

```
GET /health
→ { "status": "healthy", "db": "connected" }
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run specific module
pytest backend/features/digests/test_curator.py

# Coverage report
pytest --cov=backend
```

### Test Categories

| Type | Focus | Count |
|------|-------|-------|
| **Unit** | Individual functions | ~50 |
| **Integration** | Feature workflows | ~20 |
| **E2E** | Full user flows | ~10 |

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for public APIs
4. Include unit tests (>80% coverage)
5. Run `make lint` before commit

## Common Commands

```bash
# Development
make dev                    # Start API server
make worker                 # Start background worker
make migrations             # Create DB migrations

# Database
make db-reset              # Drop and recreate DB
make db-seed               # Populate with test data

# Quality
make lint                  # Run linting
make format                # Auto-format code
make test                  # Run test suite

# Build
make build                 # Build Docker image
make push                  # Push to registry
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **Database Connection Failed** | PostgreSQL not running | `docker-compose up -d` |
| **Email Not Sending** | SMTP credentials invalid | Check .env |
| **Signals Not Updating** | Worker not running | `make worker` |
| **401 Errors** | Token expired | Client should refresh |

---

**For frontend integration details, see [Frontend Architecture](FRONTEND.md)**
