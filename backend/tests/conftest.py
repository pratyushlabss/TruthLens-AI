"""Pytest configuration and fixtures."""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def backend_app():
    """Provide FastAPI app for testing."""
    from app.main import app
    return app


@pytest.fixture
def test_client(backend_app):
    """Provide FastAPI test client."""
    from fastapi.testclient import TestClient
    return TestClient(backend_app)
