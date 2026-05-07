from typing import Any, Dict, List, Optional, Union

"""
Users Feature Module
====================

This module manages the user lifecycle, authentication, and profile settings.
It is responsible for:
1. User onboarding and password hashing (Argon2).
2. JWT-based session management and token refreshes.
3. Managing user tracking signals (Interests and YouTube Channels).
4. Subscription and email delivery preferences.

Architecture:
- `router.py`: API endpoints for onboarding, login, and profile management.
- `repository.py`: Encapsulates all SQLAlchemy operations for the User and Feedback models.
- `model.py`: Database schema definitions.
- `schema.py`: Pydantic models for request validation and response serialization.
"""
