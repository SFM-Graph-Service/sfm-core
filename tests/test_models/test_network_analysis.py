"""
Unit tests for network_analysis module.
"""

import pytest
from uuid import uuid4
from models.network_analysis import (
    CrossImpactAnalysis,
    DeliveryRelationship,
    MatrixDeliveryNetwork,
)
from models.sfm_enums import CrossImpactType


class TestCrossImpactAnalysis:
    """Test suite for CrossImpactAnalysis class."""

    def test_cross_impact_instantiation(self):
        """Test basic CrossImpactAnalysis creation."""
        analysis = CrossImpactAnalysis(primary_cell_id=uuid4(), label="Test Analysis")
        assert analysis.label == "Test Analysis"

    def test_impact_with_source(self):
        """Test CrossImpactAnalysis with source entity."""
        cell_id = uuid4()
        analysis = CrossImpactAnalysis(
            primary_cell_id=cell_id,
            label="Sourced",
            description="Source entity analysis",
        )
        assert analysis.description == "Source entity analysis"

    def test_impact_with_magnitude(self):
        """Test CrossImpactAnalysis with impact magnitude."""
        analysis = CrossImpactAnalysis(
            primary_cell_id=uuid4(),
            label="Magnitude",
            impacted_cells={"cell1": 0.75},
        )
        assert "cell1" in analysis.impacted_cells

    def test_impact_complete(self):
        """Test CrossImpactAnalysis with all fields."""
        cell_id = uuid4()
        analysis = CrossImpactAnalysis(
            primary_cell_id=cell_id,
            label="Complete",
            description="Full impact analysis",
            impacted_cells={"cell1": 0.8, "cell2": 0.5},
            impact_type=CrossImpactType.INDIRECT,
        )
        assert analysis.label == "Complete"


class TestDeliveryRelationship:
    """Test suite for DeliveryRelationship class."""

    def test_delivery_instantiation(self):
        """Test basic DeliveryRelationship creation."""
        delivery = DeliveryRelationship(label="Test Delivery")
        assert delivery.label == "Test Delivery"

    def test_delivery_with_provider(self):
        """Test DeliveryRelationship with provider."""
        provider_id = uuid4()
        delivery = DeliveryRelationship(
            label="Provided",
            source_component_id=provider_id,
        )
        assert delivery.source_component_id == provider_id

    def test_delivery_with_recipient(self):
        """Test DeliveryRelationship with recipient."""
        recipient_id = uuid4()
        delivery = DeliveryRelationship(
            label="Received",
            target_component_id=recipient_id,
        )
        assert delivery.target_component_id == recipient_id

    def test_delivery_with_flow(self):
        """Test DeliveryRelationship with flow description."""
        delivery = DeliveryRelationship(
            label="Flowing",
            delivery_type="service",
        )
        assert delivery.delivery_type == "service"

    def test_delivery_complete(self):
        """Test DeliveryRelationship with all fields."""
        provider_id = uuid4()
        recipient_id = uuid4()
        delivery = DeliveryRelationship(
            label="Complete",
            description="Full delivery relationship",
            source_component_id=provider_id,
            target_component_id=recipient_id,
            delivery_type="resource",
        )
        assert delivery.label == "Complete"


class TestMatrixDeliveryNetwork:
    """Test suite for MatrixDeliveryNetwork class."""

    def test_network_instantiation(self):
        """Test basic MatrixDeliveryNetwork creation."""
        network = MatrixDeliveryNetwork(label="Test Network")
        assert network.label == "Test Network"

    def test_network_with_metrics(self):
        """Test MatrixDeliveryNetwork with network metrics."""
        network = MatrixDeliveryNetwork(
            label="Measured",
            network_density=0.65,
        )
        assert network.network_density == 0.65

    def test_network_complete(self):
        """Test MatrixDeliveryNetwork with all fields."""
        network = MatrixDeliveryNetwork(
            label="Complete",
            description="Full network",
            network_scope="regional",
            network_density=0.75,
            network_centralization=0.45,
        )
        assert network.label == "Complete"
