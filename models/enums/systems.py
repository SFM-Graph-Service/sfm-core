"""
System-level enumerations for the Social Fabric Matrix (SFM) framework.

Covers change types, behavior patterns, feedback mechanisms, system properties,
system archetypes, evolutionary stages, and related dynamics.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
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
]

class ChangeType(Enum):
    """
      Classification of institutional and technological change patterns.

      Defines different modes of change that can occur in socio-economic systems,
      following institutional economics and innovation theory. Essential for understanding
      how institutions, technologies, and social systems evolve over time within
      Hayden's Social Fabric Matrix framework.

      ## Theoretical Background

      Change analysis in SFM recognizes that socio-economic systems undergo various
      types of transformation processes. Understanding change patterns is crucial for
      policy design, institutional development, and system intervention strategies.
      Hayden's framework emphasizes how different change types require different
      analytical approaches and policy responses.

      ## Core Change Types

      **EVOLUTIONARY**: Gradual, adaptive change through small variations
      **REVOLUTIONARY**: Rapid, disruptive transformation of system structure
      **CYCLICAL**: Recurring patterns of change following predictable cycles
      **INCREMENTAL**: Small, continuous improvements within existing frameworks

      ## Usage Examples

      ### Evolutionary Change Processes
      ```python
      # Gradual institutional adaptation
      market_evolution = ChangeProcess(
          label="Financial Market Evolution",
          change_type=ChangeType.EVOLUTIONARY,
          description="Gradual adaptation of financial regulations to new technologies",
          success_probability=0.75
      )

      # Technology adoption process
      digital_transformation = ChangeProcess(
          label="Digital Government Services",
          change_type=ChangeType.EVOLUTIONARY,
          description="Gradual digitization of government service delivery",
          change_agents=[government_agency.id, technology_vendor.id]
      )
      ```

      ### Revolutionary Change Processes
      ```python
      # Disruptive institutional change
      regulatory_overhaul = ChangeProcess(
          label="Financial Sector Deregulation",
          change_type=ChangeType.REVOLUTIONARY,
          description="Fundamental restructuring of financial regulatory framework",
          success_probability=0.40,
          resistance_factors=[incumbent_institutions.id, regulatory_culture.id]
      )

      # Technological disruption
      ai_automation = ChangeProcess(
          label="AI-Driven Process Automation",
          change_type=ChangeType.REVOLUTIONARY,
          description="Fundamental transformation of work processes through AI",
          change_trajectory=[current_state, transition_state, future_state]
      )
      ```

      ### Cyclical Change Processes
      ```python
      # Economic cycles
      business_cycle = ChangeProcess(
          label="Economic Business Cycle",
          change_type=ChangeType.CYCLICAL,
          description="Recurring patterns of economic expansion and contraction",
          change_trajectory=[expansion, peak, contraction, trough]
      )

      # Political cycles
      electoral_cycle = ChangeProcess(
          label="Electoral Policy Cycle",
          change_type=ChangeType.CYCLICAL,
          description="Policy changes following electoral patterns",
          success_probability=0.85
      )
      ```

      ### Incremental Change Processes
      ```python
      # Continuous improvement
      efficiency_improvement = ChangeProcess(
          label="Operational Efficiency Enhancement",
          change_type=ChangeType.INCREMENTAL,
          description="Ongoing small improvements to operational processes",
          success_probability=0.90,
          change_agents=[management_team.id, operations_staff.id]
      )

      # Policy fine-tuning
      regulation_adjustment = ChangeProcess(
          label="Regulatory Parameter Adjustment",
          change_type=ChangeType.INCREMENTAL,
          description="Minor adjustments to regulatory requirements",
          resistance_factors=[]  # Minimal resistance for small changes
      )
      ```

      ## Change Process Integration

      ChangeType integrates with other SFM components:

      ### With Institutions and Actors
      ```python
      # Institutional change with actor involvement
      institution = Institution(
          label="Environmental Protection Agency",
          layer=InstitutionLayer.ORGANIZATION
      )

      change_agent = Actor(
          label="Environmental Activist Group",
          sector="Non-profit"
      )

      institutional_reform = ChangeProcess(
          label="EPA Mandate Expansion",
          change_type=ChangeType.EVOLUTIONARY,
          change_agents=[change_agent.id],
          description="Gradual expansion of environmental protection authority"
      )

      # Relationship showing change influence
      influences_rel = Relationship(
          source_id=change_agent.id,
          target_id=institution.id,
          kind=RelationshipKind.INFLUENCES,
          description="Advocacy influence on institutional change"
      )
      ```

      ### With Policy Instruments
      ```python
      # Policy change with instrument modification
      old_policy = PolicyInstrument(
          label="Traditional Command-Control Regulation",
          instrument_type=PolicyInstrumentType.REGULATORY
      )

      new_policy = PolicyInstrument(
          label="Market-Based Environmental Policy",
          instrument_type=PolicyInstrumentType.ECONOMIC
      )

      policy_transition = ChangeProcess(
          label="Regulatory Instrument Shift",
          change_type=ChangeType.EVOLUTIONARY,
          description="Transition from command-control to market-based regulation"
      )

      # Relationships showing policy evolution
      transforms_rel = Relationship(
          source_id=policy_transition.id,
          target_id=old_policy.id,
          kind=RelationshipKind.TRANSFORMS
      )
      ```

      ## Change Analysis Patterns

      Different change types require different analytical approaches:

      - **Evolutionary**: Focus on adaptation mechanisms and gradual feedback
      - **Revolutionary**: Analyze disruption sources and transformation triggers
      - **Cyclical**: Identify cycle patterns and timing factors
      - **Incremental**: Track cumulative effects and optimization processes

      ## Integration with Temporal Dynamics

      ChangeType works with temporal analysis:

      ```python
      # Change process with temporal tracking
      institutional_change = ChangeProcess(
          label="Healthcare System Reform",
          change_type=ChangeType.EVOLUTIONARY,
          change_trajectory=[
              TimeSlice(label="Pre-reform"),
              TimeSlice(label="Implementation"),
              TimeSlice(label="Post-reform")
          ],
          temporal_dynamics=TemporalDynamics(
              # Detailed time-based analysis
          )
      )
      ```

      ## References

      - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 9:
    Institutional Change
      - North, D.C. (1990). "Institutions, Institutional Change and Economic Performance"
      - Arthur, W.B. (1994). "Increasing Returns and Path Dependence in the Economy"
      - Pierson, P. (2000). "Increasing Returns, Path Dependence, and the Study
    of Politics"
      - Commons, J.R. (1924). "Legal Foundations of Capitalism", Chapter 7: Going Concerns
    """

    EVOLUTIONARY = auto()  # Gradual, adaptive change
    REVOLUTIONARY = auto()  # Rapid, disruptive transformation
    CYCLICAL = auto()  # Recurring patterns of change
    INCREMENTAL = auto()  # Small, continuous improvements


class BehaviorPatternType(Enum):
    """
    Classification of behavioral patterns in Social Fabric Matrix analysis.

    Categorizes recurring patterns of behavior that actors exhibit in
    socio-economic systems, particularly relevant to Hayden's analysis of
    ceremonial versus instrumental behavior patterns that shape institutional
    dynamics and economic outcomes.

    ## Theoretical Background

    Hayden's institutional analysis distinguishes between different behavioral
    patterns that either support or hinder adaptive institutional development.
    Understanding these patterns is crucial for predicting institutional change
    and designing effective policy interventions.

    ## Core Behavior Patterns

    - **HABITUAL**: Routine, unconscious behaviors following established patterns
    - **STRATEGIC**: Deliberate, goal-oriented behaviors with explicit objectives
    - **ADAPTIVE**: Flexible, responsive behaviors that adjust to changing conditions
    - **RESISTANT**: Change-resistant, conservative behaviors that maintain status quo

    ## Usage Examples

    ```python
    # Habitual behavior pattern
    routine_compliance = BehaviorPattern(
        label="Standard Regulatory Compliance",
        pattern_type=BehaviorPatternType.HABITUAL,
        description="Routine following of established regulatory procedures"
    )

    # Strategic behavior pattern
    market_positioning = BehaviorPattern(
        label="Competitive Market Strategy",
        pattern_type=BehaviorPatternType.STRATEGIC,
        description="Deliberate positioning for market advantage"
    )

    # Adaptive behavior pattern
    crisis_response = BehaviorPattern(
        label="Crisis Adaptation Response",
        pattern_type=BehaviorPatternType.ADAPTIVE,
        description="Flexible adjustment to emergency conditions"
    )
    ```
    """

    HABITUAL = auto()  # Routine, unconscious behaviors
    STRATEGIC = auto()  # Deliberate, goal-oriented behaviors
    ADAPTIVE = auto()  # Flexible, responsive behaviors
    RESISTANT = auto()  # Change-resistant, conservative behaviors


class FeedbackPolarity(Enum):
    """
    Classification of feedback loop polarity in system dynamics.

    Defines whether a feedback loop reinforces or balances system behavior.
    Essential for understanding system stability, growth patterns, and
    intervention points in Social Fabric Matrix analysis.

    ## Usage Examples

    ```python
    # Reinforcing feedback (amplifies change)
    growth_feedback = Feedback(
        label="Economic Growth Feedback",
        polarity=FeedbackPolarity.REINFORCING,
        description="Investment leads to growth, which attracts more investment"
    )

    # Balancing feedback (stabilizes system)
    regulatory_feedback = Feedback(
        label="Market Regulation Feedback",
        polarity=FeedbackPolarity.BALANCING,
        description="Market excess triggers regulatory response"
    )
    ```
    """

    REINFORCING = auto()  # Amplifies or accelerates change (positive feedback)
    BALANCING = auto()  # Stabilizes or counteracts change (negative feedback)


class FeedbackType(Enum):
    """
    Classification of feedback types by directional impact.

    Categorizes feedback effects based on their directional influence
    on system behavior.
    """

    POSITIVE = auto()  # Enhancing, amplifying feedback
    NEGATIVE = auto()  # Dampening, correcting feedback
    NEUTRAL = auto()  # Balanced or minimal feedback


class TemporalFunctionType(Enum):
    """
    Classification of temporal function types for modeling change over time.

    Defines mathematical functions used to model how values change
    over time in temporal dynamics analysis.
    """

    LINEAR = auto()  # Constant rate of change
    EXPONENTIAL = auto()  # Accelerating or decelerating change
    LOGISTIC = auto()  # S-curve growth with limits
    CYCLICAL = auto()  # Periodic, repeating patterns
    STEP = auto()  # Discrete jumps or threshold changes
    RANDOM = auto()  # Stochastic or unpredictable changes


class SystemPropertyType(Enum):
    """
    Classification of system-level property types in SFM analysis.

    Defines different categories of system-level metrics and properties
    that can be measured and tracked in Social Fabric Matrix systems.
    Essential for evaluating overall system performance, health, and
    development outcomes in institutional analysis.

    ## Usage Examples

    ```python
    # Structural system property
    network_density = SystemProperty(
        label="Institutional Network Density",
        property_type=SystemPropertyType.STRUCTURAL,
        value=0.65,
        unit="density_ratio",
        description="Measure of interconnectedness in institutional network"
    )

    # Performance system property
    policy_effectiveness = SystemProperty(
        label="Policy Implementation Effectiveness",
        property_type=SystemPropertyType.PERFORMANCE,
        value=78.5,
        unit="percentage",
        description="Overall effectiveness of policy implementation"
    )

    # Sustainability system property
    resource_efficiency = SystemProperty(
        label="Resource Use Efficiency",
        property_type=SystemPropertyType.SUSTAINABILITY,
        value=0.82,
        unit="efficiency_index",
        description="Long-term sustainability of resource utilization"
    )
    ```
    """

    STRUCTURAL = auto()  # Network structure properties
    DYNAMIC = auto()  # Temporal behavior properties
    PERFORMANCE = auto()  # Efficiency and effectiveness metrics
    RESILIENCE = auto()  # Adaptive capacity and robustness
    EQUITY = auto()  # Distributional fairness metrics
    SUSTAINABILITY = auto()  # Long-term viability indicators


class SystemArchetype(Enum):
    """Common system dynamics archetypes in SFM analysis."""

    LIMITS_TO_GROWTH = auto()  # Growth hitting constraints
    SHIFTING_BURDEN = auto()  # Quick fixes vs fundamental solutions
    TRAGEDY_OF_COMMONS = auto()  # Shared resource depletion
    SUCCESS_TO_SUCCESSFUL = auto()  # Winner takes all dynamics
    FIXES_THAT_FAIL = auto()  # Short-term fixes create long-term problems
    GROWTH_AND_UNDERINVESTMENT = auto()  # Growth limited by capacity constraints


class SystemLevel(Enum):
    """Levels of system analysis."""

    INDIVIDUAL = auto()  # Individual actors
    ORGANIZATIONAL = auto()  # Single organizations
    SECTORAL = auto()  # Industry/sector level
    LOCAL = auto()  # Local community level
    REGIONAL = auto()  # Regional level
    NATIONAL = auto()  # National level
    INTERNATIONAL = auto()  # Cross-national level
    GLOBAL = auto()  # Global system level


# ───────────────────────────────────────────────
# ADDITIONAL ENUMS FOR NEW SFM FRAMEWORK COMPONENTS
# ───────────────────────────────────────────────


class EvolutionaryStage(Enum):
    """Stages of institutional evolution."""

    EMERGENCE = auto()  # Institution is emerging
    ESTABLISHMENT = auto()  # Institution is being established
    MATURATION = auto()  # Institution is maturing
    ADAPTATION = auto()  # Institution is adapting to change
    DECLINE = auto()  # Institution is declining
    TRANSFORMATION = auto()  # Institution is being transformed
    REPLACEMENT = auto()  # Institution is being replaced


class DependencyStrength(Enum):
    """Strength of dependencies between matrix cells."""

    NONE = auto()  # No dependency
    WEAK = auto()  # Weak dependency
    MODERATE = auto()  # Moderate dependency
    STRONG = auto()  # Strong dependency
    CRITICAL = auto()  # Critical dependency


class SequenceStage(Enum):
    """Stages in temporal sequences."""

    INITIATION = auto()
    DEVELOPMENT = auto()
    IMPLEMENTATION = auto()
    MONITORING = auto()
    EVALUATION = auto()
    ADJUSTMENT = auto()
    COMPLETION = auto()
    CONTINUATION = auto()


class ProblemSolvingStage(Enum):
    """Stages in Hayden's problem-solving sequence."""

    PROBLEM_IDENTIFICATION = auto()  # Problem identification
    SYSTEM_BOUNDARY_DETERMINATION = auto()  # System boundary determination
    INSTITUTION_IDENTIFICATION = auto()  # Institution identification
    CRITERIA_DEVELOPMENT = auto()  # Criteria development
    MATRIX_CONSTRUCTION = auto()  # Matrix construction
    POLICY_EVALUATION = auto()  # Policy evaluation
    IMPLEMENTATION_PLANNING = auto()  # Implementation planning
    MONITORING_EVALUATION = auto()  # Monitoring and evaluation
    # Legacy names for compatibility
    IDENTIFICATION = auto()  # Problem identification (legacy)
    STATUS_QUO_ANALYSIS = auto()  # Current situation analysis (legacy)
    ALTERNATIVE_GENERATION = auto()  # Develop alternatives (legacy)
    CONSEQUENCE_ANALYSIS = auto()  # Evaluate consequences (legacy)
    SELECTION = auto()  # Choose solution (legacy)
    IMPLEMENTATION = auto()  # Implement solution (legacy)
    EVALUATION = auto()  # Assess results (legacy)

