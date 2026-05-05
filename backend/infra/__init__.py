"""
Infrastructure Layer
====================

The platform layer that provides cross-cutting concerns to the feature modules.
It is designed to be "Agnostic" to business logic.

Components:
1. `database/`: Connection pooling and SQLAlchemy metadata registry.
2. `security/`: Hashing and Token management.
3. `gatekeeper/`: Production feature-flagging utility for safe rollouts.
4. `email/`: Standardized email delivery client.
"""
