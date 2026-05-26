"""Tests for Phase 2 query analysis endpoints."""

import uuid
import pytest


def test_ceremonial_analysis_default_threshold(client, mock_service):
    """Test POST /api/v1/query/ceremonial with default threshold."""
    mock_service.get_ceremonial_analysis.return_value = {
        "ceremonial_nodes": [str(uuid.uuid4()), str(uuid.uuid4())],
        "instrumental_nodes": [str(uuid.uuid4())],
        "ceremonial_ratio": 0.67,
        "threshold": 0.5
    }

    response = client.post("/api/v1/query/ceremonial")

    assert response.status_code == 200
    data = response.json()
    assert "ceremonial_nodes" in data
    assert "instrumental_nodes" in data
    assert data["ceremonial_ratio"] == 0.67
    assert data["threshold"] == 0.5
    mock_service.get_ceremonial_analysis.assert_called_once_with(threshold=0.5)


def test_ceremonial_analysis_custom_threshold(client, mock_service):
    """Test POST /api/v1/query/ceremonial with custom threshold."""
    mock_service.get_ceremonial_analysis.return_value = {
        "ceremonial_nodes": [str(uuid.uuid4())],
        "instrumental_nodes": [str(uuid.uuid4()), str(uuid.uuid4())],
        "ceremonial_ratio": 0.33,
        "threshold": 0.7
    }

    response = client.post(
        "/api/v1/query/ceremonial",
        json={"threshold": 0.7}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threshold"] == 0.7
    assert data["ceremonial_ratio"] == 0.33
    mock_service.get_ceremonial_analysis.assert_called_once_with(threshold=0.7)


def test_ceremonial_analysis_invalid_threshold(client, mock_service):
    """Test POST /api/v1/query/ceremonial with invalid threshold."""
    response = client.post(
        "/api/v1/query/ceremonial",
        json={"threshold": 1.5}
    )

    # Should fail validation (threshold must be 0.0-1.0)
    assert response.status_code == 422


def test_circular_causation_success(client, mock_service):
    """Test GET /api/v1/query/circular-causation/{source_id} returns cycles."""
    source_id = uuid.uuid4()
    mock_cycles = [
        {
            "nodes": [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())],
            "strength": 0.8,
            "feedback_type": "reinforcing"
        },
        {
            "nodes": [str(uuid.uuid4()), str(uuid.uuid4())],
            "strength": 0.6,
            "feedback_type": "balancing"
        }
    ]
    mock_service.get_circular_causation.return_value = mock_cycles

    response = client.get(f"/api/v1/query/circular-causation/{source_id}")

    assert response.status_code == 200
    data = response.json()
    assert "cycles" in data
    assert "source_id" in data
    assert len(data["cycles"]) == 2
    assert data["cycles"][0]["feedback_type"] == "reinforcing"
    assert data["cycles"][1]["feedback_type"] == "balancing"
    mock_service.get_circular_causation.assert_called_once_with(source_id)


def test_circular_causation_no_cycles(client, mock_service):
    """Test circular causation when no cycles exist."""
    source_id = uuid.uuid4()
    mock_service.get_circular_causation.return_value = []

    response = client.get(f"/api/v1/query/circular-causation/{source_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["cycles"] == []
    assert str(source_id) in data["source_id"]


def test_circular_causation_invalid_uuid(client, mock_service):
    """Test circular causation with invalid UUID."""
    response = client.get("/api/v1/query/circular-causation/not-a-uuid")

    assert response.status_code == 422


def test_holarchy_success(client, mock_service):
    """Test GET /api/v1/query/holarchy/{institution_id} returns structure."""
    institution_id = uuid.uuid4()
    mock_holarchy = {
        "institution_id": institution_id,
        "layers": [
            {"level": 0, "institutions": [str(institution_id)]},
            {"level": 1, "institutions": [str(uuid.uuid4()), str(uuid.uuid4())]}
        ],
        "relationships": [
            {"parent": str(institution_id), "child": str(uuid.uuid4()), "type": "governs"}
        ],
        "depth": 2
    }
    mock_service.get_holarchy.return_value = mock_holarchy

    response = client.get(f"/api/v1/query/holarchy/{institution_id}")

    assert response.status_code == 200
    data = response.json()
    assert "institution_id" in data
    assert "layers" in data
    assert "relationships" in data
    assert "depth" in data
    assert data["depth"] == 2
    assert len(data["layers"]) == 2
    mock_service.get_holarchy.assert_called_once_with(institution_id)


def test_holarchy_single_level(client, mock_service):
    """Test holarchy with single institution (no hierarchy)."""
    institution_id = uuid.uuid4()
    mock_holarchy = {
        "institution_id": institution_id,
        "layers": [{"level": 0, "institutions": [str(institution_id)]}],
        "relationships": [],
        "depth": 1
    }
    mock_service.get_holarchy.return_value = mock_holarchy

    response = client.get(f"/api/v1/query/holarchy/{institution_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["depth"] == 1
    assert len(data["relationships"]) == 0


def test_conflicts_success(client, mock_service):
    """Test GET /api/v1/query/conflicts returns conflict list."""
    mock_conflicts = [
        {
            "conflict_type": "value",
            "nodes": [str(uuid.uuid4()), str(uuid.uuid4())],
            "severity": 0.8,
            "description": "Conflicting value orientations"
        },
        {
            "conflict_type": "resource",
            "nodes": [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())],
            "severity": 0.6,
            "description": "Resource allocation conflict"
        }
    ]
    mock_service.get_conflicts.return_value = mock_conflicts

    response = client.get("/api/v1/query/conflicts")

    assert response.status_code == 200
    data = response.json()
    assert "conflicts" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["conflicts"]) == 2
    assert data["conflicts"][0]["conflict_type"] == "value"
    assert data["conflicts"][1]["conflict_type"] == "resource"
    mock_service.get_conflicts.assert_called_once()


def test_conflicts_empty(client, mock_service):
    """Test conflicts endpoint when no conflicts detected."""
    mock_service.get_conflicts.return_value = []

    response = client.get("/api/v1/query/conflicts")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["conflicts"] == []


@pytest.mark.integration
def test_ceremonial_analysis_integration(integration_client):
    """Test ceremonial analysis with real service."""
    response = integration_client.post(
        "/api/v1/query/ceremonial",
        json={"threshold": 0.5}
    )

    assert response.status_code == 200
    data = response.json()
    assert "ceremonial_nodes" in data
    assert "instrumental_nodes" in data
    assert "ceremonial_ratio" in data
    assert "threshold" in data
    assert data["threshold"] == 0.5


@pytest.mark.integration
def test_conflicts_integration(integration_client):
    """Test conflict detection with real service."""
    response = integration_client.get("/api/v1/query/conflicts")

    assert response.status_code == 200
    data = response.json()
    assert "conflicts" in data
    assert "total" in data
    assert isinstance(data["conflicts"], list)
    assert isinstance(data["total"], int)
