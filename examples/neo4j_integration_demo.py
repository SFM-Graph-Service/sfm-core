"""
Demonstration of SFM Core with Neo4j backend integration.

This script shows how to:
1. Configure SFM Service to use Neo4j backend
2. Create institutional analysis models
3. Query relationships using Cypher
4. Perform ceremonial analysis with persistent storage
5. Visualize results in Neo4j Browser

Prerequisites:
    - Neo4j 5.x running (docker-compose up neo4j or standalone installation)
    - pip install neo4j

Configuration:
    Set environment variables or update NEO4J_* constants below:
    - NEO4J_URI: Bolt URI (default: bolt://localhost:7687)
    - NEO4J_USERNAME: Database username (default: neo4j)
    - NEO4J_PASSWORD: Database password (default: neo4j)

Usage:
    # Start Neo4j via Docker
    docker-compose up neo4j

    # Run this script
    python examples/neo4j_integration_demo.py

    # View results in Neo4j Browser
    open http://localhost:7474
"""

import os
from typing import cast

from api.sfm_service import SFMService, SFMServiceConfig
from models.policy_framework import PolicyInstrument, ValueJudgment
from models.institutional_analysis import InstitutionalStructure
from models.economic_analysis import TransactionCost
from models.cultural_analysis import ValueSystem
from models.sfm_enums import PolicyInstrumentType, ValueSystemType, ValueJudgmentType
from data.neo4j_repository import Neo4jSFMRepository

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f" {title}")
    print('=' * 70)


def create_sfm_service() -> SFMService:
    """
    Create SFMService configured for Neo4j backend.

    Returns:
        Configured SFMService instance
    """
    print_section("1. Initializing SFM Service with Neo4j Backend")

    config = SFMServiceConfig(
        storage_type="neo4j",
        neo4j_uri=NEO4J_URI,
        neo4j_username=NEO4J_USERNAME,
        neo4j_password=NEO4J_PASSWORD,
    )

    service = SFMService(config=config)

    print(f"✓ Connected to Neo4j at {NEO4J_URI}")
    print(f"✓ Using credentials: {NEO4J_USERNAME}")

    return service


def create_institutional_model(service: SFMService) -> dict:
    """
    Create a sample institutional analysis model.

    Models agricultural policy with:
    - Federal subsidy program (institution)
    - Direct payment policy (instrument)
    - Environmental values (value system)
    - Administrative costs (transaction cost)

    Args:
        service: SFMService instance

    Returns:
        Dictionary of created node IDs
    """
    print_section("2. Creating Institutional Analysis Model")

    node_ids = {}

    # Create institutional structure
    print("\nCreating Federal Subsidy Program institution...")
    subsidy_program = InstitutionalStructure(
        label="Federal Agricultural Subsidy Program",
        description="USDA program providing direct payments to farmers",
        meta={
            "agency": "USDA",
            "established": "1996",
            "authority": "Federal Agriculture Improvement and Reform Act"
        }
    )
    subsidy_program = cast(InstitutionalStructure, service.create_node(subsidy_program))
    node_ids["subsidy_program"] = subsidy_program.id
    print(f"✓ Created institution: {subsidy_program.label} ({subsidy_program.id})")

    # Create policy instrument
    print("\nCreating Direct Payment policy instrument...")
    direct_payment = PolicyInstrument(
        label="Direct Payment Subsidy",
        description="Annual direct cash payments to eligible farmers",
        instrument_type=PolicyInstrumentType.ECONOMIC,
        target_behavior="Maintain agricultural production capacity",
        meta={
            "payment_type": "decoupled",
            "eligibility": "historical base acres"
        }
    )
    direct_payment = cast(PolicyInstrument, service.create_node(direct_payment))
    node_ids["direct_payment"] = direct_payment.id
    print(f"✓ Created policy: {direct_payment.label} ({direct_payment.id})")

    # Create value system
    print("\nCreating Environmental Sustainability value system...")
    env_values = ValueSystem(
        label="Environmental Sustainability Values",
        description="Public values emphasizing soil conservation and ecological health",
        system_type=ValueSystemType.INSTRUMENTAL_PROBLEM_SOLVING,
        core_values=["environmental_protection", "soil_conservation", "sustainability"],
        meta={
            "emphasis": "soil_conservation",
            "time_horizon": "long_term"
        }
    )
    env_values = cast(ValueSystem, service.create_node(env_values))
    node_ids["env_values"] = env_values.id
    print(f"✓ Created value system: {env_values.label} ({env_values.id})")

    # Create transaction cost
    print("\nCreating Administrative Cost transaction cost...")
    admin_cost = TransactionCost(
        label="Subsidy Application Processing Cost",
        description="Administrative burden of processing and verifying applications",
        cost_type="coordination",
        cost_amount=250.0,
        time_cost=45.0,
        meta={
            "cost_per_application": "250",
            "processing_time_days": "45"
        }
    )
    admin_cost = cast(TransactionCost, service.create_node(admin_cost))
    node_ids["admin_cost"] = admin_cost.id
    print(f"✓ Created transaction cost: {admin_cost.label} ({admin_cost.id})")

    # Create value judgment linking policy to values
    print("\nCreating Value Judgment linking policy to values...")
    value_judgment = ValueJudgment(
        label="Subsidy-Environment Value Tension",
        description="Direct payments may incentivize production over conservation",
        justification="Economic incentives vs environmental protection",
        controversy_level=0.7,  # High controversy
        judgment_type=ValueJudgmentType.SUSTAINABILITY,
        meta={
            "conflict_type": "instrumental_vs_ceremonial",
            "resolution_status": "unresolved"
        }
    )
    value_judgment = cast(ValueJudgment, service.create_node(value_judgment))
    node_ids["value_judgment"] = value_judgment.id
    print(f"✓ Created value judgment: {value_judgment.label} ({value_judgment.id})")

    print(f"\n✓ Created {len(node_ids)} nodes in Neo4j")
    print(f"✓ Total nodes in graph: {service.get_health().node_count}")

    return node_ids


def demonstrate_cypher_queries(service: SFMService, node_ids: dict):
    """
    Demonstrate direct Cypher queries using Neo4j backend.

    Args:
        service: SFMService instance
        node_ids: Dictionary of created node IDs
    """
    print_section("3. Running Cypher Queries")

    # Access Neo4j repository directly
    neo4j_repo = cast(Neo4jSFMRepository, service.repository)

    # Query 1: Find all PolicyInstrument nodes
    print("\nQuery 1: Find all PolicyInstrument nodes")
    query1 = """
    MATCH (n:PolicyInstrument)
    RETURN n.label as label, n.description as description, n.instrument_type as type
    """
    results = neo4j_repo.execute_query(query1)
    for record in results:
        print(f"  - {record['label']}: {record['type']}")

    # Query 2: Find nodes with environmental metadata
    print("\nQuery 2: Find nodes with environmental emphasis")
    query2 = """
    MATCH (n)
    WHERE n.meta_emphasis = 'soil_conservation'
    RETURN n.label as label, labels(n) as node_types
    """
    results = neo4j_repo.execute_query(query2)
    for record in results:
        print(f"  - {record['label']} ({record['node_types'][0]})")

    # Query 3: Count nodes by type
    print("\nQuery 3: Count nodes by type")
    query3 = """
    MATCH (n)
    RETURN labels(n)[0] as node_type, count(*) as count
    ORDER BY count DESC
    """
    results = neo4j_repo.execute_query(query3)
    for record in results:
        print(f"  - {record['node_type']}: {record['count']}")

    # Query 4: Find all transaction costs
    print("\nQuery 4: Find transaction costs with cost amount")
    query4 = """
    MATCH (n:TransactionCost)
    RETURN n.label as label, n.cost_amount as cost_amount, n.cost_type as type
    """
    results = neo4j_repo.execute_query(query4)
    for record in results:
        print(f"  - {record['label']}: ${record['cost_amount']} ({record['type']})")


def demonstrate_ceremonial_analysis(service: SFMService):
    """
    Demonstrate ceremonial vs instrumental analysis with Neo4j persistence.

    Args:
        service: SFMService instance
    """
    print_section("4. Ceremonial vs Instrumental Analysis")

    print("\nRunning ceremonial analysis (threshold=0.5)...")
    analysis = service.get_ceremonial_analysis(threshold=0.5)

    print(f"\n✓ Analysis Results:")
    print(f"  - Ceremonial nodes: {len(analysis['ceremonial_nodes'])}")
    print(f"  - Instrumental nodes: {len(analysis['instrumental_nodes'])}")
    print(f"  - Ceremonial ratio: {analysis['ceremonial_ratio']:.2%}")
    print(f"  - Threshold used: {analysis['threshold']}")

    if analysis['ceremonial_nodes']:
        print(f"\n  Ceremonial node IDs:")
        for node_id in analysis['ceremonial_nodes'][:3]:  # Show first 3
            print(f"    - {node_id}")

    if analysis['instrumental_nodes']:
        print(f"\n  Instrumental node IDs:")
        for node_id in analysis['instrumental_nodes'][:3]:  # Show first 3
            print(f"    - {node_id}")


def demonstrate_statistics(service: SFMService):
    """
    Show graph statistics from Neo4j.

    Args:
        service: SFMService instance
    """
    print_section("5. Graph Statistics")

    stats = service.get_statistics()

    print(f"\n✓ Total nodes: {stats.total_nodes}")
    print(f"✓ Total relationships: {stats.total_relationships}")
    print(f"\n✓ Node types:")
    for node_type, count in sorted(stats.node_types.items()):
        print(f"  - {node_type}: {count}")


def demonstrate_neo4j_browser_queries():
    """
    Print example Cypher queries for Neo4j Browser exploration.
    """
    print_section("6. Neo4j Browser Exploration")

    print("\nOpen Neo4j Browser at: http://localhost:7474")
    print("\nUseful Cypher queries to run in Neo4j Browser:")

    print("\n1. View all nodes:")
    print("   MATCH (n) RETURN n LIMIT 25")

    print("\n2. View nodes by type:")
    print("   MATCH (n:PolicyInstrument) RETURN n")
    print("   MATCH (n:InstitutionalStructure) RETURN n")
    print("   MATCH (n:ValueSystem) RETURN n")

    print("\n3. View node properties:")
    print("   MATCH (n:PolicyInstrument)")
    print("   RETURN n.label, n.description, n.instrument_type, n.meta")

    print("\n4. Search by label:")
    print("   MATCH (n)")
    print("   WHERE n.label CONTAINS 'Subsidy'")
    print("   RETURN n")

    print("\n5. View metadata:")
    print("   MATCH (n)")
    print("   WHERE exists(n.meta_agency)")
    print("   RETURN n.label, n.meta_agency, n.meta_established")

    print("\n6. Count by type:")
    print("   MATCH (n)")
    print("   RETURN labels(n)[0] as type, count(*) as count")
    print("   ORDER BY count DESC")


def cleanup(service: SFMService):
    """
    Optional: Clear all data from Neo4j.

    Args:
        service: SFMService instance
    """
    print_section("7. Cleanup (Optional)")

    print("\nTo clear all data from Neo4j:")
    print("  Option 1: service.clear_all_data()")
    print("  Option 2: In Neo4j Browser run: MATCH (n) DETACH DELETE n")
    print("\nSkipping cleanup to allow Neo4j Browser exploration...")


def main():
    """Run all Neo4j integration demonstrations."""
    print("\n" + "=" * 70)
    print(" SFM Core with Neo4j Backend Integration")
    print("=" * 70)
    print("\nThis script demonstrates using SFM Core with Neo4j for persistent storage.")
    print(f"Neo4j URI: {NEO4J_URI}")

    try:
        # 1. Initialize service
        service = create_sfm_service()

        # 2. Create institutional model
        node_ids = create_institutional_model(service)

        # 3. Demonstrate Cypher queries
        demonstrate_cypher_queries(service, node_ids)

        # 4. Run ceremonial analysis
        demonstrate_ceremonial_analysis(service)

        # 5. Show statistics
        demonstrate_statistics(service)

        # 6. Neo4j Browser queries
        demonstrate_neo4j_browser_queries()

        # 7. Cleanup info
        cleanup(service)

        print("\n" + "=" * 70)
        print(" Demo Complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Open Neo4j Browser at http://localhost:7474")
        print("2. Login with neo4j/neo4j (or your configured password)")
        print("3. Run the Cypher queries shown above to explore the data")
        print("4. Try the REST API with Neo4j: docker-compose up api-neo4j")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Neo4j is running: docker-compose up neo4j")
        print("2. Check Neo4j credentials match configuration")
        print("3. Verify Neo4j is accessible at", NEO4J_URI)
        print("4. Check Neo4j logs: docker-compose logs neo4j")
        raise


if __name__ == "__main__":
    main()
