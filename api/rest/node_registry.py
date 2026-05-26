"""Node type registry for API validation.

This module provides a centralized registry of all available SFM node types,
enabling validation and documentation of node_type parameters in API endpoints.
"""

from typing import Set, Dict

# Complete registry of all Node subclasses from models/
# Organized by domain module for maintainability
NODE_TYPES: Dict[str, Set[str]] = {
    "base": {
        "Node",  # Base class from models/base_nodes.py
    },
    "complex_analysis": {
        "DigraphAnalysis",
        "CircularCausationProcess",
        "ConflictDetection",
    },
    "cultural_analysis": {
        "CeremonialInstrumentalClassification",
        "ValueSystem",
        "SocialBelief",
        "CulturalAttitude",
    },
    "economic_analysis": {
        "TransactionCost",
        "CoordinationMechanism",
        "CommonsGovernance",
    },
    "institutional_analysis": {
        "InstitutionalStructure",
        "PathDependencyAnalysis",
    },
    "matrix_components": {
        "MatrixCell",
        "SFMCriteria",
        "SFMMatrix",
    },
    "meta_entities": {
        "Scenario",
        "ScenarioSet",
        "ScenarioPath",
    },
    "methodological_framework": {
        "InstrumentalistInquiryFramework",
        "NormativeSystemsAnalysis",
        "PolicyRelevanceIntegration",
        "DatabaseIntegrationCapability",
    },
    "network_analysis": {
        "CrossImpactAnalysis",
        "DeliveryRelationship",
        "MatrixDeliveryNetwork",
    },
    "policy_framework": {
        "PolicyInstrument",
        "ValueJudgment",
        "ProblemSolvingSequence",
    },
    "social_assessment": {
        "SocialValueAssessment",
        "SocialFabricIndicator",
        "SocialCost",
    },
    "specialized_components": {
        "SocialIndicatorSystem",
        "EvolutionaryPathway",
        "SocialProvisioningMatrix",
    },
    "system_analysis": {
        "SystemProperty",
        "SystemLevelAnalysis",
        "InstitutionalHolarchy",
    },
    "technology_integration": {
        "ToolSkillTechnologyComplex",
        "EcologicalSystem",
    },
}


def get_all_node_types() -> Set[str]:
    """
    Get set of all valid node type names.

    Returns:
        Set of all node type class names
    """
    all_types = set()
    for types in NODE_TYPES.values():
        all_types.update(types)
    return all_types


def is_valid_node_type(node_type: str) -> bool:
    """
    Check if a node type is valid.

    Args:
        node_type: Node type name to validate

    Returns:
        True if node_type is in the registry
    """
    return node_type in get_all_node_types()


def get_node_types_by_domain() -> Dict[str, Set[str]]:
    """
    Get node types organized by domain module.

    Returns:
        Dictionary mapping domain module names to sets of node types
    """
    return NODE_TYPES.copy()


# Pre-computed set for fast validation
ALL_NODE_TYPES = get_all_node_types()
