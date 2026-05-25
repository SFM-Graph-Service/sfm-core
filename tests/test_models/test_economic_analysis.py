"""
Unit tests for economic_analysis module.
"""

import pytest
import uuid
from models.economic_analysis import (
    TransactionCost,
    CoordinationMechanism,
    CommonsGovernance,
)
from models.sfm_enums import CoordinationMechanismType, CommonsGovernanceType


class TestTransactionCost:
    def test_instantiation(self):
        tc = TransactionCost(label="Test Cost")
        assert tc.label == "Test Cost"

    def test_with_type(self):
        tc = TransactionCost(label="Search", cost_type="search_information")
        assert tc.cost_type == "search_information"

    def test_with_amount(self):
        tc = TransactionCost(label="High Cost", cost_amount=100.5)
        assert tc.cost_amount == 100.5

    def test_with_time(self):
        tc = TransactionCost(label="Time", time_cost=8.5)
        assert tc.time_cost == 8.5

    def test_complete(self):
        tc = TransactionCost(
            label="Complete", cost_type="enforcement", cost_amount=50.0, time_cost=12.0
        )
        assert tc.label == "Complete"


class TestCoordinationMechanism:
    def test_instantiation(self):
        cm = CoordinationMechanism(label="Test Mechanism")
        assert cm.label == "Test Mechanism"

    def test_with_type(self):
        cm = CoordinationMechanism(
            label="Price", mechanism_type=CoordinationMechanismType.PRICE_SYSTEM
        )
        assert cm.mechanism_type == CoordinationMechanismType.PRICE_SYSTEM

    def test_with_effectiveness(self):
        cm = CoordinationMechanism(label="Effective", effectiveness_measure=0.85)
        assert cm.effectiveness_measure == 0.85

    def test_complete(self):
        cm = CoordinationMechanism(
            label="Complete",
            mechanism_type=CoordinationMechanismType.HIERARCHY,
            effectiveness_measure=0.75,
        )
        assert cm.label == "Complete"


class TestCommonsGovernance:
    def test_instantiation(self):
        resource_id = uuid.uuid4()
        cg = CommonsGovernance(label="Test Commons", resource_id=resource_id)
        assert cg.label == "Test Commons"
        assert cg.resource_id == resource_id

    def test_with_type(self):
        resource_id = uuid.uuid4()
        cg = CommonsGovernance(
            label="Resource",
            resource_id=resource_id,
            governance_type=CommonsGovernanceType.COMMUNITY_MANAGED,
        )
        assert cg.governance_type == CommonsGovernanceType.COMMUNITY_MANAGED

    def test_with_effectiveness(self):
        resource_id = uuid.uuid4()
        cg = CommonsGovernance(
            label="Effective", resource_id=resource_id, governance_effectiveness=0.8
        )
        assert cg.governance_effectiveness == 0.8

    def test_complete(self):
        resource_id = uuid.uuid4()
        cg = CommonsGovernance(
            label="Complete",
            resource_id=resource_id,
            governance_type=CommonsGovernanceType.HYBRID_GOVERNANCE,
            governance_effectiveness=0.7,
        )
        assert cg.label == "Complete"
