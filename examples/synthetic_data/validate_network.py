#!/usr/bin/env python3
"""
Quick validation script for the synthetic climate network dataset.

Performs basic structural validation and reports statistics.
"""

import json
import sys
from pathlib import Path
from collections import Counter


def validate_network(filepath: Path):
    """Validate network structure and report statistics."""

    print("Loading network...")
    with open(filepath, 'r') as f:
        data = json.load(f)

    print(f"\nDataset: {data['metadata']['name']}")
    print(f"Generated: {data['metadata']['generated']}")
    print(f"Scenario: {data['metadata']['scenario']}")

    nodes = data['nodes']
    relationships = data['relationships']
    stats = data['statistics']

    print(f"\n{'='*60}")
    print("VALIDATION CHECKS")
    print('='*60)

    # Check node IDs are unique
    node_ids = [n['id'] for n in nodes]
    if len(node_ids) != len(set(node_ids)):
        print("✗ FAILED: Duplicate node IDs found")
        return False
    print("✓ All node IDs are unique")

    # Check node names are unique
    node_names = [n['name'] for n in nodes]
    if len(node_names) != len(set(node_names)):
        duplicates = [name for name, count in Counter(node_names).items() if count > 1]
        print(f"✗ FAILED: Duplicate node names: {duplicates[:5]}")
        return False
    print("✓ All node names are unique")

    # Check all nodes have required fields
    required_node_fields = ['id', 'name', 'type', 'category', 'metadata']
    for node in nodes:
        missing = [f for f in required_node_fields if f not in node]
        if missing:
            print(f"✗ FAILED: Node {node.get('name', '???')} missing fields: {missing}")
            return False
    print("✓ All nodes have required fields")

    # Check metadata fields
    required_metadata = ['ceremonial_score', 'instrumental_score', 'geographic_scope']
    for node in nodes:
        missing = [f for f in required_metadata if f not in node['metadata']]
        if missing:
            print(f"✗ FAILED: Node {node['name']} missing metadata: {missing}")
            return False
    print("✓ All nodes have required metadata")

    # Validate ceremonial/instrumental scores
    for node in nodes:
        c_score = node['metadata']['ceremonial_score']
        i_score = node['metadata']['instrumental_score']
        if not (0 <= c_score <= 1):
            print(f"✗ FAILED: Invalid ceremonial score for {node['name']}: {c_score}")
            return False
        if not (0 <= i_score <= 1):
            print(f"✗ FAILED: Invalid instrumental score for {node['name']}: {i_score}")
            return False
    print("✓ All ceremonial/instrumental scores valid (0-1)")

    # Check relationship IDs are unique
    rel_ids = [r['id'] for r in relationships]
    if len(rel_ids) != len(set(rel_ids)):
        print("✗ FAILED: Duplicate relationship IDs found")
        return False
    print("✓ All relationship IDs are unique")

    # Check all relationships have required fields
    required_rel_fields = ['id', 'source', 'target', 'type', 'delivery_type', 'strength']
    for rel in relationships:
        missing = [f for f in required_rel_fields if f not in rel]
        if missing:
            print(f"✗ FAILED: Relationship {rel.get('id', '???')} missing fields: {missing}")
            return False
    print("✓ All relationships have required fields")

    # Check relationship references point to valid nodes
    node_id_set = set(node_ids)
    for rel in relationships:
        if rel['source'] not in node_id_set:
            print(f"✗ FAILED: Relationship {rel['id']} has invalid source: {rel['source']}")
            return False
        if rel['target'] not in node_id_set:
            print(f"✗ FAILED: Relationship {rel['id']} has invalid target: {rel['target']}")
            return False
    print("✓ All relationship references are valid")

    # Check relationship strengths
    for rel in relationships:
        strength = rel['strength']
        if not (0 <= strength <= 1):
            print(f"✗ FAILED: Invalid relationship strength: {strength}")
            return False
    print("✓ All relationship strengths valid (0-1)")

    # Statistics validation
    if stats['total_nodes'] != len(nodes):
        print(f"✗ FAILED: Node count mismatch: {stats['total_nodes']} != {len(nodes)}")
        return False
    if stats['total_relationships'] != len(relationships):
        print(f"✗ FAILED: Relationship count mismatch")
        return False
    print("✓ Statistics match actual counts")

    print(f"\n{'='*60}")
    print("NETWORK CHARACTERISTICS")
    print('='*60)

    # Category distribution
    print("\nTop 10 Node Categories:")
    for category, count in sorted(
        stats['node_categories'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]:
        print(f"  {category:35s} {count:4d}")

    # Relationship type distribution
    print("\nTop 10 Relationship Types:")
    for rel_type, count in sorted(
        stats['relationship_types'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]:
        print(f"  {rel_type:35s} {count:4d}")

    # Degree statistics
    print(f"\nDegree Statistics:")
    print(f"  Average degree: {stats['avg_out_degree']:.2f}")
    print(f"  Max out-degree: {stats['max_out_degree']}")
    print(f"  Max in-degree: {stats['max_in_degree']}")

    # Find most connected nodes
    in_degree = Counter()
    out_degree = Counter()
    node_lookup = {n['id']: n['name'] for n in nodes}

    for rel in relationships:
        out_degree[rel['source']] += 1
        in_degree[rel['target']] += 1

    print("\nMost Influential Nodes (out-degree):")
    for node_id, count in out_degree.most_common(5):
        print(f"  {node_lookup[node_id]:40s} {count:3d}")

    print("\nMost Referenced Nodes (in-degree):")
    for node_id, count in in_degree.most_common(5):
        print(f"  {node_lookup[node_id]:40s} {count:3d}")

    print(f"\n{'='*60}")
    print("✓ ALL VALIDATION CHECKS PASSED")
    print('='*60)

    return True


if __name__ == "__main__":
    filepath = Path(__file__).parent / "climate_network.json"

    if not filepath.exists():
        print(f"Error: {filepath} not found")
        print("Run generate_large_network.py first")
        sys.exit(1)

    success = validate_network(filepath)
    sys.exit(0 if success else 1)
