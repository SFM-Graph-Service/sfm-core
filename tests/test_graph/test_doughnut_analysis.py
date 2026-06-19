"""Tests for Doughnut evaluation helpers."""

import uuid

from api.sfm_service import SFMService
from graph.doughnut_analysis import build_embedded_economy_holarchy, evaluate_doughnut
from graph.sfm_graph import Relationship
from models import Node
from models.frameworks.doughnut import build_doughnut_criteria


def test_evaluate_doughnut_flags_net_undermined_boundary_and_returns_driver_chain():
    service = SFMService()

    source = service.create_node(Node(label="Heavy Industry", description="high emissions actor"))
    criteria = {c.meta["boundary_name"]: c for c in build_doughnut_criteria()}
    air = service.create_node(criteria["air pollution"])
    health = service.create_node(criteria["health"])

    service.create_relationship(
        Relationship(source_id=source.id, target_id=air.id, kind="undermines", weight=-1.0)
    )
    service.create_relationship(
        Relationship(source_id=source.id, target_id=health.id, kind="supports", weight=0.6)
    )
    service.create_relationship(
        Relationship(source_id=source.id, target_id=source.id, kind="reinforces", weight=0.1)
    )

    report = evaluate_doughnut(service)

    by_name = {b.boundary_label: b for b in report.boundaries}
    air_boundary = next(v for k, v in by_name.items() if "air pollution" in k.lower())
    assert air_boundary.flagged
    assert air_boundary.driving_chains


def test_embedded_economy_builder_yields_three_nested_levels():
    service = SFMService()
    root_id = uuid.UUID(build_embedded_economy_holarchy(service))
    service.initialize_query_engine()
    holarchy = service.get_holarchy(root_id)
    assert holarchy["depth"] == 3
