"""
Nebraska K-12 Education Finance with Temporal Modeling

Demonstrates Hayden's polychronic modeling (1987, 1993) using Nebraska TEEOSA
formula synchronized to biennial legislative cycle.

Key Features:
- Legislative clock (biennial sessions)
- Fiscal year clock (July 1 - June 30)
- Academic year clock (August - May)
- Threshold monitoring for funding adequacy
- Multiple temporal scales operating simultaneously

Based on:
- Hayden (1987): "Tax Expenditure Incidence"
- Hayden (1993): "Institutionalist Policymaking"
- Hayden (2006): "Policymaking for a Good Society"

Nebraska TEEOSA (Tax Equity and Educational Opportunities Support Act):
- Legislature appropriates funding biennially
- State equalizes local property tax bases
- Districts receive varying amounts based on needs and resources
"""

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from models.temporal_clocks import (
    create_legislative_clock,
    create_fiscal_year_clock,
    create_academic_year_clock,
)


def create_nebraska_k12_temporal_matrix():
    """
    Create Nebraska K-12 education finance matrix with temporal modeling.

    Returns:
        Tuple of (service, matrix, clocks_dict)
    """
    service = SFMService()

    # ========================
    # Create Components
    # ========================

    legislature = Node(
        label="Nebraska Legislature",
        description="Unicameral legislature, biennial sessions"
    )

    state_dept_ed = Node(
        label="Nebraska Department of Education",
        description="Administers TEEOSA formula, distributes state aid"
    )

    school_district = Node(
        label="Local School District",
        description="Provides K-12 education, funded by state aid + local property taxes"
    )

    property_taxpayers = Node(
        label="Local Property Taxpayers",
        description="Fund local share through property taxes"
    )

    students = Node(
        label="K-12 Students",
        description="Receive educational services"
    )

    service.create_node(legislature)
    service.create_node(state_dept_ed)
    service.create_node(school_district)
    service.create_node(property_taxpayers)
    service.create_node(students)

    # ========================
    # Create Delivery Matrix
    # ========================

    matrix = service.create_delivery_matrix(
        label="Nebraska K-12 Education Finance (Temporal)",
        description="Demonstrates polychronic modeling with multiple temporal clocks",
        matrix_scope="state"
    )

    matrix.add_component(legislature.id)
    matrix.add_component(state_dept_ed.id)
    matrix.add_component(school_district.id)
    matrix.add_component(property_taxpayers.id)
    matrix.add_component(students.id)

    # ========================
    # Create Temporal Clocks
    # ========================

    # Legislative cycle - biennial sessions
    legislative_clock = create_legislative_clock(state="Nebraska", biennial=True)
    legislative_clock = service.create_temporal_clock(
        clock_name=legislative_clock.clock_name,
        label=legislative_clock.label,
        description=legislative_clock.description,
        period_length=legislative_clock.period_length,
        phases=legislative_clock.phases
    )
    legislative_clock.current_phase = "first_session"

    # Fiscal year - July 1 to June 30
    fiscal_clock = create_fiscal_year_clock(year_start_month=7, year_start_day=1)
    fiscal_clock = service.create_temporal_clock(
        clock_name=fiscal_clock.clock_name,
        label=fiscal_clock.label,
        description=fiscal_clock.description,
        period_length=fiscal_clock.period_length,
        phases=fiscal_clock.phases
    )
    fiscal_clock.current_phase = "Q1"

    # Academic year - August to May
    academic_clock = create_academic_year_clock()
    academic_clock = service.create_temporal_clock(
        clock_name=academic_clock.clock_name,
        label=academic_clock.label,
        description=academic_clock.description,
        period_length=academic_clock.period_length,
        phases=academic_clock.phases
    )
    academic_clock.current_phase = "fall_semester"

    # ========================
    # Add Deliveries with Temporal Rates
    # ========================

    # Legislature → State Dept of Ed: TEEOSA appropriation
    # Synchronized to legislative cycle, with threshold for adequacy
    teeosa_appropriation = Delivery(
        delivery_type="money",
        delivery_content="TEEOSA biennial appropriation ($1.6B over 2 years)",
        quantity=1_600_000_000,
        units="USD per biennium",
        temporal_rate="biennial",
        temporal_clock="nebraska_legislative_cycle",
        threshold=1_500_000_000,  # Minimum adequacy threshold
        threshold_direction="below",
        certainty=0.95,
        data_sources=["LB 389 (2023)", "Nebraska Department of Education"]
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        state_dept_ed.id,
        teeosa_appropriation,
        cell_description="Legislature appropriates state aid for K-12 education through TEEOSA formula. "
                         "Amount set biennially during legislative sessions. Threshold monitors adequacy "
                         "per constitutional requirement."
    )

    # Synchronize to legislative clock
    service.synchronize_delivery_to_clock(
        legislative_clock, legislature.id, state_dept_ed.id, 0
    )

    # Legislature → School District: Rules and accountability
    education_statutes = Delivery(
        delivery_type="rule",
        delivery_content="Education statutes and accountability requirements",
        temporal_rate="legislative_cycle",
        temporal_clock="nebraska_legislative_cycle",
        certainty=1.0,
        data_sources=["Neb. Rev. Stat. §79-1001 et seq."]
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        school_district.id,
        education_statutes,
        cell_description="Legislature establishes education policy, graduation requirements, "
                         "and accountability standards through biennial sessions."
    )

    # State Dept of Ed → School District: Distributed state aid
    # Synchronized to fiscal year (quarterly payments)
    state_aid_distribution = Delivery(
        delivery_type="money",
        delivery_content="TEEOSA state aid distribution (equalization payments)",
        quantity=200_000_000,  # Example district's annual allocation
        units="USD/year",
        temporal_rate="quarterly",
        temporal_clock="fiscal_year",
        threshold=180_000_000,  # 90% threshold
        threshold_direction="below",
        certainty=0.9,
        data_sources=["NDE TEEOSA calculation worksheets"]
    )

    service.add_delivery_to_matrix(
        matrix,
        state_dept_ed.id,
        school_district.id,
        state_aid_distribution,
        cell_description="Department of Education calculates and distributes state aid quarterly "
                         "based on TEEOSA formula considering local resources, student needs, "
                         "and equalization targets."
    )

    # Synchronize to fiscal year clock
    service.synchronize_delivery_to_clock(
        fiscal_clock, state_dept_ed.id, school_district.id, 0
    )

    # State Dept of Ed → School District: Guidance and oversight
    administrative_guidance = Delivery(
        delivery_type="information",
        delivery_content="Administrative guidance, compliance monitoring, technical assistance",
        temporal_rate="continuous",
        certainty=0.85,
        data_sources=["NDE website", "Rule 10 and Rule 11"]
    )

    service.add_delivery_to_matrix(
        matrix,
        state_dept_ed.id,
        school_district.id,
        administrative_guidance,
        cell_description="NDE provides ongoing administrative support, monitors compliance with "
                         "state and federal requirements, and delivers technical assistance."
    )

    # Property Taxpayers → School District: Local property tax revenue
    # Synchronized to fiscal year
    local_property_tax = Delivery(
        delivery_type="money",
        delivery_content="Local property tax revenue for education",
        quantity=150_000_000,  # Example district
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        threshold=100_000_000,  # Minimum local effort
        threshold_direction="below",
        certainty=0.8,
        data_sources=["County Assessor", "School District levy"]
    )

    service.add_delivery_to_matrix(
        matrix,
        property_taxpayers.id,
        school_district.id,
        local_property_tax,
        cell_description="Local property taxpayers fund local share of education costs. "
                         "TEEOSA formula equalizes varying local property tax bases."
    )

    # School District → Students: Educational services
    # Synchronized to academic year
    educational_services = Delivery(
        delivery_type="service",
        delivery_content="K-12 educational instruction, facilities, transportation, nutrition",
        temporal_rate="academic_year",
        temporal_clock="academic_year",
        certainty=0.95,
        data_sources=["District Annual Report"]
    )

    service.add_delivery_to_matrix(
        matrix,
        school_district.id,
        students.id,
        educational_services,
        cell_description="School district provides comprehensive K-12 education services during "
                         "academic year (August-May). Services include instruction, facilities, "
                         "transportation, meals, and special education."
    )

    # Synchronize to academic clock
    service.synchronize_delivery_to_clock(
        academic_clock, school_district.id, students.id, 0
    )

    # School District → State Dept of Ed: Reporting and data
    district_reporting = Delivery(
        delivery_type="information",
        delivery_content="Student enrollment, attendance, assessment, financial data",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.95,
        data_sources=["School Finance Report", "Student Information System"]
    )

    service.add_delivery_to_matrix(
        matrix,
        school_district.id,
        state_dept_ed.id,
        district_reporting,
        cell_description="Districts report student counts, assessment results, attendance, "
                         "and financial data annually. Data drives TEEOSA calculations."
    )

    # Students → School District: Attendance and participation
    student_participation = Delivery(
        delivery_type="participation",
        delivery_content="Student attendance, engagement, academic performance",
        temporal_rate="daily",
        temporal_clock="academic_year",
        certainty=0.85,
        data_sources=["Attendance records", "Grade reports"]
    )

    service.add_delivery_to_matrix(
        matrix,
        students.id,
        school_district.id,
        student_participation,
        cell_description="Students attend school daily during academic year. Participation "
                         "generates state aid through average daily membership (ADM) calculations."
    )

    # ========================
    # Validate Matrix
    # ========================

    errors = service.validate_delivery_matrix(matrix)
    if errors:
        print("\n⚠️  Matrix Validation Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Matrix structure valid per Hayden methodology")

    return service, matrix, {
        "legislative": legislative_clock,
        "fiscal": fiscal_clock,
        "academic": academic_clock
    }


def demonstrate_temporal_monitoring():
    """Demonstrate temporal modeling features."""
    print("\n" + "="*80)
    print("Nebraska K-12 Education Finance: Polychronic Temporal Modeling")
    print("Per Hayden (1987, 1993) - Multiple Time Scales Operating Simultaneously")
    print("="*80)

    service, matrix, clocks = create_nebraska_k12_temporal_matrix()

    print(f"\n📊 Matrix: {matrix.label}")
    print(f"   Components: {len(matrix.components)}")
    print(f"   Cells: {len(matrix.cells)}")
    print(f"   Non-empty cells: {len(matrix.get_non_empty_cells())}")

    # ========================
    # Show Temporal Clocks
    # ========================

    print("\n⏰ Temporal Clocks (Polychronic System):")
    print(f"\n   1. {clocks['legislative'].label}")
    print(f"      Period: {clocks['legislative'].period_length.days} days")
    print(f"      Phases: {len(clocks['legislative'].phases)}")
    print(f"      Current: {clocks['legislative'].current_phase}")
    for phase in clocks['legislative'].phases:
        print(f"        - {phase.phase_name}: {phase.duration.days} days")

    print(f"\n   2. {clocks['fiscal'].label}")
    print(f"      Period: {clocks['fiscal'].period_length.days} days")
    print(f"      Current: {clocks['fiscal'].current_phase}")

    print(f"\n   3. {clocks['academic'].label}")
    print(f"      Period: {clocks['academic'].period_length.days} days")
    print(f"      Current: {clocks['academic'].current_phase}")

    # ========================
    # Show Deliveries by Temporal Rate
    # ========================

    print("\n📅 Deliveries by Temporal Rate:")

    rates = ["biennial", "quarterly", "annual", "academic_year", "continuous", "daily"]
    for rate in rates:
        deliveries = service.get_deliveries_by_temporal_rate(matrix, rate)
        if deliveries:
            print(f"\n   {rate.upper()}:")
            for item in deliveries:
                delivery = item["delivery"]
                print(f"      • {delivery.delivery_content[:60]}...")
                if delivery.quantity is not None:
                    print(f"        ${delivery.quantity:,.0f} {delivery.units}")

    # ========================
    # Check Thresholds
    # ========================

    print("\n🚨 Threshold Monitoring:")
    alerts = service.check_delivery_thresholds(matrix)

    if alerts:
        print(f"   Found {len(alerts)} threshold violations:")
        for alert in alerts:
            print(f"\n   ⚠️  {alert.delivery.delivery_content}")
            print(f"      Current: ${alert.current_value:,.0f}")
            print(f"      Threshold: ${alert.threshold:,.0f}")
            print(f"      Status: {alert.direction}")
    else:
        print("   ✓ All deliveries within threshold limits")

    # ========================
    # Demonstrate Clock Advancement
    # ========================

    print("\n⏰ Advancing Legislative Clock:")
    result = service.advance_clock(clocks['legislative'], matrix)
    print(f"   Previous: {result['previous_phase']}")
    print(f"   Current: {result['new_phase']}")
    print(f"   Deliveries due: {len(result['deliveries_due'])}")

    if result['deliveries_due']:
        print("\n   Due deliveries in this phase:")
        for item in result['deliveries_due']:
            delivery = item["delivery"]
            print(f"      • {delivery.delivery_content}")
            if delivery.quantity is not None:
                print(f"        ${delivery.quantity:,.0f}")

    # ========================
    # Demonstrate Update with Threshold Check
    # ========================

    print("\n💰 Simulating Budget Cut (Update Quantity):")

    # Find TEEOSA appropriation delivery
    legislature_id = None
    state_dept_id = None
    for comp in [matrix.components[i] for i in range(len(matrix.components))]:
        node = service.get_node(comp)
        if node is None:
            continue
        if "Legislature" in node.label:
            legislature_id = comp
        elif "Department of Education" in node.label:
            state_dept_id = comp

    if legislature_id and state_dept_id:
        # Reduce appropriation below threshold
        print(f"   Reducing biennial appropriation from $1.6B to $1.4B...")
        alerts = service.update_delivery_quantity(
            matrix, legislature_id, state_dept_id, 0, 1_400_000_000
        )

        if alerts:
            print(f"   ⚠️  ALERT: Threshold violated!")
            print(f"      New value: ${alerts[0].current_value:,.0f}")
            print(f"      Threshold: ${alerts[0].threshold:,.0f}")
            print(f"      Direction: {alerts[0].direction}")
            print(f"      This signals inadequate funding per constitutional requirements")
        else:
            print("   No threshold violations")

    # ========================
    # Show Matrix Summary
    # ========================

    print("\n" + "="*80)
    print("Matrix Summary:")
    print("="*80)

    summary = matrix.get_summary()
    print(f"\nTotal deliveries: {summary['total_deliveries']}")
    print(f"Non-empty cells: {summary['non_empty_cells']}")
    print(f"Total cells: {summary['total_cells']}")
    print(f"Cells with multiple deliveries: {summary['cells_with_multiple_deliveries']}")

    print("\nDelivery types:")
    for dtype, count in summary['deliveries_by_type'].items():
        print(f"  - {dtype}: {count}")

    # Count temporal rates manually
    temporal_rates = {}
    for cell in matrix.cells.values():
        for delivery in cell.deliveries:
            if delivery.temporal_rate:
                temporal_rates[delivery.temporal_rate] = temporal_rates.get(delivery.temporal_rate, 0) + 1

    if temporal_rates:
        print("\nTemporal rates:")
        for rate, count in temporal_rates.items():
            print(f"  - {rate}: {count}")

    print("\n" + "="*80)
    print("✓ Nebraska K-12 temporal modeling demonstration complete")
    print("="*80)


if __name__ == "__main__":
    demonstrate_temporal_monitoring()
