"""
Test suite for Hayden SFM Fidelity: Core Delivery Matrix Structure

Tests implementation against Hayden's published SFM methodology:
1. Square N×N structure (components on both axes)
2. Non-symmetric: Cell(i,j) ≠ Cell(j,i)
3. Multiple heterogeneous deliveries per cell
4. Cell descriptions required for non-empty cells
5. Temporal modeling with rates and thresholds

Tests are based on requirements from Hayden (2006, 2008) and related publications.
"""

import pytest
import uuid
from datetime import datetime, timedelta

from models import Node
from models.delivery_matrix import (
    Delivery,
    SFMDeliveryCell,
    SFMDeliveryMatrix
)
from api.sfm_service import SFMService


class TestSquareMatrixStructure:
    """Test Hayden Requirement: Square N×N matrix with components on both axes."""

    def test_matrix_is_square_by_design(self, sfm_service):
        """Verify matrix is always square (N×N structure)."""
        matrix = sfm_service.create_delivery_matrix(
            label="Test Square Matrix"
        )

        # Add 3 components
        comp_a = sfm_service.create_node(Node(label="Component A"))
        comp_b = sfm_service.create_node(Node(label="Component B"))
        comp_c = sfm_service.create_node(Node(label="Component C"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)
        matrix.add_component(comp_c.id)

        # Verify square structure
        assert matrix.is_square()
        assert len(matrix.components) == 3

        # Components appear on both axes
        # Can create cells for any (i,j) combination
        assert matrix.get_cell(comp_a.id, comp_b.id) is None  # Empty cell OK
        assert matrix.get_cell(comp_b.id, comp_a.id) is None  # Empty cell OK

        # Total possible cells = N² = 9
        # (A→A, A→B, A→C, B→A, B→B, B→C, C→A, C→B, C→C)
        n = len(matrix.components)
        assert n * n == 9

    def test_non_symmetric_structure(self, sfm_service):
        """Verify Cell(i,j) ≠ Cell(j,i) (non-symmetric per Hayden)."""
        matrix = sfm_service.create_delivery_matrix()

        comp_a = sfm_service.create_node(Node(label="Legislature"))
        comp_b = sfm_service.create_node(Node(label="Agency"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        # Create Cell(A→B): Legislature delivers to Agency
        delivery_ab = Delivery(
            delivery_type="money",
            delivery_content="$500M appropriation",
            quantity=500_000_000
        )
        cell_ab = sfm_service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery_ab,
            "Legislature funds Agency"
        )

        # Create Cell(B→A): Agency delivers to Legislature
        delivery_ba = Delivery(
            delivery_type="information",
            delivery_content="Annual performance report"
        )
        cell_ba = sfm_service.add_delivery_to_matrix(
            matrix, comp_b.id, comp_a.id, delivery_ba,
            "Agency reports to Legislature"
        )

        # Verify non-symmetry
        assert cell_ab.source_component_id != cell_ba.source_component_id
        assert cell_ab.target_component_id != cell_ba.target_component_id
        assert cell_ab.deliveries[0].delivery_type != cell_ba.deliveries[0].delivery_type
        assert cell_ab.cell_description != cell_ba.cell_description

    def test_component_on_both_axes(self, sfm_service):
        """Verify same component can be both source and target (diagonal cells)."""
        matrix = sfm_service.create_delivery_matrix()

        institution = sfm_service.create_node(Node(label="Federal Reserve"))
        matrix.add_component(institution.id)

        # Cell(Fed→Fed): Self-delivery (e.g., internal coordination)
        delivery = Delivery(
            delivery_type="information",
            delivery_content="Internal policy coordination between regional banks"
        )
        cell = sfm_service.add_delivery_to_matrix(
            matrix, institution.id, institution.id, delivery,
            "Federal Reserve internal coordination"
        )

        assert cell.source_component_id == institution.id
        assert cell.target_component_id == institution.id
        assert len(cell.deliveries) == 1

    def test_components_validation(self, sfm_service):
        """Verify cells can only reference components in the matrix."""
        matrix = sfm_service.create_delivery_matrix()

        comp_a = sfm_service.create_node(Node(label="Component A"))
        comp_b = sfm_service.create_node(Node(label="Component B"))
        comp_c = sfm_service.create_node(Node(label="Component C"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)
        # Note: comp_c NOT in matrix

        # Try to create cell with comp_c (not in matrix)
        delivery = Delivery(
            delivery_type="rule",
            delivery_content="Regulation"
        )

        with pytest.raises(ValueError, match="not in matrix"):
            sfm_service.add_delivery_to_matrix(
                matrix, comp_a.id, comp_c.id, delivery,
                "A regulates C"
            )


class TestMultipleHeterogeneousDeliveries:
    """Test Hayden Requirement: Multiple distinct deliveries per cell."""

    def test_multiple_deliveries_per_cell(self, sfm_service):
        """Verify cell can hold multiple deliveries (Hayden 2008 requirement)."""
        matrix = sfm_service.create_delivery_matrix()

        legislature = sfm_service.create_node(Node(label="Legislature"))
        agency = sfm_service.create_node(Node(label="Agency"))

        matrix.add_component(legislature.id)
        matrix.add_component(agency.id)

        # Add first delivery: money
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="$800M budget appropriation",
            quantity=800_000_000,
            units="USD/year"
        )
        cell = sfm_service.add_delivery_to_matrix(
            matrix, legislature.id, agency.id, delivery1,
            "Legislature provides funding and authority to Agency"
        )

        # Add second delivery: authority
        delivery2 = Delivery(
            delivery_type="authority",
            delivery_content="Statutory enforcement power"
        )
        cell.add_delivery(delivery2)

        # Add third delivery: rule
        delivery3 = Delivery(
            delivery_type="rule",
            delivery_content="Annual reporting requirements"
        )
        cell.add_delivery(delivery3)

        # Verify multiple deliveries
        assert len(cell.deliveries) == 3
        assert cell.deliveries[0].delivery_type == "money"
        assert cell.deliveries[1].delivery_type == "authority"
        assert cell.deliveries[2].delivery_type == "rule"

    def test_heterogeneous_delivery_types(self, sfm_service):
        """Verify cell can mix different delivery types (not just scalar)."""
        matrix = sfm_service.create_delivery_matrix()

        factory = sfm_service.create_node(Node(label="Factory"))
        community = sfm_service.create_node(Node(label="Community"))

        matrix.add_component(factory.id)
        matrix.add_component(community.id)

        # Heterogeneous deliveries from factory to community
        deliveries = [
            Delivery(
                delivery_type="pollution",
                delivery_content="SO2 emissions",
                quantity=5.6,
                units="kg/km²/day",
                threshold=3.0,
                threshold_direction="below"
            ),
            Delivery(
                delivery_type="money",
                delivery_content="Local tax revenue",
                quantity=2_000_000,
                units="USD/year"
            ),
            Delivery(
                delivery_type="energy",
                delivery_content="Employment opportunities",
                quantity=500,
                units="jobs"
            )
        ]

        cell = None
        for i, delivery in enumerate(deliveries):
            if i == 0:
                cell = sfm_service.add_delivery_to_matrix(
                    matrix, factory.id, community.id, delivery,
                    "Factory impacts community through pollution, taxes, and jobs"
                )
            else:
                cell.add_delivery(delivery)

        # Verify heterogeneity
        delivery_types = set(d.delivery_type for d in cell.deliveries)
        assert len(delivery_types) == 3
        assert "pollution" in delivery_types
        assert "money" in delivery_types
        assert "energy" in delivery_types

    def test_scalar_reduction_prohibited(self, sfm_service):
        """Verify deliveries maintain full detail (no scalar reduction to +/-)."""
        matrix = sfm_service.create_delivery_matrix()

        comp_a = sfm_service.create_node(Node(label="Component A"))
        comp_b = sfm_service.create_node(Node(label="Component B"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        # Complex delivery with multiple attributes
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Industrial wastewater discharge with heavy metals",
            quantity=150_000,
            units="gallons/day",
            temporal_rate="continuous",
            temporal_clock="calendar_year",
            threshold=100_000,
            threshold_direction="below",
            certainty=0.92,
            data_sources=["EPA NPDES permit data", "State water quality reports"]
        )

        cell = sfm_service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery,
            "Component A discharges wastewater to Component B watershed"
        )

        # Verify NO scalar reduction - all attributes preserved
        retrieved = cell.deliveries[0]
        assert retrieved.delivery_type == "pollution"
        assert retrieved.delivery_content == "Industrial wastewater discharge with heavy metals"
        assert retrieved.quantity == 150_000
        assert retrieved.units == "gallons/day"
        assert retrieved.temporal_rate == "continuous"
        assert retrieved.threshold == 100_000
        assert retrieved.certainty == 0.92
        assert len(retrieved.data_sources) == 2

        # NO aggregation to simple +/- sign
        assert not hasattr(cell, 'scalar_value')


class TestCellDescriptionsRequired:
    """Test Hayden Requirement: Cell descriptions are REQUIRED deliverables."""

    def test_cell_description_required_for_nonempty_cells(self, sfm_service):
        """Verify non-empty cells require descriptions (Hayden methodology)."""
        matrix = sfm_service.create_delivery_matrix()

        comp_a = sfm_service.create_node(Node(label="Component A"))
        comp_b = sfm_service.create_node(Node(label="Component B"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment"
        )

        # Try to add delivery without description
        with pytest.raises(ValueError, match="cell_description is required"):
            sfm_service.add_delivery_to_matrix(
                matrix, comp_a.id, comp_b.id, delivery,
                ""  # Empty description
            )

    def test_cell_description_as_canonical_deliverable(self, sfm_service):
        """Verify cell descriptions are treated as canonical deliverables."""
        matrix = sfm_service.create_delivery_matrix()

        congress = sfm_service.create_node(Node(label="U.S. Congress"))
        epa = sfm_service.create_node(Node(label="EPA"))

        matrix.add_component(congress.id)
        matrix.add_component(epa.id)

        # Create cell with detailed description
        description = (
            "Congress establishes EPA through Clean Air Act of 1970, "
            "provides annual appropriations ($800M baseline), grants "
            "rulemaking authority for NAAQS, and mandates reporting requirements"
        )

        delivery = Delivery(
            delivery_type="authority",
            delivery_content="Statutory authority to regulate air quality"
        )

        cell = sfm_service.add_delivery_to_matrix(
            matrix, congress.id, epa.id, delivery,
            description
        )

        # Verify description preserved as primary deliverable
        assert cell.cell_description == description
        assert len(cell.cell_description) > 100  # Rich narrative preserved

        # Cell description is NOT optional metadata
        cell.cell_description = ""  # Try to clear it

        # Validation should catch this
        errors = sfm_service.validate_delivery_matrix(matrix)
        assert any("description" in err.lower() for err in errors)

    def test_empty_cells_no_description_required(self, sfm_service):
        """Verify empty cells (no deliveries) don't require descriptions."""
        # Empty cells are simply not present in the matrix.cells dict
        # This is valid per Hayden - sparse matrices are common
        matrix = sfm_service.create_delivery_matrix()

        comp_a = sfm_service.create_node(Node(label="Component A"))
        comp_b = sfm_service.create_node(Node(label="Component B"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        # No cell created = empty cell
        cell = matrix.get_cell(comp_a.id, comp_b.id)
        assert cell is None  # Empty cells are None, not cells with empty deliveries


class TestTemporalModeling:
    """Test Hayden Requirement: Temporal rates and threshold monitoring."""

    def test_delivery_temporal_rates(self, sfm_service):
        """Verify deliveries support temporal rates (Hayden 1987, 1993)."""
        matrix = sfm_service.create_delivery_matrix()

        legislature = sfm_service.create_node(Node(label="Legislature"))
        agency = sfm_service.create_node(Node(label="Agency"))

        matrix.add_component(legislature.id)
        matrix.add_component(agency.id)

        # Annual appropriation
        annual_delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual budget appropriation",
            quantity=800_000_000,
            units="USD/year",
            temporal_rate="annual",
            temporal_clock="fiscal_year"
        )

        # Continuous monitoring
        continuous_delivery = Delivery(
            delivery_type="information",
            delivery_content="Real-time compliance data",
            temporal_rate="continuous",
            temporal_clock="calendar_year"
        )

        cell = sfm_service.add_delivery_to_matrix(
            matrix, legislature.id, agency.id, annual_delivery,
            "Legislature provides funding and oversight to Agency"
        )
        cell.add_delivery(continuous_delivery)

        # Verify temporal rates preserved
        assert cell.deliveries[0].temporal_rate == "annual"
        assert cell.deliveries[0].temporal_clock == "fiscal_year"
        assert cell.deliveries[1].temporal_rate == "continuous"

    def test_threshold_monitoring(self, sfm_service):
        """Verify deliveries support threshold monitoring (Hayden 1987)."""
        matrix = sfm_service.create_delivery_matrix()

        power_plant = sfm_service.create_node(Node(label="Power Plant"))
        atmosphere = sfm_service.create_node(Node(label="Atmosphere"))

        matrix.add_component(power_plant.id)
        matrix.add_component(atmosphere.id)

        # Pollution delivery with threshold
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="SO2 emissions from coal combustion",
            quantity=9.0,  # Current level
            units="kg/km²/day",
            threshold=3.0,  # Target level
            threshold_direction="below",
            temporal_rate="continuous"
        )

        cell = sfm_service.add_delivery_to_matrix(
            matrix, power_plant.id, atmosphere.id, delivery,
            "Power plant emits SO2 to atmosphere, target 67% reduction"
        )

        # Verify threshold attributes
        assert cell.deliveries[0].threshold == 3.0
        assert cell.deliveries[0].threshold_direction == "below"
        assert cell.deliveries[0].quantity > cell.deliveries[0].threshold  # Currently exceeding


class TestMatrixDensityAndSummary:
    """Test matrix summary statistics and density calculations."""

    def test_matrix_summary_statistics(self, sfm_service):
        """Verify summary statistics calculation."""
        matrix = sfm_service.create_delivery_matrix()

        # Create 3 components (3×3 = 9 possible cells)
        comps = []
        for label in ["A", "B", "C"]:
            comp = sfm_service.create_node(Node(label=f"Component {label}"))
            matrix.add_component(comp.id)
            comps.append(comp)

        # Create 4 non-empty cells (density = 4/9 = 0.444)
        deliveries_data = [
            (comps[0].id, comps[1].id, "money", "Payment A→B"),
            (comps[0].id, comps[2].id, "rule", "Rule A→C"),
            (comps[1].id, comps[0].id, "information", "Info B→A"),
            (comps[1].id, comps[2].id, "energy", "Energy B→C"),
        ]

        for src, tgt, dtype, content in deliveries_data:
            delivery = Delivery(delivery_type=dtype, delivery_content=content)
            sfm_service.add_delivery_to_matrix(
                matrix, src, tgt, delivery,
                f"Delivery from {src} to {tgt}"
            )

        # Get summary
        summary = matrix.get_summary()

        assert summary["components"] == 3
        assert summary["non_empty_cells"] == 4
        assert summary["total_deliveries"] == 4

        # Verify density calculation manually
        # N×N = 9 possible cells, 4 non-empty = 4/9 ≈ 0.444
        n = len(matrix.components)
        density = summary["non_empty_cells"] / (n * n)
        assert abs(density - 4/9) < 0.001

    def test_density_calculation(self, sfm_service):
        """Verify density = non_empty_cells / N²."""
        matrix = sfm_service.create_delivery_matrix()

        # 4×4 matrix = 16 possible cells
        for i in range(4):
            comp = sfm_service.create_node(Node(label=f"Component {i}"))
            matrix.add_component(comp.id)

        # Fill 6 cells (density = 6/16 = 0.375)
        for i in range(3):
            for j in range(2):
                delivery = Delivery(
                    delivery_type="money",
                    delivery_content=f"Delivery {i}→{j}"
                )
                sfm_service.add_delivery_to_matrix(
                    matrix,
                    matrix.components[i],
                    matrix.components[j],
                    delivery,
                    f"Cell ({i},{j})"
                )

        # Calculate density manually
        summary = matrix.get_summary()
        n = len(matrix.components)
        density = summary["non_empty_cells"] / (n * n)
        assert density == 6/16


class TestIntegrationWithExistingFramework:
    """Test integration with cultural values and correlation framework."""

    def test_cultural_values_on_cells(self, sfm_service):
        """Verify delivery cells integrate with cultural framework."""
        matrix = sfm_service.create_delivery_matrix()

        citizens = sfm_service.create_node(Node(label="Nebraska Citizens"))
        state = sfm_service.create_node(Node(label="Nebraska State Government"))

        matrix.add_component(citizens.id)
        matrix.add_component(state.id)

        delivery = Delivery(
            delivery_type="rule",
            delivery_content="NIMBY opposition to waste facility"
        )

        cell = sfm_service.add_delivery_to_matrix(
            matrix, citizens.id, state.id, delivery,
            "Citizens resist facility through political opposition (CEREMONIAL)"
        )

        # Add cultural values (per LLRW case study)
        cell.ceremonial_component = 0.9  # High ceremonial resistance
        cell.instrumental_component = 0.1  # Low instrumental problem-solving
        cell.cultural_values_influence = {
            "community_sovereignty": 0.8,
            "nimby_resistance": 0.7,
            "scientific_siting": -0.6
        }

        # Verify integration
        assert cell.ceremonial_component == 0.9
        assert cell.cultural_values_influence["community_sovereignty"] == 0.8

    def test_correlation_type_on_cells(self, sfm_service):
        """Verify cells can have aggregate correlation assessment."""
        matrix = sfm_service.create_delivery_matrix()

        comp_a = sfm_service.create_node(Node(label="Component A"))
        comp_b = sfm_service.create_node(Node(label="Component B"))

        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        # Mixed correlation: both positive (money) and negative (pollution)
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="Revenue sharing"
        )
        delivery2 = Delivery(
            delivery_type="pollution",
            delivery_content="Environmental degradation"
        )

        cell = sfm_service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery1,
            "Mixed impact: economic benefit with environmental cost"
        )
        cell.add_delivery(delivery2)

        # Set aggregate assessment (using string values)
        cell.net_correlation = "mixed"
        cell.aggregate_strength = 0.6

        assert cell.net_correlation == "mixed"
        assert cell.aggregate_strength == 0.6


@pytest.fixture
def sfm_service():
    """Create SFMService instance for testing."""
    return SFMService()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
