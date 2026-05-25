"""
Specialized SFM nodes for advanced analysis and system properties.

This module provides unified access to all specialized node types that support
advanced SFM analysis. The actual class definitions have been organized into
focused modules for better maintainability.
"""

from __future__ import annotations

# Import all specialized classes from focused modules
from models.matrix_components import MatrixCell, SFMCriteria, SFMMatrix
from models.system_analysis import SystemProperty, SystemLevelAnalysis, InstitutionalHolarchy
from models.policy_framework import PolicyInstrument, ValueJudgment, ProblemSolvingSequence
from models.institutional_analysis import InstitutionalStructure, PathDependencyAnalysis
from models.economic_analysis import TransactionCost, CoordinationMechanism, CommonsGovernance
from models.cultural_analysis import (
    CeremonialInstrumentalClassification,
    ValueSystem,
    SocialBelief,
    CulturalAttitude,
)
from models.social_assessment import SocialValueAssessment, SocialFabricIndicator, SocialCost
from models.technology_integration import ToolSkillTechnologyComplex, EcologicalSystem
from models.network_analysis import CrossImpactAnalysis, DeliveryRelationship, MatrixDeliveryNetwork
from models.complex_analysis import DigraphAnalysis, CircularCausationProcess, ConflictDetection
from models.methodological_framework import (
    InstrumentalistInquiryFramework,
    NormativeSystemsAnalysis,
    PolicyRelevanceIntegration,
    DatabaseIntegrationCapability,
)
from models.specialized_components import (
    SocialIndicatorSystem,
    EvolutionaryPathway,
    SocialProvisioningMatrix,
)
from models.meta_entities import (
    TimeSlice,
    SpatialUnit,
    Scenario,
    ScenarioSet,
    ScenarioPath,
    ScenarioType,
    UncertaintyType,
)


# All specialized node classes have been moved to focused modules:
# - Matrix components: matrix_components.py
# - System analysis: system_analysis.py
# - Policy framework: policy_framework.py
# - Institutional analysis: institutional_analysis.py
# - Economic analysis: economic_analysis.py
# - Cultural analysis: cultural_analysis.py
# - Social assessment: social_assessment.py
# - Technology integration: technology_integration.py
# - Network analysis: network_analysis.py
# - Complex analysis: complex_analysis.py
# - Methodological framework: methodological_framework.py
# - Additional specialized components: specialized_components.py

# This module now serves as a unified import interface
# for backward compatibility and convenience.

__all__ = [
    # Matrix components
    'MatrixCell',
    'SFMCriteria', 
    'SFMMatrix',
    # System analysis
    'SystemProperty',
    'SystemLevelAnalysis',
    'InstitutionalHolarchy',
    # Policy framework
    'PolicyInstrument',
    'ValueJudgment',
    'ProblemSolvingSequence',
    # Institutional analysis
    'InstitutionalStructure',
    'PathDependencyAnalysis',
    # Economic analysis
    'TransactionCost',
    'CoordinationMechanism',
    'CommonsGovernance',
    # Cultural analysis
    'CeremonialInstrumentalClassification',
    'ValueSystem',
    'SocialBelief',
    'CulturalAttitude',
    # Social assessment
    'SocialValueAssessment',
    'SocialFabricIndicator',
    'SocialCost',
    # Technology integration
    'ToolSkillTechnologyComplex',
    'EcologicalSystem',
    # Network analysis
    'CrossImpactAnalysis',
    'DeliveryRelationship',
    'MatrixDeliveryNetwork',
    # Complex analysis
    'DigraphAnalysis',
    'CircularCausationProcess',
    'ConflictDetection',
    # Methodological framework
    'InstrumentalistInquiryFramework',
    'NormativeSystemsAnalysis',
    'PolicyRelevanceIntegration',
    'DatabaseIntegrationCapability',
    # Specialized components
    'SocialIndicatorSystem',
    'EvolutionaryPathway',
    'SocialProvisioningMatrix',
    # Meta entities
    'TimeSlice',
    'SpatialUnit',
    'Scenario',
    'ScenarioSet',
    'ScenarioPath',
    'ScenarioType',
    'UncertaintyType',
]
