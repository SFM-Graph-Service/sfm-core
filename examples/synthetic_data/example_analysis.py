#!/usr/bin/env python3
"""
Example analysis script demonstrating queries on the synthetic climate network.

Run this to see examples of network analysis using the generated dataset.
"""

import json
from pathlib import Path
from collections import Counter
import statistics


def load_network():
    """Load the network data."""
    filepath = Path(__file__).parent / "climate_network.json"
    with open(filepath, 'r') as f:
        return json.load(f)


def example_1_funding_flows(data):
    """Example 1: Identify major funding sources."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Major Funding Sources")
    print("="*70)

    funding_sources = Counter()
    for rel in data['relationships']:
        if rel['delivery_type'] == 'money':
            source_id = rel['source']
            source_node = next(n for n in data['nodes'] if n['id'] == source_id)
            funding_sources[source_node['name']] += 1

    print("\nTop 10 institutions providing funding:")
    for source, count in funding_sources.most_common(10):
        print(f"  {source:50s} {count:3d} grants/investments")


def example_2_regulatory_chains(data):
    """Example 2: Trace regulatory relationships."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Federal Regulatory Reach")
    print("="*70)

    # Find EPA
    epa = next(n for n in data['nodes'] if 'Environmental Protection Agency' in n['name'])

    # Find all regulatory relationships from EPA
    epa_regulations = [
        r for r in data['relationships']
        if r['source'] == epa['id'] and r['type'] == 'regulatory'
    ]

    print(f"\nEPA has {len(epa_regulations)} direct regulatory relationships")

    # Show targets by category
    targets_by_category = Counter()
    for rel in epa_regulations:
        target = next(n for n in data['nodes'] if n['id'] == rel['target'])
        targets_by_category[target['category']] += 1

    print("\nRegulatory targets by category:")
    for category, count in targets_by_category.most_common():
        print(f"  {category:30s} {count:3d}")


def example_3_geographic_distribution(data):
    """Example 3: Analyze geographic scope."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Geographic Distribution")
    print("="*70)

    scope_counts = Counter()
    for node in data['nodes']:
        scope = node['metadata'].get('geographic_scope', 'unknown')
        scope_counts[scope] += 1

    print("\nNodes by geographic scope:")
    for scope, count in sorted(scope_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {scope:20s} {count:4d}")

    # State coverage
    state_nodes = [n for n in data['nodes'] if n['category'] == 'state_agency']
    states = set(n['metadata'].get('state') for n in state_nodes if 'state' in n['metadata'])

    print(f"\nNetwork covers {len(states)} US states")


def example_4_ceremonial_instrumental(data):
    """Example 4: Ceremonial vs Instrumental scores."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Ceremonial vs Instrumental Analysis")
    print("="*70)

    ceremonial_scores = [n['metadata']['ceremonial_score'] for n in data['nodes']]
    instrumental_scores = [n['metadata']['instrumental_score'] for n in data['nodes']]

    print("\nCeremonial scores:")
    print(f"  Mean:   {statistics.mean(ceremonial_scores):.3f}")
    print(f"  Median: {statistics.median(ceremonial_scores):.3f}")
    print(f"  Min:    {min(ceremonial_scores):.3f}")
    print(f"  Max:    {max(ceremonial_scores):.3f}")

    print("\nInstrumental scores:")
    print(f"  Mean:   {statistics.mean(instrumental_scores):.3f}")
    print(f"  Median: {statistics.median(instrumental_scores):.3f}")
    print(f"  Min:    {min(instrumental_scores):.3f}")
    print(f"  Max:    {max(instrumental_scores):.3f}")

    # Correlation
    n = len(ceremonial_scores)
    mean_c = statistics.mean(ceremonial_scores)
    mean_i = statistics.mean(instrumental_scores)
    covariance = sum((c - mean_c) * (i - mean_i) for c, i in zip(ceremonial_scores, instrumental_scores)) / n
    std_c = statistics.stdev(ceremonial_scores)
    std_i = statistics.stdev(instrumental_scores)
    correlation = covariance / (std_c * std_i)

    print(f"\nCorrelation: {correlation:.3f}")
    print("(Negative correlation expected - ceremonial and instrumental are inversely related)")


def example_5_most_connected(data):
    """Example 5: Network centrality."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Most Connected Institutions")
    print("="*70)

    # Count degrees
    in_degree = Counter()
    out_degree = Counter()

    for rel in data['relationships']:
        out_degree[rel['source']] += 1
        in_degree[rel['target']] += 1

    # Find node names
    def get_node_name(node_id):
        return next(n['name'] for n in data['nodes'] if n['id'] == node_id)

    print("\nMost Influential (highest out-degree):")
    for node_id, count in out_degree.most_common(10):
        print(f"  {get_node_name(node_id):50s} {count:3d}")

    print("\nMost Referenced (highest in-degree):")
    for node_id, count in in_degree.most_common(10):
        print(f"  {get_node_name(node_id):50s} {count:3d}")


def example_6_technology_deployment(data):
    """Example 6: Technology deployment patterns."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Technology Deployment Patterns")
    print("="*70)

    tech_deployment = Counter()

    for rel in data['relationships']:
        if rel['type'] == 'deployment':
            target = next(n for n in data['nodes'] if n['id'] == rel['target'])
            if target['type'] == 'technology_system':
                tech_deployment[target['name']] += 1

    print("\nMost deployed technologies:")
    for tech, count in tech_deployment.most_common(15):
        print(f"  {tech:50s} {count:3d} deployments")


def example_7_policy_implementation(data):
    """Example 7: Policy implementation chains."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Policy Implementation")
    print("="*70)

    # Find climate-related policies
    policies = [n for n in data['nodes'] if n['category'] in ['regulation', 'program']]

    # Count implementations
    policy_implementations = Counter()
    for rel in data['relationships']:
        if rel['type'] == 'implementation':
            target = next(n for n in data['nodes'] if n['id'] == rel['target'])
            if target in policies:
                policy_implementations[target['name']] += 1

    print("\nMost widely implemented policies:")
    for policy, count in policy_implementations.most_common(10):
        print(f"  {policy:50s} {count:3d} implementations")


def example_8_collaboration_networks(data):
    """Example 8: Collaboration patterns."""
    print("\n" + "="*70)
    print("EXAMPLE 8: Collaboration Networks")
    print("="*70)

    # Count collaborations by category
    collab_by_category = Counter()
    for rel in data['relationships']:
        if rel['type'] == 'collaboration':
            source = next(n for n in data['nodes'] if n['id'] == rel['source'])
            target = next(n for n in data['nodes'] if n['id'] == rel['target'])
            pair = tuple(sorted([source['category'], target['category']]))
            collab_by_category[pair] += 1

    print("\nTop collaboration patterns (by institution type):")
    for (cat1, cat2), count in collab_by_category.most_common(10):
        print(f"  {cat1:30s} <-> {cat2:30s} {count:3d}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("SYNTHETIC CLIMATE NETWORK: EXAMPLE ANALYSES")
    print("="*70)

    data = load_network()

    print(f"\nDataset: {data['metadata']['name']}")
    print(f"Total Nodes: {data['statistics']['total_nodes']}")
    print(f"Total Relationships: {data['statistics']['total_relationships']}")

    example_1_funding_flows(data)
    example_2_regulatory_chains(data)
    example_3_geographic_distribution(data)
    example_4_ceremonial_instrumental(data)
    example_5_most_connected(data)
    example_6_technology_deployment(data)
    example_7_policy_implementation(data)
    example_8_collaboration_networks(data)

    print("\n" + "="*70)
    print("Analysis complete! See README.md for more query examples.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
