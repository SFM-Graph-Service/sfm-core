"""
SFM Analysis Battery — reusable analytical pass over any SFMService graph.

Runs the core Hayden/Veblen analytical methods in one shot and returns a
typed :class:`AnalysisReport` that every case-study can call identically.
Optionally formats the report as a human-readable text summary.

References
----------
- Hayden, F. G. (2006). *Policymaking for a Good Society*. Springer.
- Veblen, T. (1899). *The Theory of the Leisure Class*.  (ceremonial/instrumental)
- Myrdal, G. (1944). *An American Dilemma*.  (circular cumulative causation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

__all__ = [
    "AnalysisReport",
    "run_analysis_battery",
    "format_report",
]


# ---------------------------------------------------------------------------
# Report container
# ---------------------------------------------------------------------------

@dataclass
class AnalysisReport:
    """Structured result from :func:`run_analysis_battery`.

    Attributes
    ----------
    ceremonial_nodes:
        Nodes classified as ceremonially-oriented (status-quo preserving).
    instrumental_nodes:
        Nodes classified as instrumentally-oriented (problem-solving).
    ceremonial_ratio:
        Ratio of ceremonial nodes to total classified nodes (0–1).
    circular_causation_paths:
        Circular-causation feedback chains, each a list of node-info dicts.
    holarchy_levels:
        Mapping ``{node_label: {level_name: [node_dicts]}}`` for every node
        for which a holarchy was computed.
    feedback_cycles:
        Raw cycles from ``find_cycles``; each element is a list of UUIDs.
    conflicts:
        List of conflict descriptors detected by ``detect_conflicts``.
    temporal_snapshots:
        Optional temporal-evolution snapshots when a TemporalClock is present.
    node_count:
        Total graph node count at time of analysis.
    """

    ceremonial_nodes: List[Dict[str, Any]] = field(default_factory=list)
    instrumental_nodes: List[Dict[str, Any]] = field(default_factory=list)
    ceremonial_ratio: float = 0.0
    circular_causation_paths: List[List[Dict[str, Any]]] = field(default_factory=list)
    holarchy_levels: Dict[str, Dict[str, List[Dict[str, Any]]]] = field(
        default_factory=dict
    )
    feedback_cycles: List[List[uuid.UUID]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    temporal_snapshots: Optional[List[Dict[str, Any]]] = None
    node_count: int = 0


# ---------------------------------------------------------------------------
# Battery runner
# ---------------------------------------------------------------------------

def run_analysis_battery(service: Any) -> AnalysisReport:
    """Run the full SFM analysis battery on *service* and return an
    :class:`AnalysisReport`.

    The battery covers:

    1. Ceremonial vs instrumental classification (Veblen–Hayden dichotomy).
    2. Circular causation paths from every node (Myrdal's cumulative causation).
    3. Institutional holarchy levels for every node (Koestler's holarchy).
    4. Feedback cycles via ``find_cycles``.
    5. Conflict detection via ``detect_conflicts``.
    6. Temporal evolution snapshots when a :class:`TemporalClock` is present.

    The function is designed to be safe: any individual analysis that fails or
    returns nothing is handled gracefully — the rest of the battery still runs.

    Parameters
    ----------
    service:
        An initialised :class:`~api.sfm_service.SFMService` instance that
        already has nodes/relationships added.

    Returns
    -------
    AnalysisReport
        Populated report; never raises on degenerate/empty graphs.
    """
    report = AnalysisReport()

    # Ensure the query engine is available
    if service.query_engine is None:
        try:
            service.initialize_query_engine()
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not initialize query engine: %s", exc)
            return report

    engine = service.query_engine
    if engine is None:
        return report

    # ------------------------------------------------------------------
    # 1. Ceremonial vs instrumental
    # ------------------------------------------------------------------
    try:
        ci_result = service.get_ceremonial_analysis()
        report.ceremonial_nodes = ci_result.get("ceremonial_nodes", [])
        report.instrumental_nodes = ci_result.get("instrumental_nodes", [])
        report.ceremonial_ratio = ci_result.get("ceremonial_ratio", 0.0)
    except Exception as exc:
        logger.debug("Ceremonial analysis skipped: %s", exc)

    # ------------------------------------------------------------------
    # 2. Circular causation paths (from each node)
    # ------------------------------------------------------------------
    try:
        all_nodes = service.list_nodes()
        report.node_count = len(all_nodes)
        paths: List[List[Dict[str, Any]]] = []
        for node in all_nodes:
            try:
                node_paths = service.get_circular_causation(node.id)
                paths.extend(node_paths)
            except Exception:
                pass
        # Deduplicate by stringifying path node-ids
        seen: set = set()
        unique_paths = []
        for p in paths:
            key = str([n.get("id") for n in p.get("nodes", p)])
            if key not in seen:
                seen.add(key)
                unique_paths.append(p)
        report.circular_causation_paths = unique_paths
    except Exception as exc:
        logger.debug("Circular causation analysis skipped: %s", exc)

    # ------------------------------------------------------------------
    # 3. Holarchy levels (for each node)
    # ------------------------------------------------------------------
    try:
        for node in service.list_nodes():
            try:
                result = service.get_holarchy(node.id)
                levels = result.get("layers", [])
                if levels:
                    report.holarchy_levels[node.label] = {
                        layer["level"]: layer["nodes"] for layer in levels
                    }
            except Exception:
                pass
    except Exception as exc:
        logger.debug("Holarchy analysis skipped: %s", exc)

    # ------------------------------------------------------------------
    # 4. Feedback cycles
    # ------------------------------------------------------------------
    try:
        report.feedback_cycles = engine.find_cycles(max_length=10)
    except Exception as exc:
        logger.debug("Cycle detection skipped: %s", exc)

    # ------------------------------------------------------------------
    # 5. Conflict detection
    # ------------------------------------------------------------------
    try:
        report.conflicts = service.get_conflicts()
    except Exception as exc:
        logger.debug("Conflict detection skipped: %s", exc)

    # ------------------------------------------------------------------
    # 6. Temporal evolution (only when a TemporalClock is present)
    # ------------------------------------------------------------------
    try:
        from models.temporal_clocks import TemporalClock
        from datetime import datetime, timedelta

        clocks = [n for n in service.list_nodes() if isinstance(n, TemporalClock)]
        if clocks and hasattr(engine, "query_temporal_evolution"):
            start = datetime(2000, 1, 1)
            end = datetime(2025, 1, 1)
            report.temporal_snapshots = engine.query_temporal_evolution(
                start, end, timedelta(days=365)
            )
    except Exception as exc:
        logger.debug("Temporal evolution analysis skipped: %s", exc)

    return report


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def format_report(report: AnalysisReport) -> str:
    """Return a human-readable text summary of an :class:`AnalysisReport`.

    Parameters
    ----------
    report:
        The report produced by :func:`run_analysis_battery`.

    Returns
    -------
    str
        Multi-line summary string; never empty (returns a header at minimum).
    """
    lines: List[str] = []
    sep = "─" * 60

    lines.append(sep)
    lines.append("SFM ANALYSIS BATTERY RESULTS")
    lines.append(sep)

    # Nodes
    lines.append(f"\nGraph size: {report.node_count} node(s)")

    # 1. Ceremonial / instrumental
    lines.append("\n[1] Ceremonial vs Instrumental (Veblen–Hayden)")
    total_ci = len(report.ceremonial_nodes) + len(report.instrumental_nodes)
    if total_ci == 0:
        lines.append("    No ceremonially/instrumentally classified nodes found.")
    else:
        lines.append(
            f"    Ceremonial:   {len(report.ceremonial_nodes)} node(s)"
            f"  ({report.ceremonial_ratio * 100:.1f}%)"
        )
        lines.append(
            f"    Instrumental: {len(report.instrumental_nodes)} node(s)"
            f"  ({(1 - report.ceremonial_ratio) * 100:.1f}%)"
        )
        for n in report.ceremonial_nodes[:5]:
            lines.append(f"      ⊘ {n.get('label', n.get('id', '?'))} [ceremonial]")
        for n in report.instrumental_nodes[:5]:
            lines.append(f"      ✓ {n.get('label', n.get('id', '?'))} [instrumental]")

    # 2. Circular causation
    lines.append("\n[2] Circular Causation Paths (Myrdal cumulative causation)")
    if not report.circular_causation_paths:
        lines.append("    No circular causation paths detected.")
    else:
        lines.append(f"    {len(report.circular_causation_paths)} path(s) found.")
        for i, path in enumerate(report.circular_causation_paths[:3]):
            nodes_in_path = path.get("nodes", path) if isinstance(path, dict) else path
            labels = [
                n.get("label", n.get("id", "?")) if isinstance(n, dict) else str(n)
                for n in nodes_in_path[:6]
            ]
            lines.append(f"      Path {i + 1}: {' → '.join(labels)}")

    # 3. Holarchy levels
    lines.append("\n[3] Institutional Holarchy Levels (Koestler)")
    if not report.holarchy_levels:
        lines.append("    No multi-level holarchy structures found.")
    else:
        for root_label, levels in list(report.holarchy_levels.items())[:5]:
            non_empty = {k: v for k, v in levels.items() if v}
            if non_empty:
                level_summary = ", ".join(
                    f"{k}({len(v)})" for k, v in non_empty.items()
                )
                lines.append(f"    {root_label}: {level_summary}")

    # 4. Feedback cycles
    lines.append("\n[4] Feedback Cycles")
    if not report.feedback_cycles:
        lines.append("    No feedback cycles detected.")
    else:
        lines.append(f"    {len(report.feedback_cycles)} cycle(s) found.")
        for i, cycle in enumerate(report.feedback_cycles[:3]):
            lines.append(f"      Cycle {i + 1}: {len(cycle)} node(s)")

    # 5. Conflicts
    lines.append("\n[5] Conflicts / Contradictions")
    if not report.conflicts:
        lines.append("    No conflicts detected.")
    else:
        lines.append(f"    {len(report.conflicts)} conflict(s) detected.")
        for c in report.conflicts[:3]:
            ctype = c.get("conflict_type", c.get("type", "unknown"))
            detail = c.get("details", c.get("description", ""))
            lines.append(f"      [{ctype}] {detail}")

    # 6. Temporal evolution
    lines.append("\n[6] Temporal Evolution")
    if report.temporal_snapshots is None:
        lines.append("    No temporal clock present; skipped.")
    elif not report.temporal_snapshots:
        lines.append("    Temporal clock present but no snapshots generated.")
    else:
        lines.append(f"    {len(report.temporal_snapshots)} snapshot(s) produced.")
        first = report.temporal_snapshots[0]
        last = report.temporal_snapshots[-1]
        lines.append(
            f"    Range: {first.get('date', '?')} → {last.get('date', '?')}"
        )

    lines.append("\n" + sep)
    return "\n".join(lines)
