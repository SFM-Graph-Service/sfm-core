"""Tests for relationship CRUD endpoints."""

import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from api.sfm_service import SFMService, SFMServiceConfig
from graph.sfm_graph import Relationship
from models.base_nodes import Node
from models.exceptions import SFMNotFoundError


class TestRelationshipsRouter:
    """Tests for /api/v1/relationships endpoints."""

    def test_create_relationship_success(self, client, mock_service):
        """Test POST /api/v1/relationships/ creates relationship."""
        # Create mock nodes first
        source_node = Node(label="Source", id=uuid.UUID("12345678-1234-5678-1234-567812345678"))
        target_node = Node(label="Target", id=uuid.UUID("87654321-4321-8765-4321-876543218765"))

        mock_rel = Relationship(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            source_id=source_node.id,
            target_id=target_node.id,
            kind="influences",
            weight=0.8,
            meta={"test": "data"}
        )
        mock_service.create_relationship.return_value = mock_rel

        response = client.post(
            "/api/v1/relationships/",
            json={
                "source_id": str(source_node.id),
                "target_id": str(target_node.id),
                "kind": "influences",
                "weight": 0.8,
                "meta": {"test": "data"}
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source_id"] == str(source_node.id)
        assert data["target_id"] == str(target_node.id)
        assert data["kind"] == "influences"
        assert data["weight"] == 0.8
        mock_service.create_relationship.assert_called_once()

    def test_get_relationship_success(self, client, mock_service):
        """Test GET /api/v1/relationships/{id} returns relationship."""
        rel_id = uuid.uuid4()
        mock_rel = Relationship(
            id=rel_id,
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind="influences",
            weight=0.5,
            meta={}
        )
        mock_service.get_relationship.return_value = mock_rel

        response = client.get(f"/api/v1/relationships/{rel_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(rel_id)
        assert data["kind"] == "influences"

    def test_get_relationship_not_found(self, client, mock_service):
        """Test GET /api/v1/relationships/{id} returns 404."""
        rel_id = uuid.uuid4()
        mock_service.get_relationship.return_value = None

        response = client.get(f"/api/v1/relationships/{rel_id}")

        assert response.status_code == 404

    def test_update_relationship_success(self, client, mock_service):
        """Test PUT /api/v1/relationships/{id} updates relationship."""
        rel_id = uuid.uuid4()
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()

        updated_rel = Relationship(
            id=rel_id,
            source_id=source_id,
            target_id=target_id,
            kind="updated_kind",
            weight=0.9,
            meta={"updated": "true"}
        )
        mock_service.update_relationship.return_value = updated_rel

        response = client.put(
            f"/api/v1/relationships/{rel_id}",
            json={
                "source_id": str(source_id),
                "target_id": str(target_id),
                "kind": "updated_kind",
                "weight": 0.9,
                "meta": {"updated": "true"}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["kind"] == "updated_kind"
        assert data["weight"] == 0.9

    def test_delete_relationship_success(self, client, mock_service):
        """Test DELETE /api/v1/relationships/{id} deletes relationship."""
        rel_id = uuid.uuid4()
        mock_service.delete_relationship.return_value = True

        response = client.delete(f"/api/v1/relationships/{rel_id}")

        assert response.status_code == 204
        mock_service.delete_relationship.assert_called_once_with(rel_id)

    def test_delete_relationship_not_found(self, client, mock_service):
        """Test DELETE /api/v1/relationships/{id} returns 404."""
        rel_id = uuid.uuid4()
        mock_service.delete_relationship.return_value = False

        response = client.delete(f"/api/v1/relationships/{rel_id}")

        assert response.status_code == 404

    def test_list_relationships_all(self, client, mock_service):
        """Test GET /api/v1/relationships/ lists all relationships."""
        mock_rels = [
            Relationship(id=uuid.uuid4(), source_id=uuid.uuid4(), target_id=uuid.uuid4(), kind="influences"),
            Relationship(id=uuid.uuid4(), source_id=uuid.uuid4(), target_id=uuid.uuid4(), kind="depends_on"),
        ]
        mock_service.list_relationships.return_value = mock_rels

        response = client.get("/api/v1/relationships/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["relationships"]) == 2

    def test_list_relationships_filtered_by_kind(self, client, mock_service):
        """Test GET /api/v1/relationships/?kind=influences filters by kind."""
        mock_rels = [
            Relationship(id=uuid.uuid4(), source_id=uuid.uuid4(), target_id=uuid.uuid4(), kind="influences"),
        ]
        mock_service.find_relationships.return_value = mock_rels

        response = client.get("/api/v1/relationships/?kind=influences")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["relationships"][0]["kind"] == "influences"

    def test_list_relationships_filtered_by_source(self, client, mock_service):
        """Test GET /api/v1/relationships/?source_id=... filters by source."""
        source_id = uuid.uuid4()
        mock_rels = [
            Relationship(id=uuid.uuid4(), source_id=source_id, target_id=uuid.uuid4(), kind="influences"),
        ]
        mock_service.find_relationships.return_value = mock_rels

        response = client.get(f"/api/v1/relationships/?source_id={source_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_list_relationships_filtered_by_target(self, client, mock_service):
        """Test GET /api/v1/relationships/?target_id=... filters by target."""
        target_id = uuid.uuid4()
        mock_rels = [
            Relationship(id=uuid.uuid4(), source_id=uuid.uuid4(), target_id=target_id, kind="influences"),
        ]
        mock_service.find_relationships.return_value = mock_rels

        response = client.get(f"/api/v1/relationships/?target_id={target_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


@pytest.mark.integration
class TestRelationshipsIntegration:
    """Integration tests for relationships API with real service."""

    def test_relationship_crud_flow(self, integration_client, integration_app):
        """Test complete CRUD flow with real service."""
        # First create two nodes
        node1_response = integration_client.post(
            "/api/v1/nodes/",
            json={"label": "Node 1", "node_type": "Node"}
        )
        assert node1_response.status_code == 201
        node1_id = node1_response.json()["id"]

        node2_response = integration_client.post(
            "/api/v1/nodes/",
            json={"label": "Node 2", "node_type": "Node"}
        )
        assert node2_response.status_code == 201
        node2_id = node2_response.json()["id"]

        # Create relationship
        create_response = integration_client.post(
            "/api/v1/relationships/",
            json={
                "source_id": node1_id,
                "target_id": node2_id,
                "kind": "influences",
                "weight": 0.7,
                "meta": {"test": "data"}
            }
        )
        assert create_response.status_code == 201
        rel_id = create_response.json()["id"]

        # Read relationship
        get_response = integration_client.get(f"/api/v1/relationships/{rel_id}")
        assert get_response.status_code == 200
        assert get_response.json()["kind"] == "influences"
        assert get_response.json()["weight"] == 0.7

        # Update relationship
        update_response = integration_client.put(
            f"/api/v1/relationships/{rel_id}",
            json={
                "source_id": node1_id,
                "target_id": node2_id,
                "kind": "depends_on",
                "weight": 0.9,
                "meta": {"updated": "true"}
            }
        )
        assert update_response.status_code == 200
        assert update_response.json()["kind"] == "depends_on"
        assert update_response.json()["weight"] == 0.9

        # List relationships
        list_response = integration_client.get("/api/v1/relationships/")
        assert list_response.status_code == 200
        assert list_response.json()["total"] >= 1

        # Delete relationship
        delete_response = integration_client.delete(f"/api/v1/relationships/{rel_id}")
        assert delete_response.status_code == 204

        # Verify deleted
        get_deleted_response = integration_client.get(f"/api/v1/relationships/{rel_id}")
        assert get_deleted_response.status_code == 404

    def test_relationship_filtering(self, integration_client):
        """Test relationship filtering by source, target, and kind."""
        # Create nodes
        node1 = integration_client.post("/api/v1/nodes/", json={"label": "N1", "node_type": "Node"})
        node2 = integration_client.post("/api/v1/nodes/", json={"label": "N2", "node_type": "Node"})
        node3 = integration_client.post("/api/v1/nodes/", json={"label": "N3", "node_type": "Node"})

        n1_id = node1.json()["id"]
        n2_id = node2.json()["id"]
        n3_id = node3.json()["id"]

        # Create relationships
        integration_client.post("/api/v1/relationships/", json={
            "source_id": n1_id, "target_id": n2_id, "kind": "influences"
        })
        integration_client.post("/api/v1/relationships/", json={
            "source_id": n1_id, "target_id": n3_id, "kind": "depends_on"
        })
        integration_client.post("/api/v1/relationships/", json={
            "source_id": n2_id, "target_id": n3_id, "kind": "influences"
        })

        # Filter by source
        response = integration_client.get(f"/api/v1/relationships/?source_id={n1_id}")
        assert response.status_code == 200
        assert response.json()["total"] == 2

        # Filter by target
        response = integration_client.get(f"/api/v1/relationships/?target_id={n3_id}")
        assert response.status_code == 200
        assert response.json()["total"] == 2

        # Filter by kind
        response = integration_client.get("/api/v1/relationships/?kind=influences")
        assert response.status_code == 200
        # Should have at least 2 relationships with kind "influences"
        assert response.json()["total"] >= 2
