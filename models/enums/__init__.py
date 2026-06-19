"""
Enumerations package for the Social Fabric Matrix (SFM) framework.

This package provides domain-scoped enum modules. All enums are re-exported
here so that ``from models.enums import X`` works for any enum ``X``.

Domain modules
--------------
- :mod:`values`        – value categories and value-system types
- :mod:`institutions`  – institutional layers, governance, enforcement
- :mod:`resources`     – resource types, flow nature/type, provisioning
- :mod:`relationships` – relationship kinds, conflict and cross-impact types
- :mod:`policies`      – policy instrument and policy-lifecycle types
- :mod:`systems`       – system properties, feedback, change, and evolution
- :mod:`analysis`      – analytical and measurement methods, matrix/digraph ops
- :mod:`technology`    – technology, skills, knowledge, and information systems
- :mod:`stakeholders`  – stakeholder types, participation, and decision-making
- :mod:`social`        – social fabric indicators and social cost types
- :mod:`exceptions`    – exception hierarchy and ``EnumValidator``
"""

from models.enums.values import (
    ValueCategory,
    SocialValueDimension,
    ValueSystemType,
    ValueJudgmentType,
    CeremonialInstrumentalType,
)

from models.enums.institutions import (
    InstitutionLayer,
    PathDependencyType,
    InstitutionalChangeType,
    LegitimacySource,
    InstitutionalScope,
    GovernanceMechanism,
    EnforcementType,
    InstitutionalLevel,
    NormativeFramework,
    DeontologicalCategory,
    CommonsGovernanceType,
    TransactionCostType,
    CoordinationMechanismType,
    CoordinationScope,
    AdjustmentType,
    AdjustmentTrigger,
    BoundaryType,
    SystemBoundaryType,
)

from models.enums.resources import (
    ResourceType,
    FlowNature,
    FlowType,
    ProvisioningStage,
    DeliveryQuantificationMethod,
)

from models.enums.relationships import (
    RelationshipKind,
    CrossImpactType,
    ConflictType,
    ConflictResolutionMethod,
)

from models.enums.policies import (
    PolicyInstrumentType,
    PolicyType,
    PolicyScope,
    ImplementationComplexity,
    PolicyEffectiveness,
    EvaluationMethod,
)

from models.enums.systems import (
    ChangeType,
    BehaviorPatternType,
    FeedbackPolarity,
    FeedbackType,
    TemporalFunctionType,
    SystemPropertyType,
    SystemArchetype,
    SystemLevel,
    EvolutionaryStage,
    DependencyStrength,
    SequenceStage,
    ProblemSolvingStage,
)

from models.enums.analysis import (
    ValidationRuleType,
    CorrelationType,
    EvidenceQuality,
    CriteriaType,
    MeasurementApproach,
    CorrelationScale,
    CriteriaPriority,
    StatisticalMethod,
    MatrixOperationType,
    MatrixConstructionStage,
    DigraphAnalysisType,
    NetworkMetricType,
    DigraphNodeType,
    AnalyticalMethod,
    ValidationMethod,
    IndicatorType,
)

from models.enums.technology import (
    ToolSkillTechnologyType,
    TechnologyReadinessLevel,
    TechnologyMaturityLevel,
    SkillLevel,
    KnowledgeType,
    LearningMethod,
    InformationSystem,
)

from models.enums.stakeholders import (
    PowerResourceType,
    StakeholderType,
    ParticipationLevel,
    DecisionMakingApproach,
    DecisionMakingType,
    CommunicationChannel,
)

from models.enums.social import (
    SocialFabricIndicatorType,
    SocialCostType,
)

from models.enums.exceptions import (
    SFMEnumError,
    IncompatibleEnumError,
    InvalidEnumOperationError,
    EnumValidator,
    validate_enum_operation,
)

__all__ = [
    # values
    "ValueCategory",
    "SocialValueDimension",
    "ValueSystemType",
    "ValueJudgmentType",
    "CeremonialInstrumentalType",
    # institutions
    "InstitutionLayer",
    "PathDependencyType",
    "InstitutionalChangeType",
    "LegitimacySource",
    "InstitutionalScope",
    "GovernanceMechanism",
    "EnforcementType",
    "InstitutionalLevel",
    "NormativeFramework",
    "DeontologicalCategory",
    "CommonsGovernanceType",
    "TransactionCostType",
    "CoordinationMechanismType",
    "CoordinationScope",
    "AdjustmentType",
    "AdjustmentTrigger",
    "BoundaryType",
    "SystemBoundaryType",
    # resources
    "ResourceType",
    "FlowNature",
    "FlowType",
    "ProvisioningStage",
    "DeliveryQuantificationMethod",
    # relationships
    "RelationshipKind",
    "CrossImpactType",
    "ConflictType",
    "ConflictResolutionMethod",
    # policies
    "PolicyInstrumentType",
    "PolicyType",
    "PolicyScope",
    "ImplementationComplexity",
    "PolicyEffectiveness",
    "EvaluationMethod",
    # systems
    "ChangeType",
    "BehaviorPatternType",
    "FeedbackPolarity",
    "FeedbackType",
    "TemporalFunctionType",
    "SystemPropertyType",
    "SystemArchetype",
    "SystemLevel",
    "EvolutionaryStage",
    "DependencyStrength",
    "SequenceStage",
    "ProblemSolvingStage",
    # analysis
    "ValidationRuleType",
    "CorrelationType",
    "EvidenceQuality",
    "CriteriaType",
    "MeasurementApproach",
    "CorrelationScale",
    "CriteriaPriority",
    "StatisticalMethod",
    "MatrixOperationType",
    "MatrixConstructionStage",
    "DigraphAnalysisType",
    "NetworkMetricType",
    "DigraphNodeType",
    "AnalyticalMethod",
    "ValidationMethod",
    "IndicatorType",
    # technology
    "ToolSkillTechnologyType",
    "TechnologyReadinessLevel",
    "TechnologyMaturityLevel",
    "SkillLevel",
    "KnowledgeType",
    "LearningMethod",
    "InformationSystem",
    # stakeholders
    "PowerResourceType",
    "StakeholderType",
    "ParticipationLevel",
    "DecisionMakingApproach",
    "DecisionMakingType",
    "CommunicationChannel",
    # social
    "SocialFabricIndicatorType",
    "SocialCostType",
    # exceptions and utilities
    "SFMEnumError",
    "IncompatibleEnumError",
    "InvalidEnumOperationError",
    "EnumValidator",
    "validate_enum_operation",
]
