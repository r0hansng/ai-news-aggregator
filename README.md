# AI News Aggregator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/Node-18%2B-green.svg)](https://nodejs.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009485.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)

An intelligent news aggregation platform that leverages AI to curate, rank, and deliver personalized news digests through multiple channels. Built with production-grade architecture for scalability and maintainability.

## Overview

AI News Aggregator is a full-stack application designed to solve information overload by:

- **Intelligent Curation**: AI-powered agents rank and filter news based on user interests
- **Multi-Source Integration**: Aggregates content from YouTube, Anthropic, OpenAI, and custom sources
- **Personalized Delivery**: Sends tailored digests via email at user-specified intervals
- **Real-time Processing**: Event-driven architecture with background workers for continuous signal ingestion

## Architecture

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | FastAPI (Python 3.11) | RESTful API with async processing |
| **Frontend** | Next.js 14 + React 18 + TypeScript | Modern SPA with server components |
| **Database** | PostgreSQL | Persistent data storage |
| **State Management** | React Query + Zustand | Server and client state orchestration |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **HTTP Transport** | Axios | Client-side HTTP with token rotation |
| **Containerization** | Docker + Docker Compose | Development and production deployment |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### Local Development

```bash
# Clone repository
git clone https://github.com/r0hansng/ai-news-aggregator.git
cd ai-news-aggregator

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start services with Docker
docker-compose up -d

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make dev

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Access the application at `http://localhost:3000`

## Project Structure

```
ai-news-aggregator/
├── backend/                    # Python FastAPI service
│   ├── cmd/                   # CLI commands and workers
│   ├── features/              # Domain-driven features
│   │   ├── digests/          # Signal digestion and curation
│   │   ├── signals/          # Content collection and processing
│   │   └── users/            # User management
│   └── infra/                # Infrastructure layer
├── frontend/                  # Next.js application
│   ├── src/
│   │   ├── app/              # Next.js app structure
│   │   ├── core/             # API client and state
│   │   ├── features/         # Feature modules
│   │   └── shared/           # Reusable components
│   └── docs/                 # Frontend documentation
├── docker/                    # Container definitions
├── infra/                     # Infrastructure configs
└── docs/                      # Project documentation
```

## Documentation

- **[Backend Architecture](docs/BACKEND.md)** - API design, database schema, and services
- **[Frontend Architecture](docs/FRONTEND.md)** - Component structure, state management, and patterns

## Key Features

### Backend

- Multi-agent orchestration (Curator, Digest, Email agents)
- Real-time signal processing from multiple sources
- Pub/Sub pattern for request queuing and token refresh
- Comprehensive error handling and logging
- Database migrations with Alembic

### Frontend

- Server-to-Client sync for instant UI updates
- Optimistic updates with rollback capability
- Staggered animations for smooth UX
- WCAG AA compliant accessible components
- Progressive disclosure in multi-step forms

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User authentication |
| POST | `/api/v1/auth/onboard` | User registration |
| GET | `/api/v1/digests/latest` | Fetch curated signals |
| POST | `/api/v1/digests/{id}/feedback` | Submit signal feedback |
| GET | `/api/v1/signals/resolve` | Resolve YouTube channels |
| PUT | `/api/v1/signals/sources` | Update user interests |

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Backend linting
cd backend
make lint

# Frontend linting
cd frontend
npm run lint
```

### Building for Production

```bash
# Backend
cd backend
docker build -f ../docker/Dockerfile.backend -t ai-news-aggregator-backend .

# Frontend
cd frontend
npm run build
docker build -f ../docker/Dockerfile.frontend -t ai-news-aggregator-frontend .
```

## Environment Variables

See `.env.example` for complete configuration:

| Variable | Type | Description |
|----------|------|-------------|
| `GROQ_API_KEY` | string | Groq API key for LLM access |
| `MY_EMAIL` | string | Sender email for digests |
| `APP_PASSWORD` | string | Email app password |
| `POSTGRES_*` | string | Database credentials |

## Performance

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time | <200ms | ~150ms |
| Page Load Time | <1s | ~800ms |
| Feed Polling Interval | 60s | Configurable |
| Email Delivery | <30s | ~10-20s |

## Contributing

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
3. Submit a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open a GitHub issue or contact the development team.

## Acknowledgments

Built with modern web technologies and best practices for scalability, maintainability, and developer experience.

---

**Made with focus on production-grade architecture and user experience.**
