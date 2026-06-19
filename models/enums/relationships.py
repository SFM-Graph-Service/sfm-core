"""
Relationship enumerations for the Social Fabric Matrix (SFM) framework.

Covers relationship kinds, cross-impact types, conflict types,
and conflict resolution methods.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "RelationshipKind",
    "CrossImpactType",
    "ConflictType",
    "ConflictResolutionMethod",
]

class RelationshipKind(Enum):
    """
        Taxonomy of relationship types in Social Fabric Matrix systems.

        Defines the various ways actors, institutions, resources, and processes can be
        related to each other in Hayden's institutional analysis framework. This taxonomy
        enables detailed mapping of institutional dependencies, resource flows, power
        relationships, and system dynamics essential for SFM analysis.

        ## Theoretical Foundation

        Relationship analysis in SFM recognizes that socio-economic systems are
    fundamentally
        structured by relationships between actors, institutions, and resources. Hayden's
        framework emphasizes how these relationships create patterns of coordination,
        dependency, and power that shape economic outcomes and social welfare.

        ## Core Relationship Categories

        **Governance Relationships**: Authority, regulation, and institutional control
        **Resource Flow Relationships**: Economic exchanges and resource movements
        **Knowledge Relationships**: Information transfer and learning processes
        **Social Relationships**: Collaboration, coordination, and mutual support
        **Influence Relationships**: Power dynamics and behavioral modification

        ## Usage Examples

        ### Governance and Authority Relationships
        ```python
        # Government regulatory authority
        epa = Actor(label="EPA", sector="Government")
        chemical_company = Actor(label="Chemical Manufacturer", sector="Industry")

        regulatory_rel = Relationship(
            source_id=epa.id,
            target_id=chemical_company.id,
            kind=RelationshipKind.REGULATES,
            description="Environmental compliance oversight"
        )

        # Policy implementation
        city_government = Actor(label="City Government", sector="Public")
        zoning_policy = Policy(label="Zoning Regulations", authority="City")

        enacts_rel = Relationship(
            source_id=city_government.id,
            target_id=zoning_policy.id,
            kind=RelationshipKind.ENACTS,
            description="Local zoning law creation"
        )
        ```

        ### Economic and Resource Flow Relationships
        ```python
        # Supply chain relationships
        supplier = Actor(label="Raw Material Supplier", sector="Industry")
        manufacturer = Actor(label="Manufacturer", sector="Industry")

        supply_rel = Relationship(
            source_id=supplier.id,
            target_id=manufacturer.id,
            kind=RelationshipKind.SUPPLIES,
            description="Raw material provision"
        )

        # Financial relationships
        bank = Actor(label="Development Bank", sector="Financial")
        startup = Actor(label="Green Tech Startup", sector="Technology")

        funding_rel = Relationship(
            source_id=bank.id,
            target_id=startup.id,
            kind=RelationshipKind.FUNDS,
            description="Venture capital investment"
        )

        # Resource transformation
        solar_panel = Resource(label="Solar Panel", rtype=ResourceType.PRODUCED)
        electricity = Resource(label="Electrical Energy", rtype=ResourceType.RENEWABLE)

        conversion_rel = Relationship(
            source_id=solar_panel.id,
            target_id=electricity.id,
            kind=RelationshipKind.CONVERTS,
            description="Solar energy conversion"
        )
        ```

        ### Knowledge and Information Relationships
        ```python
        # Research and education
        university = Actor(label="State University", sector="Education")
        students = Actor(label="Graduate Students", sector="Education")

        education_rel = Relationship(
            source_id=university.id,
            target_id=students.id,
            kind=RelationshipKind.EDUCATES,
            description="Graduate degree programs"
        )

        # Information flow
        weather_service = Actor(label="National Weather Service", sector="Government")
        farmers = Actor(label="Agricultural Producers", sector="Agriculture")

        info_rel = Relationship(
            source_id=weather_service.id,
            target_id=farmers.id,
            kind=RelationshipKind.INFORMS,
            description="Weather forecast provision"
        )
        ```

        ### Social and Collaborative Relationships
        ```python
        # Multi-stakeholder collaboration
        ngo = Actor(label="Environmental NGO", sector="Non-profit")
        industry_group = Actor(label="Industry Association", sector="Private")

        collab_rel = Relationship(
            source_id=ngo.id,
            target_id=industry_group.id,
            kind=RelationshipKind.COLLABORATES_WITH,
            description="Sustainability initiative partnership"
        )

        # Advocacy relationships
        consumer_group = Actor(label="Consumer Advocacy Group", sector="Non-profit")
        renewable_energy = Policy(label="Renewable Energy Policy", authority="State")

        advocacy_rel = Relationship(
            source_id=consumer_group.id,
            target_id=renewable_energy.id,
            kind=RelationshipKind.ADVOCATES_FOR,
            description="Policy support campaign"
        )
        ```

        ## Complex Relationship Networks

        ### Multi-Actor Policy Networks
        ```python
        # Create network of relationships around policy issue
        federal_agency = Actor(label="Federal Environmental Agency")
        state_agency = Actor(label="State Environmental Department")
        local_government = Actor(label="City Council")
        industry = Actor(label="Manufacturing Industry")
        citizens = Actor(label="Local Citizens")

        # Hierarchical governance relationships
        mandate_rel = Relationship(
            source_id=federal_agency.id,
            target_id=state_agency.id,
            kind=RelationshipKind.MANDATES
        )

        delegate_rel = Relationship(
            source_id=state_agency.id,
            target_id=local_government.id,
            kind=RelationshipKind.DELEGATES
        )

        # Regulatory relationships
        regulate_rel = Relationship(
            source_id=local_government.id,
            target_id=industry.id,
            kind=RelationshipKind.REGULATES
        )

        # Accountability relationships
        account_rel = Relationship(
            source_id=local_government.id,
            target_id=citizens.id,
            kind=RelationshipKind.ACCOUNTABLE_TO
        )
        ```

        ## Relationship Direction and Symmetry

        Most relationships in SFM are **directional**, indicating flow or influence from
        source to target:

        - **GOVERNS**: Authority flows from government to governed entity
        - **SUPPLIES**: Resources flow from supplier to recipient
        - **INFLUENCES**: Impact flows from influencer to influenced

        Some relationships can be **bidirectional** or **symmetric**:

        - **COLLABORATES_WITH**: Mutual cooperation
        - **EXCHANGES_WITH**: Mutual exchange
        - **COMPETES_WITH**: Mutual rivalry

        ## Integration with Flow Analysis

        Relationships often involve specific flows that can be tracked:

        ```python
        # Relationship with associated flows
        payment_flow = Flow(
            label="Service Payment",
            nature=FlowNature.FINANCIAL,
            flow_type=FlowType.FINANCIAL
        )

        service_rel = Relationship(
            source_id=client.id,
            target_id=service_provider.id,
            kind=RelationshipKind.PAYS,
            flows=[payment_flow.id]  # Link specific flows to relationship
        )
        ```

        ## Hayden-Specific Institutional Relationships

        The taxonomy includes relationships particularly relevant to Hayden's analysis:

        - **REINFORCES/UNDERMINES**: Feedback relationships for institutional stability
        - **TRANSFORMS**: Fundamental institutional change relationships
        - **ENABLES/CONSTRAINS**: Capacity and limitation relationships
        - **LEGITIMIZES**: Authority and acceptance relationships

        ## Validation and Compatibility

        RelationshipKind works with validation systems to ensure logical consistency:

        ```python
        # Valid government-to-institution relationship
        governs_rel = Relationship(
            source_id=government_actor.id,
            target_id=regulated_institution.id,
            kind=RelationshipKind.GOVERNS  # Appropriate for this actor-institution pairing
        )

        # Validation will check compatibility of relationship type with actor types
        ```

        ## References

        - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 7:
      Institutional Relationships
        - Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
        - Commons, J.R. (1924). "Legal Foundations of Capitalism", Chapter 5:
      The Institutional Economics of Legal Rights
        - Mitchell, W.C. (1937). "The Backward Art of Spending Money", Chapter 3:
      Institutional Analysis
    """

    # Governance and Authority Relationships
    GOVERNS = auto()  # Authority over another entity
    REGULATES = auto()  # Creates or enforces rules for
    AUTHORIZES = auto()  # Grants permission to
    MANDATES = auto()  # Makes actions compulsory
    ENFORCES = auto()  # Ensures compliance with rules
    DELEGATES = auto()  # Transfers authority to
    REPRESENTS = auto()  # Acts on behalf of
    MONITORS = auto()  # Observes and assesses
    ACCOUNTABLE_TO = auto()  # Must answer to
    LICENSES = auto()  # Formally permits activity
    CERTIFIES = auto()  # Validates compliance or quality
    SANCTIONS = auto()  # Penalizes for non-compliance
    REINFORCES = auto()  # Positive feedback relationship
    UNDERMINES = auto()  # Negative feedback relationship
    AFFECTS = auto()  # Base Feedback relationship
    ENACTS = auto()  # Creates or modifies laws, policies, or regulations

    # Resource Flow Relationships
    FUNDS = auto()  # Provides money to
    PAYS = auto()  # Exchanges money for goods/services
    ALLOCATES = auto()  # Distributes resources to
    TRANSFERS = auto()  # Moves resources without transformation
    EXTRACTS = auto()  # Removes resources from
    CONSUMES = auto()  # Uses up resources from
    PRODUCES = auto()  # Creates outputs for
    DISTRIBUTES = auto()  # Disseminates to multiple targets
    STORES = auto()  # Holds resources for
    CONVERTS = auto()  # Transforms one resource to another
    RECYCLES = auto()  # Reprocesses for reuse

    # Economic and Market Relationships
    BUYS_FROM = auto()  # Purchases goods/services
    SELLS_TO = auto()  # Provides goods/services for payment
    COMPETES_WITH = auto()  # Rivals for resources or markets
    SUPPLIES = auto()  # Provides inputs to
    EMPLOYS = auto()  # Hires for labor
    CONTRACTS_WITH = auto()  # Formal agreement for exchange
    INVESTS_IN = auto()  # Commits resources for future return
    INSURES = auto()  # Provides risk protection for
    SUBSIDIZES = auto()  # Provides financial support to
    TAXES = auto()  # Collects mandatory payment from
    RENTS_TO = auto()  # Provides temporary use rights
    OWNS = auto()  # Has property rights over
    EXCHANGES_WITH = auto()  # Actor-to-actor transfer

    # Knowledge and Information Relationships
    INFORMS = auto()  # Provides information to
    ADVISES = auto()  # Gives guidance to
    EDUCATES = auto()  # Transfers knowledge to
    RESEARCHES = auto()  # Investigates for
    INNOVATES_FOR = auto()  # Creates new solutions for
    DOCUMENTS = auto()  # Records information about
    ANALYZES = auto()  # Examines and interprets
    FORECASTS = auto()  # Predicts outcomes for
    COMMUNICATES_WITH = auto()  # Exchanges information with
    MEASURES = auto()  # Quantifies attributes of
    CALCULATES = auto()  # Computes values related to

    # Social and Collaborative Relationships
    COLLABORATES_WITH = auto()  # Works jointly with
    SERVES = auto()  # Provides services to
    SUPPORTS = auto()  # Helps or assists
    PARTICIPATES_IN = auto()  # Takes part in
    ALLIES_WITH = auto()  # Forms strategic partnership with
    COORDINATES_WITH = auto()  # Aligns activities with
    FACILITATES = auto()  # Makes easier or enables
    MEDIATES = auto()  # Resolves conflicts between
    ADVOCATES_FOR = auto()  # Publicly supports
    ORGANIZES = auto()  # Arranges or structures
    CONVENES = auto()  # Brings together

    # Influence and Impact Relationships
    INFLUENCES = auto()  # Affects decisions or behavior of
    CONSTRAINS = auto()  # Limits actions of
    ENABLES = auto()  # Makes possible actions of
    INCENTIVIZES = auto()  # Motivates specific behaviors
    DISCOURAGES = auto()  # Deters specific behaviors
    SHAPES = auto()  # Molds or forms
    STRENGTHENS = auto()  # Increases capacity of
    WEAKENS = auto()  # Diminishes capacity of
    DISRUPTS = auto()  # Causes discontinuity in
    STABILIZES = auto()  # Maintains equilibrium of
    TRANSFORMS = auto()  # Fundamentally changes

    # Process and Operational Relationships
    IMPLEMENTS = auto()  # Puts into practice
    OPERATES = auto()  # Runs or manages
    MAINTAINS = auto()  # Keeps in working order
    TESTS = auto()  # Evaluates performance of
    INSTALLS = auto()  # Sets up for use
    TRANSPORTS = auto()  # Moves from one location to another
    INTEGRATES = auto()  # Combines into system
    OPTIMIZES = auto()  # Improves efficiency of
    AUTOMATES = auto()  # Makes self-operating
    REPAIRS = auto()  # Fixes or restores
    SOLVES = auto()  # Addresses problems or challenges
    USES = auto()  # Actor/process employs a resource or technology

    # Structural and Containment Relationships
    CONTAINS = auto()  # Has as a component
    BELONGS_TO = auto()  # Is a member of
    CONNECTS = auto()  # Links physically or logically
    COMPOSED_OF = auto()  # Consists of
    CATEGORIZES = auto()  # Places in classification
    AGGREGATES = auto()  # Combines into a whole
    SEPARATES = auto()  # Divides or keeps apart
    HOSTS = auto()  # Provides environment for
    ATTACHES_TO = auto()  # Joins or fixes to
    EMBEDS_WITHIN = auto()  # Incorporates deeply into
    ENCOMPASSES = auto()  # Includes completely
    LOCATED_IN = auto()  # Spatial anchoring

    # Temporal and Sequential Relationships
    PRECEDES = auto()  # Comes before
    FOLLOWS = auto()  # Comes after
    TRIGGERS = auto()  # Initiates or causes
    SYNCHRONIZES_WITH = auto()  # Coordinates timing with
    DELAYS = auto()  # Postpones or slows
    ACCELERATES = auto()  # Speeds up
    SCHEDULES = auto()  # Sets timing for
    ITERATES = auto()  # Repeats process with
    SUPERSEDES = auto()  # Replaces or makes obsolete
    RENEWS = auto()  # Extends or refreshes
    TERMINATES = auto()  # Ends relationship with
    OCCURS_DURING = auto()  # Temporal anchoring
    ENABLES_FUTURE = auto()
    CONSTRAINS_FUTURE = auto()

    # Environmental and Ecological Relationships
    SUSTAINS = auto()  # Maintains viability of
    POLLUTES = auto()  # Degrades quality of
    CONSERVES = auto()  # Uses carefully to prevent depletion
    RESTORES = auto()  # Returns to previous condition
    ADAPTS_TO = auto()  # Changes in response to
    MITIGATES = auto()  # Reduces negative impact on
    DEPENDS_ON = auto()  # Requires for functioning
    COEXISTS_WITH = auto()  # Lives alongside without harm
    HARVESTS = auto()  # Collects resources from
    PROCESSES = auto()  # Treats or handles materials from
    CULTIVATES = auto()  # Grows or nurtures

    # Development and Change Relationships
    DEVELOPS = auto()  # Creates growth or maturity in
    EXPANDS = auto()  # Increases size or scope of
    CONTRACTS = auto()  # Decreases size or scope of
    REDESIGNS = auto()  # Changes structure or function of
    EVOLVES_WITH = auto()  # Changes in mutual response with
    EMERGES_FROM = auto()  # Comes into existence from
    TRANSITIONS_TO = auto()  # Changes state to become
    CONSTRUCTS = auto()  # Builds or creates
    DEMOLISHES = auto()  # Tears down or removes
    UPGRADES = auto()  # Improves quality or function of
    CUSTOMIZES = auto()  # Modifies to suit specific needs
    INHIBITS = auto()  # Limiting or constraining relationship

    # Belief and Value Relationships
    VALUES = auto()  # Holds in high regard
    TRUSTS = auto()  # Has confidence in
    PERCEIVES = auto()  # Forms mental impression of
    INTERPRETS = auto()  # Ascribes meaning to
    CHALLENGES = auto()  # Questions validity of
    ACCEPTS = auto()  # Receives as valid or appropriate
    REJECTS = auto()  # Refuses to accept
    NORMALIZES = auto()  # Makes conform to standard
    PRIORITIZES = auto()  # Gives precedence to
    ALIGNS_WITH = auto()  # Positions in agreement with
    DISAGREES_WITH = auto()  # Holds contrary views to
    BELIEVES_IN = auto()  # Holds a conviction about

    # Hayden-specific relationships
    LEGITIMIZES = auto()
    DELEGITIMIZES = auto()
    CEREMONIALLY_REINFORCES = auto()
    INSTRUMENTALLY_ADAPTS = auto()
    CREATES_PATH_DEPENDENCY = auto()
    ENABLES_INNOVATION = auto()
    DISTRIBUTES_POWER = auto()
    CONCENTRATES_POWER = auto()
    BENEFITS_FROM = auto()  # Gains advantage or support from

    @property
    def ceremonial_tendency(self) -> float:
        """
        Returns a value from 0.0-1.0 indicating ceremonial vs instrumental nature.

        Based on Hayden's SFM framework distinction between ceremonial and instrumental
        behaviors. 0.0 = purely instrumental (problem-solving, adaptive),
        1.0 = purely ceremonial (status-preserving, traditional).

        Returns:
            float: Ceremonial tendency score from 0.0 (instrumental) to 1.0 (ceremonial)
        """
        # Mapping of relationship types to their ceremonial tendency
        ceremonial_tendencies = {
            # Highly ceremonial relationships (0.8-1.0) - status, tradition, hierarchy
            RelationshipKind.CEREMONIALLY_REINFORCES: 0.95,
            RelationshipKind.LEGITIMIZES: 0.85,
            RelationshipKind.GOVERNS: 0.75,
            RelationshipKind.AUTHORIZES: 0.75,
            RelationshipKind.MANDATES: 0.75,
            RelationshipKind.REPRESENTS: 0.70,
            RelationshipKind.SANCTIONS: 0.80,
            RelationshipKind.VALUES: 0.85,
            RelationshipKind.TRUSTS: 0.70,
            RelationshipKind.BELIEVES_IN: 0.80,
            RelationshipKind.NORMALIZES: 0.75,
            RelationshipKind.PRIORITIZES: 0.70,
            # Moderately ceremonial (0.5-0.8) - mixed institutional/adaptive
            RelationshipKind.REGULATES: 0.65,
            RelationshipKind.ENFORCES: 0.65,
            RelationshipKind.DELEGATES: 0.60,
            RelationshipKind.MONITORS: 0.55,
            RelationshipKind.LICENSES: 0.60,
            RelationshipKind.CERTIFIES: 0.55,
            RelationshipKind.REINFORCES: 0.60,
            RelationshipKind.ALIGNS_WITH: 0.55,
            RelationshipKind.ACCEPTS: 0.55,
            RelationshipKind.INTERPRETS: 0.50,
            # Moderately instrumental (0.2-0.5) - some adaptation with structure
            RelationshipKind.ADVISES: 0.45,
            RelationshipKind.EDUCATES: 0.40,
            RelationshipKind.INFORMS: 0.35,
            RelationshipKind.ANALYZES: 0.30,
            RelationshipKind.MEASURES: 0.25,
            RelationshipKind.CALCULATES: 0.20,
            RelationshipKind.RESEARCHES: 0.30,
            RelationshipKind.INNOVATES_FOR: 0.25,
            RelationshipKind.DEVELOPS: 0.35,
            RelationshipKind.EVOLVES_WITH: 0.40,
            RelationshipKind.ADAPTS_TO: 0.35,
            # Highly instrumental (0.0-0.2) - problem-solving, adaptive, productive
            RelationshipKind.INSTRUMENTALLY_ADAPTS: 0.05,
            RelationshipKind.PRODUCES: 0.15,
            RelationshipKind.PROCESSES: 0.10,
            RelationshipKind.CONVERTS: 0.10,
            RelationshipKind.CONSTRUCTS: 0.15,
            RelationshipKind.OPERATES: 0.15,
            RelationshipKind.MAINTAINS: 0.20,
            RelationshipKind.REPAIRS: 0.15,
            RelationshipKind.UPGRADES: 0.20,
            RelationshipKind.CUSTOMIZES: 0.15,
            RelationshipKind.ENABLES_INNOVATION: 0.10,
            RelationshipKind.SOLVES: 0.05,
            # Economic relationships - moderately instrumental (0.3-0.6)
            RelationshipKind.EXCHANGES_WITH: 0.40,
            RelationshipKind.BUYS_FROM: 0.35,
            RelationshipKind.SELLS_TO: 0.35,
            RelationshipKind.INVESTS_IN: 0.45,
            RelationshipKind.EMPLOYS: 0.50,
            RelationshipKind.CONTRACTS_WITH: 0.45,
            RelationshipKind.FUNDS: 0.40,
            RelationshipKind.PAYS: 0.30,
            RelationshipKind.ALLOCATES: 0.45,
            RelationshipKind.DISTRIBUTES: 0.40,
        }

        # Return the mapped value, or default to moderate (0.5) if not explicitly mapped
        return ceremonial_tendencies.get(self, 0.5)


class CrossImpactType(Enum):
    """Types of cross-impacts between matrix cells."""

    DIRECT = auto()  # Direct causal relationship
    INDIRECT = auto()  # Indirect through intermediary
    SYSTEMIC = auto()  # System-wide effects
    FEEDBACK = auto()  # Through feedback loops
    STRUCTURAL = auto()  # Through structural relationships


class ConflictType(Enum):
    """Types of institutional conflicts in SFM."""

    VALUE_CONFLICT = auto()  # Conflicting values
    RESOURCE_CONFLICT = auto()  # Resource competition
    AUTHORITY_CONFLICT = auto()  # Authority disputes
    PROCEDURAL_CONFLICT = auto()  # Process disagreements
    TEMPORAL_CONFLICT = auto()  # Timing conflicts
    CEREMONIAL_INSTRUMENTAL = auto()  # Ceremonial vs instrumental conflict


class ConflictResolutionMethod(Enum):
    """Methods for resolving conflicts."""

    COLLABORATIVE_PROBLEM_SOLVING = auto()
    MEDIATION = auto()
    ARBITRATION = auto()
    NEGOTIATION = auto()
    FACILITATED_DIALOGUE = auto()
    RESTORATIVE_JUSTICE = auto()
    TRADITIONAL_ADJUDICATION = auto()
    MULTI_STAKEHOLDER_PROCESSES = auto()
    COMMUNITY_CONFERENCING = auto()
    PEACE_CIRCLES = auto()

