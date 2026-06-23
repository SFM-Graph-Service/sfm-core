"""
Tests for temporal modeling features.

Covers:
- VALID_TEMPORAL_RATES enforcement
- validate_temporal_rate()
- update_delivery_quantity() with threshold checks
- get_deliveries_by_temporal_rate()
- advance_clock() and threshold integration
- ThresholdAlert extended fields (matrix_id, labels)
- Nebraska K-12 legislative cycle scenario

References:
- Hayden (1987): Real-time monitoring concept
- Hayden (1993): Polychronic systems and graphical clocks
- Hoffman & Hayden (2007): Nebraska K-12 temporal cycles
"""

import pytest
import uuid
from datetime import datetime, timedelta

from api.sfm_service import (
    SFMService,
    ThresholdAlert,
    VALID_TEMPORAL_RATES,
    validate_temporal_rate,
)
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix
from models.temporal_clocks import (
    TemporalClock,
    TemporalPhase,
    create_legislative_clock,
    create_fiscal_year_clock,
    create_academic_year_clock,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    """Fresh SFMService for each test."""
    return SFMService()


@pytest.fixture
def matrix_with_components(service):
    """Service + matrix with two components ready for deliveries."""
    comp_a = Node(label="Industry")
    comp_b = Node(label="Atmosphere")
    service.create_node(comp_a)
    service.create_node(comp_b)

    matrix = service.create_delivery_matrix(label="Test Matrix")
    matrix.add_component(comp_a.id)
    matrix.add_component(comp_b.id)
    return service, matrix, comp_a, comp_b


# ---------------------------------------------------------------------------
# VALID_TEMPORAL_RATES
# ---------------------------------------------------------------------------

class TestValidTemporalRates:
    """Tests for VALID_TEMPORAL_RATES constant."""

    def test_valid_rates_is_list(self):
        """VALID_TEMPORAL_RATES is a non-empty list."""
        assert isinstance(VALID_TEMPORAL_RATES, list)
        assert len(VALID_TEMPORAL_RATES) > 0

    def test_expected_rates_present(self):
        """Core rates from Hayden 1987/1993 are included."""
        for rate in ["continuous", "annual", "quarterly", "monthly", "weekly", "daily"]:
            assert rate in VALID_TEMPORAL_RATES

    def test_event_triggered_present(self):
        """Event-triggered rate is present."""
        assert "event-triggered" in VALID_TEMPORAL_RATES

    def test_on_demand_present(self):
        """On-demand rate is present."""
        assert "on-demand" in VALID_TEMPORAL_RATES


# ---------------------------------------------------------------------------
# validate_temporal_rate()
# ---------------------------------------------------------------------------

class TestValidateTemporalRate:
    """Tests for validate_temporal_rate() function."""

    def test_none_rate_is_valid(self):
        """Delivery with no temporal_rate is considered valid."""
        delivery = Delivery(
            delivery_type="rule",
            delivery_content="Standing regulation",
        )
        assert validate_temporal_rate(delivery) is True

    def test_annual_is_valid(self):
        """'annual' is a valid temporal rate."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual grant",
            temporal_rate="annual",
        )
        assert validate_temporal_rate(delivery) is True

    def test_continuous_is_valid(self):
        """'continuous' is a valid temporal rate."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Continuous emissions",
            temporal_rate="continuous",
        )
        assert validate_temporal_rate(delivery) is True

    def test_event_triggered_is_valid(self):
        """'event-triggered' is a valid temporal rate."""
        delivery = Delivery(
            delivery_type="information",
            delivery_content="Crisis alert",
            temporal_rate="event-triggered",
        )
        assert validate_temporal_rate(delivery) is True

    def test_unknown_rate_is_invalid(self):
        """Unrecognised rate returns False."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment",
            temporal_rate="biannual",  # not in VALID_TEMPORAL_RATES
        )
        assert validate_temporal_rate(delivery) is False

    def test_all_valid_rates_pass(self):
        """All rates in VALID_TEMPORAL_RATES validate successfully."""
        for rate in VALID_TEMPORAL_RATES:
            delivery = Delivery(
                delivery_type="rule",
                delivery_content=f"{rate} delivery",
                temporal_rate=rate,
            )
            assert validate_temporal_rate(delivery) is True, f"Rate '{rate}' should be valid"


# ---------------------------------------------------------------------------
# update_delivery_quantity()
# ---------------------------------------------------------------------------

class TestUpdateDeliveryQuantity:
    """Tests for update_delivery_quantity() method."""

    def test_basic_quantity_update(self, matrix_with_components):
        """Quantity is updated and persisted in the cell."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Grant disbursement",
            quantity=100_000,
            units="USD",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Grant from A to B"
        )

        service.update_delivery_quantity(matrix, comp_a.id, comp_b.id, 0, 200_000)

        cell = matrix.get_cell(comp_a.id, comp_b.id)
        assert cell.deliveries[0].quantity == 200_000

    def test_update_triggers_threshold_alert(self, matrix_with_components):
        """Updating past threshold returns ThresholdAlert."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
            quantity=450,
            units="million tons/year",
            threshold=500,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Industry emissions to atmosphere"
        )

        alert = service.update_delivery_quantity(
            matrix, comp_a.id, comp_b.id, 0, 550.0
        )

        assert alert is not None
        assert alert.current_value == 550.0
        assert alert.threshold == 500
        assert alert.direction == "exceeded"

    def test_update_below_threshold_no_alert(self, matrix_with_components):
        """Updating to value still within threshold returns None."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
            quantity=450,
            threshold=500,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Emissions"
        )

        alert = service.update_delivery_quantity(
            matrix, comp_a.id, comp_b.id, 0, 480.0
        )
        assert alert is None

    def test_update_with_check_threshold_false(self, matrix_with_components):
        """check_threshold=False suppresses threshold check."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
            quantity=450,
            threshold=500,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Emissions"
        )

        alert = service.update_delivery_quantity(
            matrix, comp_a.id, comp_b.id, 0, 9999.0, check_threshold=False
        )
        assert alert is None

    def test_update_missing_cell_raises(self, matrix_with_components):
        """Updating delivery in non-existent cell raises ValueError."""
        service, matrix, comp_a, comp_b = matrix_with_components

        with pytest.raises(ValueError, match="No cell found"):
            service.update_delivery_quantity(
                matrix, comp_a.id, comp_b.id, 0, 100.0
            )

    def test_update_out_of_range_index_raises(self, matrix_with_components):
        """Updating delivery with bad index raises ValueError."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment",
            quantity=100,
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Payment"
        )

        with pytest.raises(ValueError, match="out of range"):
            service.update_delivery_quantity(
                matrix, comp_a.id, comp_b.id, 5, 200.0
            )

    def test_alert_contains_matrix_id(self, matrix_with_components):
        """ThresholdAlert returned by update includes matrix_id."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=10,
            threshold=5,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Emissions"
        )

        alert = service.update_delivery_quantity(
            matrix, comp_a.id, comp_b.id, 0, 20.0
        )

        assert alert.matrix_id == matrix.id

    def test_alert_contains_component_labels(self, matrix_with_components):
        """ThresholdAlert returned by update includes component labels."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=10,
            threshold=5,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Emissions"
        )

        alert = service.update_delivery_quantity(
            matrix, comp_a.id, comp_b.id, 0, 20.0
        )

        assert alert.source_component_label == "Industry"
        assert alert.target_component_label == "Atmosphere"


# ---------------------------------------------------------------------------
# get_deliveries_by_temporal_rate()
# ---------------------------------------------------------------------------

class TestGetDeliveriesByTemporalRate:
    """Tests for get_deliveries_by_temporal_rate() method."""

    def test_returns_matching_deliveries(self, matrix_with_components):
        """Returns deliveries with matching temporal_rate."""
        service, matrix, comp_a, comp_b = matrix_with_components

        annual_delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual grant",
            quantity=1_000_000,
            temporal_rate="annual",
        )
        monthly_delivery = Delivery(
            delivery_type="money",
            delivery_content="Monthly payment",
            quantity=10_000,
            temporal_rate="monthly",
        )

        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, annual_delivery, "Funding stream"
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, monthly_delivery, "Funding stream"
        )

        results = service.get_deliveries_by_temporal_rate(matrix, "annual")

        assert len(results) == 1
        cell, delivery = results[0]
        assert delivery.delivery_content == "Annual grant"

    def test_empty_result_for_no_match(self, matrix_with_components):
        """Returns empty list when no deliveries match rate."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Monthly payment",
            quantity=1_000,
            temporal_rate="monthly",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Payment"
        )

        results = service.get_deliveries_by_temporal_rate(matrix, "quarterly")
        assert results == []

    def test_returns_cell_delivery_tuples(self, matrix_with_components):
        """Each result is a (SFMDeliveryCell, Delivery) tuple."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="rule",
            delivery_content="Continuous regulation",
            temporal_rate="continuous",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Regulation"
        )

        results = service.get_deliveries_by_temporal_rate(matrix, "continuous")
        assert len(results) == 1
        cell, d = results[0]
        assert cell.source_component_id == comp_a.id
        assert d.delivery_content == "Continuous regulation"

    def test_handles_deliveries_without_rate(self, matrix_with_components):
        """Deliveries with no temporal_rate are not included in results."""
        service, matrix, comp_a, comp_b = matrix_with_components
        no_rate = Delivery(
            delivery_type="information",
            delivery_content="Report",
        )
        annual = Delivery(
            delivery_type="money",
            delivery_content="Annual disbursement",
            temporal_rate="annual",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, no_rate, "Info and funds"
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, annual, "Info and funds"
        )

        results = service.get_deliveries_by_temporal_rate(matrix, "annual")
        assert len(results) == 1
        assert results[0][1].delivery_content == "Annual disbursement"


# ---------------------------------------------------------------------------
# advance_clock()
# ---------------------------------------------------------------------------

class TestAdvanceClock:
    """Tests for advance_clock() method."""

    def test_advance_clock_changes_phase(self, service):
        """advance_clock() moves clock to next phase."""
        clock = service.create_temporal_clock(
            clock_name="test_clock",
            label="Test Clock",
            period_length=timedelta(days=365),
            phases=[
                TemporalPhase("session", timedelta(days=120)),
                TemporalPhase("interim", timedelta(days=245)),
            ],
        )
        clock.current_phase = "session"

        service.advance_clock(clock)
        assert clock.current_phase == "interim"

    def test_advance_clock_wraps_around(self, service):
        """advance_clock() wraps from last phase back to first."""
        clock = service.create_temporal_clock(
            clock_name="fiscal",
            label="Fiscal Year",
            period_length=timedelta(days=365),
            phases=[
                TemporalPhase("Q1", timedelta(days=91)),
                TemporalPhase("Q2", timedelta(days=91)),
                TemporalPhase("Q3", timedelta(days=92)),
                TemporalPhase("Q4", timedelta(days=91)),
            ],
        )
        clock.current_phase = "Q4"

        service.advance_clock(clock)
        assert clock.current_phase == "Q1"

    def test_advance_clock_returns_empty_without_matrix(self, service):
        """advance_clock() returns empty list when no matrix provided."""
        clock = service.create_temporal_clock(
            clock_name="legislative",
            label="Legislative",
            period_length=timedelta(days=365),
            phases=[
                TemporalPhase("session", timedelta(days=120)),
                TemporalPhase("interim", timedelta(days=245)),
            ],
        )
        clock.current_phase = "session"

        alerts = service.advance_clock(clock)
        assert alerts == []

    def test_advance_clock_triggers_threshold_alerts(self, service):
        """advance_clock() returns alerts for synchronized deliveries past threshold."""
        # Setup components and matrix
        comp_a = Node(label="Legislature")
        comp_b = Node(label="School District")
        service.create_node(comp_a)
        service.create_node(comp_b)

        matrix = service.create_delivery_matrix(label="NE K-12")
        matrix.add_component(comp_a.id)
        matrix.add_component(comp_b.id)

        # Add delivery that exceeds threshold
        delivery = Delivery(
            delivery_type="money",
            delivery_content="TEEOSA appropriation",
            quantity=900_000_000,
            units="USD",
            threshold=800_000_000,
            threshold_direction="above",
            temporal_rate="annual",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery,
            "Legislature provides TEEOSA funding to schools"
        )

        # Create and synchronize clock
        clock = service.create_temporal_clock(
            clock_name="ne_legislature",
            label="Nebraska Legislature",
            period_length=timedelta(days=365),
            phases=[
                TemporalPhase("session", timedelta(days=120)),
                TemporalPhase("interim", timedelta(days=245)),
            ],
        )
        clock.current_phase = "session"
        service.synchronize_delivery_to_clock(clock, comp_a.id, comp_b.id, 0)

        alerts = service.advance_clock(clock, matrix)
        assert len(alerts) == 1
        assert alerts[0].current_value == 900_000_000
        assert alerts[0].direction == "exceeded"


# ---------------------------------------------------------------------------
# ThresholdAlert extended fields
# ---------------------------------------------------------------------------

class TestThresholdAlertFields:
    """Tests for extended ThresholdAlert fields (matrix_id, labels)."""

    def test_check_delivery_thresholds_includes_matrix_id(
        self, matrix_with_components
    ):
        """check_delivery_thresholds() populates matrix_id on alert."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=600,
            threshold=500,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Emissions"
        )

        alerts = service.check_delivery_thresholds(matrix)

        assert len(alerts) == 1
        assert alerts[0].matrix_id == matrix.id

    def test_check_delivery_thresholds_includes_labels(
        self, matrix_with_components
    ):
        """check_delivery_thresholds() populates component labels on alert."""
        service, matrix, comp_a, comp_b = matrix_with_components
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=600,
            threshold=500,
            threshold_direction="above",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Emissions"
        )

        alerts = service.check_delivery_thresholds(matrix)

        assert alerts[0].source_component_label == "Industry"
        assert alerts[0].target_component_label == "Atmosphere"

    def test_threshold_alert_timestamp_is_set(self, matrix_with_components):
        """ThresholdAlert timestamp is a recent datetime."""
        service, matrix, comp_a, comp_b = matrix_with_components
        before = datetime.now()
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Budget",
            quantity=50_000,
            threshold=100_000,
            threshold_direction="below",
        )
        service.add_delivery_to_matrix(
            matrix, comp_a.id, comp_b.id, delivery, "Budget"
        )

        alerts = service.check_delivery_thresholds(matrix)
        after = datetime.now()

        assert len(alerts) == 1
        assert before <= alerts[0].timestamp <= after


# ---------------------------------------------------------------------------
# Nebraska K-12 legislative cycle integration scenario
# ---------------------------------------------------------------------------

class TestNebraskaK12LegislativeCycle:
    """
    Integration tests using Nebraska K-12 case study.

    Based on Hoffman & Hayden (2007) Nebraska TEEOSA funding analysis
    with Hayden (1993) polychronic temporal modeling.
    """

    def setup_method(self):
        """Setup Nebraska K-12 SFM with legislative clock."""
        self.service = SFMService()

        # Create institutional components
        self.legislature = Node(label="Nebraska Legislature")
        self.dept_ed = Node(label="Dept of Education")
        self.school_districts = Node(label="School Districts")
        self.students = Node(label="Students")

        for node in [self.legislature, self.dept_ed,
                     self.school_districts, self.students]:
            self.service.create_node(node)

        # Create delivery matrix
        self.matrix = self.service.create_delivery_matrix(
            label="Nebraska K-12 Finance Matrix"
        )
        for node in [self.legislature, self.dept_ed,
                     self.school_districts, self.students]:
            self.matrix.add_component(node.id)

        # Create Nebraska biennial legislative clock
        self.leg_clock = create_legislative_clock(state="Nebraska", biennial=True)
        self.service.repository.create_node(self.leg_clock)

    def test_teeosa_delivery_with_temporal_rate(self):
        """TEEOSA annual delivery is valid per temporal rate rules."""
        teeosa = Delivery(
            delivery_type="money",
            delivery_content="$800M TEEOSA appropriation",
            quantity=800_000_000,
            units="USD",
            temporal_rate="annual",
            temporal_clock="fiscal_year",
        )
        assert validate_temporal_rate(teeosa) is True

    def test_filter_annual_deliveries(self):
        """get_deliveries_by_temporal_rate returns all annual deliveries."""
        teeosa = Delivery(
            delivery_type="money",
            delivery_content="TEEOSA formula funding",
            quantity=800_000_000,
            units="USD/year",
            temporal_rate="annual",
        )
        oversight = Delivery(
            delivery_type="authority",
            delivery_content="Continuous oversight mandate",
            temporal_rate="continuous",
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.legislature.id,
            self.school_districts.id,
            teeosa,
            "Legislature provides formula funding to school districts",
        )
        self.service.add_delivery_to_matrix(
            self.matrix,
            self.legislature.id,
            self.school_districts.id,
            oversight,
            "Legislature provides formula funding to school districts",
        )

        annual = self.service.get_deliveries_by_temporal_rate(
            self.matrix, "annual"
        )
        assert len(annual) == 1
        assert annual[0][1].delivery_content == "TEEOSA formula funding"

    def test_legislative_clock_phases(self):
        """Nebraska biennial clock has correct phases and period."""
        assert self.leg_clock.period_length == timedelta(days=730)
        phase_names = [p.phase_name for p in self.leg_clock.phases]
        assert "first_session" in phase_names
        assert "first_interim" in phase_names
        assert "second_session" in phase_names
        assert "second_interim" in phase_names

    def test_synchronize_teeosa_to_clock(self):
        """TEEOSA delivery can be synchronized to legislative clock."""
        teeosa = Delivery(
            delivery_type="money",
            delivery_content="TEEOSA appropriation",
            quantity=800_000_000,
            temporal_rate="annual",
        )
        self.service.add_delivery_to_matrix(
            self.matrix,
            self.legislature.id,
            self.school_districts.id,
            teeosa,
            "Formula funding",
        )

        self.service.synchronize_delivery_to_clock(
            self.leg_clock,
            self.legislature.id,
            self.school_districts.id,
            delivery_index=0,
        )

        key = f"{self.legislature.id}_{self.school_districts.id}"
        assert key in self.leg_clock.synchronized_deliveries

    def test_advance_legislative_clock(self):
        """Advancing legislative clock moves to next phase."""
        self.leg_clock.current_phase = "first_session"
        self.service.advance_clock(self.leg_clock)
        assert self.leg_clock.current_phase == "first_interim"
