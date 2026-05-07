# AI News Aggregator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Bun](https://img.shields.io/badge/Bun-1.1-black.svg)](https://bun.sh/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009485.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.3-green.svg)](https://docs.celeryq.dev/)

An intelligent news aggregation platform that leverages AI to curate, rank, and deliver personalized news digests. Built with a high-scale, distributed architecture to handle 10,000+ active users.

## 🚀 High-Scale Architecture

| Component | Technology | Role |
|-----------|-----------|------|
| **API Layer** | FastAPI (Python 3.11) | High-concurrency ASGI server with Gunicorn workers. |
| **Frontend** | Next.js 14 + Bun | Premium UX with server-side rendering and optimistic UI. |
| **Cache & Broker** | Redis 7 | Feed response caching, session store, and Celery broker. |
| **Task Queue** | Celery | Distributed background processing for scraping and LLM ranking. |
| **Database** | PostgreSQL 17 | Relational storage with Alembic migration management. |
| **Monitoring** | Flower + Sentry | Task tracking dashboard and production error reporting. |
| **DevOps** | Docker + Husky | Containerized services and conventional commit enforcement. |

## 🏗️ Technical Pipeline

1. **Extraction**: Distributed workers scrape signals from YouTube (RSS + Transcripts) and Technical Research sites.
2. **Persistence**: Signals are normalized and stored in PostgreSQL with unique content hashing.
3. **Caching**: Frequent feed requests are served via Redis (<1ms latency) to support high-scale traffic.
4. **Semantic Ranking**: The **AI Curator Agent** (Llama 3.3) performs persona-aware batch ranking for every user.
5. **Delivery**: Curated digests are dispatched via an asynchronous email engine.

## 🛠️ Quick Start

### Prerequisites

- [Bun](https://bun.sh/) (for Frontend & Root tools)
- [uv](https://github.com/astral-sh/uv) (for Backend dependency management)
- Docker & Docker Compose

### Deployment (Development)

```bash
# 1. Provision Infrastructure (Postgres, Redis, pgAdmin, Flower)
make db-up

# 2. Setup Database Schema (Alembic)
make db-init

# 3. Start Backend API
# In production, this uses Gunicorn/Uvicorn workers
cd backend && uv run uvicorn backend.cmd.api:app --reload

# 4. Start Frontend
make fe-dev
```

Access **Flower Dashboard** at `http://localhost:5555` to monitor background tasks.

## 📈 Scalability Features

- **Horizontal Scaling**: Backend workers and API instances can be scaled independently.
- **Rate Limiting**: Global API protection via `slowapi` to prevent resource exhaustion.
- **Failover**: LLM ranking includes automatic retry logic and "graceful degradation" fallbacks.
- **Optimized Caching**: Redis-backed feed caching with 60s TTL and event-driven invalidation.

## 🤝 Contribution & Standards

We enforce **Conventional Commits** using Husky and Commitizen.

```bash
# To commit changes, use the interactive prompt:
git add .
bun run commit  # Triggers the conventional commit wizard
```

## 📜 Documentation

- **[Architecture Deep-Dive](docs/ARCHITECTURE.md)** - Logic flow and system design.
- **[API Reference](backend/README.md)** - Detailed endpoint documentation.
- **[Frontend Guide](frontend/README.md)** - Component patterns and state management.

---

**Built with focus on production-grade resilience and sub-second user experience.**
