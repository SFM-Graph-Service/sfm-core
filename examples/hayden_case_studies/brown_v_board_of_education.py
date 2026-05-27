#!/usr/bin/env python3
"""
Brown v. Board of Education (1954): Social Fabric Matrix Analysis

Demonstration SFM analysis of the institutional, cultural, and governmental impacts
following the Supreme Court's landmark decision in Brown v. Board of Education.

SFM Methodology:
    Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix
    Approach to Policy Analysis and Program Evaluation. Springer.

Historical Context:
    Brown v. Board of Education of Topeka, 347 U.S. 483 (1954) declared state laws
    establishing separate public schools for Black and white students unconstitutional.
    This decision reversed Plessy v. Ferguson (1896) and catalyzed the Civil Rights
    Movement, triggering institutional resistance, cultural transformation, and
    decades of policy implementation challenges.

Note: This is an experimental implementation for academic research and evaluation.
Errors may exist. Claude AI was used to assist with development.
"""

from pathlib import Path
from datetime import datetime, timedelta
from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryCell, SFMDeliveryMatrix
from models.temporal_clocks import TemporalClock
from graph.exporters.xlsx_exporter import export_delivery_matrix_to_xlsx


def build_brown_v_board_matrix(service: SFMService) -> SFMDeliveryMatrix:
    """
    Build SFM delivery matrix for Brown v. Board of Education aftermath (1954-1980).

    Captures:
    - Supreme Court decision authority delivery
    - Federal enforcement mechanisms (Title VI, DOJ)
    - State/local resistance (massive resistance movement)
    - Cultural transformation (changing social norms)
    - Educational outcomes (desegregation progress)
    - Economic impacts (resource redistribution)

    Components follow Hayden's six categories:
    1. Beliefs (cultural values about racial equality)
    2. Technology (school infrastructure, busing systems)
    3. Institutions (courts, legislatures, school boards)
    4. Knowledge (legal precedents, educational research)
    5. Resources (school funding, facilities)
    6. Individuals (students, parents, teachers, judges)
    """

    print("Building Brown v. Board of Education delivery matrix...")
    print("Analyzing institutional impacts 1954-1980...")
    print()

    # Create delivery matrix
    matrix = SFMDeliveryMatrix(
        label="Brown v. Board of Education Impact Matrix (1954-1980)",
        description="Institutional, cultural, and governmental responses to school desegregation ruling",
        matrix_scope="national",
        temporal_scope=(
            datetime(1954, 5, 17),  # Brown decision date
            datetime(1980, 12, 31)  # End of analysis period
        )
    )

    # ==========================================================================
    # COMPONENTS (Hayden's six categories)
    # ==========================================================================

    # INSTITUTIONS - Formal governance structures
    supreme_court = Node(
        label="U.S. Supreme Court",
        description="Issued Brown I (1954) and Brown II (1955) rulings"
    )
    service.create_node(supreme_court)

    federal_government = Node(
        label="Federal Executive Branch",
        description="DOJ Civil Rights Division, HEW enforcement, federal troops (Little Rock)"
    )
    service.create_node(federal_government)

    southern_state_govts = Node(
        label="Southern State Governments",
        
        description="Virginia, Arkansas, Alabama, Mississippi, Georgia resistance governments"
    )
    service.create_node(southern_state_govts)

    local_school_boards = Node(
        label="Local School Boards",
        
        description="Implementation authorities (varied from compliance to massive resistance)"
    )
    service.create_node(local_school_boards)

    congress = Node(
        label="U.S. Congress",
        
        description="Passed Civil Rights Act (1964) Title VI withholding federal funds"
    )
    service.create_node(congress)

    # BELIEFS/CULTURAL VALUES
    segregationist_culture = Node(
        label="Segregationist Cultural System",
        
        description="White supremacy beliefs, states' rights ideology, anti-integration norms"
    )
    service.create_node(segregationist_culture)

    civil_rights_movement = Node(
        label="Civil Rights Movement",
        
        description="Equality norms, constitutional rights advocacy, grassroots organization"
    )
    service.create_node(civil_rights_movement)

    # KNOWLEDGE
    legal_precedent = Node(
        label="Constitutional Legal Framework",
        
        description="14th Amendment Equal Protection, reversal of Plessy, judicial interpretation"
    )
    service.create_node(legal_precedent)

    educational_research = Node(
        label="Educational Research Community",
        
        description="Kenneth Clark doll studies, achievement gap research, integration effects"
    )
    service.create_node(educational_research)

    # RESOURCES
    black_schools = Node(
        label="Historically Black Schools",
        
        description="Underfunded segregated schools, inferior facilities and materials"
    )
    service.create_node(black_schools)

    white_schools = Node(
        label="Historically White Schools",
        
        description="Better-funded schools targeted for integration"
    )
    service.create_node(white_schools)

    federal_education_funds = Node(
        label="Federal Education Funding",
        
        description="Title VI compliance funds, threat of withholding for non-compliance"
    )
    service.create_node(federal_education_funds)

    # TECHNOLOGY
    busing_system = Node(
        label="School Busing Infrastructure",
        
        description="Transportation system for achieving racial balance (post-Swann 1971)"
    )
    service.create_node(busing_system)

    # INDIVIDUALS (Aggregated groups)
    black_students = Node(
        label="African American Students",
        
        description="Students seeking equal educational opportunities, faced violence and resistance"
    )
    service.create_node(black_students)

    white_families = Node(
        label="White Families",
        
        description="Varied responses: compliance, white flight, private school academies"
    )
    service.create_node(white_families)

    # Add all components to matrix
    for component in [
        supreme_court, federal_government, southern_state_govts, local_school_boards,
        congress, segregationist_culture, civil_rights_movement, legal_precedent,
        educational_research, black_schools, white_schools, federal_education_funds,
        busing_system, black_students, white_families
    ]:
        matrix.add_component(component.id)

    # ==========================================================================
    # TEMPORAL CLOCKS (Hayden's polychronic modeling)
    # ==========================================================================
    # Note: Temporal rate information captured in individual deliveries below
    # Full temporal clock system available in models/temporal_clocks.py

    # ==========================================================================
    # DELIVERIES - Phase 1: Supreme Court Authority (1954-1955)
    # ==========================================================================

    # Supreme Court → Legal Precedent
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=supreme_court.id,
        target_component_id=legal_precedent.id,
        cell_description=(
            "Supreme Court delivers constitutional interpretation overturning Plessy. "
            "Establishes 'separate is inherently unequal' doctrine, transforms Equal "
            "Protection jurisprudence, creates legal authority for desegregation."
        ),
        deliveries=[
            Delivery(
                delivery_type="authority",
                delivery_content="Brown I: Declares school segregation unconstitutional under 14th Amendment",
                temporal_rate="singular_event",
                
                certainty=1.0,
                data_sources=["Brown v. Board, 347 U.S. 483 (1954)"]
            ),
            Delivery(
                delivery_type="rule",
                delivery_content="Brown II: Orders desegregation 'with all deliberate speed'",
                temporal_rate="singular_event",
                
                certainty=1.0,
                data_sources=["Brown v. Board, 349 U.S. 294 (1955)"]
            ),
            Delivery(
                delivery_type="information",
                delivery_content="Cites Kenneth Clark psychological harm studies in decision",
                certainty=0.9,
                data_sources=["Clark & Clark doll studies cited in footnote 11"]
            )
        ]
    ))

    # Supreme Court → Local School Boards
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=supreme_court.id,
        target_component_id=local_school_boards.id,
        cell_description=(
            "Supreme Court mandates local implementation but provides vague timeline "
            "('deliberate speed'), creating enforcement vacuum exploited by resisters."
        ),
        deliveries=[
            Delivery(
                delivery_type="rule",
                delivery_content="Mandate to desegregate schools, but timeline ambiguous",
                temporal_rate="continuous",
                
                certainty=1.0,
                data_sources=["Brown II implementation order"]
            )
        ]
    ))

    # Educational Research → Supreme Court
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=educational_research.id,
        target_component_id=supreme_court.id,
        cell_description=(
            "Kenneth Clark's doll studies provide psychological harm evidence cited "
            "in Brown decision, demonstrating segregation's damage to Black children."
        ),
        deliveries=[
            Delivery(
                delivery_type="information",
                delivery_content="Psychological harm evidence from segregation (doll studies)",
                certainty=0.8,
                data_sources=["Clark, K. B., & Clark, M. P. (1947)"]
            )
        ]
    ))

    # ==========================================================================
    # DELIVERIES - Phase 2: Massive Resistance (1956-1963)
    # ==========================================================================

    # Southern State Govts → Local School Boards
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=southern_state_govts.id,
        target_component_id=local_school_boards.id,
        cell_description=(
            "Southern states enact 'massive resistance' laws: school closures, tuition "
            "grants for private segregation academies, interposition doctrine, state "
            "sovereignty claims. Virginia closed Prince Edward County schools 1959-1964."
        ),
        deliveries=[
            Delivery(
                delivery_type="rule",
                delivery_content="Interposition laws claiming state sovereignty over federal courts",
                temporal_rate="legislative_session",
                
                certainty=1.0,
                data_sources=["Virginia Massive Resistance laws 1956-1959"]
            ),
            Delivery(
                delivery_type="authority",
                delivery_content="Authority to close public schools rather than integrate",
                certainty=1.0,
                data_sources=["Prince Edward County, VA closure 1959-1964"]
            ),
            Delivery(
                delivery_type="money",
                delivery_content="Tuition grants for private 'segregation academies'",
                quantity=None,  # Varied by state
                units="USD",
                temporal_rate="annual",
                certainty=0.9,
                data_sources=["Mississippi, Alabama tuition grant programs"]
            )
        ]
    ))

    # Segregationist Culture → Southern State Govts
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=segregationist_culture.id,
        target_component_id=southern_state_govts.id,
        cell_description=(
            "White supremacy beliefs drive political resistance. 'Southern Manifesto' "
            "(1956) signed by 101 congressmen denouncing Brown as 'judicial tyranny.'"
        ),
        deliveries=[
            Delivery(
                delivery_type="information",
                delivery_content="Political pressure to resist integration, electoral consequences for compliance",
                temporal_rate="continuous",
                certainty=0.95,
                data_sources=["Southern Manifesto (1956)", "White Citizens' Councils"]
            ),
            Delivery(
                delivery_type="authority",
                delivery_content="Cultural legitimacy for massive resistance policies",
                certainty=0.9,
                data_sources=["States' rights ideology mobilization"]
            )
        ]
    ))

    # Federal Government → Southern State Govts (Little Rock Crisis)
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=federal_government.id,
        target_component_id=southern_state_govts.id,
        cell_description=(
            "President Eisenhower federalizes Arkansas National Guard and deploys "
            "101st Airborne to enforce integration at Little Rock Central High (1957). "
            "Establishes federal enforcement authority against state resistance."
        ),
        deliveries=[
            Delivery(
                delivery_type="authority",
                delivery_content="Federal troops enforce integration at Little Rock (September 1957)",
                temporal_rate="event_triggered",
                
                certainty=1.0,
                data_sources=["Cooper v. Aaron, 358 U.S. 1 (1958)"]
            ),
            Delivery(
                delivery_type="energy",
                delivery_content="Military force: 1,000 paratroopers, federalized National Guard",
                quantity=1000,
                units="troops",
                temporal_rate="event_triggered",
                certainty=1.0,
                data_sources=["Presidential Order September 24, 1957"]
            )
        ]
    ))

    # ==========================================================================
    # DELIVERIES - Phase 3: Federal Legislation (1964-1968)
    # ==========================================================================

    # Congress → Federal Government
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=congress.id,
        target_component_id=federal_government.id,
        cell_description=(
            "Civil Rights Act Title VI (1964) authorizes withholding federal funds "
            "from segregated schools. Transforms enforcement from judicial to financial "
            "leverage, dramatically accelerating desegregation in South."
        ),
        deliveries=[
            Delivery(
                delivery_type="authority",
                delivery_content="Title VI authority to withhold federal education funds from segregated districts",
                temporal_rate="continuous",
                
                certainty=1.0,
                data_sources=["Civil Rights Act of 1964, Title VI"]
            ),
            Delivery(
                delivery_type="rule",
                delivery_content="Elementary and Secondary Education Act (1965) increases federal leverage",
                temporal_rate="annual",
                certainty=1.0,
                data_sources=["ESEA 1965 - increased federal funding"]
            )
        ]
    ))

    # Federal Government → Local School Boards
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=federal_government.id,
        target_component_id=local_school_boards.id,
        cell_description=(
            "HEW (Health, Education, Welfare) enforces Title VI by threatening to "
            "withhold funds. Southern desegregation accelerates: 2.3% of Black students "
            "in integrated schools (1964) → 91.3% (1973)."
        ),
        deliveries=[
            Delivery(
                delivery_type="money",
                delivery_content="Federal education funds (contingent on desegregation compliance)",
                quantity=None,  # Varied by district
                units="USD",
                temporal_rate="annual",
                
                threshold=0.0,  # Any non-compliance triggers review
                threshold_direction="below",
                certainty=1.0,
                data_sources=["HEW enforcement 1965-1972"]
            ),
            Delivery(
                delivery_type="rule",
                delivery_content="Desegregation plans required for federal funding eligibility",
                temporal_rate="annual",
                certainty=1.0,
                data_sources=["HEW guidelines 1965-1968"]
            )
        ]
    ))

    # Civil Rights Movement → Federal Government
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=civil_rights_movement.id,
        target_component_id=federal_government.id,
        cell_description=(
            "Grassroots organizing, protests, and litigation pressure federal action. "
            "NAACP Legal Defense Fund continues legal campaigns. March on Washington "
            "(1963) builds political will for Civil Rights Act."
        ),
        deliveries=[
            Delivery(
                delivery_type="information",
                delivery_content="Political pressure for enforcement, documentation of non-compliance",
                temporal_rate="continuous",
                certainty=0.9,
                data_sources=["NAACP litigation strategy", "March on Washington 1963"]
            ),
            Delivery(
                delivery_type="authority",
                delivery_content="Moral authority and public opinion shift toward integration",
                certainty=0.8,
                data_sources=["Civil rights protests and media coverage"]
            )
        ]
    ))

    # ==========================================================================
    # DELIVERIES - Phase 4: Busing Era (1971-1980)
    # ==========================================================================

    # Supreme Court → Busing System
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=supreme_court.id,
        target_component_id=busing_system.id,
        cell_description=(
            "Swann v. Charlotte-Mecklenburg (1971) approves busing as desegregation "
            "tool. Green v. County School Board (1968) requires 'immediate' action, "
            "ending 'deliberate speed' era."
        ),
        deliveries=[
            Delivery(
                delivery_type="authority",
                delivery_content="Legal authorization for mandatory busing to achieve racial balance",
                temporal_rate="singular_event",
                
                certainty=1.0,
                data_sources=["Swann v. Charlotte, 402 U.S. 1 (1971)"]
            ),
            Delivery(
                delivery_type="rule",
                delivery_content="School districts must eliminate racial identifiability 'root and branch'",
                temporal_rate="continuous",
                certainty=1.0,
                data_sources=["Green v. County School Board, 391 U.S. 430 (1968)"]
            )
        ]
    ))

    # Busing System → Black Students
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=busing_system.id,
        target_component_id=black_students.id,
        cell_description=(
            "Busing delivers access to previously white schools but triggers white "
            "flight and backlash. Controversial implementation, varying by region."
        ),
        deliveries=[
            Delivery(
                delivery_type="energy",
                delivery_content="Transportation to integrated schools (physical access)",
                temporal_rate="daily",
                
                certainty=0.9,
                data_sources=["Busing programs 1971-1980"]
            ),
            Delivery(
                delivery_type="information",
                delivery_content="Access to better-resourced educational facilities",
                certainty=0.7,
                data_sources=["Educational outcome studies 1970s"]
            )
        ]
    ))

    # Busing System → White Families
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=busing_system.id,
        target_component_id=white_families.id,
        cell_description=(
            "Mandatory busing triggers 'white flight' to suburbs (Milliken v. Bradley "
            "1974 blocks inter-district remedies) and private school enrollment surge."
        ),
        deliveries=[
            Delivery(
                delivery_type="rule",
                delivery_content="Mandatory assignment to achieve racial balance",
                temporal_rate="annual",
                
                certainty=1.0,
                data_sources=["Court-ordered busing plans"]
            )
        ]
    ))

    # ==========================================================================
    # DELIVERIES - Resource Flows and Outcomes
    # ==========================================================================

    # Local School Boards → Black Schools
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=local_school_boards.id,
        target_component_id=black_schools.id,
        cell_description=(
            "During desegregation, many historically Black schools closed, Black "
            "teachers/principals displaced. Loss of community institutions."
        ),
        deliveries=[
            Delivery(
                delivery_type="authority",
                delivery_content="School closures, staff terminations during consolidation",
                temporal_rate="transition_period",
                
                certainty=0.9,
                data_sources=["Black educator displacement studies 1960s-70s"]
            )
        ]
    ))

    # Local School Boards → White Schools
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=local_school_boards.id,
        target_component_id=white_schools.id,
        cell_description=(
            "White schools receive Black students via integration plans. Resource "
            "distribution and teacher assignments remain contentious."
        ),
        deliveries=[
            Delivery(
                delivery_type="energy",
                delivery_content="Integration of Black students into formerly white schools",
                temporal_rate="annual",
                
                certainty=0.95,
                data_sources=["Desegregation statistics 1968-1980"]
            )
        ]
    ))

    # Federal Education Funds → Local School Boards
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=federal_education_funds.id,
        target_component_id=local_school_boards.id,
        cell_description=(
            "Federal funding increases via ESEA (1965), conditioned on Title VI "
            "compliance. Financial leverage accelerates Southern desegregation."
        ),
        deliveries=[
            Delivery(
                delivery_type="money",
                delivery_content="Elementary and Secondary Education Act funding (compliance-dependent)",
                quantity=None,  # Billions allocated
                units="USD",
                temporal_rate="annual",
                
                threshold=1.0,  # Full compliance required
                threshold_direction="above",
                certainty=1.0,
                data_sources=["ESEA appropriations 1965-1980"]
            )
        ]
    ))

    # White Families → Segregationist Culture
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=white_families.id,
        target_component_id=segregationist_culture.id,
        cell_description=(
            "White flight and private school academies perpetuate de facto segregation. "
            "Residential segregation persists, undermining integration goals."
        ),
        deliveries=[
            Delivery(
                delivery_type="energy",
                delivery_content="Demographic movement to suburbs, private school enrollment",
                temporal_rate="continuous",
                certainty=0.9,
                data_sources=["Urban demographic shifts 1960s-1980s"]
            ),
            Delivery(
                delivery_type="information",
                delivery_content="Political backlash against busing, anti-busing activism",
                certainty=0.85,
                data_sources=["Boston busing protests 1974-1976"]
            )
        ]
    ))

    # Black Students → Civil Rights Movement
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=black_students.id,
        target_component_id=civil_rights_movement.id,
        cell_description=(
            "Black students endure harassment and violence (Little Rock Nine, Ruby "
            "Bridges), becoming symbols of civil rights struggle and courage."
        ),
        deliveries=[
            Delivery(
                delivery_type="information",
                delivery_content="Lived experience of integration, documentation of resistance and violence",
                temporal_rate="continuous",
                certainty=1.0,
                data_sources=["Little Rock Nine testimony", "Ruby Bridges experience"]
            )
        ]
    ))

    # Civil Rights Movement → Legal Precedent
    matrix.set_cell(SFMDeliveryCell(
        source_component_id=civil_rights_movement.id,
        target_component_id=legal_precedent.id,
        cell_description=(
            "NAACP Legal Defense Fund litigation expands Brown precedent: Green (1968), "
            "Swann (1971), but limited by Milliken (1974) suburban protection."
        ),
        deliveries=[
            Delivery(
                delivery_type="information",
                delivery_content="Test cases, fact patterns, litigation strategy expanding desegregation law",
                temporal_rate="continuous",
                
                certainty=0.9,
                data_sources=["NAACP LDF case history 1954-1980"]
            )
        ]
    ))

    # ==========================================================================
    # VALIDATION AND EXPORT
    # ==========================================================================

    errors = service.validate_delivery_matrix(matrix)
    if errors:
        print("⚠ Matrix validation warnings:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Matrix validation passed")

    return matrix


def analyze_matrix(matrix: SFMDeliveryMatrix, service: SFMService):
    """Analyze Brown v. Board delivery matrix for key patterns."""

    print()
    print("=" * 80)
    print("BROWN V. BOARD OF EDUCATION: SFM ANALYSIS FINDINGS")
    print("=" * 80)
    print()

    # Summary statistics
    non_empty_cells = matrix.get_non_empty_cells()
    total_deliveries = sum(len(cell.deliveries) for cell in non_empty_cells)

    print(f"Matrix Summary:")
    print(f"  Components: {len(matrix.components)}")
    print(f"  Non-empty cells: {len(non_empty_cells)}")
    print(f"  Total deliveries: {total_deliveries}")
    print()

    # Delivery type breakdown
    delivery_types = {}
    for cell in non_empty_cells:
        for delivery in cell.deliveries:
            delivery_types[delivery.delivery_type] = delivery_types.get(delivery.delivery_type, 0) + 1

    print("Deliveries by type:")
    for dtype, count in sorted(delivery_types.items()):
        print(f"  {dtype}: {count}")
    print()

    # Multiple deliveries per cell
    multi_delivery_cells = [cell for cell in non_empty_cells if len(cell.deliveries) > 1]
    print(f"Cells with multiple deliveries: {len(multi_delivery_cells)}")

    # Quantified deliveries
    quantified = sum(
        1 for cell in non_empty_cells
        for delivery in cell.deliveries
        if delivery.quantity is not None
    )
    print(f"Quantified deliveries: {quantified}")
    print()

    # Key findings
    print("=" * 80)
    print("KEY INSTITUTIONAL FINDINGS:")
    print("=" * 80)
    print()

    print("1. CEREMONIAL vs. INSTRUMENTAL CONFLICT (Hayden Framework):")
    print()
    print("   CEREMONIAL (Status-quo preservation):")
    print("   • Segregationist culture delivered authority and information to state govts")
    print("   • Massive resistance: interposition laws, school closures, tuition grants")
    print("   • White supremacy beliefs legitimized defiance of federal authority")
    print("   • Southern Manifesto (1956): 101 congressmen denounced Brown")
    print()
    print("   INSTRUMENTAL (Problem-solving):")
    print("   • Supreme Court delivered constitutional interpretation based on evidence")
    print("   • Educational research (Kenneth Clark) provided psychological harm data")
    print("   • Federal enforcement (troops, funding leverage) addressed resistance")
    print("   • Civil Rights Movement mobilized grassroots pressure for implementation")
    print()

    print("2. DELIVERY PATTERN ANALYSIS:")
    print()
    print("   Authority Deliveries:")
    print("   • Supreme Court → Legal precedent (Brown I & II)")
    print("   • Federal govt → States (Little Rock troops enforcement)")
    print("   • Congress → Federal govt (Title VI enforcement power)")
    print("   • Supreme Court → Busing system (Swann authorization)")
    print()
    print("   Rule Deliveries:")
    print("   • Supreme Court → School boards ('deliberate speed' mandate)")
    print("   • States → School boards (massive resistance laws)")
    print("   • Congress → Federal govt (Title VI withholding authority)")
    print("   • Busing system → White families (mandatory assignment)")
    print()
    print("   Money/Resource Deliveries:")
    print("   • Federal funds → School boards (ESEA, Title VI conditional)")
    print("   • States → Segregation academies (tuition grants)")
    print("   • School boards → Schools (redistribution during integration)")
    print()
    print("   Information Deliveries:")
    print("   • Research → Supreme Court (psychological harm evidence)")
    print("   • Civil Rights Movement → Federal govt (compliance documentation)")
    print("   • Black students → Movement (lived experience, testimony)")
    print()

    print("3. TEMPORAL IMPLEMENTATION PATTERNS:")
    print()
    print("   Phase 1 (1954-1955): Judicial authority without enforcement")
    print("   • 'Deliberate speed' created implementation vacuum")
    print("   • Minimal desegregation: Southern resistance mobilizes")
    print()
    print("   Phase 2 (1956-1963): Massive Resistance")
    print("   • States enact interposition laws, close schools")
    print("   • Federal military intervention (Little Rock 1957)")
    print("   • Only 2.3% of Southern Black students in integrated schools by 1964")
    print()
    print("   Phase 3 (1964-1968): Federal Legislative Leverage")
    print("   • Title VI (1964) + ESEA (1965) = financial enforcement")
    print("   • Desegregation accelerates: 2.3% (1964) → 32% (1968)")
    print("   • Green (1968) requires immediate action, ends 'deliberate speed'")
    print()
    print("   Phase 4 (1971-1980): Busing and White Flight")
    print("   • Swann (1971) authorizes busing for racial balance")
    print("   • Southern integration peaks: 91.3% by 1973")
    print("   • Milliken (1974) blocks inter-district remedies, enables suburban escape")
    print("   • Northern de facto segregation persists via residential patterns")
    print()

    print("4. UNINTENDED CONSEQUENCES:")
    print()
    print("   • Closure of historically Black schools, displacement of Black educators")
    print("   • White flight to suburbs and private 'segregation academies'")
    print("   • Northern cities re-segregate via housing patterns")
    print("   • Busing backlash creates political coalition against integration")
    print("   • De jure segregation ends, but de facto segregation persists")
    print()

    print("5. EFFECTIVENESS OF DELIVERY MECHANISMS:")
    print()
    print("   Most Effective:")
    print("   • Title VI funding leverage (dramatic acceleration 1964-1968)")
    print("   • Military enforcement (symbolic Little Rock success)")
    print("   • Judicial expansion (Green, Swann extend Brown authority)")
    print()
    print("   Least Effective:")
    print("   • Brown II 'deliberate speed' (enabled decade of resistance)")
    print("   • Busing in North (triggered white flight, political backlash)")
    print("   • State compliance without federal pressure (minimal voluntary action)")
    print()

    print("6. HAYDEN SFM INSIGHTS:")
    print()
    print("   • Ceremonial values (white supremacy) initially dominated instrumental")
    print("     problem-solving, requiring 10+ years and federal force to overcome")
    print()
    print("   • Multiple delivery types required: authority alone insufficient,")
    print("     needed money (Title VI) and energy (troops, busing) for implementation")
    print()
    print("   • Cultural transformation lagged institutional change: laws changed")
    print("     faster than beliefs, creating sustained resistance and evasion")
    print()
    print("   • Polychronic implementation: judicial (slow), legislative (episodic),")
    print("     administrative (continuous), cultural (generational) clocks misaligned")
    print()
    print("   • Resource flows (school closures, educator displacement) created")
    print("     unintended delivery patterns undermining integration goals")
    print()

    print("=" * 80)
    print("HISTORICAL OUTCOME (1954-1980):")
    print("=" * 80)
    print()
    print("Southern School Desegregation Progress:")
    print("  1954: 0% of Black students in integrated schools")
    print("  1964: 2.3% (after 10 years of resistance)")
    print("  1968: 32% (after Title VI enforcement)")
    print("  1973: 91.3% (peak integration)")
    print()
    print("Northern/Western Cities:")
    print("  • De facto segregation persisted via residential patterns")
    print("  • Busing triggered white flight and political backlash")
    print("  • Milliken (1974) protected suburban segregation")
    print()
    print("Long-term Structural Changes:")
    print("  • Dismantled de jure (legal) segregation system")
    print("  • Transformed constitutional Equal Protection doctrine")
    print("  • Created federal civil rights enforcement infrastructure")
    print("  • Catalyzed broader Civil Rights Movement (1960s legislation)")
    print()
    print("Persistent Challenges:")
    print("  • De facto segregation via housing, school district boundaries")
    print("  • Achievement gaps persist despite integration")
    print("  • Political backlash limits sustained integration efforts")
    print("  • Cultural attitudes shift slowly across generations")
    print()
    print("=" * 80)


def main():
    """Main execution: build matrix, analyze, and export."""

    service = SFMService()

    print("=" * 80)
    print("BROWN V. BOARD OF EDUCATION (1954)")
    print("Social Fabric Matrix Demonstration Analysis")
    print("=" * 80)
    print()
    print("Analyzing institutional, cultural, and governmental impacts of the")
    print("Supreme Court's landmark desegregation decision from 1954-1980.")
    print()
    print("Components:")
    print("  • Institutions: Supreme Court, Federal/State Govts, Congress, School Boards")
    print("  • Cultural: Segregationist beliefs vs. Civil Rights Movement")
    print("  • Knowledge: Legal precedent, educational research")
    print("  • Resources: Schools, federal funding, busing infrastructure")
    print("  • Individuals: Black students, white families")
    print()

    # Build matrix
    matrix = build_brown_v_board_matrix(service)

    # Export to Excel
    output_path = Path(__file__).parent / "brown_v_board_of_education.xlsx"
    export_delivery_matrix_to_xlsx(
        matrix=matrix,
        filepath=output_path,
        service=service,
        include_cell_descriptions=True
    )

    print(f"✓ Exported to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
    print()

    # Analyze results
    analyze_matrix(matrix, service)

    print("=" * 80)
    print("SOURCES:")
    print("=" * 80)
    print()
    print("1. Brown v. Board of Education, 347 U.S. 483 (1954)")
    print("   https://supreme.justia.com/cases/federal/us/347/483/")
    print()
    print("2. Brown v. Board of Education, 349 U.S. 294 (1955) [Brown II]")
    print("   https://supreme.justia.com/cases/federal/us/349/294/")
    print()
    print("3. Civil Rights Act of 1964, Title VI")
    print("   https://www.justice.gov/crt/fcs/TitleVI-Overview")
    print()
    print("4. Orfield, G., & Eaton, S. E. (1996). Dismantling Desegregation:")
    print("   The Quiet Reversal of Brown v. Board of Education. New Press.")
    print()
    print("5. Patterson, J. T. (2001). Brown v. Board of Education:")
    print("   A Civil Rights Milestone and Its Troubled Legacy. Oxford University Press.")
    print()
    print("6. Clotfelter, C. T. (2004). After Brown: The Rise and Retreat of")
    print("   School Desegregation. Princeton University Press.")
    print()
    print("7. Southern Education Reporting Service (1967).")
    print("   Statistical Summary of School Segregation-Desegregation in the Southern")
    print("   and Border States.")
    print()
    print("8. U.S. Commission on Civil Rights (1977). Reviewing a Decade of")
    print("   School Desegregation, 1966-1975.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
