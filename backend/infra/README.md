# Infrastructure Layer (`infra/`)

This directory contains the cross-cutting concerns and shared utilities for the AI News Aggregator backend.

## Structure

- **`database/`**: SQLAlchemy engine configuration, session management, and shared base models.
- **`email/`**: SMTP integration and template rendering for the delivery engine.
- **`gatekeeper.py`**: Global feature flagging and authorization logic (inspired by Meta's Gatekeeper).
- **`security.py`**: Cryptographic utilities, JWT handling, and password hashing (Argon2).

## Key Principles

1. **State-Agnostic**: Infrastructure utilities should ideally be stateless or manage their own connections.
2. **Standardized Interfaces**: Use generic types for configuration to allow easy swapping (e.g., swapping SMTP for SendGrid).
3. **Fail-Fast**: Validate environment variables at import time to prevent runtime crashes.
