"""
Stakeholder-related enumerations for the Social Fabric Matrix (SFM) framework.

Covers power resources, stakeholder types, participation levels,
decision-making approaches/types, and communication channels.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "PowerResourceType",
    "StakeholderType",
    "ParticipationLevel",
    "DecisionMakingApproach",
    "DecisionMakingType",
    "CommunicationChannel",
]

class PowerResourceType(Enum):
    """
    Classification of power resource types in Social Fabric Matrix analysis.

    Based on Hayden's analysis of power dynamics within institutional systems,
    representing different forms of power and control that actors can wield
    to influence outcomes and maintain or change institutional arrangements.
    """

    INSTITUTIONAL_AUTHORITY = auto()  # Formal authority roles and positions
    ECONOMIC_CONTROL = auto()  # Control over financial resources and economic flows
    INFORMATION_ACCESS = auto()  # Access to and control of information and knowledge
    NETWORK_POSITION = auto()  # Strategic position within networks
    CULTURAL_LEGITIMACY = auto()  # Cultural authority and legitimacy sources


class StakeholderType(Enum):
    """Types of stakeholders in SFM analysis."""

    GOVERNMENT_AGENCY = auto()
    REGULATORY_BODY = auto()
    ELECTED_OFFICIAL = auto()
    COMMUNITY_GROUP = auto()
    CIVIL_SOCIETY_ORGANIZATION = auto()
    NONPROFIT_ORGANIZATION = auto()
    BUSINESS_ASSOCIATION = auto()
    PRIVATE_COMPANY = auto()
    LABOR_UNION = auto()
    ACADEMIC_INSTITUTION = auto()
    RESEARCH_ORGANIZATION = auto()
    MEDIA_OUTLET = auto()
    INTERNATIONAL_ORGANIZATION = auto()
    INDIGENOUS_GROUP = auto()
    RELIGIOUS_ORGANIZATION = auto()
    PROFESSIONAL_ASSOCIATION = auto()
    ADVOCACY_GROUP = auto()
    THINK_TANK = auto()
    INDIVIDUAL_CITIZEN = auto()
    EXPERT_CONSULTANT = auto()


class ParticipationLevel(Enum):
    """Levels of stakeholder participation."""

    INFORMED = auto()  # Receives information only
    CONSULTED = auto()  # Provides input when asked
    INVOLVED = auto()  # Participates in analysis and option development
    COLLABORATIVE = auto()  # Partners in decision-making
    EMPOWERED = auto()  # Has decision-making authority


class DecisionMakingApproach(Enum):
    """Approaches to democratic decision-making."""

    CONSENSUS_BUILDING = auto()
    MAJORITY_VOTING = auto()
    DELIBERATIVE_POLLING = auto()
    COLLABORATIVE_GOVERNANCE = auto()
    PARTICIPATORY_BUDGETING = auto()
    CITIZENS_JURY = auto()
    STAKEHOLDER_DIALOGUE = auto()
    EXPERT_PANELS = auto()
    REPRESENTATIVE_DEMOCRACY = auto()
    DIRECT_DEMOCRACY = auto()


class DecisionMakingType(Enum):
    """Types of decision-making processes in institutions."""

    AUTOCRATIC = auto()  # Single authority decides
    DEMOCRATIC = auto()  # Majority vote/consensus
    TECHNOCRATIC = auto()  # Expert-based decisions
    CONSULTATIVE = auto()  # Input from stakeholders
    DELIBERATIVE = auto()  # Extended deliberation process
    MARKET = auto()  # Market-based allocation


class CommunicationChannel(Enum):
    """Channels for stakeholder communication."""

    FACE_TO_FACE_MEETINGS = auto()
    VIDEO_CONFERENCING = auto()
    PHONE_CALLS = auto()
    EMAIL = auto()
    WRITTEN_CORRESPONDENCE = auto()
    ONLINE_PLATFORMS = auto()
    SOCIAL_MEDIA = auto()
    WEBSITES = auto()
    NEWSLETTERS = auto()
    REPORTS = auto()
    SURVEYS = auto()
    FOCUS_GROUPS = auto()
    WORKSHOPS = auto()
    CONFERENCES = auto()
    PUBLIC_HEARINGS = auto()
    TOWN_HALLS = auto()
    COMMUNITY_MEETINGS = auto()
    MOBILE_APPLICATIONS = auto()
    TEXT_MESSAGING = auto()
    TRADITIONAL_MEDIA = auto()

