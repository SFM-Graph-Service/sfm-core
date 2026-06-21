"""
Doughnut Economics evaluation for Social Fabric Matrix (SFM).

Evaluates SFM deliveries against Raworth's Doughnut boundaries (21 criteria)
to identify:
- Which delivery chains drive boundaries into overshoot/shortfall
- Net impact direction on each boundary
- Embedded economy holarchy (economy ⊂ society ⊂ biosphere)

References
----------
- Raworth, K. (2017). *Doughnut Economics: Seven Ways to Think Like a
  21st-Century Economist*. Chelsea Green Publishing.
- Hayden, F. G. (2006). *Policymaking for a Good Society*. Springer.
  (SFM delivery chain analysis)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from api.sfm_service import SFMService

from models.matrix_components import SFMCriteria

logger = logging.getLogger(__name__)

__all__ = [
    "DoughnutReport",
    "BoundaryEvaluation",
    "evaluate_doughnut",
    "build_embedded_economy_holarchy",
]


# ---------------------------------------------------------------------------
# Report containers
# ---------------------------------------------------------------------------

@dataclass
class BoundaryEvaluation:
    """
    Evaluation of a single Doughnut boundary criterion.

    Attributes
    ----------
    criterion:
        The SFMCriteria node representing the boundary
    polarity:
        "shortfall" (social foundation) or "overshoot" (ecological ceiling)
    status:
        "met", "overshoot", or "shortfall"
    driving_chains:
        List of delivery chain paths affecting this boundary.
        Each path is a list of node dicts with id, label, type.
    net_impact:
        Net directional impact: "positive", "negative", or "neutral"
    impact_strength:
        Aggregate strength of impact (0.0-1.0)
    """

    criterion: SFMCriteria
    polarity: str
    status: str = "met"
    driving_chains: List[List[Dict[str, Any]]] = field(default_factory=list)
    net_impact: str = "neutral"
    impact_strength: float = 0.0


@dataclass
class DoughnutReport:
    """
    Comprehensive Doughnut Economics evaluation report.

    Attributes
    ----------
    social_foundation:
        Evaluations for 12 social foundation boundaries
    ecological_ceiling:
        Evaluations for 9 planetary boundaries
    overshoot_count:
        Number of boundaries in overshoot
    shortfall_count:
        Number of boundaries in shortfall
    met_count:
        Number of boundaries met
    embedded_economy_holarchy:
        3-level holarchy: economy ⊂ society ⊂ biosphere
        Format: {level_name: [node_info_dicts]}
    total_boundaries:
        Total number of boundaries evaluated (should be 21)
    """

    social_foundation: List[BoundaryEvaluation] = field(default_factory=list)
    ecological_ceiling: List[BoundaryEvaluation] = field(default_factory=list)
    overshoot_count: int = 0
    shortfall_count: int = 0
    met_count: int = 0
    embedded_economy_holarchy: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    total_boundaries: int = 21

    def get_boundary_by_label(self, label: str) -> Optional[BoundaryEvaluation]:
        """Get boundary evaluation by criterion label."""
        for boundary in self.social_foundation + self.ecological_ceiling:
            if boundary.criterion.label == label:
                return boundary
        return None

    def get_overshoot_boundaries(self) -> List[BoundaryEvaluation]:
        """Get all boundaries in overshoot status."""
        return [
            b for b in self.social_foundation + self.ecological_ceiling
            if b.status == "overshoot"
        ]

    def get_shortfall_boundaries(self) -> List[BoundaryEvaluation]:
        """Get all boundaries in shortfall status."""
        return [
            b for b in self.social_foundation + self.ecological_ceiling
            if b.status == "shortfall"
        ]


# ---------------------------------------------------------------------------
# Evaluation functions
# ---------------------------------------------------------------------------

def evaluate_doughnut(service: SFMService) -> DoughnutReport:
    """
    Evaluate deliveries against Doughnut boundaries.

    For each of the 21 Doughnut criteria:
    1. Find delivery chains that affect the boundary using reachability analysis
    2. Determine net impact direction (positive/negative/neutral)
    3. Flag boundaries under undermining pressure (overshoot/shortfall)

    Parameters
    ----------
    service:
        SFMService instance with nodes and relationships

    Returns
    -------
    DoughnutReport:
        Comprehensive evaluation of all boundaries
    """
    report = DoughnutReport()

    # Get all Doughnut criteria nodes that exist in the graph
    all_nodes = service.list_nodes()
    criteria_in_graph = [
        node for node in all_nodes
        if isinstance(node, SFMCriteria) and node.meta.get("doughnut_dimension") in ["social_foundation", "ecological_ceiling"]
    ]

    logger.info(f"Found {len(criteria_in_graph)} Doughnut criteria in graph")

    # Evaluate each criterion
    for criterion in criteria_in_graph:
        evaluation = _evaluate_boundary(service, criterion)

        if criterion.meta.get("polarity") == "shortfall":
            report.social_foundation.append(evaluation)
        else:
            report.ecological_ceiling.append(evaluation)

        # Update counts
        if evaluation.status == "overshoot":
            report.overshoot_count += 1
        elif evaluation.status == "shortfall":
            report.shortfall_count += 1
        else:
            report.met_count += 1

    # Build embedded economy holarchy
    report.embedded_economy_holarchy = build_embedded_economy_holarchy(service)

    return report


def _evaluate_boundary(service: SFMService, criterion: SFMCriteria) -> BoundaryEvaluation:
    """
    Evaluate a single boundary criterion.

    Uses reachability and circular causation analysis to identify
    delivery chains affecting the boundary.
    """
    evaluation = BoundaryEvaluation(
        criterion=criterion,
        polarity=criterion.meta.get("polarity", "unknown"),
    )

    # Find incoming relationships to this criterion
    # These represent deliveries being evaluated against the boundary
    all_relationships = service.list_relationships()
    incoming = [
        rel for rel in all_relationships
        if rel.target_id == criterion.id and rel.kind == "evaluates_to"
    ]

    logger.debug(f"Boundary '{criterion.label}': found {len(incoming)} incoming evaluations")

    # Analyze each delivery chain
    for rel in incoming:
        try:
            # Get source node (the delivery or component being evaluated)
            source_node = service.get_node(rel.source_id)
            if not source_node:
                continue

            # Build delivery chain - trace backwards from source
            # For now, just record the immediate delivery chain
            chain_nodes = []
            chain_nodes.append({
                "id": str(source_node.id),
                "label": source_node.label,
                "type": type(source_node).__name__,
            })

            # Try to get upstream nodes (producers of this delivery)
            all_rels = service.list_relationships()
            upstream = [r for r in all_rels if r.target_id == source_node.id]
            for up_rel in upstream[:2]:  # Limit to first 2 to keep manageable
                up_node = service.get_node(up_rel.source_id)
                if up_node:
                    chain_nodes.insert(0, {
                        "id": str(up_node.id),
                        "label": up_node.label,
                        "type": type(up_node).__name__,
                    })

            if chain_nodes:
                evaluation.driving_chains.append(chain_nodes)

            # Update impact based on relationship weight
            if rel.weight is not None:
                if rel.weight < 0:
                    evaluation.net_impact = "negative"
                    evaluation.impact_strength = max(evaluation.impact_strength, abs(rel.weight))
                elif rel.weight > 0:
                    evaluation.net_impact = "positive"
                    evaluation.impact_strength = max(evaluation.impact_strength, rel.weight)

        except Exception as e:
            logger.warning(f"Error analyzing chain for {criterion.label}: {e}")
            continue

    # Determine boundary status based on impact
    if evaluation.polarity == "shortfall":
        # Social foundation - negative impact = shortfall
        if evaluation.net_impact == "negative" and evaluation.impact_strength > 0.5:
            evaluation.status = "shortfall"
        elif len(incoming) > 0:
            evaluation.status = "met"

    elif evaluation.polarity == "overshoot":
        # Ecological ceiling - negative impact = overshoot
        if evaluation.net_impact == "negative" and evaluation.impact_strength > 0.5:
            evaluation.status = "overshoot"
        elif len(incoming) > 0:
            evaluation.status = "met"

    return evaluation


def build_embedded_economy_holarchy(service: SFMService) -> Dict[str, List[Dict[str, Any]]]:
    """
    Build embedded economy holarchy: economy ⊂ society ⊂ biosphere.

    Creates three nested institutional levels per Raworth's framework:
    - biosphere: planetary systems and ecological boundaries
    - society: social foundations and community systems
    - economy: economic activities and provisioning systems

    Parameters
    ----------
    service:
        SFMService instance

    Returns
    -------
    Dict[str, List[Dict[str, Any]]]:
        Holarchy with exactly 3 levels: {level_name: [node_info_dicts]}
    """
    holarchy: Dict[str, List[Dict[str, Any]]] = {
        "biosphere": [],
        "society": [],
        "economy": [],
    }

    all_nodes = service.list_nodes()

    for node in all_nodes:
        node_dict = {
            "id": str(node.id),
            "label": node.label,
            "type": type(node).__name__,
        }

        # Classify into holarchy levels based on node type and metadata
        if isinstance(node, SFMCriteria):
            # Check Doughnut dimension first
            if node.meta.get("doughnut_dimension") == "ecological_ceiling":
                holarchy["biosphere"].append(node_dict)
            elif node.meta.get("doughnut_dimension") == "social_foundation":
                holarchy["society"].append(node_dict)
            # If no doughnut dimension, use criteria_type
            elif hasattr(node, "criteria_type"):
                from models.enums import CriteriaType
                if node.criteria_type == CriteriaType.ENVIRONMENTAL:
                    holarchy["biosphere"].append(node_dict)
                elif node.criteria_type in [CriteriaType.SOCIAL, CriteriaType.POLITICAL]:
                    holarchy["society"].append(node_dict)
                elif node.criteria_type == CriteriaType.ECONOMIC:
                    holarchy["economy"].append(node_dict)

        elif hasattr(node, "criteria_type"):
            from models.enums import CriteriaType
            if node.criteria_type == CriteriaType.ENVIRONMENTAL:
                holarchy["biosphere"].append(node_dict)
            elif node.criteria_type in [CriteriaType.SOCIAL, CriteriaType.POLITICAL]:
                holarchy["society"].append(node_dict)
            elif node.criteria_type == CriteriaType.ECONOMIC:
                holarchy["economy"].append(node_dict)

        # Default: look at node metadata or label for hints
        elif "meta" in dir(node) and isinstance(node.meta, dict):
            if node.meta.get("holarchy_level"):
                level = node.meta["holarchy_level"]
                if level in holarchy:
                    holarchy[level].append(node_dict)

    logger.info(
        f"Built embedded economy holarchy: "
        f"biosphere={len(holarchy['biosphere'])}, "
        f"society={len(holarchy['society'])}, "
        f"economy={len(holarchy['economy'])}"
    )

    return holarchy
