# ADR-001: Standardization on Python 3.11 and `uv`

## Status
Accepted

## Date
2026-05-07

## Context
The project was previously running on Python 3.9 and using a mix of `pip` and manual `venv` management. This led to dependency resolution issues and limited our ability to use modern Python features (e.g., `datetime.UTC`, `| None` type hints).

## Decision
We will standardize the backend on:
1. **Python 3.11.15**: To leverage modern typing, performance improvements, and standardized libraries.
2. **`uv` Package Manager**: For extremely fast dependency resolution and standardized environment management through `pyproject.toml`.

## Consequences
- Developers must have `uv` installed.
- All dependencies must be managed via `pyproject.toml` [project.dependencies].
- `requirements.txt` will be kept as a secondary manifest for legacy tool compatibility but is no longer the primary source of truth.
- Code quality tools (Ruff/Mypy) are now configured for Python 3.11+.
