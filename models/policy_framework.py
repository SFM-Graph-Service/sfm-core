"""
Policy framework components for the Social Fabric Matrix.

This module contains classes for policy instruments, value judgments,
and problem-solving sequences that guide policy development and analysis.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import (
    PolicyInstrumentType,
    ValueJudgmentType,
    ValueCategory,
    ProblemSolvingStage,
    EnumValidator,
)


@dataclass
class PolicyInstrument(Node):
    """Specific tools used to implement policies."""

    # regulatory, economic, voluntary, information
    instrument_type: PolicyInstrumentType = PolicyInstrumentType.REGULATORY
    target_behavior: Optional[str] = None
    compliance_mechanism: Optional[str] = None
    effectiveness_measure: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate policy instrument configuration after initialization."""
        # Validate instrument type if target behavior is specified
        if self.target_behavior:
            EnumValidator.validate_policy_instrument_combination(
                self.instrument_type, self.target_behavior
            )


@dataclass
class ValueJudgment(Node):
    """Explicit value judgments in SFM policy analysis."""

    judgment_type: ValueJudgmentType = ValueJudgmentType.EFFICIENCY
    value_categories_affected: List[ValueCategory] = field(default_factory=lambda: [])
    trade_offs: Dict[str, float] = field(default_factory=lambda: {})  # What's traded for what
    stakeholder_impacts: Dict[str, float] = field(default_factory=lambda: {})  # Impact on different groups
    ethical_framework: Optional[str] = None  # Underlying ethical approach
    justification: Optional[str] = None  # Rationale for the judgment
    controversy_level: Optional[float] = None  # How contested this judgment is (0-1)
    alternative_judgments: List[str] = field(default_factory=lambda: [])  # Other possible judgments
    evidence_basis: List[str] = field(default_factory=lambda: [])
    decision_context: Optional[str] = None


@dataclass
class ProblemSolvingSequence(Node):
    """Represents Hayden's structured problem-solving approach."""

    problem_definition: str = ""  # Added default to fix dataclass ordering
    current_stage: ProblemSolvingStage = ProblemSolvingStage.IDENTIFICATION
    status_quo_analysis: Optional[str] = None
    alternative_solutions: List[uuid.UUID] = field(default_factory=lambda: [])
    evaluation_criteria: List[uuid.UUID] = field(default_factory=lambda: [])  # Links to SFMCriteria
    stakeholder_analysis: Dict[str, Any] = field(default_factory=lambda: {})
    implementation_barriers: List[str] = field(default_factory=lambda: [])
    selected_solution: Optional[uuid.UUID] = None
    implementation_plan: Optional[str] = None
    evaluation_results: Dict[str, Any] = field(default_factory=lambda: {})
    problem_urgency: Optional[float] = None  # How urgent is the problem (0-1)
    resource_requirements: Dict[str, float] = field(default_factory=lambda: {})  # Required resources
    timeline: Optional[str] = None  # Expected timeline for solution

    def __post_init__(self) -> None:
        """Validate that problem definition is provided."""
        if not self.problem_definition.strip():
            raise ValueError("problem_definition is required for ProblemSolvingSequence")
