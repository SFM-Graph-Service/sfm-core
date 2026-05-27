"""
Tests for temporal modeling and threshold monitoring.

Tests cover:
- Temporal clocks and phases
- Polychronic system modeling
- Threshold monitoring
- Clock templates (legislative, fiscal, academic)
"""

import pytest
import uuid
from datetime import datetime, timedelta

from api.sfm_service import SFMService, ThresholdAlert
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix
from models.temporal_clocks import (
    TemporalClock,
    TemporalPhase,
    create_legislative_clock,
    create_fiscal_year_clock,
    create_academic_year_clock
)


class TestTemporalPhase:
    """Test TemporalPhase class."""

    def test_create_basic_phase(self):
        """Test creating basic phase."""
        phase = TemporalPhase(
            phase_name="session",
            duration=timedelta(days=90)
        )

        assert phase.phase_name == "session"
        assert phase.duration == timedelta(days=90)
        assert phase.start_date is None
        assert phase.activities == []

    def test_create_phase_with_activities(self):
        """Test creating phase with activities."""
        phase = TemporalPhase(
            phase_name="planning",
            duration=timedelta(days=60),
            activities=["Budget preparation", "Stakeholder meetings"]
        )

        assert len(phase.activities) == 2
        assert "Budget preparation" in phase.activities

    def test_phase_requires_name(self):
        """Test phase requires name."""
        with pytest.raises(ValueError, match="phase_name is required"):
            TemporalPhase(
                phase_name="",
                duration=timedelta(days=30)
            )

    def test_phase_requires_positive_duration(self):
        """Test phase requires positive duration."""
        with pytest.raises(ValueError, match="duration must be positive"):
            TemporalPhase(
                phase_name="test",
                duration=timedelta(days=0)
            )


class TestTemporalClock:
    """Test TemporalClock class."""

    def test_create_basic_clock(self):
        """Test creating basic clock."""
        clock = TemporalClock(
            label="Test Clock",
            clock_name="test_clock",
            period_length=timedelta(days=365)
        )

        assert clock.label == "Test Clock"
        assert clock.clock_name == "test_clock"
        assert clock.period_length == timedelta(days=365)
        assert clock.phases == []

    def test_clock_uses_name_as_label(self):
        """Test clock uses clock_name as label if label not provided."""
        clock = TemporalClock(
            label="Fiscal Year",  # label is required from Node base class
            clock_name="fiscal_year",
            period_length=timedelta(days=365)
        )

        assert clock.label == "Fiscal Year"

    def test_add_phases_to_clock(self):
        """Test adding phases to clock."""
        clock = TemporalClock(
            label="Annual Cycle",
            period_length=timedelta(days=365)
        )

        phase1 = TemporalPhase("Q1", timedelta(days=91))
        phase2 = TemporalPhase("Q2", timedelta(days=91))

        clock.add_phase(phase1)
        clock.add_phase(phase2)

        assert len(clock.phases) == 2
        assert clock.phases[0].phase_name == "Q1"

    def test_phases_must_sum_to_period(self):
        """Test phases must sum to period_length."""
        phase1 = TemporalPhase("P1", timedelta(days=100))
        phase2 = TemporalPhase("P2", timedelta(days=100))

        with pytest.raises(ValueError, match="must sum to period_length"):
            TemporalClock(
                label="Test",
                period_length=timedelta(days=365),
                phases=[phase1, phase2]
            )

    def test_add_phase_validates_total(self):
        """Test adding phase validates total duration."""
        clock = TemporalClock(
            label="Test",
            period_length=timedelta(days=100)
        )

        clock.add_phase(TemporalPhase("P1", timedelta(days=80)))

        # Adding another 30 days would exceed 100
        with pytest.raises(ValueError, match="exceed period_length"):
            clock.add_phase(TemporalPhase("P2", timedelta(days=30)))

    def test_synchronize_component(self):
        """Test synchronizing component to clock."""
        clock = TemporalClock(
            label="Test Clock",
            period_length=timedelta(days=365)
        )

        comp_id = uuid.uuid4()
        clock.synchronize_component(comp_id)

        assert comp_id in clock.synchronized_components

    def test_synchronize_delivery(self):
        """Test synchronizing delivery to clock."""
        clock = TemporalClock(
            label="Test Clock",
            period_length=timedelta(days=365)
        )

        src_id = uuid.uuid4()
        tgt_id = uuid.uuid4()

        clock.synchronize_delivery(src_id, tgt_id, delivery_index=0)

        key = f"{src_id}_{tgt_id}"
        assert key in clock.synchronized_deliveries
        assert len(clock.synchronized_deliveries[key]) == 1

    def test_get_current_phase(self):
        """Test getting current phase object."""
        phase1 = TemporalPhase("session", timedelta(days=180))
        phase2 = TemporalPhase("interim", timedelta(days=185))

        clock = TemporalClock(
            label="Test",
            period_length=timedelta(days=365),
            phases=[phase1, phase2],
            current_phase="session"
        )

        current = clock.get_current_phase()
        assert current.phase_name == "session"
        assert current.duration == timedelta(days=180)

    def test_advance_phase(self):
        """Test advancing to next phase."""
        phase1 = TemporalPhase("Q1", timedelta(days=91))
        phase2 = TemporalPhase("Q2", timedelta(days=91))
        phase3 = TemporalPhase("Q3", timedelta(days=92))
        phase4 = TemporalPhase("Q4", timedelta(days=91))

        clock = TemporalClock(
            label="Fiscal Year",
            period_length=timedelta(days=365),
            phases=[phase1, phase2, phase3, phase4]
        )

        # Start unset - should start at first phase
        next_phase = clock.advance_phase()
        assert next_phase == "Q1"

        # Advance to Q2
        next_phase = clock.advance_phase()
        assert next_phase == "Q2"

        # Advance to Q3
        next_phase = clock.advance_phase()
        assert next_phase == "Q3"

        # Advance to Q4
        next_phase = clock.advance_phase()
        assert next_phase == "Q4"

        # Wrap around to Q1
        next_phase = clock.advance_phase()
        assert next_phase == "Q1"

    def test_get_phase_schedule(self):
        """Test getting phase schedule with dates."""
        phase1 = TemporalPhase("session", timedelta(days=120))
        phase2 = TemporalPhase("interim", timedelta(days=245))

        clock = TemporalClock(
            label="Legislative",
            period_length=timedelta(days=365),
            phases=[phase1, phase2]
        )

        start_date = datetime(2025, 1, 1)
        schedule = clock.get_phase_schedule(start_date)

        assert len(schedule) == 2
        assert schedule[0]["phase_name"] == "session"
        assert schedule[0]["start_date"] == datetime(2025, 1, 1)
        assert schedule[0]["end_date"] == datetime(2025, 5, 1)

        assert schedule[1]["phase_name"] == "interim"
        assert schedule[1]["start_date"] == datetime(2025, 5, 1)


class TestClockTemplates:
    """Test predefined clock templates."""

    def test_legislative_clock_biennial(self):
        """Test biennial legislative clock."""
        clock = create_legislative_clock(state="Nebraska", biennial=True)

        assert "Nebraska" in clock.label
        assert clock.period_length == timedelta(days=730)
        assert len(clock.phases) == 4
        assert clock.phases[0].phase_name == "first_session"
        assert clock.current_phase == "first_session"

    def test_legislative_clock_annual(self):
        """Test annual legislative clock."""
        clock = create_legislative_clock(state="Texas", biennial=False)

        assert "Texas" in clock.label
        assert clock.period_length == timedelta(days=365)
        assert len(clock.phases) == 2
        assert clock.phases[0].phase_name == "session"

    def test_fiscal_year_clock(self):
        """Test fiscal year clock."""
        clock = create_fiscal_year_clock(year_start_month=7, year_start_day=1)

        assert clock.label == "Fiscal Year"
        assert clock.period_length == timedelta(days=365)
        assert len(clock.phases) == 4
        assert clock.phases[0].phase_name == "Q1"
        assert clock.current_phase == "Q1"

    def test_academic_year_clock(self):
        """Test academic year clock."""
        clock = create_academic_year_clock()

        assert clock.label == "Academic Year"
        assert clock.period_length == timedelta(days=280)
        assert len(clock.phases) == 2
        assert clock.phases[0].phase_name == "fall_semester"
        assert clock.current_phase == "fall_semester"


class TestThresholdMonitoring:
    """Test threshold monitoring system."""

    def setup_method(self):
        """Setup test service and matrix."""
        self.service = SFMService()

        # Create components
        self.comp_a = Node(label="Component A")
        self.comp_b = Node(label="Component B")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)

        # Create matrix
        self.matrix = self.service.create_delivery_matrix(
            label="Test Matrix"
        )
        self.matrix.add_component(self.comp_a.id)
        self.matrix.add_component(self.comp_b.id)

    def test_threshold_monitoring_above(self):
        """Test monitoring threshold with 'above' direction."""
        delivery = Delivery(
            delivery_type="pollution",
            delivery_content="CO2 emissions",
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
            cell_description="A delivers pollution to B"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 1
        assert alerts[0].current_value == 550
        assert alerts[0].threshold == 500
        assert alerts[0].direction == "exceeded"

    def test_threshold_monitoring_below(self):
        """Test monitoring threshold with 'below' direction."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Budget allocation",
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
            cell_description="A funds B"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 1
        assert alerts[0].current_value == 75_000_000
        assert alerts[0].threshold == 100_000_000
        assert alerts[0].direction == "below"

    def test_no_alerts_when_within_threshold(self):
        """Test no alerts when values within threshold."""
        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment",
            quantity=50_000,
            threshold=100_000,
            threshold_direction="above"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Payment delivery"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 0

    def test_no_alerts_when_no_threshold(self):
        """Test no alerts when delivery has no threshold."""
        delivery = Delivery(
            delivery_type="rule",
            delivery_content="Regulation",
            quantity=100
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Regulation delivery"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 0

    def test_multiple_alerts(self):
        """Test multiple threshold violations."""
        delivery1 = Delivery(
            delivery_type="pollution",
            delivery_content="Emissions",
            quantity=600,
            threshold=500,
            threshold_direction="above"
        )

        delivery2 = Delivery(
            delivery_type="money",
            delivery_content="Budget",
            quantity=50_000_000,
            threshold=100_000_000,
            threshold_direction="below"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery1,
            cell_description="Deliveries from A to B"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery2,
            cell_description="Deliveries from A to B"
        )

        alerts = self.service.check_delivery_thresholds(self.matrix)

        assert len(alerts) == 2


class TestTemporalClockService:
    """Test temporal clock service methods."""

    def setup_method(self):
        """Setup test service."""
        self.service = SFMService()

    def test_create_temporal_clock(self):
        """Test creating clock via service."""
        clock = self.service.create_temporal_clock(
            clock_name="test_clock",
            label="Test Clock",
            description="Test clock for unit tests",
            period_length=timedelta(days=365)
        )

        assert clock.label == "Test Clock"
        assert clock.clock_name == "test_clock"
        assert clock.period_length == timedelta(days=365)

    def test_synchronize_delivery_to_clock(self):
        """Test synchronizing delivery to clock."""
        clock = self.service.create_temporal_clock(
            clock_name="fiscal_year",
            label="Fiscal Year",
            period_length=timedelta(days=365)
        )

        src_id = uuid.uuid4()
        tgt_id = uuid.uuid4()

        self.service.synchronize_delivery_to_clock(
            clock, src_id, tgt_id, delivery_index=0
        )

        key = f"{src_id}_{tgt_id}"
        assert key in clock.synchronized_deliveries
