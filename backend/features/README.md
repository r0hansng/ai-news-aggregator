# Feature Modules (`features/`)

The core business logic of the application is organized into domain-driven feature modules. Each module is self-contained and follows a standardized internal structure.

## Feature Structure

Every feature folder typically contains:
- `model.py`: Domain-specific database entities.
- `schema.py`: Pydantic models for validation and API serialization.
- `router.py`: FastAPI endpoints and request handling.
- `repository.py`: Encapsulated data access logic.

## Domain Overview

- **`digests/`**: Orchestration of AI agents to curate and summarize signals into user-specific batches.
- **`signals/`**: Real-time content collection (scrapers) and transcript processing.
- **`users/`**: Identity management, onboarding flows, and interest profiles.

## Ownership

Changes to these directories should be reviewed by the domain leads (e.g., AI/Agents team for `digests`, Crawler team for `signals`).
