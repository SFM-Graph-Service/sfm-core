"""
Technology-related enumerations for the Social Fabric Matrix (SFM) framework.

Covers tool/skill/technology types, technology readiness and maturity levels,
skill levels, knowledge types, learning methods, and information systems.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "ToolSkillTechnologyType",
    "TechnologyReadinessLevel",
    "TechnologyMaturityLevel",
    "SkillLevel",
    "KnowledgeType",
    "LearningMethod",
    "InformationSystem",
]

class ToolSkillTechnologyType(Enum):
    """
    Classification of tool-skill-technology complex components.

    Represents Hayden's concept of the tool-skill-technology complex as integrated
    systems where physical tools, human skills, and technological knowledge
    combine to enable instrumental problem-solving capabilities.
    """

    PHYSICAL_TOOL = auto()  # Material instruments and devices
    COGNITIVE_SKILL = auto()  # Mental capabilities and knowledge
    TECHNOLOGY_SYSTEM = auto()  # Integrated technological arrangements
    TECHNIQUE = auto()  # Specific methods and procedures
    METHODOLOGY = auto()  # Systematic approaches and frameworks
    CRAFT_KNOWLEDGE = auto()  # Embodied practical knowledge
    DIGITAL_CAPABILITY = auto()  # Digital tools and skills
    ANALYTICAL_METHOD = auto()  # Formal analytical techniques
    PROBLEM_SOLVING_APPROACH = auto()  # General problem-solving strategies
    INNOVATION_CAPACITY = auto()  # Capability to create new solutions


class TechnologyReadinessLevel(Enum):
    """
    NASA Technology Readiness Levels adapted for Social Fabric Matrix analysis.

    Provides a systematic metric for assessing the maturity of technologies
    within socio-economic systems, following NASA's TRL framework but adapted
    for Hayden's tool-skill-technology complex analysis.

    Based on:
    - NASA Technology Readiness Assessment (TRA) Guidance
    - Hayden's analysis of technological systems in SFM framework
    - Institutional economics perspectives on technology adoption
    """

    BASIC_PRINCIPLES = 1  # Basic principles observed and reported
    TECHNOLOGY_CONCEPT = 2  # Technology concept and/or application formulated
    EXPERIMENTAL_PROOF = 3  # Experimental proof of concept
    LABORATORY_VALIDATION = 4  # Component validation in laboratory
    RELEVANT_ENVIRONMENT = 5  # Component validation in relevant env
    DEMONSTRATION = 6  # System demonstration in relevant env
    PROTOTYPE_DEMONSTRATION = 7  # Prototype demo in operational env
    SYSTEM_COMPLETE = 8  # System completed and qualified
    ACTUAL_SYSTEM = 9  # System proven through successful missions


class TechnologyMaturityLevel(Enum):
    """Technology maturity levels."""

    EMERGING = auto()  # Early development stage
    DEVELOPING = auto()  # Under development
    MATURE = auto()  # Fully developed and tested
    ESTABLISHED = auto()  # Widely adopted
    DECLINING = auto()  # Being phased out


class SkillLevel(Enum):
    """Skill proficiency levels."""

    BASIC = auto()  # Basic proficiency
    INTERMEDIATE = auto()  # Intermediate proficiency
    ADVANCED = auto()  # Advanced proficiency
    EXPERT = auto()  # Expert level


class KnowledgeType(Enum):
    """Types of knowledge in instrumentalist inquiry."""

    EMPIRICAL_KNOWLEDGE = auto()  # Based on observation and experience
    THEORETICAL_KNOWLEDGE = auto()  # Based on theory and logic
    PRACTICAL_KNOWLEDGE = auto()  # Based on practice and application
    TACIT_KNOWLEDGE = auto()  # Implicit, hard to articulate
    EXPLICIT_KNOWLEDGE = auto()  # Clearly articulated and documented


class LearningMethod(Enum):
    """Methods for institutional learning."""

    EXPERIENTIAL_LEARNING = auto()
    ACTION_LEARNING = auto()
    CASE_STUDY_ANALYSIS = auto()
    BEST_PRACTICE_SHARING = auto()
    PEER_LEARNING = auto()
    COMMUNITIES_OF_PRACTICE = auto()
    FORMAL_TRAINING = auto()
    MENTORING_COACHING = auto()
    REFLECTION_SESSIONS = auto()
    AFTER_ACTION_REVIEWS = auto()
    LESSONS_LEARNED_SESSIONS = auto()
    KNOWLEDGE_SHARING_WORKSHOPS = auto()
    CROSS_FUNCTIONAL_TEAMS = auto()
    SIMULATION_EXERCISES = auto()
    PILOT_PROJECTS = auto()
    RESEARCH_COLLABORATION = auto()
    EXTERNAL_PARTNERSHIPS = auto()
    CONFERENCE_PARTICIPATION = auto()
    PUBLICATION_WRITING = auto()
    SYSTEMATIC_EXPERIMENTATION = auto()


class InformationSystem(Enum):
    """Types of information systems."""

    KNOWLEDGE_MANAGEMENT_SYSTEM = auto()
    DOCUMENT_MANAGEMENT_SYSTEM = auto()
    LEARNING_MANAGEMENT_SYSTEM = auto()
    COLLABORATION_PLATFORM = auto()
    DATA_WAREHOUSE = auto()
    DECISION_SUPPORT_SYSTEM = auto()
    EXPERT_SYSTEM = auto()
    CONTENT_MANAGEMENT_SYSTEM = auto()
    WORKFLOW_MANAGEMENT_SYSTEM = auto()
    PROJECT_MANAGEMENT_SYSTEM = auto()
    CUSTOMER_RELATIONSHIP_MANAGEMENT = auto()
    ENTERPRISE_RESOURCE_PLANNING = auto()
    BUSINESS_INTELLIGENCE_SYSTEM = auto()
    GEOGRAPHIC_INFORMATION_SYSTEM = auto()
    COMMUNICATION_SYSTEM = auto()
    MONITORING_SYSTEM = auto()
    EVALUATION_SYSTEM = auto()
    REPORTING_SYSTEM = auto()
    ANALYTICS_PLATFORM = auto()
    SOCIAL_NETWORK_PLATFORM = auto()


# ───────────────────────────────────────────────
# ERROR HANDLING AND VALIDATION
# ───────────────────────────────────────────────

