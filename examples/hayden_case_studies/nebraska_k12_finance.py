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
    - Dept Ed → Districts: Academic standards, audit authority

What the analysis reveals:
    - Circular funding dependencies between taxpayers, legislature, and districts.
    - Institutional layering from legislature to agency to district implementation.
    - Conflict points around tax equity and delivery adequacy.
"""

from pathlib import Path

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from graph.analysis_report import format_report, run_analysis_battery
from graph.exporters import export_delivery_matrix_to_xlsx, export_to_xmile


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

    # Register components
    service.create_node(legislature)
    service.create_node(dept_education)
    service.create_node(school_districts)
    service.create_node(taxpayers)
    service.create_node(students)

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

    report = run_analysis_battery(service)
    print("\n" + format_report(report))

    # Print delivery breakdown by type
    delivery_types = {}
    for cell in matrix.cells.values():
        for delivery in cell.deliveries:
            delivery_types[delivery.delivery_type] = delivery_types.get(delivery.delivery_type, 0) + 1

    print("\n  Deliveries by type:")
    for dtype, count in sorted(delivery_types.items()):
        print(f"    {dtype}: {count}")

    xmile_output = Path(__file__).parent / "nebraska_k12_finance.xmile"
    export_to_xmile(
        matrix=matrix,
        filepath=xmile_output,
        service=service,
        model_name="Nebraska K-12 Finance",
        model_description="System dynamics handoff from SFM delivery matrix",
    )
    print(f"  System dynamics export: {xmile_output}")


if __name__ == "__main__":
    main()
