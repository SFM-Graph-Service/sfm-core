"""Tests for Phase 3 evaluation endpoints."""

import uuid
import pytest


def test_evaluate_digraph_success(client, mock_service):
    """Test POST /api/v1/evaluate/digraph with institution list."""
    inst_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
    mock_result = {
        "dependencies": {"direct": 5, "transitive": 12},
        "sequences": [
            {"path": [str(inst_ids[0]), str(inst_ids[1])], "length": 2},
            {"path": [str(inst_ids[1]), str(inst_ids[2])], "length": 2}
        ],
        "hierarchy_depth": 3
    }
    mock_service.evaluate_digraph.return_value = mock_result

    response = client.post(
        "/api/v1/evaluate/digraph",
        json={
            "institutions": [str(id) for id in inst_ids],
            "analyze_sequences": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "digraph"
    assert "result" in data
    assert data["result"]["dependencies"]["direct"] == 5
    mock_service.evaluate_digraph.assert_called_once_with(
        institutions=inst_ids,
        analyze_sequences=True
    )


def test_evaluate_digraph_no_sequences(client, mock_service):
    """Test digraph evaluation without sequence analysis."""
    inst_ids = [uuid.uuid4()]
    mock_service.evaluate_digraph.return_value = {"dependencies": {"direct": 0}}

    response = client.post(
        "/api/v1/evaluate/digraph",
        json={
            "institutions": [str(inst_ids[0])],
            "analyze_sequences": False
        }
    )

    assert response.status_code == 200
    mock_service.evaluate_digraph.assert_called_once_with(
        institutions=inst_ids,
        analyze_sequences=False
    )


def test_evaluate_circular_causation_success(client, mock_service):
    """Test GET /api/v1/evaluate/circular-causation/{process_id}."""
    process_id = uuid.uuid4()
    mock_result = {
        "feedback_loops": [
            {"type": "reinforcing", "strength": 0.8},
            {"type": "balancing", "strength": 0.6}
        ],
        "cumulative_effect": 0.7
    }
    mock_service.evaluate_circular_causation.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/circular-causation/{process_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "circular_causation"
    assert str(process_id) in data["entity_id"]
    assert data["result"]["cumulative_effect"] == 0.7
    mock_service.evaluate_circular_causation.assert_called_once_with(process_id)


def test_evaluate_conflict_detection_success(client, mock_service):
    """Test GET /api/v1/evaluate/conflict-detection/{system_id}."""
    system_id = uuid.uuid4()
    mock_result = {
        "conflicts": [
            {"type": "value", "severity": 0.8},
            {"type": "resource", "severity": 0.5}
        ],
        "total_conflicts": 2
    }
    mock_service.evaluate_conflict_detection.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/conflict-detection/{system_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "conflict_detection"
    assert str(system_id) in data["entity_id"]
    assert data["result"]["total_conflicts"] == 2
    mock_service.evaluate_conflict_detection.assert_called_once_with(system_id)


def test_evaluate_cross_impact_success(client, mock_service):
    """Test GET /api/v1/evaluate/cross-impact/{cell_id}."""
    cell_id = uuid.uuid4()
    mock_result = {
        "direct_impacts": 3,
        "indirect_impacts": 7,
        "propagation_depth": 4
    }
    mock_service.evaluate_cross_impact.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/cross-impact/{cell_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "cross_impact"
    assert str(cell_id) in data["entity_id"]
    assert data["result"]["propagation_depth"] == 4
    mock_service.evaluate_cross_impact.assert_called_once_with(cell_id)


def test_evaluate_delivery_performance_success(client, mock_service):
    """Test GET /api/v1/evaluate/delivery-performance/{relationship_id}."""
    relationship_id = uuid.uuid4()
    mock_result = {
        "efficiency": 0.85,
        "bottlenecks": ["resource_constraint", "coordination_delay"],
        "throughput": 120
    }
    mock_service.evaluate_delivery_performance.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/delivery-performance/{relationship_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "delivery_performance"
    assert str(relationship_id) in data["entity_id"]
    assert data["result"]["efficiency"] == 0.85
    mock_service.evaluate_delivery_performance.assert_called_once_with(relationship_id)


def test_evaluate_network_performance_success(client, mock_service):
    """Test GET /api/v1/evaluate/network-performance/{network_id}."""
    network_id = uuid.uuid4()
    mock_result = {
        "overall_health": 0.75,
        "throughput": 450,
        "coordination_score": 0.82
    }
    mock_service.evaluate_network_performance.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/network-performance/{network_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "network_performance"
    assert str(network_id) in data["entity_id"]
    assert data["result"]["overall_health"] == 0.75
    mock_service.evaluate_network_performance.assert_called_once_with(network_id)


def test_evaluate_path_dependency_success(client, mock_service):
    """Test GET /api/v1/evaluate/path-dependency/{institution_id}."""
    institution_id = uuid.uuid4()
    mock_result = {
        "lock_in_strength": 0.65,
        "historical_constraints": ["precedent_A", "sunk_cost_B"],
        "flexibility_score": 0.35
    }
    mock_service.evaluate_path_dependency.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/path-dependency/{institution_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "path_dependency"
    assert str(institution_id) in data["entity_id"]
    assert data["result"]["lock_in_strength"] == 0.65
    mock_service.evaluate_path_dependency.assert_called_once_with(institution_id)


def test_evaluate_value_system_success(client, mock_service):
    """Test GET /api/v1/evaluate/value-system/{value_system_id}."""
    value_system_id = uuid.uuid4()
    mock_result = {
        "coherence": 0.88,
        "institutional_alignment": 0.72,
        "stability": 0.90
    }
    mock_service.evaluate_value_system.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/value-system/{value_system_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "value_system"
    assert str(value_system_id) in data["entity_id"]
    assert data["result"]["coherence"] == 0.88
    mock_service.evaluate_value_system.assert_called_once_with(value_system_id)


def test_evaluate_belief_stability_success(client, mock_service):
    """Test GET /api/v1/evaluate/belief-stability/{belief_id}."""
    belief_id = uuid.uuid4()
    mock_result = {
        "stability_score": 0.75,
        "change_potential": 0.25,
        "paradigm_shift_risk": "low"
    }
    mock_service.evaluate_belief_stability.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/belief-stability/{belief_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "belief_stability"
    assert str(belief_id) in data["entity_id"]
    assert data["result"]["stability_score"] == 0.75
    mock_service.evaluate_belief_stability.assert_called_once_with(belief_id)


def test_evaluate_attitude_mediation_success(client, mock_service):
    """Test GET /api/v1/evaluate/attitude-mediation/{attitude_id}."""
    attitude_id = uuid.uuid4()
    mock_result = {
        "mediation_effectiveness": 0.80,
        "belief_to_practice_gap": 0.20,
        "coherence": 0.85
    }
    mock_service.evaluate_attitude_mediation.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/attitude-mediation/{attitude_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "attitude_mediation"
    assert str(attitude_id) in data["entity_id"]
    assert data["result"]["mediation_effectiveness"] == 0.80
    mock_service.evaluate_attitude_mediation.assert_called_once_with(attitude_id)


def test_evaluate_system_holarchy_success(client, mock_service):
    """Test GET /api/v1/evaluate/system-holarchy/{holarchy_id}."""
    holarchy_id = uuid.uuid4()
    mock_result = {
        "coherence_score": 0.78,
        "leverage_points": ["top_institution", "critical_link"],
        "depth": 4
    }
    mock_service.evaluate_system_holarchy.return_value = mock_result

    response = client.get(f"/api/v1/evaluate/system-holarchy/{holarchy_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "system_holarchy"
    assert str(holarchy_id) in data["entity_id"]
    assert data["result"]["coherence_score"] == 0.78
    mock_service.evaluate_system_holarchy.assert_called_once_with(holarchy_id)


def test_evaluate_invalid_uuid(client, mock_service):
    """Test evaluation endpoints reject invalid UUIDs."""
    response = client.get("/api/v1/evaluate/circular-causation/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.integration
def test_evaluate_digraph_integration(integration_client):
    """Test digraph evaluation with real service."""
    # Create some test institutions first would be needed for real test
    # For now, just verify endpoint is accessible
    inst_id = uuid.uuid4()
    response = integration_client.post(
        "/api/v1/evaluate/digraph",
        json={
            "institutions": [str(inst_id)],
            "analyze_sequences": False
        }
    )

    # Should get 200 even with non-existent institutions (evaluation handles gracefully)
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_type"] == "digraph"
    assert "result" in data
