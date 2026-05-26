"""Tests for node CRUD endpoints."""

import uuid
import pytest
from models.base_nodes import Node
from models.exceptions import SFMNotFoundError


def test_create_node_success(client, mock_service):
    """Test POST /api/v1/nodes/ creates node."""
    mock_node = Node(label="Test Node", description="Test description")
    mock_service.create_node.return_value = mock_node

    response = client.post(
        "/api/v1/nodes/",
        json={
            "label": "Test Node",
            "description": "Test description",
            "node_type": "Node"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["label"] == "Test Node"
    assert data["description"] == "Test description"
    assert "id" in data
    assert "created_at" in data
    mock_service.create_node.assert_called_once()


def test_create_node_with_meta(client, mock_service):
    """Test creating node with metadata."""
    mock_node = Node(
        label="Test Node",
        meta={"source": "test", "year": "2024"}
    )
    mock_service.create_node.return_value = mock_node

    response = client.post(
        "/api/v1/nodes/",
        json={
            "label": "Test Node",
            "node_type": "Node",
            "meta": {"source": "test", "year": "2024"}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["meta"]["source"] == "test"
    assert data["meta"]["year"] == "2024"


def test_get_node_success(client, mock_service):
    """Test GET /api/v1/nodes/{id} returns node."""
    node_id = uuid.uuid4()
    mock_node = Node(label="Test Node")
    mock_node.id = node_id
    mock_service.get_node.return_value = mock_node

    response = client.get(f"/api/v1/nodes/{node_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "Test Node"
    assert uuid.UUID(data["id"]) == node_id
    mock_service.get_node.assert_called_once_with(node_id)


def test_get_node_not_found(client, mock_service):
    """Test GET /api/v1/nodes/{id} returns 404 when node doesn't exist."""
    node_id = uuid.uuid4()
    mock_service.get_node.return_value = None

    response = client.get(f"/api/v1/nodes/{node_id}")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NOT_FOUND_ERROR"
    assert "Node" in data["message"]


def test_update_node_success(client, mock_service):
    """Test PUT /api/v1/nodes/{id} updates node."""
    node_id = uuid.uuid4()
    mock_node = Node(label="Updated Node")
    mock_node.id = node_id
    mock_service.update_node.return_value = mock_node

    response = client.put(
        f"/api/v1/nodes/{node_id}",
        json={
            "label": "Updated Node",
            "description": "Updated description",
            "node_type": "Node"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "Updated Node"
    assert uuid.UUID(data["id"]) == node_id
    mock_service.update_node.assert_called_once()


def test_update_node_not_found(client, mock_service):
    """Test PUT /api/v1/nodes/{id} returns 404 when node doesn't exist."""
    node_id = uuid.uuid4()
    mock_service.update_node.side_effect = SFMNotFoundError(
        entity_type="Node",
        entity_id=node_id
    )

    response = client.put(
        f"/api/v1/nodes/{node_id}",
        json={"label": "Updated", "node_type": "Node"}
    )

    assert response.status_code == 404


def test_delete_node_success(client, mock_service):
    """Test DELETE /api/v1/nodes/{id} deletes node."""
    node_id = uuid.uuid4()
    mock_service.delete_node.return_value = True

    response = client.delete(f"/api/v1/nodes/{node_id}")

    assert response.status_code == 204
    mock_service.delete_node.assert_called_once_with(node_id)


def test_delete_node_not_found(client, mock_service):
    """Test DELETE /api/v1/nodes/{id} returns 404 when node doesn't exist."""
    node_id = uuid.uuid4()
    mock_service.delete_node.return_value = False

    response = client.delete(f"/api/v1/nodes/{node_id}")

    assert response.status_code == 404


def test_list_nodes_success(client, mock_service):
    """Test GET /api/v1/nodes/ lists all nodes."""
    nodes = [
        Node(label="Node 1"),
        Node(label="Node 2"),
        Node(label="Node 3")
    ]
    mock_service.list_nodes.return_value = nodes

    response = client.get("/api/v1/nodes/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["nodes"]) == 3
    assert data["nodes"][0]["label"] == "Node 1"
    assert data["nodes"][1]["label"] == "Node 2"
    assert data["nodes"][2]["label"] == "Node 3"


def test_list_nodes_empty(client, mock_service):
    """Test GET /api/v1/nodes/ returns empty list when no nodes."""
    mock_service.list_nodes.return_value = []

    response = client.get("/api/v1/nodes/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["nodes"]) == 0


def test_clear_all_data_success(client, mock_service):
    """Test DELETE /api/v1/nodes/clear deletes all data."""
    mock_service.clear_all_data.return_value = {
        "status": "success",
        "message": "All data cleared"
    }

    response = client.delete("/api/v1/nodes/clear")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    mock_service.clear_all_data.assert_called_once()


@pytest.mark.integration
def test_node_crud_flow_integration(integration_client):
    """Test complete CRUD flow with real service."""
    # Create
    create_response = integration_client.post(
        "/api/v1/nodes/",
        json={
            "label": "Integration Test Node",
            "description": "Test node for integration testing",
            "node_type": "Node"
        }
    )
    assert create_response.status_code == 201
    node_id = create_response.json()["id"]

    # Read
    get_response = integration_client.get(f"/api/v1/nodes/{node_id}")
    assert get_response.status_code == 200
    assert get_response.json()["label"] == "Integration Test Node"

    # Update
    update_response = integration_client.put(
        f"/api/v1/nodes/{node_id}",
        json={
            "label": "Updated Integration Test Node",
            "description": "Updated description",
            "node_type": "Node"
        }
    )
    assert update_response.status_code == 200
    assert update_response.json()["label"] == "Updated Integration Test Node"

    # List (should contain our node)
    list_response = integration_client.get("/api/v1/nodes/")
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # Delete
    delete_response = integration_client.delete(f"/api/v1/nodes/{node_id}")
    assert delete_response.status_code == 204

    # Verify deleted
    get_after_delete = integration_client.get(f"/api/v1/nodes/{node_id}")
    assert get_after_delete.status_code == 404


# Node Types Registry Tests


def test_list_node_types_basic(client):
    """Test GET /api/v1/nodes/types returns all node types."""
    response = client.get("/api/v1/nodes/types")

    assert response.status_code == 200
    data = response.json()
    assert "node_types" in data
    assert "total" in data
    assert isinstance(data["node_types"], list)
    assert data["total"] == len(data["node_types"])
    assert data["total"] > 30  # We have ~40 node types
    assert "Node" in data["node_types"]  # Base type should be included
    assert data["by_domain"] is None  # Not included by default


def test_list_node_types_with_domains(client):
    """Test GET /api/v1/nodes/types?include_domains=true."""
    response = client.get("/api/v1/nodes/types?include_domains=true")

    assert response.status_code == 200
    data = response.json()
    assert "node_types" in data
    assert "total" in data
    assert "by_domain" in data
    assert isinstance(data["by_domain"], dict)

    # Check domain structure
    assert "base" in data["by_domain"]
    assert "Node" in data["by_domain"]["base"]
    assert "policy_framework" in data["by_domain"]
    assert len(data["by_domain"]) > 10  # Should have 14 domains


def test_list_nodes_with_invalid_type(client, mock_service):
    """Test GET /api/v1/nodes/?node_type=InvalidType returns 400."""
    mock_service.list_nodes.return_value = []

    response = client.get("/api/v1/nodes/?node_type=InvalidType")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["error"] == "VALIDATION_ERROR"
    assert "InvalidType" in data["detail"]["message"]
    assert "invalid_type" in data["detail"]["context"]
    assert data["detail"]["context"]["invalid_type"] == "InvalidType"
    assert "valid_types_sample" in data["detail"]["context"]
    assert "remediation" in data["detail"]


def test_list_nodes_with_valid_type(client, mock_service):
    """Test GET /api/v1/nodes/?node_type=Node filters correctly."""
    from api.rest.node_registry import ALL_NODE_TYPES

    # Verify Node is in registry
    assert "Node" in ALL_NODE_TYPES

    # Mock service returns mixed node types
    mock_nodes = [
        Node(label="Base Node 1"),
        Node(label="Base Node 2"),
    ]
    mock_service.list_nodes.return_value = mock_nodes

    response = client.get("/api/v1/nodes/?node_type=Node")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["nodes"]) == 2
    # All returned nodes should have node_type == "Node"
    for node in data["nodes"]:
        assert node["node_type"] == "Node"


@pytest.mark.integration
def test_node_types_integration(integration_client):
    """Test node types endpoint with real service."""
    response = integration_client.get("/api/v1/nodes/types?include_domains=true")

    assert response.status_code == 200
    data = response.json()

    # Verify expected types are present
    expected_types = [
        "Node",
        "PolicyInstrument",
        "ValueSystem",
        "TransactionCost",
        "InstitutionalStructure",
    ]
    for expected_type in expected_types:
        assert expected_type in data["node_types"]

    # Verify domains are populated
    assert len(data["by_domain"]) == 14  # 14 domain modules
    assert "base" in data["by_domain"]
    assert "policy_framework" in data["by_domain"]
