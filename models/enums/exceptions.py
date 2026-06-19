"""
Exception classes and validation utilities for the Social Fabric Matrix (SFM) framework.

Provides base exception hierarchy and the EnumValidator class for validating
enum combinations and relationships.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Dict, List, Tuple, Type, Union

from models.enums.values import ValueCategory
from models.enums.institutions import (
    InstitutionLayer,
    LegitimacySource,
)
from models.enums.resources import FlowNature, FlowType
from models.enums.relationships import RelationshipKind
from models.enums.policies import PolicyInstrumentType
from models.enums.technology import TechnologyReadinessLevel

__all__ = [
    "SFMEnumError",
    "IncompatibleEnumError",
    "InvalidEnumOperationError",
    "EnumValidator",
    "validate_enum_operation",
]

class SFMEnumError(Exception):
    """Base exception for SFM enum-related errors."""


class IncompatibleEnumError(SFMEnumError):
    """Raised when incompatible enum values are used together."""


class InvalidEnumOperationError(SFMEnumError):
    """Raised when an invalid operation is attempted on enum values."""


class EnumValidator:
    """Validates enum values and combinations for SFM consistency."""

    # Define node type mappings - these correspond to the actual model classes
    ACTOR_TYPES = {"Actor"}
    INSTITUTION_TYPES = {"Institution", "Policy"}
    RESOURCE_TYPES = {"Resource"}
    PROCESS_TYPES = {"Process", "Flow"}
    SYSTEM_TYPES = {"TechnologySystem", "BeliefSystem", "ValueSystem"}
    OTHER_TYPES = {
        "FeedbackLoop",
        "Indicator",
        "AnalyticalContext",
        "SystemProperty",
        "CeremonialBehavior",
        "InstrumentalBehavior",
        "PolicyInstrument",
    }

    # Define relationship context rules
    RELATIONSHIP_RULES: Dict[
        RelationshipKind, Dict[str, Union[List[Tuple[str, str]], str]]
    ] = {
        RelationshipKind.GOVERNS: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Actor", "Institution"),
                ("Actor", "Policy"),
                (
                    "Actor",
                    "Resource",
                ),  # Actors can govern resources (ownership, stewardship)
                ("Institution", "Institution"),
                ("Institution", "Actor"),
                ("Institution", "Policy"),  # Institutions can govern policies
                (
                    "Institution",
                    "Resource",
                ),  # Institutions can govern/regulate resources
                ("Policy", "Actor"),
                ("Policy", "Institution"),
                ("Policy", "Resource"),  # Policies can govern resources (regulations)
            ],
            "description": (
                "GOVERNS relationship requires entities capable of "
                "authority or regulation"
            ),
            "invalid_message": (
                "GOVERNS relationship requires authority-capable "
                "entities (Actors, Institutions, Policies) "
                "governing appropriate targets"
            ),
        },
        RelationshipKind.EMPLOYS: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Institution", "Actor"),  # Organizations can employ people
            ],
            "description": "EMPLOYS relationship for labor relationships",
            "invalid_message": (
                "EMPLOYS relationship requires Actor or Institution "
                "employing Actor entities"
            ),
        },
        RelationshipKind.OWNS: {
            "valid_combinations": [
                ("Actor", "Resource"),
                ("Institution", "Resource"),
                ("Actor", "TechnologySystem"),
                ("Institution", "TechnologySystem"),
            ],
            "description": (
                "OWNS relationship requires an entity capable of ownership "
                "and an ownable resource"
            ),
            "invalid_message": (
                "OWNS relationship requires Actor/Institution "
                "owning Resource/TechnologySystem"
            ),
        },
        RelationshipKind.USES: {
            "valid_combinations": [
                ("Actor", "Resource"),
                ("Process", "Resource"),
                ("Actor", "TechnologySystem"),
                ("Process", "TechnologySystem"),
                ("Actor", "Institution"),
                ("Process", "Institution"),
            ],
            "description": "USES relationship requires a user and a usable entity",
            "invalid_message": (
                "USES relationship requires Actor/Process using "
                "Resource/TechnologySystem/Institution"
            ),
        },
        RelationshipKind.PRODUCES: {
            "valid_combinations": [
                ("Actor", "Resource"),
                ("Process", "Resource"),
                ("TechnologySystem", "Resource"),
                ("Actor", "Flow"),
                ("Process", "Flow"),
                ("TechnologySystem", "Flow"),
                ("Actor", "ValueFlow"),
                ("Process", "ValueFlow"),
                ("TechnologySystem", "ValueFlow"),
                ("PolicyInstrument", "Flow"),
                ("PolicyInstrument", "ValueFlow"),
                ("PolicyInstrument", "Resource"),
            ],
            "description": "PRODUCES relationship requires a producer and a producible output",
            "invalid_message": (
                "PRODUCES relationship requires "
                "Actor/Process/TechnologySystem/PolicyInstrument "
                "producing Resource/Flow/ValueFlow"
            ),
        },
        # Enhanced governance relationships
        RelationshipKind.REGULATES: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Institution", "Actor"),
                ("Policy", "Actor"),
                ("Actor", "Institution"),
                ("Institution", "Institution"),
                ("Policy", "Institution"),
                ("Actor", "Resource"),
                ("Institution", "Resource"),
                ("Policy", "Resource"),
                ("Actor", "TechnologySystem"),
                ("Institution", "TechnologySystem"),
                ("Policy", "TechnologySystem"),
            ],
            "description": "REGULATES relationship requires regulatory authority",
            "invalid_message": (
                "REGULATES relationship requires authority entities "
                "(Actor/Institution/Policy) regulating appropriate targets"
            ),
        },
        RelationshipKind.INFLUENCES: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Actor", "Institution"),
                ("Actor", "Policy"),
                ("Institution", "Actor"),
                ("Institution", "Institution"),
                ("Institution", "Policy"),
                ("Policy", "Actor"),  # Policies can influence actors
                ("Policy", "Institution"),  # Policies can influence institutions
                (
                    "Policy",
                    "Resource",
                ),  # Policies can influence resource management/usage
                ("Resource", "Actor"),
                ("Resource", "Institution"),
                ("Flow", "Actor"),
                ("Flow", "Institution"),
                ("TechnologySystem", "Actor"),
                ("TechnologySystem", "Institution"),
                ("TechnologySystem", "Policy"),
                ("Actor", "InstrumentalBehavior"),  # Actors can influence behaviors
                ("Actor", "CeremonialBehavior"),  # Actors can influence behaviors
                (
                    "Institution",
                    "InstrumentalBehavior",
                ),  # Institutions can influence behaviors
                (
                    "Institution",
                    "CeremonialBehavior",
                ),  # Institutions can influence behaviors
                # Policy instruments can influence behaviors
                ("PolicyInstrument", "InstrumentalBehavior"),
                # Policy instruments can influence behaviors
                ("PolicyInstrument", "CeremonialBehavior"),
            ],
            "description": "INFLUENCES relationship for impact and effect patterns",
            "invalid_message": (
                "INFLUENCES relationship requires influence-capable entities "
                "affecting decision-makers or systems"
            ),
        },
        RelationshipKind.FUNDS: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Institution", "Actor"),
                ("Actor", "Institution"),
                ("Institution", "Institution"),
                ("Policy", "Actor"),  # Policies can establish funding for actors
                (
                    "Policy",
                    "Institution",
                ),  # Policies can establish funding for institutions
                ("Actor", "Resource"),
                ("Institution", "Resource"),
                ("Actor", "Process"),
                ("Institution", "Process"),
                ("Actor", "TechnologySystem"),
                ("Institution", "TechnologySystem"),
            ],
            "description": "FUNDS relationship for financial resource provision",
            "invalid_message": (
                "FUNDS relationship requires funding entities "
                "(Actor/Institution/Policy) providing financial resources"
            ),
        },
        RelationshipKind.SUPPLIES: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Institution", "Actor"),
                ("Actor", "Institution"),
                ("Institution", "Institution"),
                ("Actor", "Process"),
                ("Institution", "Process"),
                ("Resource", "Actor"),
                ("Resource", "Institution"),
                ("Resource", "Process"),
                ("TechnologySystem", "Actor"),
                ("TechnologySystem", "Institution"),
                ("TechnologySystem", "Process"),
            ],
            "description": "SUPPLIES relationship for resource provision",
            "invalid_message": (
                "SUPPLIES relationship requires suppliers providing "
                "resources to recipients"
            ),
        },
        RelationshipKind.IMPLEMENTS: {
            "valid_combinations": [
                ("Actor", "Policy"),
                ("Institution", "Policy"),
                ("Actor", "Institution"),
                ("Institution", "Institution"),
                ("Process", "Policy"),
                ("TechnologySystem", "Policy"),
                ("PolicyInstrument", "Policy"),
                (
                    "Policy",
                    "PolicyInstrument",
                ),  # Policies implement through policy instruments
            ],
            "description": "IMPLEMENTS relationship for policy and institutional execution",
            "invalid_message": (
                "IMPLEMENTS relationship requires implementing entities "
                "executing policies or institutional arrangements"
            ),
        },
        RelationshipKind.TRANSFORMS: {
            "valid_combinations": [
                ("Process", "Resource"),
                ("TechnologySystem", "Resource"),
                ("PolicyInstrument", "Resource"),
                ("Process", "Actor"),
                ("TechnologySystem", "Actor"),
                ("PolicyInstrument", "Actor"),
                ("Process", "Flow"),
                ("TechnologySystem", "Flow"),
                ("PolicyInstrument", "Flow"),
                ("Process", "ValueFlow"),
                ("TechnologySystem", "ValueFlow"),
                ("PolicyInstrument", "ValueFlow"),
            ],
            "description": "TRANSFORMS relationship for change and conversion processes",
            "invalid_message": (
                "TRANSFORMS relationship requires active change agents "
                "(Process/TechnologySystem/PolicyInstrument) transforming targets"
            ),
        },
        RelationshipKind.COLLABORATES_WITH: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Institution", "Institution"),
                ("Actor", "Institution"),
                ("Institution", "Actor"),
                ("Process", "Process"),
                ("Actor", "Process"),
                ("Institution", "Process"),
            ],
            "description": "COLLABORATES_WITH relationship for cooperative arrangements",
            "invalid_message": (
                "COLLABORATES_WITH relationship requires cooperative entities "
                "working together"
            ),
        },
        RelationshipKind.COORDINATES_WITH: {
            "valid_combinations": [
                ("Actor", "Actor"),
                ("Institution", "Institution"),
                ("Actor", "Institution"),
                ("Institution", "Actor"),
                ("Process", "Process"),
                ("Actor", "Process"),
                ("Institution", "Process"),
                ("TechnologySystem", "TechnologySystem"),
                ("TechnologySystem", "Process"),
            ],
            "description": "COORDINATES_WITH relationship for alignment and synchronization",
            "invalid_message": (
                "COORDINATES_WITH relationship requires coordinating entities "
                "aligning activities"
            ),
        },
    }

    @staticmethod
    def validate_relationship_context(
        kind: RelationshipKind, source_type: str, target_type: str
    ) -> None:
        """Validate that relationship makes sense in context.

        Args:
            kind: The type of relationship
            source_type: Type of source node (class name)
            target_type: Type of target node (class name)

        Raises:
            IncompatibleEnumError: If relationship doesn't make sense
            InvalidEnumOperationError: If invalid parameters provided
        """

        if not source_type or not target_type:
            raise InvalidEnumOperationError(
                "Source and target types must be provided and non-empty"
            )

        # Check if we have specific rules for this relationship kind
        if kind in EnumValidator.RELATIONSHIP_RULES:
            rule = EnumValidator.RELATIONSHIP_RULES[kind]
            valid_combinations = rule["valid_combinations"]

            if (
                isinstance(valid_combinations, str)
                or (source_type, target_type) not in valid_combinations
            ):
                suggestions = EnumValidator._generate_suggestions(
                    kind, source_type, target_type
                )
                raise IncompatibleEnumError(
                    f"{rule['invalid_message']}. "
                    f"Got {source_type}->{target_type}. "
                    f"{suggestions}"
                )

    @staticmethod
    def validate_flow_combination(nature: FlowNature, flow_type: FlowType) -> None:
        """Validate that flow nature and type are compatible.

        Args:
            nature: The nature of the flow
            flow_type: The type of the flow

        Raises:
            IncompatibleEnumError: If flow nature and type are incompatible
            InvalidEnumOperationError: If invalid parameters provided
        """

        # Define obviously incompatible combinations (semantically impossible)
        strictly_incompatible = {
            # These combinations are clearly nonsensical
            (FlowNature.ENERGY, FlowType.INFORMATION),
            (FlowNature.INFORMATION, FlowType.ENERGY),
            # Physical flows cannot be purely informational
            (FlowNature.MATERIAL, FlowType.INFORMATION),
            (FlowNature.MATERIAL, FlowType.SOCIAL),
            # Financial flows cannot be material or energy
            (FlowNature.FINANCIAL, FlowType.MATERIAL),
            (FlowNature.FINANCIAL, FlowType.ENERGY),
            # Information flows cannot be material or energy
            (FlowNature.INFORMATION, FlowType.MATERIAL),
            # Energy flows cannot be informational or social
            (FlowNature.ENERGY, FlowType.SOCIAL),
            # Social flows are not material or energy based
            (FlowNature.SOCIAL, FlowType.MATERIAL),
            (FlowNature.SOCIAL, FlowType.ENERGY),
            # Service flows are not typically material
            (FlowNature.SERVICE, FlowType.MATERIAL),
            (FlowNature.SERVICE, FlowType.ENERGY),
            # Cultural flows are not material or energy based
            (FlowNature.CULTURAL, FlowType.MATERIAL),
            (FlowNature.CULTURAL, FlowType.ENERGY),
            # Regulatory flows are primarily informational
            (FlowNature.REGULATORY, FlowType.MATERIAL),
            (FlowNature.REGULATORY, FlowType.ENERGY),
        }

        if (nature, flow_type) in strictly_incompatible:
            raise IncompatibleEnumError(
                f"Flow nature {nature.name} is semantically incompatible with "
                f"flow type {flow_type.name}. Consider using compatible combinations."
            )

    @staticmethod
    def validate_institution_layer_context(
        layer: InstitutionLayer, institution_type: str
    ) -> None:
        """Validate that institution layer makes sense for the institution type.

        Args:
            layer: The institutional layer
            institution_type: Type of institution

        Raises:
            IncompatibleEnumError: If layer doesn't match institution type
            InvalidEnumOperationError: If invalid parameters provided
        """

        # Formal rules should typically apply to formal institutions
        if layer == InstitutionLayer.FORMAL_RULE and institution_type in [
            "BeliefSystem",
            "ValueSystem",
        ]:
            raise IncompatibleEnumError(
                f"FORMAL_RULE layer is typically not appropriate for {institution_type}. "
                f"Consider using CULTURAL_VALUE or KNOWLEDGE_SYSTEM layers for "
                f"belief/value systems."
            )

    @staticmethod
    def validate_policy_instrument_combination(
        instrument_type: PolicyInstrumentType, target_context: str
    ) -> None:
        """Validate that policy instrument type is appropriate for target context.

        Args:
            instrument_type: The type of policy instrument
            target_context: Context where the instrument is being applied

        Raises:
            IncompatibleEnumError: If instrument type doesn't match context
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not target_context:
            raise InvalidEnumOperationError(
                "Target context must be provided and non-empty"
            )

        # Define inappropriate combinations
        inappropriate_combinations = {
            # Regulatory instruments should not be used for voluntary contexts
            (PolicyInstrumentType.REGULATORY, "voluntary"),
            (PolicyInstrumentType.REGULATORY, "market_based"),
            # Economic instruments less effective for information provision
            (PolicyInstrumentType.ECONOMIC, "information_provision"),
            (PolicyInstrumentType.ECONOMIC, "awareness_building"),
        }

        if (instrument_type, target_context.lower()) in inappropriate_combinations:
            raise IncompatibleEnumError(
                f"Policy instrument {instrument_type.name} may not be appropriate for "
                f"{target_context} context. Consider alternative instrument types that "
                f"better align with the target context."
            )

    @staticmethod
    def validate_value_category_context(
        category: ValueCategory, measurement_context: str
    ) -> None:
        """Validate that value category is appropriate for measurement context.

        Args:
            category: The value category being measured
            measurement_context: Context of measurement (e.g., 'quantitative', 'qualitative')

        Raises:
            IncompatibleEnumError: If category doesn't match measurement context
            InvalidEnumOperationError: If invalid parameters provided
        """

        if not measurement_context:
            raise InvalidEnumOperationError(
                "Measurement context must be provided and non-empty"
            )

        # Define categories that are difficult to measure quantitatively
        qualitative_preferred = {
            ValueCategory.CULTURAL,
            ValueCategory.SPIRITUAL,
            ValueCategory.AESTHETIC,
            ValueCategory.ETHICAL,
            ValueCategory.PSYCHOLOGICAL,
            ValueCategory.COMMUNITY,
        }

        # Define categories that are typically quantitative
        quantitative_preferred = {
            ValueCategory.ECONOMIC,
            ValueCategory.PERFORMANCE,
            ValueCategory.EFFICIENCY,
            ValueCategory.EFFECTIVENESS,
            ValueCategory.DEMOGRAPHIC,
        }

        context_lower = measurement_context.lower()

        if context_lower == "quantitative" and category in qualitative_preferred:
            raise IncompatibleEnumError(
                f"Value category {category.name} is typically difficult to measure "
                f"quantitatively. Consider qualitative measurement approaches or "
                f"complementary quantitative indicators."
            )

        if context_lower == "qualitative" and category in quantitative_preferred:
            raise IncompatibleEnumError(
                f"Value category {category.name} is typically measured quantitatively. "
                f"Consider quantitative measurement approaches or mixed-method evaluation."
            )

    @staticmethod
    def validate_cross_enum_dependency(
        primary_enum: Enum, dependent_enum: Enum, relationship_type: str
    ) -> None:
        """Validate cross-enum dependencies and relationships.

        Args:
            primary_enum: The primary enum that constrains choices
            dependent_enum: The dependent enum that must align with primary
            relationship_type: Type of dependency relationship

        Raises:
            IncompatibleEnumError: If enums are incompatible
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not relationship_type:
            raise InvalidEnumOperationError(
                "Relationship type must be provided and non-empty"
            )

        # Handle flow nature and institution layer dependencies
        if (
            isinstance(primary_enum, FlowNature)
            and isinstance(dependent_enum, InstitutionLayer)
            and relationship_type.lower() == "governance"
        ):

            # Financial flows should typically be governed by formal institutions
            if (
                primary_enum == FlowNature.FINANCIAL
                and dependent_enum == InstitutionLayer.INFORMAL_NORM
            ):
                raise IncompatibleEnumError(
                    f"Financial flows ({primary_enum.name}) typically require formal "
                    f"institutional governance, not {dependent_enum.name}. "
                    f"Consider FORMAL_RULE or ORGANIZATION layers."
                )

            # Cultural flows align better with cultural value layers
            if (
                primary_enum == FlowNature.CULTURAL
                and dependent_enum == InstitutionLayer.FORMAL_RULE
            ):
                raise IncompatibleEnumError(
                    f"Cultural flows ({primary_enum.name}) may be over-regulated by "
                    f"{dependent_enum.name}. Consider CULTURAL_VALUE or INFORMAL_NORM layers."
                )

    @staticmethod
    def validate_required_enum_context(
        enum_value: Enum, context: str, is_required: bool = True
    ) -> None:
        """Validate whether an enum is required or optional in given context.

        Args:
            enum_value: The enum value to validate
            context: The context where the enum is used
            is_required: Whether the enum is required in this context

        Raises:
            InvalidEnumOperationError: If required enum is missing or invalid
        """
        if not context:
            raise InvalidEnumOperationError("Context must be provided and non-empty")

        # Define contexts where specific enums are required
        required_contexts: Dict[str, List[Type[Enum]]] = {
            "financial_transaction": [FlowNature, FlowType],
            "policy_implementation": [PolicyInstrumentType],
            "institutional_analysis": [InstitutionLayer],
            "value_measurement": [ValueCategory],
            "relationship_creation": [RelationshipKind],
        }

        context_lower = context.lower()
        if context_lower in required_contexts:
            required_enum_types = required_contexts[context_lower]
            enum_type = type(enum_value)

            if is_required and enum_type not in required_enum_types:
                raise InvalidEnumOperationError(
                    f"Context '{context}' requires one of these enum types: "
                    f"{[t.__name__ for t in required_enum_types]}, but got {enum_type.__name__}"
                )

            if not is_required and enum_type in required_enum_types:
                # This is fine - optional usage of a typically required enum
                pass

    @staticmethod
    def validate_technology_readiness_level(
        level: TechnologyReadinessLevel, context: str = "general"
    ) -> None:
        """Validate TechnologyReadinessLevel usage in context.

        Args:
            level: The TRL level to validate
            context: Context where TRL is being used

        Raises:
            InvalidEnumOperationError: If invalid parameters provided
            IncompatibleEnumError: If TRL inappropriate for context
        """
        if not context:
            raise InvalidEnumOperationError("Context must be provided and non-empty")

        # Define context-specific validation rules
        context_lower = context.lower()

        # Research contexts typically use lower TRL levels
        if context_lower in ["research", "basic_research", "laboratory"]:
            if level.value > 6:
                raise IncompatibleEnumError(
                    f"TRL {level.value} ({level.name}) may be too advanced for {context} context. "
                    f"Research contexts typically use TRL 1-6."
                )

        # Commercial contexts typically require higher TRL levels
        elif context_lower in ["commercial", "production", "deployment"]:
            if level.value < 7:
                raise IncompatibleEnumError(
                    f"TRL {level.value} ({level.name}) may be too early for {context} context. "
                    f"Commercial contexts typically require TRL 7-9."
                )

    @staticmethod
    def validate_legitimacy_source_context(
        source: LegitimacySource, institutional_context: str
    ) -> None:
        """Validate LegitimacySource appropriateness for institutional context.

        Args:
            source: The legitimacy source to validate
            institutional_context: Type of institutional context

        Raises:
            InvalidEnumOperationError: If invalid parameters provided
            IncompatibleEnumError: If source inappropriate for context
        """
        if not institutional_context:
            raise InvalidEnumOperationError(
                "Institutional context must be provided and non-empty"
            )

        context_lower = institutional_context.lower()

        # Traditional legitimacy rarely appropriate for modern bureaucratic contexts
        if source == LegitimacySource.TRADITIONAL and context_lower in [
            "bureaucracy",
            "modern_government",
            "corporation",
            "scientific_institution",
        ]:
            raise IncompatibleEnumError(
                f"Traditional legitimacy may not be appropriate for "
                f"{institutional_context}. Consider LEGAL_RATIONAL or EXPERT "
                f"legitimacy sources."
            )

        # Charismatic legitimacy typically unstable for large-scale institutions
        if source == LegitimacySource.CHARISMATIC and context_lower in [
            "large_organization",
            "government_agency",
            "public_administration",
        ]:
            raise IncompatibleEnumError(
                f"Charismatic legitimacy may be inappropriate for "
                f"{institutional_context}. Large-scale institutions typically "
                f"require LEGAL_RATIONAL legitimacy."
            )

        # Expert legitimacy most appropriate for technical/scientific contexts
        if source != LegitimacySource.EXPERT and context_lower in [
            "technical_organization",
            "research_institution",
            "professional_body",
        ]:
            # This is a warning rather than error - other sources can exist
            # but expert is preferred
            pass

    @staticmethod
    def _generate_suggestions(
        kind: RelationshipKind, source_type: str, target_type: str
    ) -> str:
        """Generate intelligent, context-aware suggestions for valid combinations.

        Enhanced suggestion algorithm that provides:
        - Semantic analysis of relationship types
        - Entity type compatibility assessment
        - Context-aware alternative recommendations
        - SFM-specific business logic guidance
        """
        suggestions: List[str] = []

        # Try specific rules first for basic suggestions
        if kind in EnumValidator.RELATIONSHIP_RULES:
            valid_combinations = EnumValidator.RELATIONSHIP_RULES[kind][
                "valid_combinations"
            ]

            # Find suggestions for the source type
            source_suggestions = [
                combo[1] for combo in valid_combinations if combo[0] == source_type
            ]
            target_suggestions = [
                combo[0] for combo in valid_combinations if combo[1] == target_type
            ]

            if source_suggestions:
                suggestions.append(
                    f"For {source_type} sources, valid targets are: "
                    f"{', '.join(set(source_suggestions))}"
                )
            if target_suggestions:
                suggestions.append(
                    f"For {target_type} targets, valid sources are: "
                    f"{', '.join(set(target_suggestions))}"
                )

        # Always enhance with intelligent suggestion algorithms
        semantic_suggestions = EnumValidator._generate_semantic_suggestions(
            kind, source_type, target_type
        )
        if semantic_suggestions:
            suggestions.extend(semantic_suggestions)

        # Business logic suggestions based on SFM principles
        business_suggestions = EnumValidator._generate_business_logic_suggestions(
            kind, source_type, target_type
        )
        if business_suggestions:
            suggestions.extend(business_suggestions)

        # Context-aware entity compatibility suggestions
        entity_suggestions = EnumValidator._generate_entity_compatibility_suggestions(
            source_type, target_type
        )
        if entity_suggestions:
            suggestions.extend(entity_suggestions)

        if suggestions:
            return "Suggestions: " + "; ".join(suggestions)

        return "Check the relationship documentation for valid combinations."

    @staticmethod
    def _generate_semantic_suggestions(
        kind: RelationshipKind, source_type: str, target_type: str
    ) -> List[str]:
        """Generate suggestions based on semantic analysis of relationship types."""
        suggestions: List[str] = []

        # Categorize relationships by semantic meaning
        governance_relations = {
            RelationshipKind.GOVERNS,
            RelationshipKind.REGULATES,
            RelationshipKind.MANDATES,
            RelationshipKind.AUTHORIZES,
            RelationshipKind.ENFORCES,
            RelationshipKind.DELEGATES,
            RelationshipKind.LICENSES,
            RelationshipKind.CERTIFIES,
            RelationshipKind.SANCTIONS,
        }

        resource_flow_relations = {
            RelationshipKind.FUNDS,
            RelationshipKind.PAYS,
            RelationshipKind.ALLOCATES,
            RelationshipKind.TRANSFERS,
            RelationshipKind.SUPPLIES,
            RelationshipKind.PRODUCES,
            RelationshipKind.DISTRIBUTES,
            RelationshipKind.CONVERTS,
            RelationshipKind.EXCHANGES_WITH,
        }

        knowledge_relations = {
            RelationshipKind.INFORMS,
            RelationshipKind.EDUCATES,
            RelationshipKind.ADVISES,
            RelationshipKind.RESEARCHES,
            RelationshipKind.ANALYZES,
            RelationshipKind.COMMUNICATES_WITH,
            RelationshipKind.DOCUMENTS,
            RelationshipKind.MEASURES,
        }

        collaborative_relations = {
            RelationshipKind.COLLABORATES_WITH,
            RelationshipKind.COORDINATES_WITH,
            RelationshipKind.SUPPORTS,
            RelationshipKind.ALLIES_WITH,
            RelationshipKind.FACILITATES,
            RelationshipKind.PARTICIPATES_IN,
            RelationshipKind.ORGANIZES,
        }

        # Provide semantic category guidance
        if kind in governance_relations:
            if source_type not in ["Actor", "Institution", "Policy"]:
                suggestions.append(
                    f"Governance relationships like {kind.name} typically "
                    "require Actor, Institution, or Policy as source"
                )
            if target_type in ["Actor", "Institution", "Policy", "Resource"]:
                suggestions.append(
                    f"Consider {kind.name} with governable entities: "
                    "Actor, Institution, Policy, or Resource"
                )

        elif kind in resource_flow_relations:
            if source_type not in [
                "Actor",
                "Institution",
                "Process",
                "PolicyInstrument",
            ]:
                suggestions.append(
                    f"Resource flow relationships like {kind.name} typically "
                    "require entities capable of resource handling"
                )
            if target_type not in ["Actor", "Resource", "Flow", "ValueFlow"]:
                suggestions.append(
                    f"Consider {kind.name} targeting resource-receiving entities: "
                    "Actor, Resource, Flow, or ValueFlow"
                )

        elif kind in knowledge_relations:
            if source_type not in ["Actor", "Institution", "TechnologySystem"]:
                suggestions.append(
                    f"Knowledge relationships like {kind.name} typically "
                    "require information-capable entities"
                )
            if target_type not in [
                "Actor",
                "Institution",
                "Resource",
                "TechnologySystem",
            ]:
                suggestions.append(
                    f"Consider {kind.name} with information-receiving entities"
                )

        elif kind in collaborative_relations:
            if source_type not in ["Actor", "Institution"]:
                suggestions.append(
                    f"Collaborative relationships like {kind.name} typically "
                    "require social entities like Actor or Institution"
                )
            if target_type not in ["Actor", "Institution", "Process"]:
                suggestions.append(
                    f"Consider {kind.name} with collaborative entities: "
                    "Actor, Institution, or Process"
                )

        return suggestions

    @staticmethod
    def _generate_business_logic_suggestions(
        kind: RelationshipKind, source_type: str, target_type: str
    ) -> List[str]:
        # pylint: disable=too-many-branches
        # This function requires many branches to handle different SFM relationship patterns
        # and institutional analysis rules from Hayden's framework
        """Generate suggestions based on SFM business logic and domain constraints."""
        suggestions: List[str] = []

        # SFM-specific institutional analysis patterns
        if kind == RelationshipKind.IMPLEMENTS and source_type == "Actor":
            if target_type not in ["Policy", "Institution"]:
                suggestions.append(
                    "Actors typically implement Policies or "
                    "institutional arrangements"
                )

        elif kind == RelationshipKind.INFLUENCES:
            if source_type in ["Resource", "Flow"] and target_type in [
                "Actor",
                "Institution",
            ]:
                suggestions.append(
                    "Resources and Flows can influence decision-making entities"
                )
            elif source_type in ["Actor", "Institution"] and target_type in [
                "Actor",
                "Institution",
                "Policy",
            ]:
                suggestions.append(
                    "Social entities can influence other social entities "
                    "and policies"
                )

        elif kind == RelationshipKind.TRANSFORMS:
            if source_type not in ["Process", "TechnologySystem", "PolicyInstrument"]:
                suggestions.append(
                    "Transformation typically requires active change agents: "
                    "Process, TechnologySystem, or PolicyInstrument"
                )
            if target_type not in ["Resource", "Flow", "ValueFlow", "Actor"]:
                suggestions.append(
                    "Consider transformation targets: Resource, Flow, "
                    "ValueFlow, or Actor"
                )

        # Hayden's institutional layer compatibility
        elif kind in [RelationshipKind.ENFORCES, RelationshipKind.SANCTIONS]:
            if source_type != "Institution":
                suggestions.append(
                    "Enforcement and sanctions typically come from "
                    "institutional authority"
                )

        # Economic flow patterns
        elif kind in [
            RelationshipKind.BUYS_FROM,
            RelationshipKind.SELLS_TO,
            RelationshipKind.PAYS,
        ]:
            if source_type not in ["Actor", "Institution"]:
                suggestions.append("Economic transactions require economic actors")
            if target_type not in ["Actor", "Institution"]:
                suggestions.append("Economic transactions target other economic actors")

        return suggestions

    @staticmethod
    def _generate_entity_compatibility_suggestions(
        source_type: str, target_type: str
    ) -> List[str]:
        """Generate suggestions based on entity type compatibility in SFM framework."""
        suggestions: List[str] = []

        # Get entity type categories for analysis
        source_category = EnumValidator._get_entity_category(source_type)
        target_category = EnumValidator._get_entity_category(target_type)

        # Suggest compatible entity combinations
        if source_category == "social" and target_category == "structural":
            suggestions.append(
                "Social entities (Actor, Institution) work well with "
                "structural entities (Resource, TechnologySystem)"
            )

        elif source_category == "active" and target_category == "passive":
            suggestions.append(
                "Active entities (Actor, Process) can effectively "
                "operate on passive entities (Resource, Flow)"
            )

        elif source_category == "authority" and target_category in [
            "social",
            "structural",
        ]:
            suggestions.append(
                "Authority entities (Institution, Policy) can govern "
                "social and structural entities"
            )

        elif source_type == target_type:
            suggestions.append(
                f"Same-type relationships ({source_type}->{target_type}) "
                f"may indicate peer interaction patterns"
            )

        return suggestions

    @staticmethod
    def _get_entity_category(entity_type: str) -> str:
        """Categorize entity types for compatibility analysis."""
        if entity_type in EnumValidator.ACTOR_TYPES:
            return "social"
        if entity_type in EnumValidator.INSTITUTION_TYPES:
            return "authority"
        if entity_type in EnumValidator.RESOURCE_TYPES:
            return "structural"
        if entity_type in EnumValidator.PROCESS_TYPES:
            return "active"
        if entity_type in EnumValidator.SYSTEM_TYPES:
            return "structural"
        return "other"

    @staticmethod
    def validate_cross_entity_consistency(
        entity_1_type: str,
        entity_2_type: str,
        relationship_kind: RelationshipKind,
        context: str = "general",
    ) -> None:
        """Validate consistency across multiple entities in SFM framework.

        This method implements advanced cross-entity validation rules that ensure
        entities work together coherently within the SFM framework, considering
        business logic and domain constraints.

        Args:
            entity_1_type: Type of first entity
            entity_2_type: Type of second entity
            relationship_kind: The relationship connecting them
            context: Additional context for validation

        Raises:
            IncompatibleEnumError: If entities are inconsistent
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not entity_1_type or not entity_2_type:
            raise InvalidEnumOperationError(
                "Entity types must be provided and non-empty"
            )

        # Basic relationship validation first
        EnumValidator.validate_relationship_context(
            relationship_kind, entity_1_type, entity_2_type
        )

        # Advanced consistency checks based on SFM principles
        EnumValidator._validate_authority_consistency(
            relationship_kind, entity_1_type, entity_2_type
        )
        EnumValidator._validate_economic_consistency(
            relationship_kind, entity_1_type, entity_2_type
        )
        EnumValidator._validate_context_specific_consistency(
            relationship_kind, entity_1_type, entity_2_type, context
        )

    @staticmethod
    def _validate_authority_consistency(
        relationship_kind: RelationshipKind, entity_1_type: str, entity_2_type: str
    ) -> None:
        """Validate authority consistency for governance relationships."""
        governance_relationships = {
            RelationshipKind.GOVERNS,
            RelationshipKind.REGULATES,
            RelationshipKind.MANDATES,
            RelationshipKind.AUTHORIZES,
            RelationshipKind.ENFORCES,
        }

        if relationship_kind in governance_relationships:
            if entity_1_type in ["Resource", "Flow"] and entity_2_type in [
                "Actor",
                "Institution",
            ]:
                raise IncompatibleEnumError(
                    f"Authority inconsistency: {entity_1_type} cannot exercise governance "
                    f"over {entity_2_type}. Governance requires authority-capable entities."
                )

    @staticmethod
    def _validate_economic_consistency(
        relationship_kind: RelationshipKind, entity_1_type: str, entity_2_type: str
    ) -> None:
        """Validate economic consistency for financial relationships."""
        economic_relationships = {
            RelationshipKind.FUNDS,
            RelationshipKind.PAYS,
            RelationshipKind.BUYS_FROM,
            RelationshipKind.SELLS_TO,
            RelationshipKind.INVESTS_IN,
        }

        if relationship_kind in economic_relationships:
            non_economic_entities = ["Flow", "ValueFlow", "Process"]
            if (
                entity_1_type in non_economic_entities
                or entity_2_type in non_economic_entities
            ):
                raise IncompatibleEnumError(
                    f"Economic inconsistency: {relationship_kind.name} relationship "
                    f"between {entity_1_type} and {entity_2_type} requires economic actors. "
                    f"Consider Actor or Institution entities for economic transactions."
                )

    @staticmethod
    def _validate_context_specific_consistency(
        relationship_kind: RelationshipKind,
        entity_1_type: str,
        entity_2_type: str,
        context: str,
    ) -> None:
        """Validate context-specific consistency rules."""
        context_lower = context.lower()

        # Temporal consistency
        if context_lower in ["temporal", "time_series"]:
            EnumValidator._validate_temporal_consistency(
                relationship_kind, entity_1_type, entity_2_type
            )

        # Spatial consistency
        if context_lower in ["spatial", "geographic"]:
            EnumValidator._validate_spatial_consistency(
                relationship_kind, entity_1_type, entity_2_type
            )

    @staticmethod
    def _validate_temporal_consistency(
        relationship_kind: RelationshipKind, entity_1_type: str, entity_2_type: str
    ) -> None:
        """Validate temporal consistency for time-sensitive relationships."""
        temporal_sensitive = {
            RelationshipKind.PRECEDES,
            RelationshipKind.FOLLOWS,
            RelationshipKind.TRIGGERS,
            RelationshipKind.SYNCHRONIZES_WITH,
            RelationshipKind.SUPERSEDES,
        }

        if relationship_kind in temporal_sensitive:
            # Structural entities (Resources, Systems) may have different temporal patterns
            if entity_1_type in ["Resource", "TechnologySystem"] and entity_2_type in [
                "Actor"
            ]:
                # This is acceptable but requires careful temporal modeling
                pass

    @staticmethod
    def _validate_spatial_consistency(
        relationship_kind: RelationshipKind, entity_1_type: str, entity_2_type: str
    ) -> None:
        """Validate spatial consistency for location-based relationships."""
        spatial_relationships = {
            RelationshipKind.LOCATED_IN,
            RelationshipKind.CONNECTS,
            RelationshipKind.TRANSPORTS,
            RelationshipKind.CONTAINS,
            RelationshipKind.ENCOMPASSES,
        }

        if relationship_kind in spatial_relationships:
            if entity_1_type in ["Flow", "ValueFlow"] and entity_2_type in [
                "Flow",
                "ValueFlow",
            ]:
                raise IncompatibleEnumError(
                    f"Spatial inconsistency: {relationship_kind.name} between flows "
                    f"may require spatial anchor entities (Actor, Institution, Resource)."
                )

    @staticmethod
    def validate_business_rule_constraints(
        relationship_kind: RelationshipKind,
        source_type: str,
        target_type: str,
        domain_context: str = "general",
    ) -> None:
        """Validate SFM-specific business rules and domain constraints.

        This method implements domain-specific validation rules based on Hayden's
        institutional analysis framework and SFM methodology.

        Args:
            relationship_kind: The relationship type to validate
            source_type: Source entity type
            target_type: Target entity type
            domain_context: Domain-specific context (e.g., 'environmental', 'economic')

        Raises:
            IncompatibleEnumError: If business rules are violated
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not all([relationship_kind, source_type, target_type]):
            raise InvalidEnumOperationError(
                "All parameters must be provided and non-empty"
            )

        domain_lower = domain_context.lower()

        # Delegate to domain-specific validation methods
        if domain_lower in ["environmental", "sustainability", "ecological"]:
            EnumValidator._validate_environmental_constraints(
                relationship_kind, source_type, target_type
            )
        elif domain_lower in ["economic", "financial", "market"]:
            EnumValidator._validate_economic_constraints(
                relationship_kind, source_type, target_type
            )
        elif domain_lower in ["social", "community", "governance"]:
            EnumValidator._validate_social_constraints(
                relationship_kind, source_type, target_type
            )
        elif domain_lower in ["institutional", "policy", "governance"]:
            EnumValidator._validate_institutional_constraints(
                relationship_kind, source_type, target_type
            )

    @staticmethod
    def _validate_environmental_constraints(
        relationship_kind: RelationshipKind, source_type: str, target_type: str
    ) -> None:
        """Validate environmental domain constraints."""
        # Environmental policies should primarily regulate actors and resources
        if relationship_kind == RelationshipKind.REGULATES and source_type == "Policy":
            if target_type not in ["Actor", "Resource", "TechnologySystem"]:
                raise IncompatibleEnumError(
                    f"Environmental regulatory constraint: Policy should regulate "
                    f"entities with environmental impact (Actor/Resource/TechnologySystem), "
                    f"not {target_type}."
                )

        # Environmental flows should connect to resource or actor entities
        if relationship_kind in [RelationshipKind.PRODUCES, RelationshipKind.CONSUMES]:
            if source_type == "Flow" and target_type not in ["Resource", "Actor"]:
                raise IncompatibleEnumError(
                    f"Environmental flow constraint: {relationship_kind.name} from Flow "
                    f"should target Resource or Actor entities in environmental context."
                )

    @staticmethod
    def _validate_economic_constraints(
        relationship_kind: RelationshipKind, source_type: str, target_type: str
    ) -> None:
        """Validate economic domain constraints."""
        # Market relationships require economic actors
        market_relationships = {
            RelationshipKind.COMPETES_WITH,
            RelationshipKind.BUYS_FROM,
            RelationshipKind.SELLS_TO,
            RelationshipKind.CONTRACTS_WITH,
        }

        if relationship_kind in market_relationships:
            if source_type not in ["Actor", "Institution"] or target_type not in [
                "Actor",
                "Institution",
            ]:
                raise IncompatibleEnumError(
                    f"Economic constraint: Market relationship {relationship_kind.name} "
                    f"requires economic actors (Actor/Institution), "
                    f"got {source_type}->{target_type}."
                )

        # Investment relationships require financial capability
        if relationship_kind == RelationshipKind.INVESTS_IN:
            if source_type not in ["Actor", "Institution"]:
                raise IncompatibleEnumError(
                    f"Economic constraint: Investment requires Actor or Institution "
                    f"as investor, not {source_type}."
                )

    @staticmethod
    def _validate_social_constraints(
        relationship_kind: RelationshipKind, source_type: str, target_type: str
    ) -> None:
        """Validate social domain constraints."""
        # Social coordination requires social entities
        social_relationships = {
            RelationshipKind.COLLABORATES_WITH,
            RelationshipKind.COORDINATES_WITH,
            RelationshipKind.PARTICIPATES_IN,
            RelationshipKind.ORGANIZES,
        }

        if relationship_kind in social_relationships:
            if source_type not in ["Actor", "Institution"]:
                raise IncompatibleEnumError(
                    f"Social constraint: {relationship_kind.name} requires social entities "
                    f"(Actor/Institution) as participants, not {source_type}."
                )

    @staticmethod
    def _validate_institutional_constraints(
        relationship_kind: RelationshipKind, source_type: str, target_type: str
    ) -> None:
        """Validate institutional domain constraints (Hayden's framework)."""
        # Institutional implementation requires clear authority
        if relationship_kind == RelationshipKind.IMPLEMENTS:
            if source_type not in ["Actor", "Institution", "PolicyInstrument"]:
                raise IncompatibleEnumError(
                    f"Institutional constraint: Policy implementation requires "
                    f"implementing entities (Actor/Institution/PolicyInstrument), "
                    f"not {source_type}."
                )

            if target_type not in ["Policy", "Institution"]:
                raise IncompatibleEnumError(
                    f"Institutional constraint: Implementation should target "
                    f"institutional arrangements (Policy/Institution), not {target_type}."
                )


def validate_enum_operation(
    operation_name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to validate enum operations and provide better error messages.

    Args:
        operation_name: Name of the operation being performed

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (TypeError, ValueError, AttributeError) as e:
                raise InvalidEnumOperationError(
                    f"Invalid {operation_name} operation: {str(e)}"
                ) from e

        return wrapper

    return decorator
