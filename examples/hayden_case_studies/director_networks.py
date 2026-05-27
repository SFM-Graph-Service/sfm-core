"""
Corporate Director Networks Case Study

Based on:
Hayden, F. G., Wood, S., & Kaya, I. (2002). "Patterns of Delivery and
Correlation Coefficients in Social Fabric Matrix Analyses of Corporate
Director Networks." Journal of Economic Issues, 36(2), 345-352.

Models interlocking corporate directorates as power delivery systems.
Demonstrates network centrality analysis through SFM delivery patterns.

Key concepts:
- Directors serving on multiple boards deliver authority and strategic guidance
- Financial institutions deliver capital and credit to corporations
- Industry associations coordinate policy positions
- Information flows through director networks
"""

from pathlib import Path
from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from graph.exporters import export_delivery_matrix_to_xlsx


def create_director_network_matrix():
    """
    Create SFM for corporate director network.

    Simplified Fortune 500 network focusing on financial-industrial linkages.
    """
    service = SFMService()

    # =========================================================================
    # STEP 1: Define components (simplified network)
    # =========================================================================

    # Major financial institutions
    citigroup = Node(
        label="Citigroup",
        description="Major commercial bank with extensive corporate lending"
    )

    jp_morgan = Node(
        label="JP Morgan Chase",
        description="Investment banking and commercial banking"
    )

    goldman = Node(
        label="Goldman Sachs",
        description="Investment banking and asset management"
    )

    # Industrial corporations
    general_electric = Node(
        label="General Electric",
        description="Industrial conglomerate with finance division"
    )

    boeing = Node(
        label="Boeing",
        description="Aerospace and defense manufacturer"
    )

    att = Node(
        label="AT&T",
        description="Telecommunications and media"
    )

    # Coordinating bodies
    business_roundtable = Node(
        label="Business Roundtable",
        description="CEO association for corporate policy coordination"
    )

    us_chamber = Node(
        label="U.S. Chamber of Commerce",
        description="Business advocacy organization"
    )

    # Individual directors (key nodes in network)
    director_smith = Node(
        label="Director Smith",
        description="Serves on Citigroup, Boeing, Business Roundtable boards"
    )

    director_jones = Node(
        label="Director Jones",
        description="Serves on JP Morgan, GE, U.S. Chamber boards"
    )

    # Register all components
    components = [
        citigroup, jp_morgan, goldman,
        general_electric, boeing, att,
        business_roundtable, us_chamber,
        director_smith, director_jones
    ]

    for comp in components:
        service.create_node(comp)

    # =========================================================================
    # STEP 2: Create delivery matrix
    # =========================================================================

    matrix = service.create_delivery_matrix(
        label="Corporate Director Network",
        description="Interlocking directorates in Fortune 500 companies (simplified)",
        components=[c.id for c in components],
        matrix_scope="national"
    )

    # =========================================================================
    # STEP 3: Financial institutions → Corporations (capital delivery)
    # =========================================================================

    # Citigroup → Boeing (lending relationship)
    service.add_delivery_to_matrix(
        matrix,
        citigroup.id,
        boeing.id,
        Delivery(
            delivery_type="money",
            delivery_content="$2.5B credit facility for aircraft production",
            quantity=2_500_000_000,
            units="USD",
            temporal_rate="continuous",
            certainty=0.95
        ),
        cell_description="Citigroup provides credit facility to Boeing for production financing"
    )

    service.add_delivery_to_matrix(
        matrix,
        citigroup.id,
        boeing.id,
        Delivery(
            delivery_type="information",
            delivery_content="Market intelligence and financial advisory",
            certainty=0.85
        ),
        cell_description="Citigroup provides credit facility to Boeing for production financing"
    )

    # JP Morgan → General Electric
    service.add_delivery_to_matrix(
        matrix,
        jp_morgan.id,
        general_electric.id,
        Delivery(
            delivery_type="money",
            delivery_content="$5B revolving credit and investment banking services",
            quantity=5_000_000_000,
            units="USD",
            temporal_rate="continuous",
            certainty=0.98
        ),
        cell_description="JP Morgan provides capital and investment banking to GE"
    )

    # Goldman Sachs → AT&T (M&A advisory)
    service.add_delivery_to_matrix(
        matrix,
        goldman.id,
        att.id,
        Delivery(
            delivery_type="information",
            delivery_content="Mergers and acquisitions advisory services",
            certainty=0.90
        ),
        cell_description="Goldman Sachs provides M&A advisory to AT&T"
    )

    service.add_delivery_to_matrix(
        matrix,
        goldman.id,
        att.id,
        Delivery(
            delivery_type="money",
            delivery_content="Underwriting for debt offerings",
            quantity=3_000_000_000,
            units="USD",
            temporal_rate="annual",
            certainty=0.85
        ),
        cell_description="Goldman Sachs provides M&A advisory to AT&T"
    )

    # =========================================================================
    # STEP 4: Directors → Corporations (authority and strategic guidance)
    # =========================================================================

    # Director Smith → Citigroup (board authority)
    service.add_delivery_to_matrix(
        matrix,
        director_smith.id,
        citigroup.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Board governance and strategic oversight",
            certainty=1.0
        ),
        cell_description="Director Smith serves on Citigroup board providing governance oversight"
    )

    service.add_delivery_to_matrix(
        matrix,
        director_smith.id,
        citigroup.id,
        Delivery(
            delivery_type="information",
            delivery_content="Industry intelligence from Boeing and Business Roundtable connections",
            certainty=0.85
        ),
        cell_description="Director Smith serves on Citigroup board providing governance oversight"
    )

    # Director Smith → Boeing
    service.add_delivery_to_matrix(
        matrix,
        director_smith.id,
        boeing.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Board governance and strategic oversight",
            certainty=1.0
        ),
        cell_description="Director Smith serves on Boeing board providing governance and financial expertise"
    )

    service.add_delivery_to_matrix(
        matrix,
        director_smith.id,
        boeing.id,
        Delivery(
            delivery_type="information",
            delivery_content="Financial sector intelligence from Citigroup connections",
            certainty=0.85
        ),
        cell_description="Director Smith serves on Boeing board providing governance and financial expertise"
    )

    # Director Jones → JP Morgan
    service.add_delivery_to_matrix(
        matrix,
        director_jones.id,
        jp_morgan.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Board governance and strategic oversight",
            certainty=1.0
        ),
        cell_description="Director Jones serves on JP Morgan board providing governance oversight"
    )

    # Director Jones → General Electric
    service.add_delivery_to_matrix(
        matrix,
        director_jones.id,
        general_electric.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Board governance and strategic oversight",
            certainty=1.0
        ),
        cell_description="Director Jones serves on GE board providing governance and banking expertise"
    )

    service.add_delivery_to_matrix(
        matrix,
        director_jones.id,
        general_electric.id,
        Delivery(
            delivery_type="information",
            delivery_content="Financial sector intelligence from JP Morgan connections",
            certainty=0.85
        ),
        cell_description="Director Jones serves on GE board providing governance and banking expertise"
    )

    # =========================================================================
    # STEP 5: Corporations → Directors (compensation and access)
    # =========================================================================

    # Citigroup → Director Smith
    service.add_delivery_to_matrix(
        matrix,
        citigroup.id,
        director_smith.id,
        Delivery(
            delivery_type="money",
            delivery_content="Annual board compensation and stock options",
            quantity=350_000,
            units="USD/year",
            temporal_rate="annual",
            certainty=1.0
        ),
        cell_description="Citigroup compensates Director Smith for board service"
    )

    service.add_delivery_to_matrix(
        matrix,
        citigroup.id,
        director_smith.id,
        Delivery(
            delivery_type="information",
            delivery_content="Access to confidential financial data and strategic plans",
            certainty=0.95
        ),
        cell_description="Citigroup compensates Director Smith for board service"
    )

    # Boeing → Director Smith
    service.add_delivery_to_matrix(
        matrix,
        boeing.id,
        director_smith.id,
        Delivery(
            delivery_type="money",
            delivery_content="Annual board compensation and stock options",
            quantity=300_000,
            units="USD/year",
            temporal_rate="annual",
            certainty=1.0
        ),
        cell_description="Boeing compensates Director Smith for board service"
    )

    # JP Morgan → Director Jones
    service.add_delivery_to_matrix(
        matrix,
        jp_morgan.id,
        director_jones.id,
        Delivery(
            delivery_type="money",
            delivery_content="Annual board compensation and stock options",
            quantity=400_000,
            units="USD/year",
            temporal_rate="annual",
            certainty=1.0
        ),
        cell_description="JP Morgan compensates Director Jones for board service"
    )

    # General Electric → Director Jones
    service.add_delivery_to_matrix(
        matrix,
        general_electric.id,
        director_jones.id,
        Delivery(
            delivery_type="money",
            delivery_content="Annual board compensation and stock options",
            quantity=325_000,
            units="USD/year",
            temporal_rate="annual",
            certainty=1.0
        ),
        cell_description="GE compensates Director Jones for board service"
    )

    # =========================================================================
    # STEP 6: Industry associations → Corporations (policy coordination)
    # =========================================================================

    # Business Roundtable → Corporations
    for corp in [citigroup, jp_morgan, general_electric, boeing, att]:
        service.add_delivery_to_matrix(
            matrix,
            business_roundtable.id,
            corp.id,
            Delivery(
                delivery_type="information",
                delivery_content="Coordinated policy positions on corporate governance and regulation",
                certainty=0.80
            ),
            cell_description=f"Business Roundtable coordinates policy positions for {corp.label}"
        )

    # U.S. Chamber → Corporations
    for corp in [citigroup, general_electric, att]:
        service.add_delivery_to_matrix(
            matrix,
            us_chamber.id,
            corp.id,
            Delivery(
                delivery_type="rule",
                delivery_content="Advocacy positions and legislative recommendations",
                certainty=0.75
            ),
            cell_description=f"U.S. Chamber provides advocacy for {corp.label}"
        )

    # =========================================================================
    # STEP 7: Directors → Industry associations (participation)
    # =========================================================================

    # Director Smith → Business Roundtable
    service.add_delivery_to_matrix(
        matrix,
        director_smith.id,
        business_roundtable.id,
        Delivery(
            delivery_type="information",
            delivery_content="Industry intelligence and policy input",
            certainty=0.85
        ),
        cell_description="Director Smith participates in Business Roundtable policy formation"
    )

    # Director Jones → U.S. Chamber
    service.add_delivery_to_matrix(
        matrix,
        director_jones.id,
        us_chamber.id,
        Delivery(
            delivery_type="information",
            delivery_content="Banking sector perspective and policy input",
            certainty=0.85
        ),
        cell_description="Director Jones participates in U.S. Chamber banking policy"
    )

    return matrix, service


def main():
    """Generate director network SFM and export to XLSX."""

    print("="*70)
    print("CORPORATE DIRECTOR NETWORK CASE STUDY")
    print("Hayden, Wood & Kaya (2002)")
    print("="*70)

    # Create matrix
    matrix, service = create_director_network_matrix()

    # Display summary
    summary = matrix.get_summary()

    print(f"\nMatrix Summary:")
    print(f"  Components: {summary['components']}")
    print(f"  Non-empty cells: {summary['non_empty_cells']}")
    print(f"  Total deliveries: {summary['total_deliveries']}")
    print(f"\nDeliveries by type:")
    for dtype, count in summary['deliveries_by_type'].items():
        print(f"  {dtype}: {count}")

    print(f"\nCells with multiple deliveries: {summary['cells_with_multiple_deliveries']}")
    print(f"Quantified deliveries: {summary['quantified_deliveries']}")

    # Export to XLSX
    output_path = Path(__file__).parent / "director_networks.xlsx"
    export_delivery_matrix_to_xlsx(
        matrix,
        output_path,
        service,
        include_cell_descriptions=True,
        include_delivery_details=True
    )

    print(f"\nExported to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Key findings (per Hayden, Wood & Kaya 2002)
    print("\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)

    print("\n1. Network Centrality:")
    print("   - Directors serving on multiple boards deliver information across")
    print("     financial-industrial boundaries")
    print("   - High-centrality directors (Smith, Jones) facilitate capital flows")

    print("\n2. Interlocking Pattern:")
    print("   - Financial institutions → Industrial corporations: Capital delivery")
    print("   - Directors → Corporations: Authority and strategic guidance")
    print("   - Corporations → Directors: Compensation and information access")
    print("   - Industry associations → All: Policy coordination")

    print("\n3. Power Delivery Analysis:")
    print("   - Money deliveries show capital allocation power")
    print("   - Authority deliveries show governance control")
    print("   - Information deliveries show knowledge network effects")

    print("\n4. Delivery Correlation (Hayden 2002):")
    print("   - Positive correlation: Money + Authority (directors compensated + govern)")
    print("   - Positive correlation: Information + Authority (board access + control)")
    print("   - Network density increases with director interlocks")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
