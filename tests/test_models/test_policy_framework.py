"""
Unit tests for policy_framework module.
"""

import pytest
from uuid import uuid4
from models.policy_framework import (
    PolicyInstrument,
    ValueJudgment,
    ProblemSolvingSequence,
)
from models.sfm_enums import (
    PolicyInstrumentType,
    ValueJudgmentType,
    ProblemSolvingStage,
)


class TestPolicyInstrument:
    """Test suite for PolicyInstrument class."""

    def test_policy_instrument_instantiation(self):
        """Test basic PolicyInstrument creation."""
        instrument = PolicyInstrument(label="Test Instrument")
        assert instrument.label == "Test Instrument"

    def test_instrument_with_type(self):
        """Test PolicyInstrument with instrument type."""
        instrument = PolicyInstrument(
            label="Regulation",
            instrument_type=PolicyInstrumentType.REGULATORY,
        )
        assert instrument.instrument_type == PolicyInstrumentType.REGULATORY

    def test_instrument_with_mechanism(self):
        """Test PolicyInstrument with target behavior."""
        instrument = PolicyInstrument(
            label="Tax",
            target_behavior="Price signals",
        )
        assert instrument.target_behavior == "Price signals"

    def test_instrument_with_targets(self):
        """Test PolicyInstrument with description."""
        instrument = PolicyInstrument(
            label="Targeted",
            description="Targets specific entities",
        )
        assert instrument.description == "Targets specific entities"

    def test_instrument_with_implementation(self):
        """Test PolicyInstrument with implementation details."""
        instrument = PolicyInstrument(
            label="Implementable",
            description="Legislative approval required",
        )
        assert instrument.description == "Legislative approval required"

    def test_instrument_complete(self):
        """Test PolicyInstrument with all fields."""
        instrument = PolicyInstrument(
            label="Complete Instrument",
            description="Comprehensive policy tool",
            instrument_type=PolicyInstrumentType.ECONOMIC,
            target_behavior="Market incentives",
        )
        assert instrument.label == "Complete Instrument"


class TestValueJudgment:
    """Test suite for ValueJudgment class."""

    def test_value_judgment_instantiation(self):
        """Test basic ValueJudgment creation."""
        judgment = ValueJudgment(label="Test Judgment")
        assert judgment.label == "Test Judgment"

    def test_judgment_with_type(self):
        """Test ValueJudgment with judgment type."""
        judgment = ValueJudgment(
            label="Normative",
            judgment_type=ValueJudgmentType.EQUITY,
        )
        assert judgment.judgment_type == ValueJudgmentType.EQUITY

    def test_judgment_with_criterion(self):
        """Test ValueJudgment with description."""
        judgment = ValueJudgment(
            label="Equity",
            description="Distributive justice",
        )
        assert judgment.description == "Distributive justice"

    def test_judgment_with_rationale(self):
        """Test ValueJudgment with rationale."""
        judgment = ValueJudgment(
            label="Justified",
            description="Ethical considerations",
        )
        assert judgment.description == "Ethical considerations"

    def test_judgment_complete(self):
        """Test ValueJudgment with all fields."""
        judgment = ValueJudgment(
            label="Complete Judgment",
            description="Full value assessment",
            judgment_type=ValueJudgmentType.EFFICIENCY,
        )
        assert judgment.label == "Complete Judgment"


class TestProblemSolvingSequence:
    """Test suite for ProblemSolvingSequence class."""

    def test_sequence_instantiation(self):
        """Test basic ProblemSolvingSequence creation."""
        sequence = ProblemSolvingSequence(
            problem_definition="Test problem", label="Test Sequence"
        )
        assert sequence.label == "Test Sequence"
        assert sequence.problem_definition == "Test problem"

    def test_sequence_with_stages(self):
        """Test ProblemSolvingSequence with current stage."""
        sequence = ProblemSolvingSequence(
            problem_definition="Multi-stage problem",
            label="Multi-stage",
            current_stage=ProblemSolvingStage.STATUS_QUO_ANALYSIS,
        )
        assert sequence.current_stage == ProblemSolvingStage.STATUS_QUO_ANALYSIS

    def test_sequence_with_context(self):
        """Test ProblemSolvingSequence with problem context."""
        sequence = ProblemSolvingSequence(
            problem_definition="Urban planning",
            label="Contextual",
            status_quo_analysis="Current state analysis",
        )
        assert sequence.status_quo_analysis == "Current state analysis"

    def test_sequence_with_outcomes(self):
        """Test ProblemSolvingSequence with expected outcomes."""
        sequence = ProblemSolvingSequence(
            problem_definition="Service delivery",
            label="Outcome-focused",
            description="Improved service delivery",
        )
        assert sequence.description == "Improved service delivery"

    def test_sequence_complete(self):
        """Test ProblemSolvingSequence with all fields."""
        sequence = ProblemSolvingSequence(
            problem_definition="Healthcare access",
            label="Complete Sequence",
            description="End-to-end process",
            current_stage=ProblemSolvingStage.IDENTIFICATION,
            status_quo_analysis="Current healthcare gaps",
        )
        assert sequence.label == "Complete Sequence"
        assert sequence.problem_definition == "Healthcare access"
