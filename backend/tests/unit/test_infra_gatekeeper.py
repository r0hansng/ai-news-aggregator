import os
import pytest
from backend.infra.gatekeeper import gk

def test_gatekeeper_default_values():
    # Test a flag that is True by default
    assert gk.is_enabled("ENABLE_AGENTIC_DIGESTS") is True
    # Test a flag that is False by default
    assert gk.is_enabled("USE_EXPERIMENTAL_RANKER") is False
    # Test a non-existent flag with default fallback
    assert gk.is_enabled("NON_EXISTENT", default=True) is True

def test_gatekeeper_env_override(monkeypatch):
    # Override a flag via environment variable
    monkeypatch.setenv("GK_ENABLE_AGENTIC_DIGESTS", "false")
    assert gk.is_enabled("ENABLE_AGENTIC_DIGESTS") is False
    
    monkeypatch.setenv("GK_USE_EXPERIMENTAL_RANKER", "true")
    assert gk.is_enabled("USE_EXPERIMENTAL_RANKER") is True

def test_gatekeeper_get_all_flags():
    flags = gk.get_all_flags()
    assert "ENABLE_AGENTIC_DIGESTS" in flags
    assert "USE_EXPERIMENTAL_RANKER" in flags
    assert isinstance(flags["ENABLE_AGENTIC_DIGESTS"], bool)
