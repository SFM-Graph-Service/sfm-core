"""
Cross-Case Comparison for Hayden Case Studies

Runs the SFM analysis battery across all four case studies and produces
a comparison table showing relative complexity, analytical patterns, and
methodological features.

Usage:
    python examples/hayden_case_studies/compare_cases.py
"""

from pathlib import Path
from typing import Dict, Any, List, Callable
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.hayden_case_studies.clean_air_act_1970 import create_clean_air_act_matrix
from examples.hayden_case_studies.director_networks import create_director_network_matrix
from examples.hayden_case_studies.radioactive_waste import create_llrw_matrix
from examples.hayden_case_studies.nebraska_k12_finance import build_nebraska_k12_matrix
from graph.analysis_report import run_analysis_battery


def analyze_case_study(name: str, builder_func: Callable[[], Any]) -> Dict[str, Any]:
    """
    Run analysis battery on a case study and extract comparison metrics.

    Args:
        name: Name of the case study
        builder_func: Function that builds the matrix

    Returns:
        Dict with comparison metrics
    """
    print(f"\nAnalyzing {name}...")

    # Build matrix
    matrix, service = builder_func()

    # Run analysis battery
    report = run_analysis_battery(service)

    # Extract metrics
    total_deliveries = sum(len(cell.deliveries) for cell in matrix.cells.values())
    metrics: Dict[str, Any] = {
        "name": name,
        "components": len(matrix.components),
        "cells": len(matrix.get_non_empty_cells()),
        "deliveries": total_deliveries,
    }

    # Extract analysis battery results
    if report:
        # Circular causation paths
        metrics["circular_paths"] = len(report.circular_causation_paths)

        # Ceremonial-instrumental
        ceremonial_count = len(report.ceremonial_nodes)
        instrumental_count = len(report.instrumental_nodes)
        total_classified = ceremonial_count + instrumental_count

        if total_classified > 0:
            metrics["ci_ratio"] = round(report.ceremonial_ratio, 2)
        else:
            metrics["ci_ratio"] = "N/A"

        # Holarchy levels
        # holarchy_levels is Dict[str, Dict[str, List[Dict]]]
        # Count unique levels across all nodes
        all_levels: set[str] = set()
        for node_label, level_dict in report.holarchy_levels.items():
            all_levels.update(level_dict.keys())
        metrics["holarchy_levels"] = len(all_levels)

        # Conflicts
        metrics["conflicts"] = len(report.conflicts)

        # Feedback cycles
        metrics["feedback_cycles"] = len(report.feedback_cycles)

        # Temporal evolution
        metrics["has_temporal"] = report.temporal_snapshots is not None and len(report.temporal_snapshots) > 0

    # Delivery type diversity
    delivery_types = set()
    for cell in matrix.cells.values():
        for delivery in cell.deliveries:
            delivery_types.add(delivery.delivery_type)
    metrics["delivery_types"] = len(delivery_types)

    # Quantified deliveries
    quantified = sum(
        1 for cell in matrix.cells.values()
        for delivery in cell.deliveries
        if delivery.quantity is not None
    )
    metrics["quantified_deliveries"] = quantified
    metrics["quantification_rate"] = round(quantified / total_deliveries * 100, 1) if total_deliveries > 0 else 0

    # Check for criteria evaluation
    from models import SFMCriteria
    criteria_count = sum(1 for node in service.list_nodes() if isinstance(node, SFMCriteria))
    metrics["criteria_count"] = criteria_count

    # Cells with multiple deliveries
    multi_delivery_cells = sum(1 for cell in matrix.cells.values() if len(cell.deliveries) > 1)
    metrics["multi_delivery_cells"] = multi_delivery_cells

    return metrics


def print_comparison_table(results: List[Dict[str, Any]]) -> None:
    """
    Print formatted comparison table.

    Args:
        results: List of metrics dicts from analyze_case_study
    """
    print("\n" + "=" * 120)
    print("HAYDEN CASE STUDIES COMPARISON TABLE")
    print("=" * 120)
    print()

    # Header row
    header = f"{'Case Study':<30} {'Comp':<6} {'Cells':<6} {'Deliv':<6} {'Types':<6} {'Quant%':<7} {'Circ':<6} {'C/I':<6} {'Levels':<7} {'Conf':<6} {'Feed':<6} {'Crit':<6} {'Multi':<6}"
    print(header)
    print("-" * 120)

    # Data rows
    for metrics in results:
        row = f"{metrics['name']:<30} "
        row += f"{metrics['components']:<6} "
        row += f"{metrics['cells']:<6} "
        row += f"{metrics['deliveries']:<6} "
        row += f"{metrics['delivery_types']:<6} "
        row += f"{metrics['quantification_rate']:<7} "
        row += f"{metrics.get('circular_paths', 0):<6} "
        row += f"{str(metrics.get('ci_ratio', 'N/A')):<6} "
        row += f"{metrics.get('holarchy_levels', 0):<7} "
        row += f"{metrics.get('conflicts', 0):<6} "
        row += f"{metrics.get('feedback_cycles', 0):<6} "
        row += f"{metrics.get('criteria_count', 0):<6} "
        row += f"{metrics.get('multi_delivery_cells', 0):<6}"
        print(row)

    print()
    print("Column Legend:")
    print("  Comp   = Components in matrix")
    print("  Cells  = Non-empty delivery cells")
    print("  Deliv  = Total deliveries")
    print("  Types  = Distinct delivery types (money, rule, authority, etc.)")
    print("  Quant% = Percentage of deliveries with quantified values")
    print("  Circ   = Circular causation paths detected")
    print("  C/I    = Ceremonial/Instrumental ratio (ceremonial / total classified)")
    print("  Levels = Holarchy levels detected")
    print("  Conf   = Conflicts/contradictions detected")
    print("  Feed   = Feedback cycles detected")
    print("  Crit   = Normative criteria defined")
    print("  Multi  = Cells with multiple deliveries")
    print()


def print_summary_insights(results: List[Dict[str, Any]]) -> None:
    """
    Print summary insights from cross-case comparison.

    Args:
        results: List of metrics dicts
    """
    print("=" * 120)
    print("CROSS-CASE INSIGHTS")
    print("=" * 120)
    print()

    # Find extremes
    most_complex = max(results, key=lambda x: x["deliveries"])
    most_quantified = max(results, key=lambda x: x["quantification_rate"])
    most_criteria = max(results, key=lambda x: x.get("criteria_count", 0))

    print(f"Most Complex: {most_complex['name']}")
    print(f"  - {most_complex['deliveries']} deliveries across {most_complex['cells']} cells")
    print(f"  - {most_complex['delivery_types']} distinct delivery types")
    print()

    print(f"Most Quantified: {most_quantified['name']}")
    print(f"  - {most_quantified['quantification_rate']}% of deliveries have quantified values")
    print(f"  - {most_quantified['quantified_deliveries']}/{most_quantified['deliveries']} deliveries quantified")
    print()

    print(f"Most Normative Analysis: {most_criteria['name']}")
    print(f"  - {most_criteria.get('criteria_count', 0)} normative criteria defined")
    print("  - Demonstrates criteria evaluation framework")
    print()

    # Methodological coverage
    print("Methodological Feature Coverage:")
    temporal_count = sum(1 for r in results if r.get("has_temporal", False))
    criteria_count = sum(1 for r in results if r.get("criteria_count", 0) > 0)
    multi_delivery_count = sum(1 for r in results if r.get("multi_delivery_cells", 0) > 0)

    print(f"  - Temporal modeling: {temporal_count}/{len(results)} case studies")
    print(f"  - Normative criteria: {criteria_count}/{len(results)} case studies")
    print(f"  - Multiple deliveries per cell: {multi_delivery_count}/{len(results)} case studies")
    print()

    # Average metrics
    avg_components = sum(r["components"] for r in results) / len(results)
    avg_deliveries = sum(r["deliveries"] for r in results) / len(results)
    avg_quant_rate = sum(r["quantification_rate"] for r in results) / len(results)

    print("Average Metrics Across All Cases:")
    print(f"  - Components: {avg_components:.1f}")
    print(f"  - Deliveries: {avg_deliveries:.1f}")
    print(f"  - Quantification rate: {avg_quant_rate:.1f}%")
    print()


def main():
    """
    Run comparison across all Hayden case studies.
    """
    print("=" * 120)
    print("HAYDEN CASE STUDIES CROSS-CASE COMPARISON")
    print("=" * 120)
    print()
    print("Running SFM analysis battery on all four case studies...")
    print("This may take a minute...")

    # Define case studies
    case_studies = [
        ("Clean Air Act 1970", create_clean_air_act_matrix),
        ("Corporate Director Networks", create_director_network_matrix),
        ("Low-Level Radioactive Waste", create_llrw_matrix),
        ("Nebraska K-12 Finance", build_nebraska_k12_matrix),
    ]

    # Analyze each case
    results = []
    for name, builder in case_studies:
        try:
            metrics = analyze_case_study(name, builder)
            results.append(metrics)
        except Exception as e:
            print(f"  ERROR analyzing {name}: {e}")
            import traceback
            traceback.print_exc()

    # Print comparison table
    if results:
        print_comparison_table(results)
        print_summary_insights(results)
    else:
        print("No results to compare - all case studies failed analysis")

    print("=" * 120)
    print("Comparison complete. See individual case study files for detailed analysis.")
    print("=" * 120)


if __name__ == "__main__":
    main()
