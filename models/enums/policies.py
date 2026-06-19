"""
Policy-related enumerations for the Social Fabric Matrix (SFM) framework.

Covers policy instrument types, policy types, policy scope,
implementation complexity, policy effectiveness, and evaluation methods.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "PolicyInstrumentType",
    "PolicyType",
    "PolicyScope",
    "ImplementationComplexity",
    "PolicyEffectiveness",
    "EvaluationMethod",
]

class PolicyInstrumentType(Enum):
    """
      Classification of policy instrument types for implementation analysis.

      Categorizes the different mechanisms through which policies can be implemented
      and enforced in socio-economic systems, based on institutional economics and
      public policy analysis frameworks. Essential for understanding how policy goals
      are translated into specific implementation strategies.

      ## Theoretical Background

      Policy instrument classification recognizes that governments and institutions have
      multiple tools available for achieving policy objectives. The choice of instrument
      affects implementation costs, compliance mechanisms, distributional impacts, and
      political feasibility. This taxonomy enables systematic analysis of policy design
      choices within SFM frameworks.

      ## Core Instrument Types

      **REGULATORY**: Command-and-control mechanisms using legal authority
      **ECONOMIC**: Market-based mechanisms using financial incentives
      **VOLUNTARY**: Cooperative mechanisms relying on voluntary compliance
      **INFORMATION**: Education and disclosure mechanisms using information provision

      ## Usage Examples

      ### Regulatory Instruments
      ```python
      # Environmental regulation
      emission_standard = PolicyInstrument(
          label="Vehicle Emission Standards",
          instrument_type=PolicyInstrumentType.REGULATORY,
          target_behavior="Reduce vehicle emissions",
          compliance_mechanism="Mandatory testing and certification"
      )

      # Zoning regulation
      zoning_law = PolicyInstrument(
          label="Industrial Zoning Restrictions",
          instrument_type=PolicyInstrumentType.REGULATORY,
          target_behavior="Control industrial development location",
          compliance_mechanism="Building permit requirements"
      )
      ```

      ### Economic Instruments
      ```python
      # Market-based environmental policy
      carbon_tax = PolicyInstrument(
          label="Carbon Tax",
          instrument_type=PolicyInstrumentType.ECONOMIC,
          target_behavior="Reduce greenhouse gas emissions",
          compliance_mechanism="Tax collection system"
      )

      # Subsidy program
      renewable_subsidy = PolicyInstrument(
          label="Solar Panel Installation Subsidy",
          instrument_type=PolicyInstrumentType.ECONOMIC,
          target_behavior="Increase renewable energy adoption",
          compliance_mechanism="Rebate application process"
      )
      ```

      ### Voluntary Instruments
      ```python
      # Industry self-regulation
      sustainability_pledge = PolicyInstrument(
          label="Corporate Sustainability Commitment",
          instrument_type=PolicyInstrumentType.VOLUNTARY,
          target_behavior="Adopt sustainable business practices",
          compliance_mechanism="Self-reporting and peer review"
      )

      # Public-private partnership
      energy_efficiency_agreement = PolicyInstrument(
          label="Voluntary Energy Efficiency Agreement",
          instrument_type=PolicyInstrumentType.VOLUNTARY,
          target_behavior="Improve industrial energy efficiency",
          compliance_mechanism="Performance monitoring and recognition"
      )
      ```

      ### Information Instruments
      ```python
      # Public education campaign
      conservation_campaign = PolicyInstrument(
          label="Water Conservation Education Program",
          instrument_type=PolicyInstrumentType.INFORMATION,
          target_behavior="Reduce household water consumption",
          compliance_mechanism="Public awareness and social norms"
      )

      # Disclosure requirement
      environmental_reporting = PolicyInstrument(
          label="Corporate Environmental Disclosure",
          instrument_type=PolicyInstrumentType.INFORMATION,
          target_behavior="Increase transparency in environmental performance",
          compliance_mechanism="Mandatory reporting standards"
      )
      ```

      ## Policy Instrument Networks

      Complex policy problems often require multiple instrument types:

      ```python
      # Climate policy instrument mix
      regulatory_component = PolicyInstrument(
          label="Renewable Energy Standard",
          instrument_type=PolicyInstrumentType.REGULATORY
      )

      economic_component = PolicyInstrument(
          label="Carbon Pricing System",
          instrument_type=PolicyInstrumentType.ECONOMIC
      )

      information_component = PolicyInstrument(
          label="Energy Efficiency Labeling",
          instrument_type=PolicyInstrumentType.INFORMATION
      )

      # Relationships showing instrument coordination
      coordinates_rel = Relationship(
          source_id=regulatory_component.id,
          target_id=economic_component.id,
          kind=RelationshipKind.COORDINATES_WITH
      )
      ```

      ## Integration with SFM Analysis

      PolicyInstrumentType enables:
      - **Implementation Analysis**: Understanding how policies are operationalized
      - **Effectiveness Assessment**: Evaluating instrument performance
      - **Design Optimization**: Selecting appropriate instruments for policy goals
      - **Institutional Mapping**: Connecting instruments to implementing organizations

      ## References

      - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 8:
    Policy Instruments
      - Hood, C. (1983). "The Tools of Government"
      - Salamon, L.M. (2002). "The Tools of Government: A Guide to the New Governance"
      - Vedung, E. (1998). "Policy Instruments: Typologies and Theories"
    """

    REGULATORY = auto()  # Rules, regulations, legal requirements
    ECONOMIC = auto()  # Taxes, subsidies, market-based mechanisms
    VOLUNTARY = auto()  # Voluntary agreements, codes of conduct
    INFORMATION = auto()  # Education, disclosure, awareness campaigns


class PolicyType(Enum):
    """Types of policy interventions."""

    REGULATORY = auto()  # Rules and regulations
    INCENTIVE_BASED = auto()  # Economic incentives and disincentives
    CAPACITY_BUILDING = auto()  # Building institutional capacity
    COORDINATION = auto()  # Improving coordination mechanisms
    STRUCTURAL_REFORM = auto()  # Changing institutional structures
    INFORMATION_PROVISION = auto()  # Providing information and transparency


class PolicyScope(Enum):
    """Scope of policy interventions."""

    INSTITUTION_SPECIFIC = auto()  # Specific to one institution
    SECTOR_WIDE = auto()  # Entire sector or domain
    SYSTEM_WIDE = auto()  # Entire system
    CROSS_SYSTEM = auto()  # Multiple systems


class ImplementationComplexity(Enum):
    """Complexity levels for policy implementation."""

    LOW = auto()  # Simple implementation
    MEDIUM = auto()  # Moderate complexity
    HIGH = auto()  # High complexity


class PolicyEffectiveness(Enum):
    """Levels of policy effectiveness."""

    HIGHLY_EFFECTIVE = auto()
    MODERATELY_EFFECTIVE = auto()
    SOMEWHAT_EFFECTIVE = auto()
    INEFFECTIVE = auto()


class EvaluationMethod(Enum):
    """Methods for policy evaluation."""

    COST_BENEFIT_ANALYSIS = auto()
    MULTI_CRITERIA_ANALYSIS = auto()
    STAKEHOLDER_ASSESSMENT = auto()
    IMPACT_EVALUATION = auto()
    COMPARATIVE_ANALYSIS = auto()

