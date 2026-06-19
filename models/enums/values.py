"""
Value-related enumerations for the Social Fabric Matrix (SFM) framework.

Covers value categories, social value dimensions, value system types,
value judgment types, and ceremonial/instrumental classifications.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Set

__all__ = [
    "ValueCategory",
    "SocialValueDimension",
    "ValueSystemType",
    "ValueJudgmentType",
    "CeremonialInstrumentalType",
]

class ValueCategory(Enum):
    """
      Categories of value in Hayden's Social Fabric Matrix framework.

      Based on F. Gregory Hayden's institutional analysis, these categories represent
      different dimensions of value creation, distribution, and impact within
      socio-economic systems. Hayden's framework extends beyond market-based value
      measurements to include social, environmental, and institutional dimensions
      essential for policy analysis.

      ## Theoretical Background

      Hayden's SFM approach recognizes that economic systems create multiple types of
      value that cannot be adequately captured by market prices alone. This enum
      implements his multi-dimensional value framework, allowing analysts to track
      social benefits, environmental costs, institutional capacity, and other
      non-market values crucial for policy evaluation.

      ## Usage Examples

      ### Basic Indicator Creation
      ```python
      # Economic indicator (traditional market-based measurement)
      gdp_growth = Indicator(
          label="GDP Growth Rate",
          value_category=ValueCategory.ECONOMIC,
          measurement_unit="percent_annual",
          current_value=2.3
      )

      # Social equity indicator
      income_inequality = Indicator(
          label="Gini Coefficient",
          value_category=ValueCategory.SOCIAL,
          measurement_unit="gini_index",
          current_value=0.45
      )

      # Environmental sustainability indicator
      carbon_footprint = Indicator(
          label="Carbon Emissions per Capita",
          value_category=ValueCategory.ENVIRONMENTAL,
          measurement_unit="tons_co2_per_person",
          current_value=8.2
      )
      ```

      ### Multi-Dimensional Value Analysis
      ```python
      # Complex sustainability indicator spanning multiple value categories
      sustainability_index = Indicator(
          label="Community Sustainability Index",
          value_category=ValueCategory.ENVIRONMENTAL,  # Primary dimension
          measurement_unit="composite_score",
          current_value=68.5
      )
      # Note: Secondary categories can be tracked through metadata or
      # additional indicator relationships
      ```

      ### Policy Impact Measurement
      ```python
      # Institutional capacity indicator for policy evaluation
      governance_quality = Indicator(
          label="Government Effectiveness Score",
          value_category=ValueCategory.INSTITUTIONAL,
          measurement_unit="percentile_rank",
          current_value=85.2
      )

      # Educational outcome indicator
      literacy_rate = Indicator(
          label="Adult Literacy Rate",
          value_category=ValueCategory.EDUCATIONAL,
          measurement_unit="percentage",
          current_value=99.1
      )
      ```

      ## Value Category Guidance

      **Core Hayden Categories** (from original SFM framework):
      - ECONOMIC: Market transactions, monetary flows, financial returns
      - SOCIAL: Distributional equity, social cohesion, community well-being
      - ENVIRONMENTAL: Resource stocks, ecological integrity, sustainability
      - CULTURAL: Norms, beliefs, heritage, knowledge systems
      - INSTITUTIONAL: Governance quality, rule consistency, organizational capacity
      - TECHNOLOGICAL: Knowledge base, production techniques, innovation systems

      **Extended Categories** (for detailed analysis):
      Use when core categories are insufficient for capturing specific value dimensions
      relevant to your SFM analysis context.

      ## Integration with SFM Models

      ValueCategory integrates with:
      - `Indicator`: Primary classification for measurement metrics
      - `ValueSystem`: Hierarchical value structure definition
      - `PolicyInstrument`: Target value areas for policy intervention
      - `ChangeProcess`: Value dimensions affected by institutional change

      ## References

      - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 4: Value Theory
      - Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
      - Tool, M.R. (1977). "A Social Value Theory in Neoinstitutional Economics"
      - Hodgson, G.M. (1988). "Economics and Institutions", Chapter 8: Values and
    Valuation
    """

    # Original categories
    ECONOMIC = auto()  # Market-priced goods, services, financial returns
    SOCIAL = auto()  # Distributional equity, social cohesion, well-being
    ENVIRONMENTAL = auto()  # Resource stocks, ecological integrity
    CULTURAL = auto()  # Norms, beliefs, heritage
    INSTITUTIONAL = auto()  # Governance quality, rule consistency
    TECHNOLOGICAL = auto()  # Knowledge base, production techniques

    # Additional common SFM value categories
    POLITICAL = auto()  # Power distribution, democratic participation, governance
    EDUCATIONAL = auto()  # Learning outcomes, knowledge transfer, skill development
    HEALTH = auto()  # Public health, medical outcomes, wellness indicators
    SECURITY = auto()  # Safety, defense, risk management, stability
    INFRASTRUCTURE = (
        auto()
    )  # Physical systems, utilities, transportation, communication
    LEGAL = auto()  # Legal frameworks, rights, justice, compliance
    ETHICAL = auto()  # Moral considerations, fairness, integrity
    AESTHETIC = auto()  # Beauty, design quality, artistic value
    RECREATIONAL = auto()  # Leisure, entertainment, quality of life
    SPIRITUAL = auto()  # Religious values, meaning, purpose
    DEMOGRAPHIC = auto()  # Population characteristics, migration, age structure
    SPATIAL = auto()  # Geographic distribution, land use, location value
    TEMPORAL = auto()  # Time preferences, sustainability, intergenerational equity
    INFORMATIONAL = auto()  # Data quality, knowledge systems, communication
    PSYCHOLOGICAL = auto()  # Mental health, stress, satisfaction, motivation
    COMMUNITY = auto()  # Social capital, civic engagement, collective action
    RESOURCE = auto()  # Natural resource management, conservation, efficiency
    PERFORMANCE = auto()  # Effectiveness, efficiency, productivity measures
    QUALITY = auto()  # Standards, excellence, reliability
    ACCESSIBILITY = auto()  # Inclusion, barrier removal, universal design
    RESILIENCE = auto()  # Adaptability, recovery capacity, robustness
    INNOVATION = auto()  # Creativity, research, development, change capacity
    EQUITY = auto()  # Fairness, distributive justice, equal opportunity
    TRANSPARENCY = auto()  # Openness, accountability, information access
    PARTICIPATION = auto()  # Stakeholder involvement, democratic engagement
    SUSTAINABILITY = auto()  # Long-term viability, resource preservation
    DIVERSITY = auto()  # Variety, inclusion, representation
    COOPERATION = auto()  # Collaboration, partnership, collective action
    COMPETITIVENESS = auto()  # Market position, comparative advantage
    MOBILITY = auto()  # Movement, transportation, migration
    COMMUNICATION = auto()  # Information flow, dialogue, understanding
    ADAPTATION = auto()  # Flexibility, responsiveness, evolution
    INTEGRATION = auto()  # Coordination, coherence, synergy
    AUTONOMY = auto()  # Independence, self-determination, freedom
    STABILITY = auto()  # Consistency, predictability, equilibrium
    EFFICIENCY = auto()  # Resource optimization, productivity, waste reduction
    EFFECTIVENESS = auto()  # Goal achievement, impact, outcomes
    ACCOUNTABILITY = auto()  # Responsibility, oversight, governance
    LEGITIMACY = auto()  # Acceptance, authority, credibility
    CAPACITY = auto()  # Capability, resources, potential
    CONNECTIVITY = auto()  # Networks, relationships, linkages
    FLEXIBILITY = auto()  # Adaptability, responsiveness, agility
    SCALABILITY = auto()  # Growth potential, expansion capability
    INTEROPERABILITY = auto()  # Compatibility, integration, coordination

    @classmethod
    def get_core_categories(cls) -> Set["ValueCategory"]:
        """Return the six core Hayden framework categories."""
        return {
            cls.ECONOMIC,
            cls.SOCIAL,
            cls.ENVIRONMENTAL,
            cls.CULTURAL,
            cls.INSTITUTIONAL,
            cls.TECHNOLOGICAL,
        }

    @classmethod
    def get_extended_categories(cls) -> Set["ValueCategory"]:
        """Return extended categories beyond core framework."""
        return set(cls) - cls.get_core_categories()


class SocialValueDimension(Enum):
    """Dimensions of social value in Hayden's framework."""

    LIFE_PROCESS_IMPACT = auto()  # Impact on life processes
    COMMUNITY_CONTINUITY = auto()  # Effect on community cohesion
    ENVIRONMENTAL_INTEGRATION = auto()  # Environmental harmony
    CULTURAL_DEVELOPMENT = auto()  # Cultural advancement
    INSTRUMENTAL_EFFICIENCY = auto()  # Problem-solving effectiveness


class ValueSystemType(Enum):
    """Types of value systems in Hayden's framework."""

    CULTURAL_DOMINANT = auto()  # Dominant cultural values
    SUBCULTURE_SPECIFIC = auto()  # Specific to subcultural groups
    INSTITUTIONAL_EMBEDDED = auto()  # Embedded in institutional structures
    EMERGING_ALTERNATIVE = auto()  # New/emerging value systems
    TRADITIONAL_CEREMONIAL = auto()  # Traditional ceremonial values
    INSTRUMENTAL_PROBLEM_SOLVING = auto()  # Problem-solving oriented values


class ValueJudgmentType(Enum):
    """Types of explicit value judgments in SFM policy analysis."""

    DISTRIBUTIONAL = auto()  # Who gets what resources/benefits
    EFFICIENCY = auto()  # Resource allocation efficiency
    SUSTAINABILITY = auto()  # Long-term environmental/social viability
    EQUITY = auto()  # Fairness and justice considerations
    AUTONOMY = auto()  # Self-determination and freedom
    PARTICIPATION = auto()  # Democratic involvement in decisions
    PRECAUTIONARY = auto()  # Risk assessment and prevention


class CeremonialInstrumentalType(Enum):
    """Classification based on Hayden's ceremonial vs instrumental distinction."""

    CEREMONIAL = auto()  # Status quo maintaining, traditional
    INSTRUMENTAL = auto()  # Problem-solving oriented, adaptive
    MIXED = auto()  # Contains both ceremonial and instrumental elements
    TRANSITIONAL = auto()  # Moving between ceremonial and instrumental

