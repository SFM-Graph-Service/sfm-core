"""Cross-case comparison utility for Hayden case studies."""

from __future__ import annotations

from typing import Dict, List

from graph.analysis_report import run_analysis_battery
from examples.hayden_case_studies.clean_air_act_1970 import (
    create_clean_air_act_matrix,
    create_clean_air_temporal_clock,
)
from examples.hayden_case_studies.director_networks import create_director_network_matrix
from examples.hayden_case_studies.nebraska_k12_finance import build_nebraska_k12_matrix
from examples.hayden_case_studies.radioactive_waste import create_llrw_matrix


def _run_case(label: str, builder):
    matrix, service = builder()
    if label == "clean_air_act_1970":
        create_clean_air_temporal_clock(service)
    report = run_analysis_battery(service)
    return {
        "study": label,
        "cycles": len(report.feedback_cycles),
        "ci_ratio": round(report.ceremonial_ratio, 3),
        "levels": len(report.holarchy_levels),
        "conflicts": len(report.conflicts),
        "nodes": report.node_count,
        "deliveries": sum(len(cell.deliveries) for cell in matrix.cells.values()),
    }


def compare_cases() -> List[Dict[str, object]]:
    """Run the analysis battery across all four Hayden case studies."""
    return [
        _run_case("clean_air_act_1970", create_clean_air_act_matrix),
        _run_case("director_networks", create_director_network_matrix),
        _run_case("nebraska_k12_finance", build_nebraska_k12_matrix),
        _run_case("radioactive_waste", create_llrw_matrix),
    ]


def format_comparison_table(rows: List[Dict[str, object]]) -> str:
    """Render comparison rows as a plain-text table."""
    headers = ["study", "cycles", "ci_ratio", "levels", "conflicts", "nodes", "deliveries"]
    lines = [" | ".join(headers), " | ".join(["---"] * len(headers))]
    for row in rows:
        lines.append(" | ".join(str(row[h]) for h in headers))
    return "\n".join(lines)


def main() -> None:
    rows = compare_cases()
    print(format_comparison_table(rows))


if __name__ == "__main__":
    main()
