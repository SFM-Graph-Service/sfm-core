"""
Temporal Clocks for Polychronic System Modeling.

Implements Hayden's graphical clock concept from:
- Hayden (1993): "Institutionalist Policymaking" - polychronic time concept
- Hayden (2006): "Real-Time for Social Processes" - multiple temporal scales

Different components operate on different time scales:
- Legislative cycles (biennial sessions)
- Budget years (annual appropriations)
- Fiscal years (July 1 - June 30)
- Academic years (August - May)
- Continuous processes (ongoing monitoring)

Clocks enable synchronization of deliveries that occur at different rates
and prevent temporal misalignment in policy analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid

from models.base_nodes import Node


@dataclass
class TemporalPhase:
    """
    Single phase within a temporal clock cycle.

    Example phases:
    - Legislative: "session", "interim"
    - Budget: "planning", "approval", "execution", "audit"
    - Academic: "fall_semester", "spring_semester", "summer"

    Attributes:
        phase_name: Name of this phase
        duration: How long this phase lasts
        start_date: When this phase begins (optional)
        activities: Key activities during this phase
    """

    phase_name: str
    duration: timedelta
    start_date: Optional[datetime] = None
    activities: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate phase attributes."""
        if not self.phase_name:
            raise ValueError("phase_name is required")
        if self.duration <= timedelta(0):
            raise ValueError("duration must be positive")


@dataclass
class TemporalClock(Node):
    """
    Hayden's graphical clock for polychronic system modeling.

    Different components operate on different time scales. Clocks synchronize
    deliveries and prevent temporal misalignment.

    Example clocks:
    - Legislative: 2-year cycle (session + interim)
    - Budget: Annual cycle (plan, approve, execute, audit)
    - Fiscal: July 1 - June 30 annual cycle
    - Academic: August - May school year

    Attributes:
        clock_name: Unique identifier (e.g., "nebraska_legislative_cycle")
        period_length: Full cycle duration
        phases: List of phases within cycle
        current_phase: Which phase we're currently in
        cycle_start_date: When current cycle began
        synchronized_components: Components using this clock
        synchronized_deliveries: Deliveries governed by this clock
    """

    clock_name: str = ""
    period_length: Optional[timedelta] = None

    # Phases within cycle
    phases: List[TemporalPhase] = field(default_factory=list)
    current_phase: Optional[str] = None

    # Timing information
    cycle_start_date: Optional[datetime] = None

    # Synchronization tracking
    synchronized_components: List[uuid.UUID] = field(default_factory=list)
    synchronized_deliveries: Dict[str, List[tuple]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate clock structure."""
        if self.clock_name and not self.label:
            # Use clock_name as label if not provided
            object.__setattr__(self, 'label', self.clock_name)

        # Validate phases sum to period_length
        if self.phases and self.period_length:
            total_duration = sum(
                (phase.duration for phase in self.phases),
                timedelta(0)
            )
            if total_duration != self.period_length:
                raise ValueError(
                    f"Phase durations ({total_duration}) must sum to period_length ({self.period_length})"
                )

        # Validate current_phase exists
        if self.current_phase:
            phase_names = [p.phase_name for p in self.phases]
            if self.current_phase not in phase_names:
                raise ValueError(
                    f"current_phase '{self.current_phase}' not in phases: {phase_names}"
                )

    def add_phase(self, phase: TemporalPhase) -> None:
        """
        Add phase to clock cycle.

        Args:
            phase: Phase to add

        Raises:
            ValueError: If phases would exceed period_length
        """
        if self.period_length:
            total_duration = sum(
                (p.duration for p in self.phases),
                timedelta(0)
            ) + phase.duration

            if total_duration > self.period_length:
                raise ValueError(
                    f"Adding phase would exceed period_length: {total_duration} > {self.period_length}"
                )

        self.phases.append(phase)

    def synchronize_component(self, component_id: uuid.UUID) -> None:
        """
        Synchronize component to this clock.

        Args:
            component_id: Component UUID to synchronize
        """
        if component_id not in self.synchronized_components:
            self.synchronized_components.append(component_id)

    def synchronize_delivery(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        delivery_index: int = 0
    ) -> None:
        """
        Synchronize specific delivery to this clock.

        Args:
            source_id: Source component UUID
            target_id: Target component UUID
            delivery_index: Index of delivery in cell's delivery list
        """
        key = f"{source_id}_{target_id}"
        if key not in self.synchronized_deliveries:
            self.synchronized_deliveries[key] = []

        self.synchronized_deliveries[key].append((source_id, target_id, delivery_index))

    def get_current_phase(self) -> Optional[TemporalPhase]:
        """
        Get current phase object.

        Returns:
            Current phase or None if not set
        """
        if not self.current_phase:
            return None

        for phase in self.phases:
            if phase.phase_name == self.current_phase:
                return phase

        return None

    def advance_phase(self) -> Optional[str]:
        """
        Advance to next phase in cycle.

        Returns:
            Name of new current phase or None if no phases
        """
        if not self.phases:
            return None

        if not self.current_phase:
            # Start at first phase
            self.current_phase = self.phases[0].phase_name
            return self.current_phase

        # Find current phase index
        phase_names = [p.phase_name for p in self.phases]
        try:
            current_idx = phase_names.index(self.current_phase)
        except ValueError:
            # Current phase not found, reset to first
            self.current_phase = self.phases[0].phase_name
            return self.current_phase

        # Advance to next phase (wrap around)
        next_idx = (current_idx + 1) % len(self.phases)
        self.current_phase = self.phases[next_idx].phase_name

        return self.current_phase

    def get_phase_schedule(self, start_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get phase schedule with start/end dates.

        Args:
            start_date: Cycle start date (uses cycle_start_date if not provided)

        Returns:
            List of dicts with phase_name, start_date, end_date, duration
        """
        if not self.phases:
            return []

        base_date = start_date or self.cycle_start_date or datetime.now()
        schedule = []
        current_date = base_date

        for phase in self.phases:
            end_date = current_date + phase.duration
            schedule.append({
                "phase_name": phase.phase_name,
                "start_date": current_date,
                "end_date": end_date,
                "duration": phase.duration,
                "activities": phase.activities
            })
            current_date = end_date

        return schedule

    def get_deliveries_due(self, matrix: Any) -> List[Dict]:
        """
        Get deliveries synchronized to this clock that are due in current phase.

        Args:
            matrix: SFMDeliveryMatrix to check for synchronized deliveries

        Returns:
            List of dicts with delivery info: {
                "delivery": Delivery object,
                "cell": SFMDeliveryCell,
                "source_id": UUID,
                "target_id": UUID,
                "delivery_index": int,
                "clock_name": str
            }

        Example:
            >>> deliveries_due = clock.get_deliveries_due(matrix)
            >>> for item in deliveries_due:
            ...     print(f"Due: {item['delivery'].delivery_content}")
        """
        deliveries_due = []

        # Check all synchronized deliveries
        for cell_key, delivery_refs in self.synchronized_deliveries.items():
            for source_id, target_id, delivery_index in delivery_refs:
                # Get cell from matrix
                cell = matrix.get_cell(source_id, target_id)
                if cell is None:
                    continue

                # Get delivery
                if delivery_index >= len(cell.deliveries):
                    continue

                delivery = cell.deliveries[delivery_index]

                # Check if delivery's temporal_clock matches this clock
                if delivery.temporal_clock == self.clock_name:
                    deliveries_due.append({
                        "delivery": delivery,
                        "cell": cell,
                        "source_id": source_id,
                        "target_id": target_id,
                        "delivery_index": delivery_index,
                        "clock_name": self.clock_name
                    })

        return deliveries_due


# Predefined clock templates for common use cases

def create_legislative_clock(
    state: str = "Nebraska",
    biennial: bool = True
) -> TemporalClock:
    """
    Create legislative cycle clock.

    Args:
        state: State name for labeling
        biennial: True for 2-year cycle, False for annual

    Returns:
        TemporalClock configured for legislative cycles
    """
    period = timedelta(days=730) if biennial else timedelta(days=365)

    clock = TemporalClock(
        label=f"{state} Legislative Cycle",
        clock_name=f"{state.lower()}_legislative_cycle",
        description=f"{'Biennial' if biennial else 'Annual'} legislative session cycle",
        period_length=period
    )

    if biennial:
        # Nebraska-style: 90-day session, then 270-day interim, then 60-day session, then 310-day interim
        # Total: 90 + 270 + 60 + 310 = 730 days
        clock.add_phase(TemporalPhase(
            phase_name="first_session",
            duration=timedelta(days=90),
            activities=["Bill introduction", "Committee hearings", "Floor debate", "Governor action"]
        ))
        clock.add_phase(TemporalPhase(
            phase_name="first_interim",
            duration=timedelta(days=270),
            activities=["Interim study", "Committee work", "Constituent service"]
        ))
        clock.add_phase(TemporalPhase(
            phase_name="second_session",
            duration=timedelta(days=60),
            activities=["Budget finalization", "Remaining bills", "Override attempts"]
        ))
        clock.add_phase(TemporalPhase(
            phase_name="second_interim",
            duration=timedelta(days=310),
            activities=["Transition to new biennium", "Interim study"]
        ))
    else:
        # Annual: 120-day session, 245-day interim
        clock.add_phase(TemporalPhase(
            phase_name="session",
            duration=timedelta(days=120),
            activities=["Legislation", "Budget", "Oversight"]
        ))
        clock.add_phase(TemporalPhase(
            phase_name="interim",
            duration=timedelta(days=245),
            activities=["Interim study", "Preparation"]
        ))

    clock.current_phase = clock.phases[0].phase_name
    return clock


def create_fiscal_year_clock(
    year_start_month: int = 7,
    year_start_day: int = 1
) -> TemporalClock:
    """
    Create fiscal year clock.

    Args:
        year_start_month: Month fiscal year starts (1-12)
        year_start_day: Day of month fiscal year starts

    Returns:
        TemporalClock configured for fiscal year
    """
    clock = TemporalClock(
        label="Fiscal Year",
        clock_name="fiscal_year",
        description=f"Annual fiscal year starting {year_start_month}/{year_start_day}",
        period_length=timedelta(days=365)
    )

    # Quarterly phases
    clock.add_phase(TemporalPhase(
        phase_name="Q1",
        duration=timedelta(days=91),
        activities=["First quarter execution"]
    ))
    clock.add_phase(TemporalPhase(
        phase_name="Q2",
        duration=timedelta(days=91),
        activities=["Second quarter execution"]
    ))
    clock.add_phase(TemporalPhase(
        phase_name="Q3",
        duration=timedelta(days=92),
        activities=["Third quarter execution"]
    ))
    clock.add_phase(TemporalPhase(
        phase_name="Q4",
        duration=timedelta(days=91),
        activities=["Fourth quarter execution", "Year-end closeout"]
    ))

    clock.current_phase = "Q1"
    return clock


def create_academic_year_clock() -> TemporalClock:
    """
    Create academic year clock (August - May).

    Returns:
        TemporalClock configured for K-12 academic year
    """
    clock = TemporalClock(
        label="Academic Year",
        clock_name="academic_year",
        description="K-12 school year (August - May)",
        period_length=timedelta(days=280)  # ~9 months
    )

    clock.add_phase(TemporalPhase(
        phase_name="fall_semester",
        duration=timedelta(days=140),
        activities=["Fall instruction", "Fall assessments"]
    ))
    clock.add_phase(TemporalPhase(
        phase_name="spring_semester",
        duration=timedelta(days=140),
        activities=["Spring instruction", "Spring assessments", "Year-end closeout"]
    ))

    clock.current_phase = "fall_semester"
    return clock
