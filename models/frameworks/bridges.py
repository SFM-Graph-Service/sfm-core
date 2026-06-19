"""Framework bridge helpers for SFM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from graph.sfm_graph import Relationship
from models import Node


@dataclass
class BoundaryDeliveryState:
    """Normalized delivery signal derived from a continuous boundary indicator."""

    state: str
    weight: float


def boundary_state_to_delivery(
    indicator_value: float,
    threshold: float,
    polarity: str,
) -> BoundaryDeliveryState:
    """Convert a continuous boundary reading into an SFM delivery state."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")

    normalized_gap = min(abs(indicator_value - threshold) / threshold, 1.0)
    if indicator_value == threshold:
        return BoundaryDeliveryState(state="neutral", weight=0.0)

    polarity_norm = polarity.strip().lower()
    if polarity_norm not in {"shortfall", "overshoot"}:
        raise ValueError("polarity must be 'shortfall' or 'overshoot'")

    if polarity_norm == "shortfall":
        if indicator_value < threshold:
            return BoundaryDeliveryState(state="undermines", weight=normalized_gap)
        return BoundaryDeliveryState(state="serves", weight=normalized_gap)

    if indicator_value > threshold:
        return BoundaryDeliveryState(state="undermines", weight=normalized_gap)
    return BoundaryDeliveryState(state="serves", weight=normalized_gap)


def build_ses_iad_example(service: Any) -> Dict[str, str]:
    """Build a minimal SES/IAD mapping fragment in the provided service."""
    rules_in_use = Node(
        label="Rules-in-use",
        description="SES/IAD rules structuring action situations",
        meta={"framework": "ostrom_ses_iad", "role": "rules_in_use"},
    )
    action_arena = Node(
        label="Action Arena",
        description="SES/IAD action arena represented as an institutional node cluster",
        meta={"framework": "ostrom_ses_iad", "role": "action_arena"},
    )
    actor_cluster = Node(
        label="Actors Cluster",
        description="Participants interacting in the action arena",
        meta={"framework": "ostrom_ses_iad", "role": "actors"},
    )

    service.create_node(rules_in_use)
    service.create_node(action_arena)
    service.create_node(actor_cluster)

    service.create_relationship(
        Relationship(source_id=rules_in_use.id, target_id=action_arena.id, kind="governs")
    )
    service.create_relationship(
        Relationship(source_id=actor_cluster.id, target_id=action_arena.id, kind="participates_in")
    )

    return {
        "rules_in_use": str(rules_in_use.id),
        "action_arena": str(action_arena.id),
        "actors": str(actor_cluster.id),
    }
