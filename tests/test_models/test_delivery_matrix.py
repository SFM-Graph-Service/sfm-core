"""
Unit tests for delivery_matrix module (models layer).

Covers:
- Matrix Structure Tests (10 tests): Square matrix creation, component management,
  non-symmetric validation, empty matrix handling
- Delivery Tests (10 tests): Single/multiple heterogeneous deliveries, type validation,
  temporal rates, threshold monitoring
- Cell Description Tests (5 tests): Required for non-empty cells, validation errors,
  persistence across updates
- Service Method Tests (5+ tests): create_delivery_matrix, add_delivery_to_matrix,
  validate_delivery_matrix, integration tests
"""

import pytest
import uuid
from datetime import datetime

from models.delivery_matrix import (
    Delivery,
    SFMDeliveryCell,
    SFMDeliveryMatrix,
)
from api.sfm_service import SFMService


# ---------------------------------------------------------------------------
# Matrix Structure Tests (10 tests)
# ---------------------------------------------------------------------------

class TestMatrixStructure:
    """Matrix structure tests per Hayden's N×N square matrix requirement."""

    def setup_method(self):
        self.comp_a = uuid.uuid4()
        self.comp_b = uuid.uuid4()
        self.comp_c = uuid.uuid4()

    def test_create_empty_square_matrix(self):
        """Empty matrix is always square (0×0 is still square)."""
        matrix = SFMDeliveryMatrix(label="Empty Matrix")
        assert matrix.is_square()
        assert len(matrix.components) == 0
        assert len(matrix.cells) == 0

    def test_create_matrix_with_initial_components(self):
        """Matrix can be initialised with a component list."""
        matrix = SFMDeliveryMatrix(
            label="Pre-populated Matrix",
            components=[self.comp_a, self.comp_b]
        )
        assert len(matrix.components) == 2
        assert self.comp_a in matrix.components
        assert self.comp_b in matrix.components

    def test_add_component_to_both_axes(self):
        """Adding a component places it on both the row and column axis."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)
        matrix.add_component(self.comp_c)

        assert len(matrix.components) == 3
        # All three are available as both rows and columns
        for comp in (self.comp_a, self.comp_b, self.comp_c):
            assert comp in matrix.components

    def test_duplicate_component_is_ignored(self):
        """Adding the same component twice does not duplicate it."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_a)  # duplicate
        assert len(matrix.components) == 1

    def test_remove_component_from_matrix(self):
        """Removing a component deletes it from the component list."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        matrix.remove_component(self.comp_a)

        assert self.comp_a not in matrix.components
        assert self.comp_b in matrix.components

    def test_remove_component_removes_associated_cells(self):
        """Removing a component also removes every cell that references it."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)
        matrix.add_component(self.comp_c)

        # Create two cells involving comp_a
        for tgt in (self.comp_b, self.comp_c):
            cell = SFMDeliveryCell(
                label=f"Cell A→{tgt}",
                source_component_id=self.comp_a,
                target_component_id=tgt,
                cell_description="Test cell"
            )
            matrix.set_cell(cell)

        # And one cell not involving comp_a
        cell_bc = SFMDeliveryCell(
            label="Cell B→C",
            source_component_id=self.comp_b,
            target_component_id=self.comp_c,
            cell_description="B to C"
        )
        matrix.set_cell(cell_bc)

        assert len(matrix.cells) == 3

        matrix.remove_component(self.comp_a)

        # Only the B→C cell should survive
        assert len(matrix.cells) == 1
        assert matrix.get_cell(self.comp_b, self.comp_c) is not None

    def test_matrix_is_always_square(self):
        """is_square() always returns True (square by design)."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        for _ in range(5):
            matrix.add_component(uuid.uuid4())
        assert matrix.is_square()

    def test_non_symmetric_cells(self):
        """Cell (i,j) and Cell (j,i) are independent — matrix is non-symmetric."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)
        matrix.add_component(self.comp_b)

        cell_ab = SFMDeliveryCell(
            label="A→B",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,
            cell_description="A delivers to B"
        )
        matrix.set_cell(cell_ab)

        # Reverse cell must be absent
        assert matrix.get_cell(self.comp_b, self.comp_a) is None

        cell_ba = SFMDeliveryCell(
            label="B→A",
            source_component_id=self.comp_b,
            target_component_id=self.comp_a,
            cell_description="B delivers to A"
        )
        matrix.set_cell(cell_ba)

        # Both cells exist independently
        assert matrix.get_cell(self.comp_a, self.comp_b).cell_description == "A delivers to B"
        assert matrix.get_cell(self.comp_b, self.comp_a).cell_description == "B delivers to A"

    def test_set_cell_rejects_unknown_source(self):
        """set_cell raises ValueError when source component is not in matrix."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_b)  # Only comp_b is registered

        cell = SFMDeliveryCell(
            label="Bad cell",
            source_component_id=self.comp_a,  # comp_a not in matrix
            target_component_id=self.comp_b,
            cell_description="Should fail"
        )
        with pytest.raises(ValueError, match="Source component .* not in matrix"):
            matrix.set_cell(cell)

    def test_set_cell_rejects_unknown_target(self):
        """set_cell raises ValueError when target component is not in matrix."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        matrix.add_component(self.comp_a)

        cell = SFMDeliveryCell(
            label="Bad cell",
            source_component_id=self.comp_a,
            target_component_id=self.comp_b,  # comp_b not in matrix
            cell_description="Should fail"
        )
        with pytest.raises(ValueError, match="Target component .* not in matrix"):
            matrix.set_cell(cell)


# ---------------------------------------------------------------------------
# Delivery Tests (10 tests)
# ---------------------------------------------------------------------------

class TestDelivery:
    """Tests for the Delivery dataclass."""

    def test_create_minimal_delivery(self):
        """Delivery can be created with just type and content."""
        d = Delivery(delivery_type="money", delivery_content="Annual grant")
        assert d.delivery_type == "money"
        assert d.delivery_content == "Annual grant"
        assert d.quantity is None
        assert d.units is None

    def test_create_quantified_delivery(self):
        """Delivery can carry numeric quantity and units."""
        d = Delivery(
            delivery_type="money",
            delivery_content="TEEOSA appropriation",
            quantity=800_000_000,
            units="USD/year"
        )
        assert d.quantity == 800_000_000
        assert d.units == "USD/year"

    def test_delivery_type_required(self):
        """Empty delivery_type raises ValueError."""
        with pytest.raises(ValueError, match="delivery_type is required"):
            Delivery(delivery_type="", delivery_content="Test")

    def test_delivery_content_required(self):
        """Empty delivery_content raises ValueError."""
        with pytest.raises(ValueError, match="delivery_content is required"):
            Delivery(delivery_type="money", delivery_content="")

    def test_multiple_heterogeneous_deliveries_in_cell(self):
        """A single cell supports multiple deliveries of different types per Hayden 2008."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=src,
            target_component_id=tgt,
            cell_description="Multi-type deliveries"
        )
        for dtype, content in [
            ("money", "Appropriation"),
            ("rule", "Compliance mandate"),
            ("authority", "Oversight power"),
            ("information", "Reporting data"),
        ]:
            cell.add_delivery(Delivery(delivery_type=dtype, delivery_content=content))

        assert len(cell.deliveries) == 4
        types = {d.delivery_type for d in cell.deliveries}
        assert types == {"money", "rule", "authority", "information"}

    def test_temporal_rate_stored(self):
        """Delivery stores temporal_rate for Hayden 1987/1993 modeling."""
        d = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
            temporal_rate="annual",
            temporal_clock="fiscal_year"
        )
        assert d.temporal_rate == "annual"
        assert d.temporal_clock == "fiscal_year"

    def test_threshold_direction_above(self):
        """Threshold direction 'above' is accepted."""
        d = Delivery(
            delivery_type="pollution",
            delivery_content="CO2",
            threshold=500,
            threshold_direction="above"
        )
        assert d.threshold == 500
        assert d.threshold_direction == "above"

    def test_threshold_direction_below(self):
        """Threshold direction 'below' is accepted."""
        d = Delivery(
            delivery_type="water",
            delivery_content="River flow",
            threshold=10.0,
            threshold_direction="below"
        )
        assert d.threshold_direction == "below"

    def test_invalid_threshold_direction_rejected(self):
        """Invalid threshold_direction raises ValueError."""
        with pytest.raises(ValueError, match="threshold_direction must be"):
            Delivery(
                delivery_type="pollution",
                delivery_content="Test",
                threshold_direction="sideways"
            )

    def test_certainty_range_valid(self):
        """Certainty accepts values in [0.0, 1.0]."""
        d = Delivery(delivery_type="money", delivery_content="Test", certainty=0.75)
        assert d.certainty == 0.75

    def test_certainty_out_of_range_rejected(self):
        """Certainty outside [0.0, 1.0] raises ValueError."""
        with pytest.raises(ValueError, match="certainty must be between"):
            Delivery(delivery_type="money", delivery_content="Test", certainty=1.1)


# ---------------------------------------------------------------------------
# Cell Description Tests (5 tests)
# ---------------------------------------------------------------------------

class TestCellDescription:
    """Tests for the cell description requirement per Hayden methodology."""

    def setup_method(self):
        self.src = uuid.uuid4()
        self.tgt = uuid.uuid4()

    def test_empty_cell_does_not_require_description(self):
        """An empty cell (no deliveries) may have an empty description."""
        cell = SFMDeliveryCell(
            label="Empty",
            source_component_id=self.src,
            target_component_id=self.tgt
        )
        assert cell.cell_description == ""
        assert len(cell.deliveries) == 0

    def test_non_empty_cell_requires_description_at_construction(self):
        """Creating a non-empty cell without a description raises ValueError."""
        delivery = Delivery(delivery_type="money", delivery_content="Grant")
        with pytest.raises(ValueError, match="Non-empty SFM cells require cell_description"):
            SFMDeliveryCell(
                label="Bad",
                source_component_id=self.src,
                target_component_id=self.tgt,
                deliveries=[delivery],
                cell_description=""
            )

    def test_add_delivery_to_cell_without_description_fails(self):
        """add_delivery raises ValueError when no description is set."""
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.src,
            target_component_id=self.tgt
        )
        with pytest.raises(ValueError, match="Cannot add delivery to cell without cell_description"):
            cell.add_delivery(Delivery(delivery_type="money", delivery_content="Grant"))

    def test_description_persists_after_multiple_deliveries(self):
        """Cell description is unchanged after multiple deliveries are added."""
        description = "Legislature funds school district via TEEOSA"
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=self.src,
            target_component_id=self.tgt,
            cell_description=description
        )
        for i in range(3):
            cell.add_delivery(
                Delivery(delivery_type="money", delivery_content=f"Payment {i}")
            )
        assert cell.cell_description == description

    def test_validate_structure_reports_missing_description(self):
        """validate_structure() flags a cell that has deliveries but no description."""
        matrix = SFMDeliveryMatrix(label="Test Matrix")
        comp_a, comp_b = uuid.uuid4(), uuid.uuid4()
        matrix.add_component(comp_a)
        matrix.add_component(comp_b)

        # Bypass add_delivery guard by directly manipulating cell internals
        cell = SFMDeliveryCell(
            label="Cell",
            source_component_id=comp_a,
            target_component_id=comp_b,
            cell_description=""
        )
        # Force a delivery without going through add_delivery()
        cell.deliveries.append(Delivery(delivery_type="money", delivery_content="Grant"))
        # Bypass set_cell validation too
        matrix.cells[(comp_a, comp_b)] = cell

        errors = matrix.validate_structure()
        assert any("no description" in e for e in errors)


# ---------------------------------------------------------------------------
# Service Method Tests (5+ tests)
# ---------------------------------------------------------------------------

class TestServiceMethods:
    """Integration tests for delivery matrix service layer methods."""

    def setup_method(self):
        self.service = SFMService()

        # Create nodes to act as matrix components
        from models import Node
        self.node_a = Node(label="Component A")
        self.node_b = Node(label="Component B")
        self.node_c = Node(label="Component C")
        for node in (self.node_a, self.node_b, self.node_c):
            self.service.create_node(node)

    # --- create_delivery_matrix ---

    def test_create_delivery_matrix_default_parameters(self):
        """create_delivery_matrix returns a valid SFMDeliveryMatrix with defaults."""
        matrix = self.service.create_delivery_matrix()
        assert isinstance(matrix, SFMDeliveryMatrix)
        assert matrix.is_square()
        assert len(matrix.components) == 0

    def test_create_delivery_matrix_with_label_and_scope(self):
        """create_delivery_matrix accepts label, description, and matrix_scope."""
        matrix = self.service.create_delivery_matrix(
            label="Nebraska K-12 Finance",
            description="TEEOSA funding model",
            matrix_scope="state"
        )
        assert matrix.label == "Nebraska K-12 Finance"
        assert matrix.description == "TEEOSA funding model"
        assert matrix.matrix_scope == "state"

    def test_create_delivery_matrix_with_preset_components(self):
        """create_delivery_matrix accepts an initial component list."""
        matrix = self.service.create_delivery_matrix(
            label="Pre-populated",
            components=[self.node_a.id, self.node_b.id]
        )
        assert self.node_a.id in matrix.components
        assert self.node_b.id in matrix.components

    def test_create_delivery_matrix_with_explicit_id(self):
        """create_delivery_matrix uses the supplied UUID when provided."""
        fixed_id = uuid.uuid4()
        matrix = self.service.create_delivery_matrix(
            matrix_id=fixed_id,
            label="Fixed ID Matrix"
        )
        assert matrix.id == fixed_id

    # --- add_delivery_to_matrix ---

    def test_add_delivery_creates_cell_when_absent(self):
        """add_delivery_to_matrix creates a new cell if one does not exist."""
        matrix = self.service.create_delivery_matrix(label="Test")
        matrix.add_component(self.node_a.id)
        matrix.add_component(self.node_b.id)

        delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual appropriation",
            quantity=500_000,
            units="USD"
        )

        cell = self.service.add_delivery_to_matrix(
            matrix=matrix,
            source_id=self.node_a.id,
            target_id=self.node_b.id,
            delivery=delivery,
            cell_description="A funds B annually"
        )

        assert cell is not None
        assert len(cell.deliveries) == 1
        assert cell.deliveries[0].delivery_type == "money"
        assert cell.cell_description == "A funds B annually"

    def test_add_delivery_appends_to_existing_cell(self):
        """Calling add_delivery_to_matrix twice on the same cell appends deliveries."""
        matrix = self.service.create_delivery_matrix(label="Test")
        matrix.add_component(self.node_a.id)
        matrix.add_component(self.node_b.id)

        for dtype, content in [("money", "Grant"), ("rule", "Mandate")]:
            self.service.add_delivery_to_matrix(
                matrix=matrix,
                source_id=self.node_a.id,
                target_id=self.node_b.id,
                delivery=Delivery(delivery_type=dtype, delivery_content=content),
                cell_description="A provides to B"
            )

        cell = matrix.get_cell(self.node_a.id, self.node_b.id)
        assert len(cell.deliveries) == 2
        assert {d.delivery_type for d in cell.deliveries} == {"money", "rule"}

    def test_add_delivery_rejects_source_not_in_matrix(self):
        """add_delivery_to_matrix raises ValueError for unregistered source."""
        matrix = self.service.create_delivery_matrix(label="Test")
        matrix.add_component(self.node_b.id)

        with pytest.raises(ValueError, match="Source component .* not in matrix"):
            self.service.add_delivery_to_matrix(
                matrix=matrix,
                source_id=self.node_a.id,  # not registered
                target_id=self.node_b.id,
                delivery=Delivery(delivery_type="money", delivery_content="Grant"),
                cell_description="Should fail"
            )

    def test_add_delivery_rejects_empty_cell_description(self):
        """add_delivery_to_matrix raises ValueError when cell_description is empty."""
        matrix = self.service.create_delivery_matrix(label="Test")
        matrix.add_component(self.node_a.id)
        matrix.add_component(self.node_b.id)

        with pytest.raises(ValueError, match="cell_description is required"):
            self.service.add_delivery_to_matrix(
                matrix=matrix,
                source_id=self.node_a.id,
                target_id=self.node_b.id,
                delivery=Delivery(delivery_type="money", delivery_content="Grant"),
                cell_description=""
            )

    # --- validate_delivery_matrix ---

    def test_validate_valid_matrix_returns_no_errors(self):
        """validate_delivery_matrix returns an empty list for a valid matrix."""
        matrix = self.service.create_delivery_matrix(label="Valid")
        matrix.add_component(self.node_a.id)
        matrix.add_component(self.node_b.id)

        errors = self.service.validate_delivery_matrix(matrix)
        assert errors == []

    def test_validate_detects_missing_component_in_graph(self):
        """validate_delivery_matrix flags a component UUID not in the repository."""
        matrix = self.service.create_delivery_matrix(label="Bad")
        phantom_id = uuid.uuid4()
        matrix.components.append(phantom_id)

        errors = self.service.validate_delivery_matrix(matrix)
        assert any("not found in graph" in e for e in errors)

    def test_full_integration_workflow(self):
        """End-to-end: create matrix, add components, add heterogeneous deliveries, validate."""
        matrix = self.service.create_delivery_matrix(
            label="Full Workflow Test",
            matrix_scope="national"
        )
        matrix.add_component(self.node_a.id)
        matrix.add_component(self.node_b.id)
        matrix.add_component(self.node_c.id)

        # Multiple heterogeneous deliveries into the same cell
        for dtype, content in [
            ("money", "Budget allocation"),
            ("rule", "Regulatory framework"),
            ("authority", "Enforcement power"),
        ]:
            self.service.add_delivery_to_matrix(
                matrix=matrix,
                source_id=self.node_a.id,
                target_id=self.node_b.id,
                delivery=Delivery(delivery_type=dtype, delivery_content=content),
                cell_description="A governs B"
            )

        # Add a delivery in the reverse direction (non-symmetric)
        self.service.add_delivery_to_matrix(
            matrix=matrix,
            source_id=self.node_b.id,
            target_id=self.node_a.id,
            delivery=Delivery(
                delivery_type="information",
                delivery_content="Compliance reports"
            ),
            cell_description="B reports back to A"
        )

        errors = self.service.validate_delivery_matrix(matrix)
        assert errors == []

        # Matrix structure
        cell_ab = matrix.get_cell(self.node_a.id, self.node_b.id)
        cell_ba = matrix.get_cell(self.node_b.id, self.node_a.id)

        assert cell_ab is not None and len(cell_ab.deliveries) == 3
        assert cell_ba is not None and len(cell_ba.deliveries) == 1
        # Confirm non-symmetry
        assert cell_ab.cell_description != cell_ba.cell_description

        # Non-empty cell aggregation
        non_empty = matrix.get_non_empty_cells()
        assert len(non_empty) == 2
