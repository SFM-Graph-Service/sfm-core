"""Pytest fixtures for REST API tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from api.rest.app import create_app
from api.rest.dependencies import get_sfm_service
from api.sfm_service import SFMService, SFMServiceConfig


@pytest.fixture
def mock_service():
    """Mock SFMService for unit tests."""
    return Mock(spec=SFMService)


@pytest.fixture
def app(mock_service):
    """FastAPI app with mocked service for unit tests."""
    application = create_app()
    application.dependency_overrides[get_sfm_service] = lambda: mock_service
    return application


@pytest.fixture
def client(app):
    """Test client for unit tests with mocked service."""
    return TestClient(app)


@pytest.fixture
def integration_app():
    """FastAPI app with real service for integration tests."""
    real_service = SFMService(SFMServiceConfig(storage_type="networkx"))
    application = create_app()
    application.dependency_overrides[get_sfm_service] = lambda: real_service
    return application


@pytest.fixture
def integration_client(integration_app):
    """Test client with real service for integration tests."""
    return TestClient(integration_app)
