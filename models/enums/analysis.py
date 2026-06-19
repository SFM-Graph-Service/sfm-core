"""
Analysis and measurement enumerations for the Social Fabric Matrix (SFM) framework.

Covers validation rules, correlation types, evidence quality, criteria types,
measurement approaches, statistical methods, matrix operations, and digraph analysis.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
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
]

class ValidationRuleType(Enum):
    """
    Classification of validation rule types for data integrity.

    Defines different types of validation rules that can be applied
    to ensure data quality and consistency.
    """

    RANGE = auto()  # Value within specified bounds
    SUM = auto()  # Sum constraints across multiple values
    REQUIRED = auto()  # Mandatory field validation
    UNIQUE = auto()  # Uniqueness constraints
    FORMAT = auto()  # Format or pattern validation
    RELATIONSHIP = auto()  # Cross-field relationship validation


class CorrelationType(Enum):
    """Types of correlations in SFM matrix cells."""

    POSITIVE = auto()  # Institution supports criteria
    NEGATIVE = auto()  # Institution hinders criteria
    NEUTRAL = auto()  # No significant relationship
    UNKNOWN = auto()  # Relationship unclear


class EvidenceQuality(Enum):
    """Quality levels for evidence supporting matrix cell correlations."""

    LOW = auto()  # Anecdotal or weak evidence
    MEDIUM = auto()  # Some empirical support
    HIGH = auto()  # Strong empirical evidence
    VERIFIED = auto()  # Peer-reviewed or validated evidence


class CriteriaType(Enum):
    """Types of criteria used in SFM evaluation."""

    SOCIAL = auto()  # Social well-being indicators
    ENVIRONMENTAL = auto()  # Environmental sustainability
    ECONOMIC = auto()  # Economic performance
    CULTURAL = auto()  # Cultural preservation/development
    POLITICAL = auto()  # Democratic participation
    TECHNOLOGICAL = auto()  # Innovation and technological capacity


class MeasurementApproach(Enum):
    """Approaches for measuring criteria in SFM."""

    QUANTITATIVE = auto()  # Numerical measurement
    QUALITATIVE = auto()  # Descriptive assessment
    MIXED = auto()  # Combined quantitative and qualitative
    ORDINAL = auto()  # Ranked ordering
    BINARY = auto()  # Yes/no or present/absent


class CorrelationScale(Enum):
    """Standardized correlation scale for SFM (-3 to +3)."""

    STRONGLY_NEGATIVE = auto()  # -3: Strong negative correlation
    MODERATELY_NEGATIVE = auto()  # -2: Moderate negative correlation
    WEAKLY_NEGATIVE = auto()  # -1: Weak negative correlation
    NEUTRAL = auto()  # 0: No correlation or neutral
    WEAKLY_POSITIVE = auto()  # +1: Weak positive correlation
    MODERATELY_POSITIVE = auto()  # +2: Moderate positive correlation
    STRONGLY_POSITIVE = auto()  # +3: Strong positive correlation


class CriteriaPriority(Enum):
    """Priority classification for SFM criteria per Hayden's framework."""

    PRIMARY = auto()  # Life process enhancement criteria
    SECONDARY = auto()  # Efficiency and instrumental criteria
    TERTIARY = auto()  # Supporting or contextual criteria


class StatisticalMethod(Enum):
    """Statistical methods for SFM analysis."""

    DESCRIPTIVE_STATISTICS = auto()
    CORRELATION_ANALYSIS = auto()
    REGRESSION_ANALYSIS = auto()
    TIME_SERIES_ANALYSIS = auto()
    FACTOR_ANALYSIS = auto()
    CLUSTER_ANALYSIS = auto()
    NETWORK_ANALYSIS = auto()
    PANEL_DATA_ANALYSIS = auto()


class MatrixOperationType(Enum):
    """Types of matrix operations."""

    CELL_AGGREGATION = auto()  # Combining cell values
    MATRIX_MULTIPLICATION = auto()  # Mathematical matrix operations
    CORRELATION_ANALYSIS = auto()  # Finding correlations
    SENSITIVITY_ANALYSIS = auto()  # Parameter sensitivity
    OPTIMIZATION = auto()  # Finding optimal configurations
    COMPARISON = auto()  # Comparing different matrices
    TRANSFORMATION = auto()  # Converting matrix formats
    VALIDATION = auto()  # Checking matrix consistency


class MatrixConstructionStage(Enum):
    """Stages in matrix construction process."""

    INITIALIZATION = auto()  # Initial setup and planning
    INSTITUTION_MAPPING = auto()  # Identifying institutions
    CRITERIA_DEVELOPMENT = auto()  # Developing evaluation criteria
    DATA_POPULATION = auto()  # Populating matrix cells
    VALIDATION = auto()  # Validating matrix content
    ANALYSIS = auto()  # Analyzing completed matrix
    REFINEMENT = auto()  # Refining based on feedback


# ───────────────────────────────────────────────
# STAKEHOLDER AND ENGAGEMENT ENUMS
# ───────────────────────────────────────────────


class DigraphAnalysisType(Enum):
    """Types of digraph analysis methods."""

    DEPENDENCY_ANALYSIS = auto()
    PATH_ANALYSIS = auto()
    CENTRALITY_ANALYSIS = auto()
    FLOW_ANALYSIS = auto()
    LOOP_DETECTION = auto()
    REACHABILITY_ANALYSIS = auto()
    STRUCTURAL_ANALYSIS = auto()
    INFLUENCE_ANALYSIS = auto()


class NetworkMetricType(Enum):
    """Types of network metrics for digraph analysis."""

    BETWEENNESS_CENTRALITY = auto()
    CLOSENESS_CENTRALITY = auto()
    EIGENVECTOR_CENTRALITY = auto()
    PAGE_RANK = auto()
    CLUSTERING_COEFFICIENT = auto()
    DEGREE_CENTRALITY = auto()
    AUTHORITY_SCORE = auto()
    HUB_SCORE = auto()


class DigraphNodeType(Enum):
    """Types of nodes in digraph analysis."""

    SOURCE = auto()  # Node with only outgoing dependencies
    SINK = auto()  # Node with only incoming dependencies
    INTERMEDIATE = auto()  # Node with both incoming and outgoing
    ISOLATED = auto()  # Node with no dependencies
    CRITICAL = auto()  # Node whose removal breaks system coherence


class AnalyticalMethod(Enum):
    """Analytical methods used in SFM framework."""

    MATRIX_ANALYSIS = auto()  # Social Fabric Matrix analysis
    NETWORK_ANALYSIS = auto()  # Network and graph analysis
    SYSTEMS_ANALYSIS = auto()  # Systems thinking approaches
    INSTITUTIONAL_ANALYSIS = auto()  # Institutional economics analysis
    STAKEHOLDER_ANALYSIS = auto()  # Stakeholder mapping and analysis
    VALUE_ANALYSIS = auto()  # Value identification and analysis
    SCENARIO_ANALYSIS = auto()  # Scenario planning and analysis


class ValidationMethod(Enum):
    """Methods for validating knowledge claims."""

    PEER_REVIEW = auto()  # Expert peer review
    EMPIRICAL_TESTING = auto()  # Testing with data and evidence
    PRACTICAL_APPLICATION = auto()  # Testing through practical use
    STAKEHOLDER_VALIDATION = auto()  # Validation by stakeholders
    LOGICAL_ANALYSIS = auto()  # Logical consistency checking


class IndicatorType(Enum):
    """Types of social indicators."""

    PERFORMANCE_INDICATOR = auto()
    OUTCOME_INDICATOR = auto()
    IMPACT_INDICATOR = auto()
    PROCESS_INDICATOR = auto()
    STRUCTURAL_INDICATOR = auto()
    CONTEXTUAL_INDICATOR = auto()
    COMPOSITE_INDICATOR = auto()
    DASHBOARD_INDICATOR = auto()

