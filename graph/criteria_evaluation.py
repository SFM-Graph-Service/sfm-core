"""Normative criteria evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from models.matrix_components import SFMCriteria

_SERVE_KINDS = {"supports", "serves", "enables", "improves", "reinforces"}
_UND_KINDS = {"undermines", "harms", "blocks", "degrades", "opposes"}


@dataclass
class EvaluationResult:
    criterion_id: str
    criterion_label: str
    served_by: List[Dict[str, Any]] = field(default_factory=list)
    undermined_by: List[Dict[str, Any]] = field(default_factory=list)
    neutral_links: List[Dict[str, Any]] = field(default_factory=list)
    net_score: int = 0


def _delivery_record(service: Any, relationship: Any) -> Dict[str, Any]:
    source = service.get_node(relationship.source_id)
    return {
        "source_id": str(relationship.source_id),
        "source_label": source.label if source else str(relationship.source_id),
        "relationship_id": str(relationship.id),
        "kind": relationship.kind,
        "weight": relationship.weight,
    }


def _classify_link(rel: Any) -> str:
    kind = (rel.kind or "").lower()
    if kind in _SERVE_KINDS:
        return "serve"
    if kind in _UND_KINDS:
        return "undermine"

    impact = str(rel.meta.get("impact", "")).lower() if rel.meta else ""
    if impact in {"serve", "supports", "positive"}:
        return "serve"
    if impact in {"undermine", "negative", "harm"}:
        return "undermine"

    if rel.weight is not None:
        if rel.weight > 0:
            return "serve"
        if rel.weight < 0:
            return "undermine"

    return "neutral"


def evaluate_against_criteria(service: Any) -> Dict[str, EvaluationResult]:
    """Evaluate delivery links that target criterion nodes."""
    criteria = [
        node
        for node in service.list_nodes()
        if isinstance(node, SFMCriteria) or node.meta.get("is_criterion") == "true"
    ]

    results: Dict[str, EvaluationResult] = {}
    relationships = service.list_relationships()

    for criterion in criteria:
        criterion_id = str(criterion.id)
        result = EvaluationResult(
            criterion_id=criterion_id,
            criterion_label=criterion.label,
        )

        for rel in relationships:
            if rel.target_id != criterion.id:
                continue
            record = _delivery_record(service, rel)
            status = _classify_link(rel)
            if status == "serve":
                result.served_by.append(record)
                result.net_score += 1
            elif status == "undermine":
                result.undermined_by.append(record)
                result.net_score -= 1
            else:
                result.neutral_links.append(record)

        results[criterion_id] = result

    return results
