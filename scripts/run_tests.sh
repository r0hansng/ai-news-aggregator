#!/bin/bash

# ==============================================================================
# AI News Aggregator — Global Test Runner
# ==============================================================================
#
# This script executes the entire testing pyramid, providing a high-level 
# summary of project health across backend, frontend, and E2E layers.
#
# Usage:
#   ./scripts/run_tests.sh
# ==============================================================================

set -e # Exit on first error

echo "===================================================="
echo "🚀 Starting Project-Wide Validation Pipeline"
echo "===================================================="

# 1. Backend Validation
echo -e "\n[1/3] Running Backend Tests (Pytest)..."
make test-backend

# 2. Frontend Validation
echo -e "\n[2/3] Running Frontend Logic Tests (Vitest)..."
make test-frontend

# 3. E2E Validation (Optional: Can be skipped with --no-e2e)
if [[ "$*" != *"--no-e2e"* ]]; then
    echo -e "\n[3/3] Running E2E User Journey Tests (Playwright)..."
    echo "Note: This requires the dev server to be running (make fe-dev & make db-up)"
    make test-e2e
else
    echo -e "\n[3/3] Skipping E2E tests as requested."
fi

echo -e "\n===================================================="
echo "✅ All tests passed successfully!"
echo "===================================================="
