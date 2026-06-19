"""Doughnut-coupled Clean Air Act case study.

References:
- Raworth, K. (2017). Doughnut Economics.
- Hayden, F. G. (2006). Policymaking for a Good Society.
"""

from __future__ import annotations

from graph.analysis_report import format_report, run_analysis_battery
from graph.doughnut_analysis import DoughnutReport, evaluate_doughnut
from graph.sfm_graph import Relationship
from models.frameworks.doughnut import build_doughnut_criteria

from examples.hayden_case_studies.clean_air_act_1970 import (
    create_clean_air_act_matrix,
    create_clean_air_temporal_clock,
)


def create_clean_air_act_doughnut_case():
    """Build the clean-air matrix and link it to Doughnut boundaries."""
    matrix, service = create_clean_air_act_matrix()
    create_clean_air_temporal_clock(service)

    criteria = build_doughnut_criteria()
    selected = {
        c.meta.get("boundary_name"): c
        for c in criteria
        if c.meta.get("boundary_name") in {"air pollution", "health", "water"}
    }

    for criterion in selected.values():
        service.create_node(criterion)

    nodes_by_label = {n.label: n for n in service.list_nodes()}
    epa = nodes_by_label.get("Environmental Protection Agency (EPA)")
    industrial = nodes_by_label.get("Industrial Facilities (Steel, Chemical, Manufacturing)")
    public = nodes_by_label.get("American Public (210 million in 1970)")

    if industrial and selected.get("air pollution"):
        service.create_relationship(
            Relationship(
                source_id=industrial.id,
                target_id=selected["air pollution"].id,
                kind="undermines",
                weight=-1.0,
                meta={"impact": "undermine"},
            )
        )
    if epa and selected.get("health"):
        service.create_relationship(
            Relationship(
                source_id=epa.id,
                target_id=selected["health"].id,
                kind="supports",
                weight=1.0,
                meta={"impact": "serve"},
            )
        )
    if public and selected.get("water"):
        service.create_relationship(
            Relationship(
                source_id=public.id,
                target_id=selected["water"].id,
                kind="supports",
                weight=0.3,
            )
        )

    report = run_analysis_battery(service)
    doughnut_report: DoughnutReport = evaluate_doughnut(service)
    return matrix, service, report, doughnut_report


def main() -> None:
    _, _, report, doughnut_report = create_clean_air_act_doughnut_case()
    print(format_report(report))
    print("\nFlagged Doughnut boundaries:")
    for boundary in doughnut_report.flagged_boundaries:
        print(f"- {boundary}")


if __name__ == "__main__":
    main()
