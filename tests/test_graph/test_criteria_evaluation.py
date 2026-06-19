"""Tests for delivery-vs-criteria evaluation."""

from api.sfm_service import SFMService
from graph.criteria_evaluation import evaluate_against_criteria
from graph.sfm_graph import Relationship
from models import Node
from models.matrix_components import SFMCriteria


def test_evaluate_against_criteria_classifies_serve_and_undermine_links():
    service = SFMService()

    producer = service.create_node(Node(label="Producer", description="supplies public goods"))
    polluter = service.create_node(Node(label="Polluter", description="creates environmental pressure"))
    criterion = service.create_node(
        SFMCriteria(label="Health criterion", description="health outcomes", meta={"is_criterion": "true"})
    )

    service.create_relationship(
        Relationship(source_id=producer.id, target_id=criterion.id, kind="supports", weight=0.8)
    )
    service.create_relationship(
        Relationship(source_id=polluter.id, target_id=criterion.id, kind="undermines", weight=-0.7)
    )

    results = evaluate_against_criteria(service)
    result = results[str(criterion.id)]

    assert len(result.served_by) == 1
    assert len(result.undermined_by) == 1
    assert result.net_score == 0
