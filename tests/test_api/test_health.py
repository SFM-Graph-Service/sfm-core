"""Tests for health and statistics endpoints."""

import pytest
from api.sfm_service import ServiceHealth, GraphStatistics


def test_get_health_success(client, mock_service):
    """Test GET /api/v1/health returns health status."""
    mock_service.get_health.return_value = ServiceHealth(
        status="healthy",
        node_count=100,
        relationship_count=150
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["node_count"] == 100
    assert data["relationship_count"] == 150
    assert "timestamp" in data
    mock_service.get_health.assert_called_once()


def test_get_statistics_success(client, mock_service):
    """Test GET /api/v1/statistics returns graph statistics."""
    mock_service.get_statistics.return_value = GraphStatistics(
        total_nodes=100,
        total_relationships=150,
        node_types={"Node": 50, "Actor": 30, "Institution": 20}
    )

    response = client.get("/api/v1/statistics")

    assert response.status_code == 200
    data = response.json()
    assert data["total_nodes"] == 100
    assert data["total_relationships"] == 150
    assert data["node_types"]["Node"] == 50
    assert data["node_types"]["Actor"] == 30
    assert data["node_types"]["Institution"] == 20
    mock_service.get_statistics.assert_called_once()


@pytest.mark.integration
def test_health_integration(integration_client):
    """Test health endpoint with real service."""
    response = integration_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "node_count" in data
    assert "relationship_count" in data
    assert "timestamp" in data


@pytest.mark.integration
def test_statistics_integration(integration_client):
    """Test statistics endpoint with real service."""
    response = integration_client.get("/api/v1/statistics")

    assert response.status_code == 200
    data = response.json()
    assert "total_nodes" in data
    assert "total_relationships" in data
    assert "node_types" in data
