"""Doughnut analysis built on top of SFM service queries."""

from __future__ import annotations

from dataclasses import dataclass, field
import uuid
from typing import Any, Dict, List

from graph.criteria_evaluation import evaluate_against_criteria
from graph.sfm_graph import Relationship
from models import Node
from models.frameworks.doughnut import build_doughnut_criteria


@dataclass
class DoughnutBoundaryResult:
    boundary_id: str
    boundary_label: str
    polarity: str
    net_score: int
    flagged: bool
    driving_chains: List[List[str]] = field(default_factory=list)


@dataclass
class DoughnutReport:
    boundaries: List[DoughnutBoundaryResult] = field(default_factory=list)
    flagged_boundaries: List[str] = field(default_factory=list)


def build_embedded_economy_holarchy(service: Any) -> str:
    """Build economy ⊂ society ⊂ biosphere and return biosphere node id."""
    biosphere = Node(label="Biosphere", description="Ecological context", meta={"framework": "doughnut"})
    society = Node(label="Society", description="Social system", meta={"framework": "doughnut"})
    economy = Node(label="Economy", description="Embedded economy", meta={"framework": "doughnut"})

    service.create_node(biosphere)
    service.create_node(society)
    service.create_node(economy)

    service.create_relationship(Relationship(source_id=biosphere.id, target_id=society.id, kind="contains"))
    service.create_relationship(Relationship(source_id=society.id, target_id=economy.id, kind="contains"))
    return str(biosphere.id)


def _ensure_doughnut_criteria(service: Any) -> None:
    existing = {
        node.meta.get("boundary_name")
        for node in service.list_nodes()
        if node.meta.get("framework") == "doughnut"
    }
    for criterion in build_doughnut_criteria():
        if criterion.meta.get("boundary_name") in existing:
            continue
        service.create_node(criterion)


def evaluate_doughnut(service: Any) -> DoughnutReport:
    """Evaluate Doughnut boundaries and identify net-undermined boundaries."""
    _ensure_doughnut_criteria(service)
    if service.query_engine is None:
        service.initialize_query_engine()

    criteria_results = evaluate_against_criteria(service)
    criteria_by_id: Dict[str, Any] = {str(node.id): node for node in service.list_nodes() if node.meta.get("framework") == "doughnut"}

    report = DoughnutReport()
    for criterion_id, result in criteria_results.items():
        criterion = criteria_by_id.get(criterion_id)
        if criterion is None:
            continue

        chains: List[List[str]] = []
        for entry in result.served_by + result.undermined_by:
            source_id = entry["source_id"]
            source_node = service.get_node(uuid.UUID(source_id))
            if source_node is None:
                continue
            paths = service.get_circular_causation(source_node.id)
            if not paths:
                chains.append([source_node.label, criterion.label])
                continue
            for path in paths:
                labels = [node.get("label", "") for node in path.get("nodes", [])]
                if labels:
                    chains.append(labels)

        boundary = DoughnutBoundaryResult(
            boundary_id=criterion_id,
            boundary_label=criterion.label,
            polarity=criterion.meta.get("polarity", "unknown"),
            net_score=result.net_score,
            flagged=result.net_score < 0,
            driving_chains=chains,
        )
        report.boundaries.append(boundary)
        if boundary.flagged:
            report.flagged_boundaries.append(boundary.boundary_label)

    return report
