"""
Nebraska K-12 Education Finance with Temporal Modeling

Extends the base Nebraska K-12 case study (Hoffman & Hayden 2007) with
Hayden's polychronic temporal modeling (1993):
- Legislative cycle clock (biennial Nebraska sessions)
- Fiscal year clock (July 1 - June 30)
- Academic year clock (August - May)
- Threshold monitoring for funding equity alerts
- Temporal rate annotation for all deliveries

References:
    Hayden, F. G. (1987). "Policy Analysis with the Social Fabric Matrix Approach."
    Journal of Economic Issues, 21(3), 1092-1108.
    (Real-time monitoring concept)

    Hayden, F. G. (1993). "Institutionalist Policymaking." In M. Tool (Ed.),
    Institutional Economics: Theory, Method, Policy (pp. 283-333). Kluwer.
    (Polychronic systems and graphical clocks)

    Hoffman, S., & Hayden, F. G. (2007). "Equilibrium and Emergence for Social
    Fabric Matrix Analysis." Journal of Economic Issues, 41(4), 1105-1126.
    (Nebraska K-12 temporal cycles)

Components:
    - State Legislature (biennial sessions)
    - Department of Education (continuous administration)
    - School Districts (academic-year cycle)
    - Taxpayers (fiscal-year cycle)
    - Students (academic-year cycle)

Temporal Clocks:
    1. Nebraska Legislative Cycle: 730-day biennial (first/second session + interims)
    2. State Fiscal Year: July 1 - June 30, quarterly phases
    3. K-12 Academic Year: August - May, fall/spring semesters

Threshold Monitoring:
    - TEEOSA appropriation: Alert if below $750M equity threshold
    - Per-pupil spending: Alert if any district falls below $8,000/student
    - CO2 monitoring: Not in education, but demonstrates environmental use case
"""

from datetime import timedelta

from api.sfm_service import SFMService, VALID_TEMPORAL_RATES, validate_temporal_rate
from models import Node
from models.delivery_matrix import Delivery
from models.temporal_clocks import (
    TemporalPhase,
    create_legislative_clock,
    create_fiscal_year_clock,
    create_academic_year_clock,
)


def build_nebraska_k12_temporal_model():
    """
    Build Nebraska K-12 SFM with full temporal modeling.

    Returns:
        Tuple of (service, matrix, clocks dict) for further analysis
    """
    service = SFMService()

    # -------------------------------------------------------------------------
    # Institutional Components
    # -------------------------------------------------------------------------
    legislature = Node(
        label="Nebraska Legislature",
        description="Unicameral legislature — appropriates TEEOSA formula funds"
    )
    dept_ed = Node(
        label="Nebraska Dept of Education",
        description="State education agency — administers TEEOSA implementation"
    )
    school_districts = Node(
        label="Nebraska School Districts",
        description="~244 districts receiving formula-based state aid"
    )
    taxpayers = Node(
        label="Nebraska Taxpayers",
        description="Property tax base — primary local revenue source"
    )
    students = Node(
        label="Nebraska Students",
        description="~320,000 K-12 students receiving educational services"
    )

    for node in [legislature, dept_ed, school_districts, taxpayers, students]:
        service.create_node(node)

    # -------------------------------------------------------------------------
    # Delivery Matrix
    # -------------------------------------------------------------------------
    matrix = service.create_delivery_matrix(
        label="Nebraska K-12 Finance SFM — Temporal",
        description=(
            "Polychronic SFM with legislative, fiscal, and academic clocks. "
            "Hoffman & Hayden (2007) case study extended with Hayden (1993) temporal modeling."
        )
    )
    for node in [legislature, dept_ed, school_districts, taxpayers, students]:
        matrix.add_component(node.id)

    # -------------------------------------------------------------------------
    # Deliveries with Temporal Annotations
    # -------------------------------------------------------------------------

    # Legislature → School Districts: TEEOSA formula funding
    teeosa_delivery = Delivery(
        delivery_type="money",
        delivery_content="TEEOSA equalization aid (~$800M annually)",
        quantity=800_000_000,
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        threshold=750_000_000,      # Equity threshold: alert if funding falls below
        threshold_direction="below",
        certainty=0.95,
        data_sources=["Hoffman & Hayden 2007", "NDE Annual Report 2023"]
    )
    assert validate_temporal_rate(teeosa_delivery), "temporal_rate must be valid"

    teeosa_rule = Delivery(
        delivery_type="rule",
        delivery_content="TEEOSA formula rules and compliance requirements",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.99,
        data_sources=["NRS 79-1001 et seq."]
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        school_districts.id,
        teeosa_delivery,
        "Legislature provides formula aid and compliance rules to school districts"
    )
    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        school_districts.id,
        teeosa_rule,
        "Legislature provides formula aid and compliance rules to school districts"
    )

    # Legislature → Dept of Education: oversight and administrative budget
    admin_budget = Delivery(
        delivery_type="money",
        delivery_content="NDE administrative budget",
        quantity=45_000_000,
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.90,
    )
    oversight_authority = Delivery(
        delivery_type="authority",
        delivery_content="Audit and enforcement authority",
        temporal_rate="continuous",
        certainty=0.99,
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        dept_ed.id,
        admin_budget,
        "Legislature funds and empowers Dept of Education"
    )
    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        dept_ed.id,
        oversight_authority,
        "Legislature funds and empowers Dept of Education"
    )

    # Dept of Education → School Districts: standards and reporting
    standards_delivery = Delivery(
        delivery_type="rule",
        delivery_content="Academic standards and curriculum requirements",
        temporal_rate="annual",
        temporal_clock="academic_year",
        certainty=0.95,
    )
    report_requirement = Delivery(
        delivery_type="information",
        delivery_content="Annual financial and academic reporting requirements",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.98,
    )

    service.add_delivery_to_matrix(
        matrix,
        dept_ed.id,
        school_districts.id,
        standards_delivery,
        "NDE sets standards and reporting requirements for districts"
    )
    service.add_delivery_to_matrix(
        matrix,
        dept_ed.id,
        school_districts.id,
        report_requirement,
        "NDE sets standards and reporting requirements for districts"
    )

    # Taxpayers → Legislature: property tax revenue
    property_tax = Delivery(
        delivery_type="money",
        delivery_content="Property tax levy revenue ($1.5B local share)",
        quantity=1_500_000_000,
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.85,
        data_sources=["NDE School Finance Report 2023"]
    )

    service.add_delivery_to_matrix(
        matrix,
        taxpayers.id,
        legislature.id,
        property_tax,
        "Taxpayers fund state education through property tax levy"
    )

    # School Districts → Students: educational services
    education_services = Delivery(
        delivery_type="information",
        delivery_content="K-12 educational instruction and services",
        temporal_rate="annual",
        temporal_clock="academic_year",
        certainty=0.99,
    )
    per_pupil_funding = Delivery(
        delivery_type="money",
        delivery_content="Per-pupil expenditure (~$11,000/student)",
        quantity=11_000,
        units="USD/student/year",
        temporal_rate="annual",
        temporal_clock="academic_year",
        threshold=8_000,            # Alert if per-pupil drops below adequacy threshold
        threshold_direction="below",
        certainty=0.90,
        data_sources=["NCES 2023 State Finance Data"]
    )

    service.add_delivery_to_matrix(
        matrix,
        school_districts.id,
        students.id,
        education_services,
        "School districts deliver K-12 educational services to students"
    )
    service.add_delivery_to_matrix(
        matrix,
        school_districts.id,
        students.id,
        per_pupil_funding,
        "School districts deliver K-12 educational services to students"
    )

    # School Districts → Dept of Education: compliance reporting
    compliance_report = Delivery(
        delivery_type="information",
        delivery_content="Annual enrollment and financial compliance reports",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.97,
    )

    service.add_delivery_to_matrix(
        matrix,
        school_districts.id,
        dept_ed.id,
        compliance_report,
        "School districts report enrollment and financial data to NDE"
    )

    # -------------------------------------------------------------------------
    # Temporal Clocks
    # -------------------------------------------------------------------------

    # Nebraska biennial legislative cycle (Hayden 1993 polychronic concept)
    leg_clock = create_legislative_clock(state="Nebraska", biennial=True)
    service.repository.create_node(leg_clock)

    # State fiscal year (July 1 – June 30)
    fiscal_clock = create_fiscal_year_clock(year_start_month=7, year_start_day=1)
    service.repository.create_node(fiscal_clock)

    # K-12 academic year (August – May)
    academic_clock = create_academic_year_clock()
    service.repository.create_node(academic_clock)

    # -------------------------------------------------------------------------
    # Synchronize Deliveries to Clocks
    # -------------------------------------------------------------------------

    # TEEOSA funding tied to legislative and fiscal cycles
    service.synchronize_delivery_to_clock(
        leg_clock,
        legislature.id,
        school_districts.id,
        delivery_index=0  # TEEOSA money delivery
    )
    service.synchronize_delivery_to_clock(
        fiscal_clock,
        legislature.id,
        school_districts.id,
        delivery_index=0  # TEEOSA money delivery
    )

    # Academic services tied to academic year
    service.synchronize_delivery_to_clock(
        academic_clock,
        school_districts.id,
        students.id,
        delivery_index=0  # Education services
    )

    clocks = {
        "legislative": leg_clock,
        "fiscal": fiscal_clock,
        "academic": academic_clock,
    }

    return service, matrix, clocks


def demonstrate_threshold_monitoring(service, matrix):
    """
    Demonstrate Hayden 1987 real-time threshold monitoring.

    Shows how policy makers can monitor TEEOSA equity thresholds.
    """
    print("\n" + "=" * 60)
    print("THRESHOLD MONITORING — Hayden (1987) Real-Time Concept")
    print("=" * 60)

    alerts = service.check_delivery_thresholds(matrix)

    if alerts:
        print(f"\n⚠️  {len(alerts)} threshold alert(s) detected:\n")
        for alert in alerts:
            print(
                f"  [{alert.direction.upper()}] "
                f"{alert.source_component_label} → {alert.target_component_label}"
            )
            print(
                f"    {alert.delivery.delivery_content}: "
                f"{alert.current_value:,.0f} {alert.direction} "
                f"threshold {alert.threshold:,.0f}"
            )
            if alert.delivery.units:
                print(f"    Units: {alert.delivery.units}")
            print()
    else:
        print("\n✓ All deliveries within thresholds.\n")

    return alerts


def demonstrate_budget_cut_scenario(service, matrix, legislature, school_districts):
    """
    Simulate a TEEOSA budget cut and demonstrate threshold alert.

    Hayden (1987): Real-time monitoring triggers policy response.
    """
    print("\n" + "=" * 60)
    print("BUDGET CUT SCENARIO — update_delivery_quantity()")
    print("=" * 60)

    # Simulate legislature cutting TEEOSA by $100M
    print("\nSimulating $100M budget cut: $800M → $700M TEEOSA funding...")

    alert = service.update_delivery_quantity(
        matrix,
        legislature.id,
        school_districts.id,
        delivery_index=0,
        new_quantity=700_000_000,
    )

    if alert:
        print(f"\n⚠️  POLICY ALERT: TEEOSA funding fell below equity threshold!")
        print(f"   Threshold: ${alert.threshold:,.0f}")
        print(f"   Current: ${alert.current_value:,.0f}")
        print(f"   Direction: {alert.direction}")
        print(f"   Matrix: {alert.matrix_id}")
        print(f"   {alert.source_component_label} → {alert.target_component_label}")
    else:
        print("   No threshold crossed.")

    return alert


def demonstrate_temporal_rates(service, matrix):
    """
    Filter deliveries by temporal rate.

    Useful for batch processing at fiscal year end.
    """
    print("\n" + "=" * 60)
    print("TEMPORAL RATE FILTERING — get_deliveries_by_temporal_rate()")
    print("=" * 60)

    for rate in ["annual", "continuous", "monthly"]:
        results = service.get_deliveries_by_temporal_rate(matrix, rate)
        print(f"\n  Rate '{rate}': {len(results)} deliveries")
        for cell, delivery in results:
            print(f"    - {delivery.delivery_content[:60]}")


def demonstrate_clock_advance(service, matrix, clocks):
    """
    Advance the legislative clock and check for due deliveries.

    Hayden (1993): Clock advance triggers synchronized delivery review.
    """
    print("\n" + "=" * 60)
    print("CLOCK ADVANCE — advance_clock() (Hayden 1993 Polychronic)")
    print("=" * 60)

    leg_clock = clocks["legislative"]
    print(f"\nCurrent legislative phase: {leg_clock.current_phase}")

    alerts = service.advance_clock(leg_clock, matrix)
    print(f"New legislative phase: {leg_clock.current_phase}")

    if alerts:
        print(f"\n{len(alerts)} delivery alert(s) triggered by clock advance:")
        for alert in alerts:
            print(
                f"  [{alert.direction}] {alert.delivery.delivery_content[:50]}"
            )
    else:
        print("No threshold alerts triggered by clock advance.")


def main():
    """Run complete Nebraska K-12 temporal modeling demonstration."""
    print("Nebraska K-12 Education Finance — Temporal Modeling")
    print("Based on Hoffman & Hayden (2007) with Hayden (1993) clocks")
    print()

    # Build model
    service, matrix, clocks = build_nebraska_k12_temporal_model()

    # Get component nodes for scenario functions
    all_nodes = service.list_nodes()
    legislature = next(n for n in all_nodes if n.label == "Nebraska Legislature")
    school_districts = next(n for n in all_nodes if n.label == "Nebraska School Districts")

    print(f"Matrix built: {len(matrix.components)} components, "
          f"{len(matrix.cells)} cells, "
          f"{sum(len(c.deliveries) for c in matrix.cells.values())} deliveries")

    # Show temporal rates
    print("\nTemporal rate summary:")
    for rate in ["annual", "continuous"]:
        results = service.get_deliveries_by_temporal_rate(matrix, rate)
        print(f"  {rate}: {len(results)} deliveries")

    # Initial threshold check (should be clean)
    demonstrate_threshold_monitoring(service, matrix)

    # Budget cut scenario — triggers threshold alert
    demonstrate_budget_cut_scenario(service, matrix, legislature, school_districts)

    # Temporal rate filtering
    demonstrate_temporal_rates(service, matrix)

    # Clock advance
    demonstrate_clock_advance(service, matrix, clocks)

    print("\nDemonstration complete.")
    print("\nReferences:")
    print("  Hayden (1987): Real-time monitoring concept")
    print("  Hayden (1993): Polychronic systems and graphical clocks")
    print("  Hoffman & Hayden (2007): Nebraska K-12 temporal cycles")


if __name__ == "__main__":
    main()
