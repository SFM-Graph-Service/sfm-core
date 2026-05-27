"""
Demonstration of migrating data between NetworkX and Neo4j backends.

This script shows how to:
1. Create a model using NetworkX (in-memory) backend
2. Export the model to JSON
3. Import the model into Neo4j backend
4. Verify data consistency across backends
5. Use export/import for backup and restore

Prerequisites:
    - Neo4j 5.x running for import demonstration
    - pip install neo4j

Usage:
    # Scenario 1: Prototype in NetworkX, deploy to Neo4j
    python examples/backend_migration_demo.py --mode prototype-to-production

    # Scenario 2: Backup Neo4j data to JSON
    python examples/backend_migration_demo.py --mode backup

    # Scenario 3: Restore JSON backup to Neo4j
    python examples/backend_migration_demo.py --mode restore
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import cast

from api.sfm_service import SFMService, SFMServiceConfig
from models.policy_framework import PolicyInstrument
from models.institutional_analysis import InstitutionalStructure
from models.economic_analysis import TransactionCost
from models.sfm_enums import PolicyInstrumentType


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f" {title}")
    print('=' * 70)


def create_sample_model_networkx() -> tuple[SFMService, dict]:
    """
    Create a sample policy model using NetworkX backend.

    Returns:
        Tuple of (service, node_ids_dict)
    """
    print_section("1. Creating Sample Model in NetworkX (In-Memory)")

    # Initialize NetworkX service
    config = SFMServiceConfig(storage_type="networkx")
    service = SFMService(config=config)

    print("✓ Initialized NetworkX backend (in-memory)")

    node_ids = {}

    # Create regulatory institution
    print("\nCreating nodes...")
    regulatory_agency = InstitutionalStructure(
        label="Environmental Protection Agency",
        description="Federal agency responsible for environmental regulation",
        meta={
            "established": "1970",
            "authority": "Clean Air Act",
            "jurisdiction": "federal"
        }
    )
    regulatory_agency = cast(InstitutionalStructure, service.create_node(regulatory_agency))
    node_ids["agency"] = regulatory_agency.id
    print(f"✓ Created: {regulatory_agency.label}")

    # Create policy instrument
    emissions_cap = PolicyInstrument(
        label="Emissions Cap-and-Trade Program",
        description="Market-based approach to controlling pollution",
        instrument_type=PolicyInstrumentType.REGULATORY,
        target_behavior="Reduce greenhouse gas emissions",
        meta={
            "sector": "energy",
            "baseline_year": "2005"
        }
    )
    emissions_cap = cast(PolicyInstrument, service.create_node(emissions_cap))
    node_ids["policy"] = emissions_cap.id
    print(f"✓ Created: {emissions_cap.label}")

    # Create transaction cost
    compliance_cost = TransactionCost(
        label="Emissions Monitoring and Reporting Cost",
        description="Cost of monitoring, measuring, and reporting emissions",
        cost_type="information",
        cost_amount=50000.0,
        meta={
            "frequency": "quarterly",
            "cost_per_facility": "50000"
        }
    )
    compliance_cost = cast(TransactionCost, service.create_node(compliance_cost))
    node_ids["cost"] = compliance_cost.id
    print(f"✓ Created: {compliance_cost.label}")

    stats = service.get_statistics()
    print(f"\n✓ NetworkX model statistics:")
    print(f"  - Total nodes: {stats.total_nodes}")
    print(f"  - Node types: {stats.node_types}")

    return service, node_ids


def export_to_json(service: SFMService, filepath: str):
    """
    Export model from service to JSON file.

    Args:
        service: SFMService instance
        filepath: Path to export JSON file
    """
    print_section("2. Exporting Model to JSON")

    # Create export directory if it doesn't exist
    export_dir = Path(filepath).parent
    export_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting to: {filepath}")

    # Export via service
    export_data = service.export_to_json()

    # Write to file
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)

    # Show file size
    file_size = Path(filepath).stat().st_size
    print(f"✓ Exported {len(export_data['nodes'])} nodes")
    print(f"✓ File size: {file_size:,} bytes")
    print(f"✓ Created: {filepath}")

    # Show sample of exported data
    print(f"\n✓ Export structure:")
    print(f"  - nodes: {len(export_data['nodes'])} items")
    print(f"  - relationships: {len(export_data['relationships'])} items")
    print(f"  - metadata: {export_data['metadata']}")


def import_to_neo4j(filepath: str, neo4j_config: dict) -> SFMService:
    """
    Import model from JSON into Neo4j backend.

    Args:
        filepath: Path to JSON export file
        neo4j_config: Neo4j connection configuration

    Returns:
        SFMService instance connected to Neo4j
    """
    print_section("3. Importing Model into Neo4j")

    # Initialize Neo4j service
    config = SFMServiceConfig(
        storage_type="neo4j",
        neo4j_uri=neo4j_config["uri"],
        neo4j_username=neo4j_config["username"],
        neo4j_password=neo4j_config["password"],
    )
    neo4j_service = SFMService(config=config)

    print(f"✓ Connected to Neo4j at {neo4j_config['uri']}")

    # Clear existing data if any
    initial_stats = neo4j_service.get_statistics()
    if initial_stats.total_nodes > 0:
        print(f"\n⚠ Warning: Neo4j contains {initial_stats.total_nodes} existing nodes")
        print("  Clearing existing data before import...")
        neo4j_service.clear_all_data()
        print("  ✓ Cleared existing data")

    # Read JSON file
    print(f"\nReading from: {filepath}")
    with open(filepath, 'r') as f:
        import_data = json.load(f)

    print(f"✓ Loaded {len(import_data['nodes'])} nodes from JSON")

    # Import into Neo4j
    print("\nImporting into Neo4j...")
    neo4j_service.import_from_json(import_data)

    stats = neo4j_service.get_statistics()
    print(f"\n✓ Import complete!")
    print(f"✓ Neo4j model statistics:")
    print(f"  - Total nodes: {stats.total_nodes}")
    print(f"  - Node types: {stats.node_types}")

    return neo4j_service


def verify_migration(networkx_service: SFMService, neo4j_service: SFMService, original_node_ids: dict):
    """
    Verify that data was migrated correctly between backends.

    Args:
        networkx_service: Original NetworkX service
        neo4j_service: Target Neo4j service
        original_node_ids: Dictionary of original node IDs
    """
    print_section("4. Verifying Migration Consistency")

    # Compare statistics
    nx_stats = networkx_service.get_statistics()
    neo_stats = neo4j_service.get_statistics()

    print("\n✓ Comparing statistics:")
    print(f"  NetworkX nodes: {nx_stats.total_nodes}")
    print(f"  Neo4j nodes: {neo_stats.total_nodes}")
    print(f"  Match: {nx_stats.total_nodes == neo_stats.total_nodes}")

    # Compare node types
    print(f"\n✓ Comparing node types:")
    all_types = set(list(nx_stats.node_types.keys()) + list(neo_stats.node_types.keys()))
    for node_type in sorted(all_types):
        nx_count = nx_stats.node_types.get(node_type, 0)
        neo_count = neo_stats.node_types.get(node_type, 0)
        match = "✓" if nx_count == neo_count else "✗"
        print(f"  {match} {node_type}: NetworkX={nx_count}, Neo4j={neo_count}")

    # Verify individual nodes
    print(f"\n✓ Verifying individual nodes:")
    for key, node_id in original_node_ids.items():
        nx_node = networkx_service.get_node(node_id)
        neo_node = neo4j_service.get_node(node_id)

        if nx_node and neo_node:
            labels_match = nx_node.label == neo_node.label
            match = "✓" if labels_match else "✗"
            print(f"  {match} {key}: {neo_node.label}")
        else:
            print(f"  ✗ {key}: Missing in target backend")


def demonstrate_prototype_to_production():
    """
    Demonstrate typical workflow: prototype in NetworkX, deploy to Neo4j.
    """
    print("\n" + "=" * 70)
    print(" Scenario: Prototype in NetworkX → Deploy to Neo4j")
    print("=" * 70)

    # Step 1: Create model in NetworkX
    networkx_service, node_ids = create_sample_model_networkx()

    # Step 2: Export to JSON
    export_path = "exports/policy_model_backup.json"
    export_to_json(networkx_service, export_path)

    # Step 3: Import to Neo4j
    neo4j_config = {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "neo4j"),
    }

    try:
        neo4j_service = import_to_neo4j(export_path, neo4j_config)

        # Step 4: Verify migration
        verify_migration(networkx_service, neo4j_service, node_ids)

        print_section("Migration Complete!")
        print("\n✓ Model successfully migrated from NetworkX to Neo4j")
        print("✓ Data is now persisted in Neo4j database")
        print("\nNext steps:")
        print("1. View data in Neo4j Browser: http://localhost:7474")
        print("2. Run queries in Neo4j: MATCH (n) RETURN n")
        print("3. Use REST API with Neo4j: docker-compose up api-neo4j")

    except Exception as e:
        print(f"\n✗ Error connecting to Neo4j: {e}")
        print("\nTo complete this demonstration:")
        print("1. Start Neo4j: docker-compose up neo4j")
        print("2. Verify Neo4j is accessible at bolt://localhost:7687")
        print("3. Re-run this script")


def demonstrate_backup():
    """
    Demonstrate backing up Neo4j data to JSON.
    """
    print("\n" + "=" * 70)
    print(" Scenario: Backup Neo4j Data to JSON")
    print("=" * 70)

    neo4j_config = {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "neo4j"),
    }

    try:
        # Connect to Neo4j
        print_section("1. Connecting to Neo4j")
        config = SFMServiceConfig(
            storage_type="neo4j",
            neo4j_uri=neo4j_config["uri"],
            neo4j_username=neo4j_config["username"],
            neo4j_password=neo4j_config["password"],
        )
        service = SFMService(config=config)

        stats = service.get_statistics()
        print(f"✓ Connected to Neo4j at {neo4j_config['uri']}")
        print(f"✓ Found {stats.total_nodes} nodes to backup")

        # Export with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"exports/neo4j_backup_{timestamp}.json"

        export_to_json(service, export_path)

        print_section("Backup Complete!")
        print(f"\n✓ Neo4j data backed up to: {export_path}")
        print("✓ Backup can be restored to any backend (NetworkX or Neo4j)")

    except Exception as e:
        print(f"\n✗ Error connecting to Neo4j: {e}")
        print("\nEnsure Neo4j is running: docker-compose up neo4j")


def demonstrate_restore():
    """
    Demonstrate restoring JSON backup to Neo4j.
    """
    print("\n" + "=" * 70)
    print(" Scenario: Restore JSON Backup to Neo4j")
    print("=" * 70)

    # List available backups
    print_section("1. Available Backups")
    exports_dir = Path("exports")
    if exports_dir.exists():
        backups = list(exports_dir.glob("*.json"))
        if backups:
            print("\nFound backup files:")
            for i, backup in enumerate(backups, 1):
                file_size = backup.stat().st_size
                print(f"  {i}. {backup.name} ({file_size:,} bytes)")

            # Use most recent backup
            latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
            print(f"\n✓ Using latest backup: {latest_backup.name}")

            # Restore to Neo4j
            neo4j_config = {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "username": os.getenv("NEO4J_USERNAME", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "neo4j"),
            }

            try:
                _ = import_to_neo4j(str(latest_backup), neo4j_config)  # Restore to Neo4j

                print_section("Restore Complete!")
                print(f"\n✓ Data restored to Neo4j from: {latest_backup.name}")
                print("✓ View in Neo4j Browser: http://localhost:7474")

            except Exception as e:
                print(f"\n✗ Error restoring to Neo4j: {e}")
                print("\nEnsure Neo4j is running: docker-compose up neo4j")
        else:
            print("✗ No backup files found in exports/")
            print("\nCreate a backup first:")
            print("  python examples/backend_migration_demo.py --mode backup")
    else:
        print("✗ exports/ directory not found")
        print("\nCreate a backup first:")
        print("  python examples/backend_migration_demo.py --mode backup")


def main():
    """Parse arguments and run appropriate demonstration."""
    parser = argparse.ArgumentParser(
        description="Demonstrate migrating data between NetworkX and Neo4j backends"
    )
    parser.add_argument(
        "--mode",
        choices=["prototype-to-production", "backup", "restore"],
        default="prototype-to-production",
        help="Migration scenario to demonstrate"
    )

    args = parser.parse_args()

    if args.mode == "prototype-to-production":
        demonstrate_prototype_to_production()
    elif args.mode == "backup":
        demonstrate_backup()
    elif args.mode == "restore":
        demonstrate_restore()


if __name__ == "__main__":
    main()
