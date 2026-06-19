"""Tests for framework bridge helpers."""

import uuid

from api.sfm_service import SFMService
from models.frameworks.bridges import boundary_state_to_delivery, build_ses_iad_example


def test_boundary_state_to_delivery_shortfall_polarity():
    below = boundary_state_to_delivery(0.3, threshold=0.5, polarity="shortfall")
    at = boundary_state_to_delivery(0.5, threshold=0.5, polarity="shortfall")
    above = boundary_state_to_delivery(0.8, threshold=0.5, polarity="shortfall")

    assert below.state == "undermines"
    assert at.state == "neutral"
    assert above.state == "serves"


def test_boundary_state_to_delivery_overshoot_polarity():
    below = boundary_state_to_delivery(0.3, threshold=0.5, polarity="overshoot")
    at = boundary_state_to_delivery(0.5, threshold=0.5, polarity="overshoot")
    above = boundary_state_to_delivery(0.8, threshold=0.5, polarity="overshoot")

    assert below.state == "serves"
    assert at.state == "neutral"
    assert above.state == "undermines"


def test_ses_iad_example_builds_without_error():
    service = SFMService()
    ids = build_ses_iad_example(service)
    assert service.get_node(uuid.UUID(ids["rules_in_use"])) is not None
    assert service.get_node(uuid.UUID(ids["action_arena"])) is not None
    assert service.get_node(uuid.UUID(ids["actors"])) is not None
