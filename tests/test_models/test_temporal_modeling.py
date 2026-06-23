"""
Comprehensive tests for temporal modeling features.

Tests cover:
- Threshold monitoring system
- Temporal clock operations
- Delivery synchronization
- Temporal rate validation
- Service integration
- Clock phase advancement
- Deliveries due checking

Per Issue #42 acceptance criteria.
"""

import pytest
import uuid
from datetime import datetime, timedelta

from api.sfm_service import SFMService, ThresholdAlert
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix, SFMDeliveryCell
from models.temporal_clocks import (
    TemporalClock,
    TemporalPhase,
    create_legislative_clock,
    create_fiscal_year_clock,
)


class TestThresholdMonitoringSystem:
    """Test threshold monitoring system per Hayden 1987/1993."""

    def setup_method(self):
        """Setup test service and matrix."""
        self.service = SFMService()

        # Create components
        self.comp_a = Node(label="Component A")
        self.comp_b = Node(label="Component B")
        self.comp_c = Node(label="Component C")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)
        self.service.create_node(self.comp_c)

        # Create matrix
        self.matrix = self.service.create_delivery_matrix(
            label="Test Threshold Matrix"
        )
        self.matrix.add_component(self.comp_a.id)
        self.matrix.add_component(self.comp_b.id)
        self.matrix.add_component(self.comp_c.id)

    def test_threshold_monitoring_above_triggered(self):
        """Test threshold monitoring with 'above' direction triggered."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions from factory",
            quantity=550,
            units="million tons/year",
            threshold=500,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="A pollutes B"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 1
        assert alerts[0].current_value == 550
        assert alerts[0].threshold == 500
        assert alerts[0].direction == "exceeded"
        assert alerts[0].delivery.delivery_type == "pollution"
        assert isinstance(alerts[0].timestamp, datetime)

    def test_threshold_monitoring_below_triggered(self):
        """Test threshold monitoring with 'below' direction triggered."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual school funding",
            quantity=75_000_000,
            units="USD/year",
            threshold=100_000_000,
            threshold_direction="below"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Legislature funds schools"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 1
        assert alerts[0].current_value == 75_000_000
        assert alerts[0].threshold == 100_000_000
        assert alerts[0].direction == "below"

    def test_no_alerts_within_threshold_above(self):
        """Test no alerts when value below 'above' threshold."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=400,
            threshold=500,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Delivery"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)
        assert len(alerts) == 0

    def test_no_alerts_within_threshold_below(self):
        """Test no alerts when value above 'below' threshold."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Funding",
            quantity=120_000_000,
            threshold=100_000_000,
            threshold_direction="below"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Funding delivery"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)
        assert len(alerts) == 0

    def test_no_alerts_when_no_threshold(self):
        """Test no alerts when delivery has no threshold."""
        delivery = Delivery(
            delivery_type="rule",
            delivery_content="Regulation XYZ",
            quantity=100
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Regulation"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)
        assert len(alerts) == 0

    def test_multiple_threshold_violations(self):
        """Test detecting multiple threshold violations across cells."""
        delivery1 = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions A->B",
            quantity=600,
            threshold=500,
            threshold_direction="above"
        )

        delivery2 = Delivery(
            delivery_type="money",
            delivery_content="Budget B->C",
            quantity=50_000_000,
            threshold=100_000_000,
            threshold_direction="below"
        )

        delivery3 = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions C->A",
            quantity=700,
            threshold=600,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery1, "A->B"
        )
        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_b.id, self.comp_c.id, delivery2, "B->C"
        )
        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_c.id, self.comp_a.id, delivery3, "C->A"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 3
        exceeded_count = sum(1 for a in alerts if a.direction == "exceeded")
        below_count = sum(1 for a in alerts if a.direction == "below")
        assert exceeded_count == 2
        assert below_count == 1


class TestUpdateDeliveryQuantity:
    """Test update_delivery_quantity with threshold checking."""

    def setup_method(self):
        """Setup test service and matrix."""
        self.service = SFMService()

        self.comp_a = Node(label="Component A")
        self.comp_b = Node(label="Component B")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)

        self.matrix = self.service.create_delivery_matrix(
            label="Update Test Matrix"
        )
        self.matrix.add_component(self.comp_a.id)
        self.matrix.add_component(self.comp_b.id)

    def test_update_quantity_triggers_threshold_above(self):
        """Test updating quantity triggers 'above' threshold alert."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
            quantity=400,
            threshold=500,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery, "A->B"
        )

        # Update to exceed threshold
        alerts = self.service.update_delivery_quantity(
            self.matrix, self.comp_a.id, self.comp_b.id, 0, 550
        )

        assert len(alerts) == 1
        assert alerts[0].current_value == 550
        assert alerts[0].direction == "exceeded"

        # Verify quantity was updated
        cell = self.matrix.get_cell(self.comp_a.id, self.comp_b.id)
        assert cell.deliveries[0].quantity == 550

    def test_update_quantity_triggers_threshold_below(self):
        """Test updating quantity triggers 'below' threshold alert."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Funding",
            quantity=120_000_000,
            threshold=100_000_000,
            threshold_direction="below"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery, "Funding"
        )

        # Update to go below threshold
        alerts = self.service.update_delivery_quantity(
            self.matrix, self.comp_a.id, self.comp_b.id, 0, 75_000_000
        )

        assert len(alerts) == 1
        assert alerts[0].current_value == 75_000_000
        assert alerts[0].direction == "below"

    def test_update_quantity_no_alert_within_threshold(self):
        """Test updating quantity within threshold generates no alert."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=400,
            threshold=500,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery, "Emissions"
        )

        # Update but stay within threshold
        alerts = self.service.update_delivery_quantity(
            self.matrix, self.comp_a.id, self.comp_b.id, 0, 450
        )

        assert len(alerts) == 0

        # Verify quantity was updated
        cell = self.matrix.get_cell(self.comp_a.id, self.comp_b.id)
        assert cell.deliveries[0].quantity == 450

    def test_update_quantity_invalid_cell(self):
        """Test updating quantity for non-existent cell raises error."""
        with pytest.raises(ValueError, match="Cell .* not found"):
            self.service.update_delivery_quantity(
                self.matrix, uuid.uuid4(), uuid.uuid4(), 0, 100
            )

    def test_update_quantity_invalid_delivery_index(self):
        """Test updating quantity with invalid index raises error."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment",
            quantity=100
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery, "Payment"
        )

        with pytest.raises(ValueError, match="index .* out of range"):
            self.service.update_delivery_quantity(
                self.matrix, self.comp_a.id, self.comp_b.id, 5, 200
            )

    def test_update_quantity_multiple_deliveries(self):
        """Test updating specific delivery when cell has multiple."""
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="Payment 1",
            quantity=100
        )
        delivery2 = Delivery(
            delivery_type="energy",
            delivery_content="Power",
            quantity=50,
            threshold=40,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery1, "Multi"
        )
        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery2, "Multi"
        )

        # Update second delivery
        alerts = self.service.update_delivery_quantity(
            self.matrix, self.comp_a.id, self.comp_b.id, 1, 60
        )

        assert len(alerts) == 1
        assert alerts[0].delivery.delivery_type == "energy"

        # Verify first delivery unchanged
        cell = self.matrix.get_cell(self.comp_a.id, self.comp_b.id)
        assert cell.deliveries[0].quantity == 100
        assert cell.deliveries[1].quantity == 60


class TestGetDeliveriesByTemporalRate:
    """Test get_deliveries_by_temporal_rate filtering."""

    def setup_method(self):
        """Setup test service and matrix."""
        self.service = SFMService()

        self.comp_a = Node(label="Component A")
        self.comp_b = Node(label="Component B")
        self.comp_c = Node(label="Component C")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)
        self.service.create_node(self.comp_c)

        self.matrix = self.service.create_delivery_matrix(
            label="Temporal Rate Test Matrix"
        )
        self.matrix.add_component(self.comp_a.id)
        self.matrix.add_component(self.comp_b.id)
        self.matrix.add_component(self.comp_c.id)

    def test_filter_annual_deliveries(self):
        """Test filtering annual deliveries."""
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="Annual budget",
            quantity=1_000_000,
            temporal_rate="annual"
        )
        delivery2 = Delivery(
            delivery_type="money",
            delivery_content="Monthly payment",
            quantity=50_000,
            temporal_rate="monthly"
        )
        delivery3 = Delivery(
            delivery_type="money",
            delivery_content="Annual grant",
            quantity=500_000,
            temporal_rate="annual"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery1, "Budget"
        )
        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_b.id, self.comp_c.id, delivery2, "Payment"
        )
        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_c.id, self.comp_a.id, delivery3, "Grant"
        )

        results = self.service.get_deliveries_by_temporal_rate(self.matrix, "annual")

        assert len(results) == 2
        assert all(r["delivery"].temporal_rate == "annual" for r in results)

    def test_filter_no_matches(self):
        """Test filtering returns empty when no matches."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment",
            quantity=100,
            temporal_rate="quarterly"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery, "Payment"
        )

        results = self.service.get_deliveries_by_temporal_rate(self.matrix, "annual")
        assert len(results) == 0

    def test_filter_result_structure(self):
        """Test filter result contains expected fields."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment",
            quantity=100,
            temporal_rate="monthly"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id, delivery, "Payment"
        )

        results = self.service.get_deliveries_by_temporal_rate(self.matrix, "monthly")

        assert len(results) == 1
        result = results[0]
        assert "delivery" in result
        assert "cell" in result
        assert "source_id" in result
        assert "target_id" in result
        assert "delivery_index" in result
        assert result["source_id"] == self.comp_a.id
        assert result["target_id"] == self.comp_b.id
        assert result["delivery_index"] == 0


class TestTemporalRateValidation:
    """Test temporal rate validation."""

    def setup_method(self):
        """Setup test service."""
        self.service = SFMService()

    def test_valid_temporal_rates(self):
        """Test all valid temporal rates pass validation."""
        valid_rates = [
            "continuous", "real_time", "daily", "weekly", "monthly",
            "quarterly", "annual", "biennial", "event_triggered",
            "on_demand", "legislative_cycle", "fiscal_year", "academic_year"
        ]

        for rate in valid_rates:
            delivery = Delivery(
                delivery_type="money",
                delivery_content="Test",
                temporal_rate=rate
            )
            assert self.service.validate_temporal_rate(delivery) is True

    def test_invalid_temporal_rate(self):
        """Test invalid temporal rate fails validation."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Test",
            temporal_rate="invalid_rate"
        )
        assert self.service.validate_temporal_rate(delivery) is False

    def test_none_temporal_rate_valid(self):
        """Test None temporal rate is valid (optional field)."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Test",
            temporal_rate=None
        )
        assert self.service.validate_temporal_rate(delivery) is True


class TestTemporalClockOperations:
    """Test temporal clock operations."""

    def setup_method(self):
        """Setup test service."""
        self.service = SFMService()

    def test_get_deliveries_due(self):
        """Test getting deliveries due for current phase."""
        # Create clock
        clock = create_legislative_clock(state="Nebraska", biennial=True)
        clock = self.service.create_temporal_clock(
            clock_name=clock.clock_name,
            label=clock.label,
            period_length=clock.period_length,
            phases=clock.phases
        )
        clock.current_phase = "first_session"

        # Create matrix with synchronized delivery
        comp_a = Node(label="Legislature")
        comp_b = Node(label="School District")
        self.service.create_node(comp_a)
        self.service.create_node(comp_b)

        matrix = self.service.create_delivery_matrix(label="Test Matrix")
        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        delivery = Delivery(
            delivery_type="money",
            delivery_content="TEEOSA funding",
            quantity=800_000_000,
            temporal_rate="biennial",
            temporal_clock="nebraska_legislative_cycle"
        )

        self.service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Legislature funds schools"
        )

        # Synchronize delivery to clock
        self.service.synchronize_delivery_to_clock(
            clock, comp_a.id, comp_b.id, 0
        )

        # Get deliveries due
        deliveries_due = clock.get_deliveries_due(matrix)

        assert len(deliveries_due) == 1
        assert deliveries_due[0]["delivery"].delivery_content == "TEEOSA funding"
        assert deliveries_due[0]["clock_name"] == "nebraska_legislative_cycle"

    def test_advance_clock_without_matrix(self):
        """Test advancing clock without checking deliveries."""
        clock = create_fiscal_year_clock()
        clock = self.service.create_temporal_clock(
            clock_name=clock.clock_name,
            label=clock.label,
            period_length=clock.period_length,
            phases=clock.phases
        )
        # Set current phase explicitly
        clock.current_phase = "Q1"

        result = self.service.advance_clock(clock)

        assert result["new_phase"] == "Q2"  # Advanced from Q1
        assert result["previous_phase"] == "Q1"
        assert result["deliveries_due"] == []
        assert result["alerts"] == []

    def test_advance_clock_with_deliveries_due(self):
        """Test advancing clock triggers deliveries due check."""
        # Create clock
        clock = create_fiscal_year_clock()
        clock = self.service.create_temporal_clock(
            clock_name=clock.clock_name,
            label=clock.label,
            period_length=clock.period_length,
            phases=clock.phases
        )
        clock.current_phase = "Q1"

        # Create matrix
        comp_a = Node(label="A")
        comp_b = Node(label="B")
        self.service.create_node(comp_a)
        self.service.create_node(comp_b)

        matrix = self.service.create_delivery_matrix(label="Test")
        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        delivery = Delivery(
            delivery_type="money",
            delivery_content="Quarterly payment",
            quantity=100_000,
            temporal_rate="quarterly",
            temporal_clock="fiscal_year"
        )

        self.service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Payment"
        )

        self.service.synchronize_delivery_to_clock(clock, comp_a.id, comp_b.id, 0)

        # Advance clock
        result = self.service.advance_clock(clock, matrix)

        assert result["new_phase"] == "Q2"
        assert len(result["deliveries_due"]) == 1
        assert result["deliveries_due"][0]["delivery"].delivery_content == "Quarterly payment"

    def test_advance_clock_with_threshold_alerts(self):
        """Test advancing clock triggers threshold alerts for due deliveries."""
        clock = create_fiscal_year_clock()
        clock = self.service.create_temporal_clock(
            clock_name=clock.clock_name,
            label=clock.label,
            period_length=clock.period_length,
            phases=clock.phases
        )

        comp_a = Node(label="A")
        comp_b = Node(label="B")
        self.service.create_node(comp_a)
        self.service.create_node(comp_b)

        matrix = self.service.create_delivery_matrix(label="Test")
        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        delivery = Delivery(
            delivery_type="money",
            delivery_content="Budget allocation",
            quantity=75_000,
            threshold=100_000,
            threshold_direction="below",
            temporal_rate="quarterly",
            temporal_clock="fiscal_year"
        )

        self.service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Budget"
        )

        self.service.synchronize_delivery_to_clock(clock, comp_a.id, comp_b.id, 0)

        result = self.service.advance_clock(clock, matrix)

        assert len(result["alerts"]) == 1
        assert result["alerts"][0].direction == "below"
        assert result["alerts"][0].current_value == 75_000


class TestDeliverySynchronization:
    """Test delivery synchronization to clocks."""

    def setup_method(self):
        """Setup test service."""
        self.service = SFMService()

    def test_synchronize_delivery_to_clock(self):
        """Test synchronizing delivery to clock."""
        clock = self.service.create_temporal_clock(
            clock_name="test_clock",
            label="Test Clock",
            period_length=timedelta(days=365)
        )

        src_id = uuid.uuid4()
        tgt_id = uuid.uuid4()

        self.service.synchronize_delivery_to_clock(clock, src_id, tgt_id, 0)

        key = f"{src_id}_{tgt_id}"
        assert key in clock.synchronized_deliveries
        assert (src_id, tgt_id, 0) in clock.synchronized_deliveries[key]

    def test_multiple_deliveries_synchronization(self):
        """Test synchronizing multiple deliveries to same clock."""
        clock = self.service.create_temporal_clock(
            clock_name="multi_clock",
            label="Multi Clock",
            period_length=timedelta(days=365)
        )

        comp_a = Node(label="A")
        comp_b = Node(label="B")
        comp_c = Node(label="C")

        self.service.create_node(comp_a)
        self.service.create_node(comp_b)
        self.service.create_node(comp_c)

        self.service.synchronize_delivery_to_clock(clock, comp_a.id, comp_b.id, 0)
        self.service.synchronize_delivery_to_clock(clock, comp_b.id, comp_c.id, 0)
        self.service.synchronize_delivery_to_clock(clock, comp_a.id, comp_b.id, 1)

        assert len(clock.synchronized_deliveries) >= 2
        key_ab = f"{comp_a.id}_{comp_b.id}"
        assert len(clock.synchronized_deliveries[key_ab]) == 2
