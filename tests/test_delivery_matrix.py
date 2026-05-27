"""
Comprehensive tests for Hayden-compliant delivery matrix model.

Tests cover:
- Square matrix structure validation
- Multiple heterogeneous deliveries per cell
- Cell description requirements
- Component management
- Delivery filtering and aggregation
- Integration with service layer
"""

import pytest
import uuid
from datetime import datetime, timedelta

from models.delivery_matrix import (
    Delivery,
    SFMDeliveryCell,
    SFMDeliveryMatrix,
)
from api.sfm_service import SFMService


class TestDelivery:
    """Test Delivery class."""

    def test_create_basic_delivery(self):
        """Test creating basic delivery."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual appropriation"
        )

        assert delivery.delivery_type == "money"
        assert delivery.delivery_content == "Annual appropriation"
        assert delivery.quantity is None
        assert delivery.units is None

    def test_create_quantified_delivery(self):
        """Test creating delivery with quantity."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="$800M annual appropriation",
            quantity=800_000_000,
            units="USD/year"
        )

        assert delivery.quantity == 800_000_000
        assert delivery.units == "USD/year"

    def test_create_delivery_with_temporal_attributes(self):
        """Test creating delivery with temporal modeling attributes."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
            quantity=550,
            units="million tons/year",
            temporal_rate="annual",
            temporal_clock="fiscal_year",
            threshold=500,
            threshold_direction="above"
        )

        assert delivery.temporal_rate == "annual"
        assert delivery.temporal_clock == "fiscal_year"
        assert delivery.threshold == 500
        assert delivery.threshold_direction == "above"

    def test_delivery_requires_type_and_content(self):
        """Test that delivery_type and delivery_content are required."""
        with pytest.raises(ValueError, match="delivery_type is required"):
            Delivery(delivery_type="", delivery_content="Test")

        with pytest.raises(ValueError, match="delivery_content is required"):
            Delivery(delivery_type="money", delivery_content="")

    def test_delivery_validates_threshold_direction(self):
        """Test threshold_direction validation."""
        with pytest.raises(ValueError, match="threshold_direction must be"):
            Delivery(
                delivery_type="pollution",
                delivery_content="Test",
                threshold_direction="invalid"
            )

        # Valid values should work
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Test",
            threshold_direction="above"
        )
        assert delivery.threshold_direction == "above"

        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Test",
            threshold_direction="below"
        )
        assert delivery.threshold_direction == "below"

    def test_delivery_validates_certainty_range(self):
        """Test certainty validation (0.0-1.0)."""
        with pytest.raises(ValueError, match="certainty must be between"):
            Delivery(
                delivery_type="money",
                delivery_content="Test",
                certainty=1.5
            )

        with pytest.raises(ValueError, match="certainty must be between"):
            Delivery(
                delivery_type="money",
                delivery_content="Test",
                certainty=-0.1
            )

        # Valid certainty
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Test",
            certainty=0.85
        )
        assert delivery.certainty == 0.85


class TestSFMDeliveryCell:
    """Test SFMDeliveryCell class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.source_id = uuid.uuid4()
        self.target_id = uuid.uuid4()

    def test_create_empty_cell(self):
        """Test creating empty cell (no deliveries)."""
        cell = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.source_id,
            target_component_id=self.target_id
        )

        assert cell.source_component_id == self.source_id
        assert cell.target_component_id == self.target_id
        assert len(cell.deliveries) == 0
        assert cell.cell_description == ""

    def test_create_cell_with_delivery_requires_description(self):
        """Test Hayden requirement: non-empty cells require descriptions."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Test delivery"
        )

        # Creating cell with delivery but no description should fail
        with pytest.raises(ValueError, match="Non-empty SFM cells require cell_description"):
            SFMDeliveryCell(
                label="Cell",
                source_component_id=self.source_id,
                target_component_id=self.target_id,
                deliveries=[delivery],
                cell_description=""  # Empty description
            )

    def test_create_cell_with_delivery_and_description(self):
        """Test creating valid non-empty cell."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="$800M annual appropriation"
        )

        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.source_id,
            target_component_id=self.target_id,
            deliveries=[delivery],
            cell_description="Legislature provides funding to school district"
        )

        assert len(cell.deliveries) == 1
        assert cell.cell_description == "Legislature provides funding to school district"

    def test_add_delivery_to_cell(self):
        """Test adding delivery to existing cell."""
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.source_id,
            target_component_id=self.target_id,
            cell_description="Test cell"
        )

        # Add first delivery
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="$800M appropriation"
        )
        cell.add_delivery(delivery1)

        assert len(cell.deliveries) == 1
        assert cell.deliveries[0].delivery_type == "money"

        # Add second delivery (heterogeneous)
        delivery2 = Delivery(
            delivery_type="rule",
            delivery_content="TEEOSA formula requirements"
        )
        cell.add_delivery(delivery2)

        assert len(cell.deliveries) == 2
        assert cell.deliveries[1].delivery_type == "rule"

    def test_add_delivery_without_description_fails(self):
        """Test that adding delivery to cell without description fails."""
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.source_id,
            target_component_id=self.target_id
        )

        delivery = Delivery(
            delivery_type="money",
            delivery_content="Test"
        )

        with pytest.raises(ValueError, match="Cannot add delivery to cell without cell_description"):
            cell.add_delivery(delivery)

    def test_get_deliveries_by_type(self):
        """Test filtering deliveries by type."""
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.source_id,
            target_component_id=self.target_id,
            cell_description="Test cell"
        )

        # Add multiple delivery types
        cell.add_delivery(Delivery(delivery_type="money", delivery_content="Payment 1", quantity=100))
        cell.add_delivery(Delivery(delivery_type="rule", delivery_content="Regulation"))
        cell.add_delivery(Delivery(delivery_type="money", delivery_content="Payment 2", quantity=200))
        cell.add_delivery(Delivery(delivery_type="authority", delivery_content="Audit power"))

        # Filter by type
        money_deliveries = cell.get_deliveries_by_type("money")
        assert len(money_deliveries) == 2
        assert all(d.delivery_type == "money" for d in money_deliveries)

        rule_deliveries = cell.get_deliveries_by_type("rule")
        assert len(rule_deliveries) == 1

        # Non-existent type
        empty = cell.get_deliveries_by_type("nonexistent")
        assert len(empty) == 0

    def test_get_total_quantity_by_type(self):
        """Test summing quantities by delivery type."""
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.source_id,
            target_component_id=self.target_id,
            cell_description="Test cell"
        )

        cell.add_delivery(Delivery(delivery_type="money", delivery_content="Payment 1", quantity=100.5))
        cell.add_delivery(Delivery(delivery_type="money", delivery_content="Payment 2", quantity=200.3))
        cell.add_delivery(Delivery(delivery_type="energy", delivery_content="Power", quantity=50))

        # Sum money deliveries
        total_money = cell.get_total_quantity_by_type("money")
        assert total_money == pytest.approx(300.8)

        # Sum energy
        total_energy = cell.get_total_quantity_by_type("energy")
        assert total_energy == 50

        # Type with no quantities
        total_rule = cell.get_total_quantity_by_type("rule")
        assert total_rule is None


class TestSFMDeliveryMatrix:
    """Test SFMDeliveryMatrix class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.comp_a = uuid.uuid4()
        self.comp_b = uuid.uuid4()
        self.comp_c = uuid.uuid4()

    def test_create_empty_matrix(self):
        """Test creating empty matrix."""
        matrix = SFMDeliveryMatrix(
            label="Test Matrix"
        )

        assert matrix.label == "Test Matrix"
        assert len(matrix.components) == 0
        assert len(matrix.cells) == 0
        assert matrix.is_square()

    def test_add_components(self):
        """Test adding components to matrix."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")

        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)
        matrix.add_component(self.comp_c)

        assert len(matrix.components) == 3
        assert self.comp_a in matrix.components
        assert self.comp_b in matrix.components
        assert self.comp_c in matrix.components

    def test_add_duplicate_component(self):
        """Test that adding duplicate component is ignored."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")

        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_a)  # Duplicate

        assert len(matrix.components) == 1

    def test_remove_component(self):
        """Test removing component from matrix."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")

        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        matrix.remove_component(self.comp_a)

        assert self.comp_a not in matrix.components
        assert self.comp_b in matrix.components

    def test_remove_component_removes_cells(self):
        """Test that removing component removes associated cells."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        # Add cell
        cell = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="Test"
        )
        matrix.set_cell(cell)

        assert len(matrix.cells) == 1

        # Remove component A
        matrix.remove_component(self.comp_a)

        # Cell should be removed
        assert len(matrix.cells) == 0

    def test_set_and_get_cell(self):
        """Test setting and retrieving cells."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        cell = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="A delivers to B"
        )

        matrix.set_cell(cell)

        retrieved_cell = matrix.get_cell(self.comp_a, self.comp_b)
        assert retrieved_cell is not None
        assert retrieved_cell.source_component_id == self.comp_a
        assert retrieved_cell.target_component_id == self.comp_b

    def test_set_cell_validates_components(self):
        """Test that set_cell validates component membership."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        # comp_b not added

        cell = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="Test"
        )

        with pytest.raises(ValueError, match="Target component .* not in matrix"):
            matrix.set_cell(cell)

    def test_matrix_is_non_symmetric(self):
        """Test that matrix is non-symmetric: Cell (i,j) ≠ Cell (j,i)."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        # Set cell (A, B)
        cell_ab = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="A to B"
        )
        matrix.set_cell(cell_ab)

        # Cell (B, A) should be None (independent)
        cell_ba = matrix.get_cell(self.comp_b, self.comp_a)
        assert cell_ba is None

        # Set cell (B, A) with different content
        cell_ba = SFMDeliveryCell(
            label="Cell B→A",
            source_component_id=self.comp_b,
            target_component_id=self.comp_a,
            cell_description="B to A"
        )
        matrix.set_cell(cell_ba)

        # Both cells exist independently
        retrieved_ab = matrix.get_cell(self.comp_a, self.comp_b)
        retrieved_ba = matrix.get_cell(self.comp_b, self.comp_a)

        assert retrieved_ab.cell_description == "A to B"
        assert retrieved_ba.cell_description == "B to A"

    def test_get_non_empty_cells(self):
        """Test retrieving only non-empty cells."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)
        matrix.add_component(self.comp_c)

        # Add cell with deliveries
        cell1 = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="A to B"
        )
        cell1.add_delivery(Delivery(delivery_type="money", delivery_content="Payment"))
        matrix.set_cell(cell1)

        # Add empty cell (no deliveries)
        cell2 = SFMDeliveryCell(
            label="Cell B→C",
            source_component_id=self.comp_b,
            target_component_id=self.comp_c
        )
        matrix.set_cell(cell2)

        non_empty = matrix.get_non_empty_cells()
        assert len(non_empty) == 1
        assert non_empty[0].source_component_id == self.comp_a

    def test_get_component_outgoing_cells(self):
        """Test getting outgoing cells (component as source)."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)
        matrix.add_component(self.comp_c)

        # A → B
        cell1 = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="A to B"
        )
        matrix.set_cell(cell1)

        # A → C
        cell2 = SFMDeliveryCell(
            label="Cell A→C",
            source_component_id=self.comp_a,
            target_component_id=self.comp_c,
            cell_description="A to C"
        )
        matrix.set_cell(cell2)

        # B → A
        cell3 = SFMDeliveryCell(
            label="Cell B→A",
            source_component_id=self.comp_b,
            target_component_id=self.comp_a,
            cell_description="B to A"
        )
        matrix.set_cell(cell3)

        # Get A's outgoing cells
        outgoing = matrix.get_component_outgoing_cells(self.comp_a)
        assert len(outgoing) == 2

        # Get B's outgoing cells
        outgoing_b = matrix.get_component_outgoing_cells(self.comp_b)
        assert len(outgoing_b) == 1

    def test_get_component_incoming_cells(self):
        """Test getting incoming cells (component as target)."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)
        matrix.add_component(self.comp_c)

        # A → B
        cell1 = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="A to B"
        )
        matrix.set_cell(cell1)

        # C → B
        cell2 = SFMDeliveryCell(
            label="Cell C→B",
            source_component_id=self.comp_c,
            target_component_id=self.comp_b,
            cell_description="C to B"
        )
        matrix.set_cell(cell2)

        # Get B's incoming cells
        incoming = matrix.get_component_incoming_cells(self.comp_b)
        assert len(incoming) == 2

    def test_validate_structure(self):
        """Test matrix structure validation."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        # Valid matrix
        errors = matrix.validate_structure()
        assert len(errors) == 0

        # Add cell with deliveries but no description
        cell = SFMDeliveryCell(
            label="Cell A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description=""  # Will be set after to bypass __post_init__
        )
        cell.deliveries.append(Delivery(delivery_type="money", delivery_content="Test"))
        matrix.cells[(self.comp_a, self.comp_b)] = cell  # Bypass set_cell validation

        errors = matrix.validate_structure()
        assert len(errors) > 0
        assert any("no description" in e for e in errors)


class TestSFMServiceDeliveryMatrixIntegration:
    """Test SFMService integration with delivery matrix."""

    def setup_method(self):
        """Set up test service."""
        self.service = SFMService()

        # Create test components
        from models import Node
        self.legislature = Node(label="State Legislature")
        self.school_district = Node(label="School District")
        self.value_system = Node(label="Educational Values")

        self.service.create_node(self.legislature)
        self.service.create_node(self.school_district)
        self.service.create_node(self.value_system)

    def test_create_delivery_matrix_via_service(self):
        """Test creating delivery matrix through service."""
        matrix = self.service.create_delivery_matrix(
            label="Nebraska K-12 Education Finance",
            description="TEEOSA funding delivery system",
            matrix_scope="state"
        )

        assert matrix.label == "Nebraska K-12 Education Finance"
        assert matrix.matrix_scope == "state"
        assert matrix.is_square()

    def test_add_components_and_delivery_to_matrix(self):
        """Test complete workflow: create matrix, add components, add delivery."""
        # Create matrix
        matrix = self.service.create_delivery_matrix(
            label="Test Matrix"
        )

        # Add components
        matrix.add_component(self.legislature.id)
        matrix.add_component(self.school_district.id)

        # Create delivery
        from models.delivery_matrix import Delivery
        delivery = Delivery(
            delivery_type="money",
            delivery_content="$800M annual appropriation via TEEOSA formula",
            quantity=800_000_000,
            units="USD/year",
            temporal_rate="annual"
        )

        # Add delivery via service
        cell = self.service.add_delivery_to_matrix(
            matrix=matrix,
            source_id=self.legislature.id,
            target_id=self.school_district.id,
            delivery=delivery,
            cell_description="Legislature provides TEEOSA funding to school district"
        )

        assert len(cell.deliveries) == 1
        assert cell.deliveries[0].quantity == 800_000_000
        assert cell.cell_description == "Legislature provides TEEOSA funding to school district"

    def test_add_multiple_heterogeneous_deliveries(self):
        """Test Hayden 2008 requirement: multiple heterogeneous deliveries per cell."""
        matrix = self.service.create_delivery_matrix(label="Test Matrix")
        matrix.add_component(self.legislature.id)
        matrix.add_component(self.school_district.id)

        from models.delivery_matrix import Delivery

        # Add money delivery
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="$800M annual appropriation",
            quantity=800_000_000,
            units="USD/year"
        )

        cell = self.service.add_delivery_to_matrix(
            matrix=matrix,
            source_id=self.legislature.id,
            target_id=self.school_district.id,
            delivery=delivery1,
            cell_description="Legislature provides funding and mandates to school district"
        )

        # Add rule delivery to same cell
        delivery2 = Delivery(
            delivery_type="rule",
            delivery_content="TEEOSA formula requirements and compliance mandates"
        )

        cell.add_delivery(delivery2)

        # Add authority delivery
        delivery3 = Delivery(
            delivery_type="authority",
            delivery_content="Audit and oversight power"
        )

        cell.add_delivery(delivery3)

        # Verify multiple heterogeneous deliveries
        assert len(cell.deliveries) == 3
        delivery_types = set(d.delivery_type for d in cell.deliveries)
        assert delivery_types == {"money", "rule", "authority"}

    def test_validate_matrix_via_service(self):
        """Test matrix validation through service."""
        matrix = self.service.create_delivery_matrix(label="Test Matrix")
        matrix.add_component(self.legislature.id)
        matrix.add_component(self.school_district.id)

        # Valid matrix
        errors = self.service.validate_delivery_matrix(matrix)
        assert len(errors) == 0

    def test_validate_matrix_with_invalid_component(self):
        """Test validation catches invalid component references."""
        matrix = self.service.create_delivery_matrix(label="Test Matrix")

        # Add non-existent component
        fake_id = uuid.uuid4()
        matrix.components.append(fake_id)

        errors = self.service.validate_delivery_matrix(matrix)
        assert len(errors) > 0
        assert any("not found in graph" in e for e in errors)
