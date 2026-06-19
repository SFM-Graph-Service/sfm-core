"""
Social assessment enumerations for the Social Fabric Matrix (SFM) framework.

Covers social fabric indicator types and social cost types.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "SocialFabricIndicatorType",
    "SocialCostType",
]

class SocialFabricIndicatorType(Enum):
    """Types of social fabric health indicators."""

    INSTITUTIONAL_COHERENCE = auto()  # How well institutions work together
    SOCIAL_INTEGRATION = auto()  # Level of social cohesion
    ADAPTIVE_CAPACITY = auto()  # Ability to adapt to change
    LEGITIMACY_STRENGTH = auto()  # Institutional legitimacy
    PARTICIPATION_QUALITY = auto()  # Quality of democratic participation
    CONFLICT_RESOLUTION = auto()  # Effectiveness of conflict resolution
    KNOWLEDGE_INTEGRATION = auto()  # Integration of different knowledge systems
    VALUE_ALIGNMENT = auto()  # Alignment between values and institutions


class SocialCostType(Enum):
    """Types of social costs per Kapp's theory integrated with SFM."""

    ENVIRONMENTAL_DEGRADATION = auto()  # Environmental damage costs
    SOCIAL_DISRUPTION = auto()  # Community/social disruption costs
    HEALTH_IMPACTS = auto()  # Public health costs
    INSTITUTIONAL_BREAKDOWN = auto()  # Costs of institutional failure
    CULTURAL_EROSION = auto()  # Loss of cultural values/practices
    INEQUALITY_AMPLIFICATION = auto()  # Costs of increasing inequality
    DEMOCRATIC_DEFICIT = auto()  # Costs of reduced democratic participation
    FUTURE_GENERATION_BURDEN = auto()  # Intergenerational cost transfer

