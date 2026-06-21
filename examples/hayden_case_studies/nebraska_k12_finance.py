"""
Nebraska K-12 Education Finance Demonstration

Demonstration SFM analysis based on Hoffman & Hayden (2007):
"Equilibrium and Emergence for Social Fabric Matrix Analysis"

Demonstrates Nebraska's TEEOSA (Tax Equity and Educational
Opportunities Support Act) school funding formula as a delivery system.

SFM Methodology:
    Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix
    Approach to Policy Analysis and Program Evaluation. Springer.

Case Study Reference:
    Hoffman, S., & Hayden, F. G. (2007). Equilibrium and emergence
    for social fabric matrix analysis. Journal of Economic Issues,
    41(4), 1105-1126.

Components:
    - State Legislature: Appropriates funds, sets formula rules
    - Department of Education: Oversees implementation, enforces standards
    - School Districts: Receive funding, deliver educational services
    - Taxpayers: Provide property tax revenue
    - Students: Receive educational services

Key Deliveries:
    - Legislature → Districts: $800M annually via TEEOSA formula
    - Legislature → Dept Ed: Oversight authority, administrative budget
    - Taxpayers → Legislature: Property tax revenue
    - Districts → Students: K-12 educational services

What the Analysis Reveals:
    The SFM analysis battery demonstrates Nebraska's education finance system
    as a circular causation mechanism with strong holarchical structure. The
    analysis identifies:

    1. Circular causation paths: Property taxes → state appropriations →
       TEEOSA formula → district funding → student outcomes → property values

    2. Institutional holarchy: Three governance levels (state legislature,
       department of education, local school districts) with nested authority

    3. Ceremonial vs instrumental: TEEOSA formula (instrumental equalization)
       balanced against local control and property tax autonomy (ceremonial)

    4. Feedback cycles: Student enrollment → formula calculations → funding
       allocations → service delivery → enrollment changes

    5. Conflicts: Urban-rural funding disparities may reveal tensions between
       equalization goals and local property wealth concentration
    - Dept Ed → Districts: Academic standards, audit authority
"""

from pathlib import Path

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from graph.exporters import export_delivery_matrix_to_xlsx
from graph.analysis_report import run_analysis_battery, format_report


def build_nebraska_k12_matrix():
    """
    Build Nebraska K-12 Education Finance delivery matrix.

    Returns:
        Tuple of (SFMDeliveryMatrix, SFMService)
    """
    # Initialize service
    service = SFMService()

    # Create components
    legislature = Node(
        label="State Legislature",
        description="Nebraska Unicameral Legislature - appropriates funds and sets TEEOSA formula"
    )

    dept_education = Node(
        label="Department of Education",
        description="State education agency - oversees school districts and enforces standards"
    )

    school_districts = Node(
        label="School Districts",
        description="Local school districts - 249 districts (at time of study)"
    )

    taxpayers = Node(
        label="Taxpayers",
        description="Property taxpayers - fund local share of education"
    )

    students = Node(
        label="Students",
        description="K-12 students receiving educational services"
    )

    # Federal oversight
    federal_dept_ed = Node(
        label="Federal Department of Education",
        description="Federal oversight via ESSA (Every Student Succeeds Act, successor to NCLB)"
    )

    # State Board of Education
    state_board = Node(
        label="State Board of Education",
        description="Sets academic standards and certifies teachers - appointed by governor"
    )

    # Local communities (stakeholders)
    local_communities = Node(
        label="Local Communities",
        description="Parents, voters, and community members demanding accountability"
    )

    # Teachers union (ceremonial actor)
    teachers_union = Node(
        label="Nebraska State Education Association (NSEA)",
        description="Teachers union advocating for local control and professional autonomy"
    )

    # Property assessment system
    property_assessors = Node(
        label="County Property Assessors",
        description="Assess property values that drive TEEOSA formula calculations"
    )

    # Register components
    service.create_node(legislature)
    service.create_node(dept_education)
    service.create_node(school_districts)
    service.create_node(taxpayers)
    service.create_node(students)
    service.create_node(federal_dept_ed)
    service.create_node(state_board)
    service.create_node(local_communities)
    service.create_node(teachers_union)
    service.create_node(property_assessors)

    # Create delivery matrix
    matrix = service.create_delivery_matrix(
        label="Nebraska K-12 Education Finance (2007)",
        description="TEEOSA funding formula delivery system per Hoffman & Hayden",
        matrix_scope="state"
    )

    # Add components to matrix
    matrix.add_component(legislature.id)
    matrix.add_component(dept_education.id)
    matrix.add_component(school_districts.id)
    matrix.add_component(taxpayers.id)
    matrix.add_component(students.id)
    matrix.add_component(federal_dept_ed.id)
    matrix.add_component(state_board.id)
    matrix.add_component(local_communities.id)
    matrix.add_component(teachers_union.id)
    matrix.add_component(property_assessors.id)

    # DELIVERY 1: Legislature → School Districts
    # Money delivery: TEEOSA appropriation
    legislature_to_districts_money = Delivery(
        delivery_type="money",
        delivery_content="$800 million annual state aid appropriation distributed via TEEOSA formula",
        quantity=800_000_000,
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.95,
        data_sources=["LB 1024 (2007)", "Nebraska Department of Education Annual Report"]
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        school_districts.id,
        legislature_to_districts_money,
        cell_description="Legislature provides state aid to school districts through TEEOSA formula, "
                        "which equalizes funding based on property valuations and student needs. "
                        "Formula includes basic allowance, special education weighting, poverty adjustments, "
                        "and transportation costs."
    )

    # Rule delivery: Formula requirements
    legislature_to_districts_rule = Delivery(
        delivery_type="rule",
        delivery_content="TEEOSA formula compliance requirements including cost grouping, needs calculations, "
                        "and local effort rate provisions",
        certainty=1.0,
        data_sources=["Nebraska Revised Statute 79-1007 to 79-1028"]
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        school_districts.id,
        legislature_to_districts_rule,
        cell_description="Legislature provides state aid to school districts through TEEOSA formula, "
                        "which equalizes funding based on property valuations and student needs. "
                        "Formula includes basic allowance, special education weighting, poverty adjustments, "
                        "and transportation costs."
    )

    # DELIVERY 2: Legislature → Department of Education
    # Authority delivery
    legislature_to_dept_authority = Delivery(
        delivery_type="authority",
        delivery_content="Statutory authority to oversee school district compliance, conduct audits, "
                        "and enforce academic standards",
        certainty=1.0,
        data_sources=["Nebraska Revised Statute 79-101 to 79-158"]
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        dept_education.id,
        legislature_to_dept_authority,
        cell_description="Legislature grants Department of Education oversight authority over school districts, "
                        "including power to audit financial records, review academic programs, and enforce "
                        "state standards."
    )

    # Money delivery: Administrative budget
    legislature_to_dept_money = Delivery(
        delivery_type="money",
        delivery_content="Department of Education operational budget for administration and oversight",
        quantity=25_000_000,
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.90
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        dept_education.id,
        legislature_to_dept_money,
        cell_description="Legislature grants Department of Education oversight authority over school districts, "
                        "including power to audit financial records, review academic programs, and enforce "
                        "state standards."
    )

    # DELIVERY 3: Department of Education → School Districts
    # Information delivery: Standards
    dept_to_districts_info = Delivery(
        delivery_type="information",
        delivery_content="Academic performance standards, curriculum frameworks, assessment requirements, "
                        "and data reporting specifications",
        temporal_rate="continuous",
        certainty=1.0,
        data_sources=["Nebraska Academic Content Standards", "Rule 10 - Regulations and Standards"]
    )

    service.add_delivery_to_matrix(
        matrix,
        dept_education.id,
        school_districts.id,
        dept_to_districts_info,
        cell_description="Department of Education establishes academic standards and reporting requirements "
                        "for school districts, including student performance benchmarks, teacher certification "
                        "standards, and financial accountability measures."
    )

    # Authority delivery: Audit power
    dept_to_districts_authority = Delivery(
        delivery_type="authority",
        delivery_content="Authority to conduct compliance audits, review instructional programs, "
                        "and approve/deny accreditation",
        temporal_rate="event-triggered",
        certainty=1.0
    )

    service.add_delivery_to_matrix(
        matrix,
        dept_education.id,
        school_districts.id,
        dept_to_districts_authority,
        cell_description="Department of Education establishes academic standards and reporting requirements "
                        "for school districts, including student performance benchmarks, teacher certification "
                        "standards, and financial accountability measures."
    )

    # DELIVERY 4: School Districts → Students
    # Energy delivery: Educational services
    districts_to_students = Delivery(
        delivery_type="energy",  # Human energy/services in Hayden's taxonomy
        delivery_content="K-12 instructional services including core subjects, special education, "
                        "extracurricular activities, counseling, and transportation",
        temporal_rate="continuous",
        temporal_clock="school_year",
        certainty=0.98,
        data_sources=["School District Annual Reports"]
    )

    service.add_delivery_to_matrix(
        matrix,
        school_districts.id,
        students.id,
        districts_to_students,
        cell_description="School districts provide K-12 educational services to students, "
                        "including classroom instruction, special education, extracurricular activities, "
                        "transportation, food services, and counseling."
    )

    # DELIVERY 5: Taxpayers → Legislature
    # Money delivery: Property taxes
    taxpayers_to_legislature = Delivery(
        delivery_type="money",
        delivery_content="Property tax revenue collected at local and state levels to fund education",
        quantity=1_200_000_000,  # Local share exceeds state share in Nebraska
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        threshold=1_500_000_000,
        threshold_direction="above",
        certainty=0.92,
        data_sources=["Nebraska Property Tax Administrator Reports"]
    )

    service.add_delivery_to_matrix(
        matrix,
        taxpayers.id,
        legislature.id,
        taxpayers_to_legislature,
        cell_description="Taxpayers provide property tax revenue that funds both state aid (via general fund) "
                        "and local school district budgets. Nebraska relies heavily on property taxes for "
                        "education funding, creating ongoing tension over tax equity."
    )

    # DELIVERY 6: Taxpayers → School Districts (direct local funding)
    taxpayers_to_districts = Delivery(
        delivery_type="money",
        delivery_content="Direct property tax levies for local school district operations",
        quantity=800_000_000,
        units="USD/year",
        temporal_rate="annual",
        temporal_clock="fiscal_year",
        certainty=0.95
    )

    service.add_delivery_to_matrix(
        matrix,
        taxpayers.id,
        school_districts.id,
        taxpayers_to_districts,
        cell_description="Taxpayers directly fund school districts through local property tax levies, "
                        "which supplement state aid and create funding disparities based on local wealth."
    )

    # =========================================================================
    # ADDITIONAL DELIVERIES FOR FULL BATTERY ANALYSIS
    # =========================================================================

    # DELIVERY 7: Federal Dept of Education → State Dept of Education
    federal_to_state_money = Delivery(
        delivery_type="money",
        delivery_content="Title I grants, special education funding (IDEA), and other federal programs",
        quantity=150_000_000,
        units="USD/year",
        temporal_rate="annual",
        certainty=0.90,
        data_sources=["ED.gov Federal Education Budget for States"]
    )

    service.add_delivery_to_matrix(
        matrix,
        federal_dept_ed.id,
        dept_education.id,
        federal_to_state_money,
        cell_description="Federal Department of Education provides categorical grants to Nebraska "
                        "for Title I (low-income schools), IDEA (special education), and other programs."
    )

    federal_to_state_rules = Delivery(
        delivery_type="rule",
        delivery_content="ESSA compliance requirements, civil rights mandates, data reporting standards",
        certainty=1.0,
        data_sources=["Every Student Succeeds Act of 2015"]
    )

    service.add_delivery_to_matrix(
        matrix,
        federal_dept_ed.id,
        dept_education.id,
        federal_to_state_rules,
        cell_description="Federal Department of Education provides categorical grants to Nebraska "
                        "for Title I (low-income schools), IDEA (special education), and other programs."
    )

    # DELIVERY 8: State Board → Department of Education
    board_to_dept_rules = Delivery(
        delivery_type="rule",
        delivery_content="Academic content standards, teacher certification requirements, graduation criteria",
        certainty=1.0,
        data_sources=["Nebraska Board of Education Policy"]
    )

    service.add_delivery_to_matrix(
        matrix,
        state_board.id,
        dept_education.id,
        board_to_dept_rules,
        cell_description="State Board of Education sets academic standards that Department must enforce. "
                        "Board is appointed by governor but operates with statutory independence."
    )

    # DELIVERY 9: Property Assessors → Legislature
    assessors_to_legislature_info = Delivery(
        delivery_type="information",
        delivery_content="County property valuation data that drives TEEOSA formula calculations",
        temporal_rate="annual",
        certainty=0.95,
        data_sources=["Nebraska Property Tax Administrator"]
    )

    service.add_delivery_to_matrix(
        matrix,
        property_assessors.id,
        legislature.id,
        assessors_to_legislature_info,
        cell_description="County assessors provide property valuation data that Legislature uses in "
                        "TEEOSA formula. Valuations determine each district's 'needs' and 'resources', "
                        "creating circular causation with funding allocations."
    )

    # DELIVERY 10: School Districts → Property Assessors (feedback)
    districts_to_assessors_info = Delivery(
        delivery_type="information",
        delivery_content="School quality signals affecting property values (feedback to assessment system)",
        temporal_rate="continuous",
        certainty=0.70
    )

    service.add_delivery_to_matrix(
        matrix,
        school_districts.id,
        property_assessors.id,
        districts_to_assessors_info,
        cell_description="School district performance affects local property values, which assessors "
                        "capture in valuations. Creates circular causation: better schools → higher "
                        "property values → higher local resources → different TEEOSA needs calculation."
    )

    # DELIVERY 11: Local Communities → School Districts
    communities_to_districts_authority = Delivery(
        delivery_type="authority",
        delivery_content="Electoral accountability via school board elections and budget approval votes",
        temporal_rate="event-triggered",
        certainty=1.0
    )

    service.add_delivery_to_matrix(
        matrix,
        local_communities.id,
        school_districts.id,
        communities_to_districts_authority,
        cell_description="Local communities exercise democratic control over school districts through "
                        "elected school boards and budget referendums, creating ceremonial preference "
                        "for local autonomy over state-mandated equalization."
    )

    communities_to_districts_demands = Delivery(
        delivery_type="information",
        delivery_content="Demands for academic excellence, fiscal restraint, and local responsiveness",
        temporal_rate="continuous",
        certainty=0.85
    )

    service.add_delivery_to_matrix(
        matrix,
        local_communities.id,
        school_districts.id,
        communities_to_districts_demands,
        cell_description="Local communities exercise democratic control over school districts through "
                        "elected school boards and budget referendums, creating ceremonial preference "
                        "for local autonomy over state-mandated equalization."
    )

    # DELIVERY 12: Teachers Union → Legislature (CEREMONIAL RESISTANCE)
    union_to_legislature_resistance = Delivery(
        delivery_type="information",
        delivery_content="Lobbying for local control, professional autonomy, and resistance to "
                        "centralized accountability (ceremonial preservation of status quo)",
        temporal_rate="continuous",
        certainty=0.90
    )

    service.add_delivery_to_matrix(
        matrix,
        teachers_union.id,
        legislature.id,
        union_to_legislature_resistance,
        cell_description="Nebraska State Education Association advocates for local control and teacher "
                        "professional autonomy, creating ceremonial resistance to state accountability "
                        "mandates. Demonstrates Veblen-Hayden ceremonial vs instrumental conflict."
    )

    # Set ceremonial component for this cell
    union_leg_cell = matrix.get_cell(teachers_union.id, legislature.id)
    if union_leg_cell:
        union_leg_cell.ceremonial_component = 0.75  # HIGH ceremonial (status quo preservation)
        union_leg_cell.instrumental_component = 0.25  # LOW instrumental (not problem-solving)

    # DELIVERY 13: Teachers Union → School Districts
    union_to_districts_rules = Delivery(
        delivery_type="rule",
        delivery_content="Collective bargaining agreements on wages, working conditions, class sizes",
        temporal_rate="periodic",
        certainty=0.95,
        data_sources=["NSEA Collective Bargaining Agreements"]
    )

    service.add_delivery_to_matrix(
        matrix,
        teachers_union.id,
        school_districts.id,
        union_to_districts_rules,
        cell_description="Teachers union negotiates contracts that constrain district flexibility, "
                        "creating tension between formula efficiency and labor agreements."
    )

    # DELIVERY 14: Students → Local Communities (feedback loop)
    students_to_communities_outcomes = Delivery(
        delivery_type="information",
        delivery_content="Student achievement outcomes, graduation rates, college enrollment data",
        temporal_rate="annual",
        certainty=0.90
    )

    service.add_delivery_to_matrix(
        matrix,
        students.id,
        local_communities.id,
        students_to_communities_outcomes,
        cell_description="Student outcomes create feedback loop: performance data drives community "
                        "demands for district accountability, completing circular causation path."
    )

    # DELIVERY 15: Department of Education → Federal Dept of Education (compliance reporting)
    dept_to_federal_info = Delivery(
        delivery_type="information",
        delivery_content="ESSA compliance reports, test score data, accountability metrics",
        temporal_rate="annual",
        certainty=1.0
    )

    service.add_delivery_to_matrix(
        matrix,
        dept_education.id,
        federal_dept_ed.id,
        dept_to_federal_info,
        cell_description="Nebraska reports to federal government on ESSA compliance, creating "
                        "hierarchical accountability chain: federal → state → districts."
    )

    # DELIVERY 16: Legislature → State Board (appointments and budget)
    legislature_to_board_authority = Delivery(
        delivery_type="authority",
        delivery_content="Governor appointment power (with legislative confirmation) for Board members",
        certainty=1.0
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        state_board.id,
        legislature_to_board_authority,
        cell_description="Legislature confirms State Board appointments and funds Board operations, "
                        "creating hierarchical control despite Board's statutory independence."
    )

    legislature_to_board_money = Delivery(
        delivery_type="money",
        delivery_content="State Board operational budget",
        quantity=5_000_000,
        units="USD/year",
        temporal_rate="annual",
        certainty=0.95
    )

    service.add_delivery_to_matrix(
        matrix,
        legislature.id,
        state_board.id,
        legislature_to_board_money,
        cell_description="Legislature confirms State Board appointments and funds Board operations, "
                        "creating hierarchical control despite Board's statutory independence."
    )

    return matrix, service


def main():
    """
    Build and export Nebraska K-12 Education Finance matrix.

    Generates XLSX file in examples/hayden_case_studies/ directory.
    """
    print("Building Nebraska K-12 Education Finance delivery matrix...")
    matrix, service = build_nebraska_k12_matrix()

    # Validate matrix
    errors = service.validate_delivery_matrix(matrix)
    if errors:
        print(f"⚠ Matrix validation errors: {errors}")
    else:
        print("✓ Matrix validation passed")

    # Run SFM analysis battery
    print("\n" + "=" * 70)
    print("RUNNING SFM ANALYSIS BATTERY")
    print("=" * 70)
    report = run_analysis_battery(service)
    analysis_text = format_report(report)
    print(analysis_text)

    # Export to XLSX
    output_path = Path(__file__).parent / "nebraska_k12_finance.xlsx"
    export_delivery_matrix_to_xlsx(
        matrix,
        output_path,
        service,
        include_cell_descriptions=True,
        include_delivery_details=True
    )

    print(f"✓ Exported to: {output_path}")

    # Print summary
    print("\nMatrix Summary:")
    print(f"  Components: {len(matrix.components)}")
    print(f"  Non-empty cells: {len(matrix.get_non_empty_cells())}")

    total_deliveries = sum(len(cell.deliveries) for cell in matrix.cells.values())
    print(f"  Total deliveries: {total_deliveries}")

    # Print delivery breakdown by type
    delivery_types = {}
    for cell in matrix.cells.values():
        for delivery in cell.deliveries:
            delivery_types[delivery.delivery_type] = delivery_types.get(delivery.delivery_type, 0) + 1

    print("\n  Deliveries by type:")
    for dtype, count in sorted(delivery_types.items()):
        print(f"    {dtype}: {count}")


if __name__ == "__main__":
    main()
