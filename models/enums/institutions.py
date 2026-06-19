"""
Institution-related enumerations for the Social Fabric Matrix (SFM) framework.

Covers institutional layers, governance mechanisms, enforcement types,
transaction costs, coordination, normative frameworks, and boundaries.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
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
]

class InstitutionLayer(Enum):
    """
        Hayden's three-layer institutional framework plus extended institutional forms.

        Based on F. Gregory Hayden's analysis of institutional structure, this enum
    represents
        the different layers at which institutions operate within socio-economic systems.
        Hayden's framework distinguishes between formal constitutional rules, organizational
        structures, and informal cultural norms, providing a taxonomy for institutional
        analysis in SFM applications.

        ## Theoretical Foundation

        Hayden's institutional layering concept recognizes that social coordination occurs
        through multiple, interconnected institutional levels. This hierarchical structure
        helps analysts understand how formal rules, organizational structures, and cultural
        norms interact to shape economic behavior and social outcomes.

        ## Core Institutional Layers (Hayden's Framework)

        **FORMAL_RULE**: Constitutional and legal frameworks
        - Examples: Constitutions, statutes, property law, regulatory frameworks
        - Function: Establishes formal constraints and rights
        - SFM Role: Foundation for institutional matrix analysis

        **ORGANIZATION**: Structured collective entities
        - Examples: Firms, government agencies, NGOs, labor unions, cooperatives
        - Function: Implements and operationalizes formal rules
        - SFM Role: Key actors in resource flows and value creation

        **INFORMAL_NORM**: Cultural practices and social expectations
        - Examples: Customs, habits, social expectations, professional ethics
        - Function: Guides behavior through social coordination mechanisms
        - SFM Role: Influences how formal institutions actually function

        ## Usage Examples

        ### Basic Institution Classification
        ```python
        # Formal legal institution
        environmental_law = Institution(
            label="Clean Air Act",
            layer=InstitutionLayer.FORMAL_RULE,
            description="Federal environmental regulation"
        )

        # Organizational institution
        epa = Institution(
            label="Environmental Protection Agency",
            layer=InstitutionLayer.ORGANIZATION,
            description="Federal environmental regulatory agency"
        )

        # Informal institutional norm
        recycling_norm = Institution(
            label="Community Recycling Practices",
            layer=InstitutionLayer.INFORMAL_NORM,
            description="Local cultural practices for waste management"
        )
        ```

        ### Institutional Relationship Analysis
        ```python
        # Hierarchical institutional relationships
        constitution = Institution(label="US Constitution",
                                   layer=InstitutionLayer.FORMAL_RULE)
        congress = Institution(label="US Congress", layer=InstitutionLayer.ORGANIZATION)
        political_norms = Institution(label="Democratic Norms",
                                      layer=InstitutionLayer.INFORMAL_NORM)

        # Relationships showing institutional hierarchy
        implements_rel = Relationship(
            source_id=congress.id,
            target_id=constitution.id,
            kind=RelationshipKind.IMPLEMENTS
        )

        guided_by_rel = Relationship(
            source_id=congress.id,
            target_id=political_norms.id,
            kind=RelationshipKind.GUIDED_BY
        )
        ```

        ### Extended Institutional Forms
        ```python
        # Market mechanism as institutional form
        carbon_market = Institution(
            label="Carbon Credit Trading System",
            layer=InstitutionLayer.MARKET_MECHANISM,
            description="Market-based environmental policy instrument"
        )

        # International institutional regime
        paris_accord = Institution(
            label="Paris Climate Agreement",
            layer=InstitutionLayer.INTERNATIONAL_REGIME,
            description="Global climate governance framework"
        )

        # Hybrid public-private institution
        public_private_partnership = Institution(
            label="Infrastructure PPP",
            layer=InstitutionLayer.HYBRID_INSTITUTION,
            description="Mixed governance arrangement for infrastructure"
        )
        ```

        ## Integration with SFM Analysis

        InstitutionLayer enables:
        - **Hierarchical Analysis**: Understanding how different institutional levels
      interact
        - **Change Process Mapping**: Tracking how changes propagate across
      institutional layers
        - **Policy Design**: Identifying appropriate institutional levels for intervention
        - **Governance Assessment**: Evaluating institutional capacity at different layers

        ## Extended Categories

        Beyond Hayden's core three layers, the enum includes additional institutional forms
        relevant for contemporary SFM analysis:

        - **MARKET_MECHANISM**: Price systems, contracts, trading platforms
        - **NETWORK**: Collaborative structures, alliances, partnerships
        - **INTERNATIONAL_REGIME**: Transnational agreements, global governance
        - **HYBRID_INSTITUTION**: Public-private partnerships, mixed governance forms

        ## References

        - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 3:
      Institutional Structure
        - Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
        - North, D.C. (1990). "Institutions, Institutional Change and Economic Performance"
        - Ostrom, E. (2005). "Understanding Institutional Diversity"
    """

    # Existing values
    FORMAL_RULE = auto()  # Constitutions, statutes, property law
    ORGANIZATION = auto()  # Firms, ministries, NGOs, unions
    INFORMAL_NORM = auto()  # Customs, habits, social expectations

    # Additional values
    CULTURAL_VALUE = auto()  # Deep cultural beliefs that underpin institutions
    POLICY_INSTRUMENT = auto()  # Specific implementation tools (taxes, subsidies)
    MARKET_MECHANISM = auto()  # Price systems, contracts, trading platforms
    NETWORK = auto()  # Collaborative structures, alliances, partnerships
    TECHNOLOGICAL_STANDARD = auto()  # Technical specifications and protocols
    PROFESSIONAL_PRACTICE = auto()  # Professional codes, methodologies, best practices
    COMMUNITY_GOVERNANCE = auto()  # Local and community-based governance
    INTERNATIONAL_REGIME = auto()  # Transnational agreements, treaties
    HYBRID_INSTITUTION = auto()  # Public-private partnerships, mixed governance
    KNOWLEDGE_SYSTEM = auto()  # Scientific paradigms, research programs
    PLANNING_FRAMEWORK = auto()  # Strategic planning systems
    REGULATORY_REGIME = auto()  # Enforcement and compliance systems
    TRADITIONAL_AUTHORITY = auto()  # Customary and indigenous governance structures
    EMERGENT_INSTITUTION = auto()  # Newly forming institutional arrangements


class PathDependencyType(Enum):
    """
    Classification of path dependency strength in institutional systems.

    Represents the degree to which institutional arrangements become locked-in
    and resistant to change due to historical patterns, sunk costs, and
    reinforcing mechanisms.
    """

    WEAK = auto()  # Easy to change, low switching costs, flexible arrangements
    MODERATE = auto()  # Some resistance to change, moderate switching costs
    STRONG = auto()  # High resistance to change, significant switching costs
    LOCKED_IN = auto()  # Extremely difficult to change, path dependency dominates


class InstitutionalChangeType(Enum):
    """
    Classification of institutional change mechanisms and patterns.

    Represents different modes and patterns through which institutional
    arrangements evolve, transform, or maintain stability over time.
    """

    INCREMENTAL = auto()  # Gradual, small-scale adjustments
    TRANSFORMATIONAL = auto()  # Significant structural changes
    REVOLUTIONARY = auto()  # Rapid, fundamental system overhaul
    EVOLUTIONARY = auto()  # Organic adaptation over time
    ADAPTIVE = auto()  # Responsive changes to environmental pressures
    CRISIS_DRIVEN = auto()  # Changes triggered by system crises
    INNOVATION_LED = auto()  # Changes driven by technological or social innovation
    REFORM_BASED = auto()  # Planned, policy-driven changes
    EMERGENT = auto()  # Bottom-up, spontaneous changes
    CYCLICAL = auto()  # Recurring patterns of change and stability


class LegitimacySource(Enum):
    """
    Weber's types of authority and legitimacy sources adapted for SFM analysis.

    Based on Max Weber's tripartite classification of authority types,
    extended with additional sources relevant to contemporary institutional
    analysis within Social Fabric Matrix framework.

    References:
    - Weber, M. "Economy and Society" - three pure types of legitimate domination
    - Hayden's analysis of legitimacy in institutional systems
    - Contemporary institutional theory on authority and legitimacy
    """

    TRADITIONAL = auto()  # Custom, precedent, established traditions
    CHARISMATIC = auto()  # Personal qualities - exceptional individual
    LEGAL_RATIONAL = auto()  # Rules, procedures - impersonal order
    EXPERT = auto()  # Technical knowledge and competence
    DEMOCRATIC = auto()  # Popular consent and participation


# ───────────────────────────────────────────────
# SFM MATRIX AND ANALYSIS ENUMS
# ───────────────────────────────────────────────


class InstitutionalScope(Enum):
    """Geographic/social scope of institutional reach."""

    LOCAL = auto()
    REGIONAL = auto()
    NATIONAL = auto()
    INTERNATIONAL = auto()
    GLOBAL = auto()


class GovernanceMechanism(Enum):
    """How institutions exercise governance."""

    HIERARCHICAL = auto()  # Top-down control
    MARKET_BASED = auto()  # Market mechanisms
    NETWORK_BASED = auto()  # Collaborative networks
    COMMUNITY_BASED = auto()  # Community self-governance
    HYBRID = auto()  # Mixed mechanisms


class EnforcementType(Enum):
    """Mechanisms for institutional enforcement."""

    LEGAL = auto()  # Legal sanctions
    SOCIAL = auto()  # Social pressure/norms
    ECONOMIC = auto()  # Economic incentives/penalties
    CULTURAL = auto()  # Cultural expectations
    TECHNICAL = auto()  # Technical constraints
    SELF_ENFORCING = auto()  # Built-in compliance mechanisms


class InstitutionalLevel(Enum):
    """Levels in institutional holarchy."""

    META_CONSTITUTIONAL = auto()  # Constitutional/foundational level
    CONSTITUTIONAL = auto()  # Basic rules and structures
    COLLECTIVE_CHOICE = auto()  # Policy-making level
    OPERATIONAL = auto()  # Day-to-day operations
    LOCAL_PRACTICE = auto()  # Local implementation and practice


class NormativeFramework(Enum):
    """Normative frameworks for evaluating institutions."""

    LIFE_PROCESS_ENHANCEMENT = auto()  # Enhances life processes
    COMMUNITY_CONTINUITY = auto()  # Supports community continuity
    ENVIRONMENTAL_SUSTAINABILITY = auto()  # Environmental stewardship
    DEMOCRATIC_PARTICIPATION = auto()  # Enables democratic participation
    SOCIAL_EQUITY = auto()  # Promotes social equity
    CULTURAL_DEVELOPMENT = auto()  # Supports cultural development
    PROBLEM_SOLVING_EFFECTIVENESS = auto()  # Effective problem solving


class DeontologicalCategory(Enum):
    """Deontic logic categories based on Polanyi and Commons."""

    PERMISSION = auto()  # What is allowed
    OBLIGATION = auto()  # What is required
    PROHIBITION = auto()  # What is forbidden
    PRIVILEGE = auto()  # Special permissions
    DUTY = auto()  # Specific obligations
    LIABILITY = auto()  # Potential negative obligations
    RIGHT = auto()  # Protected permissions
    IMMUNITY = auto()  # Protection from obligations


class CommonsGovernanceType(Enum):
    """Types of commons governance arrangements."""

    COMMUNITY_MANAGED = auto()  # Community self-governance
    GOVERNMENT_MANAGED = auto()  # State management
    PRIVATE_PROPERTY = auto()  # Private ownership
    HYBRID_GOVERNANCE = auto()  # Mixed arrangements
    OPEN_ACCESS = auto()  # No governance (tragedy of commons)


class TransactionCostType(Enum):
    """Types of transaction costs in institutional analysis."""

    SEARCH_INFORMATION = auto()  # Finding relevant information
    BARGAINING_NEGOTIATION = auto()  # Contract negotiation
    MONITORING_ENFORCEMENT = auto()  # Ensuring compliance
    UNCERTAINTY_RISK = auto()  # Risk and uncertainty costs
    COORDINATION = auto()  # Coordination between parties


class CoordinationMechanismType(Enum):
    """Types of coordination mechanisms."""

    PRICE_SYSTEM = auto()  # Market price coordination
    HIERARCHY = auto()  # Organizational hierarchy
    CLAN_CULTURE = auto()  # Cultural/social coordination
    NETWORK = auto()  # Network-based coordination
    HYBRID = auto()  # Mixed mechanisms


class CoordinationScope(Enum):
    """Scope of coordination mechanisms."""

    LOCAL = auto()
    REGIONAL = auto()
    NATIONAL = auto()
    INTERNATIONAL = auto()
    SECTORAL = auto()  # Within specific sectors


class AdjustmentType(Enum):
    """Types of institutional adjustments."""

    ADAPTIVE_ADJUSTMENT = auto()
    CORRECTIVE_ADJUSTMENT = auto()
    STRUCTURAL_ADJUSTMENT = auto()
    FUNCTIONAL_ADJUSTMENT = auto()
    PROCEDURAL_ADJUSTMENT = auto()
    NORMATIVE_ADJUSTMENT = auto()
    TECHNOLOGICAL_ADJUSTMENT = auto()
    ORGANIZATIONAL_ADJUSTMENT = auto()


class AdjustmentTrigger(Enum):
    """What triggers institutional adjustments."""

    PERFORMANCE_DECLINE = auto()  # Poor performance metrics
    EXTERNAL_PRESSURE = auto()  # External forces for change
    INTERNAL_INITIATIVE = auto()  # Internal drive for improvement
    REGULATORY_CHANGE = auto()  # Legal/regulatory requirements
    TECHNOLOGICAL_CHANGE = auto()  # Technology-driven adaptation
    RESOURCE_CONSTRAINT = auto()  # Resource limitations
    STAKEHOLDER_DEMAND = auto()  # Stakeholder pressure
    CRISIS_RESPONSE = auto()  # Response to crisis/emergency


class BoundaryType(Enum):
    """Types of system boundaries in SFM analysis."""

    GEOGRAPHIC = auto()  # Geographic boundaries
    INSTITUTIONAL = auto()  # Institutional boundaries
    TEMPORAL = auto()  # Time boundaries
    SECTORAL = auto()  # Economic sector boundaries
    FUNCTIONAL = auto()  # Functional system boundaries
    ANALYTICAL = auto()  # Analytical convenience boundaries


class SystemBoundaryType(Enum):
    """Types of system boundaries in WSO."""

    PHYSICAL_BOUNDARY = auto()  # Geographic or physical limits
    INSTITUTIONAL_BOUNDARY = auto()  # Organizational limits
    FUNCTIONAL_BOUNDARY = auto()  # Activity-based limits
    TEMPORAL_BOUNDARY = auto()  # Time-based limits
    CONCEPTUAL_BOUNDARY = auto()  # Analytical limits
    PERMEABLE_BOUNDARY = auto()  # Boundary allows some crossing
    RIGID_BOUNDARY = auto()  # Strict boundary enforcement

