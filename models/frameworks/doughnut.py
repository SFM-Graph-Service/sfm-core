"""Doughnut framework criteria factory for SFM."""

from __future__ import annotations

import uuid
from typing import List

from models.matrix_components import SFMCriteria
from models.enums.analysis import CriteriaPriority, CriteriaType, IndicatorType, MeasurementApproach
from models.enums.values import SocialValueDimension

_DOUGHNUT_NAMESPACE = uuid.UUID("243f4c95-8fd4-4832-9f39-a130f6ebecf6")

_SOCIAL_BOUNDARIES = [
    "food",
    "health",
    "education",
    "income & work",
    "peace & justice",
    "political voice",
    "social equity",
    "gender equality",
    "housing",
    "networks",
    "energy",
    "water",
]

_ECOLOGICAL_BOUNDARIES = [
    "climate change",
    "ocean acidification",
    "chemical pollution",
    "nitrogen & phosphorus loading",
    "freshwater withdrawals",
    "land-system change",
    "biodiversity loss",
    "air pollution",
    "ozone depletion",
]


def _criterion_id(name: str) -> uuid.UUID:
    return uuid.uuid5(_DOUGHNUT_NAMESPACE, name)


def _build_social_criterion(name: str) -> SFMCriteria:
    return SFMCriteria(
        id=_criterion_id(f"social:{name}"),
        label=f"Doughnut social foundation: {name}",
        description=f"Minimum social foundation for {name}",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.MIXED,
        priority=CriteriaPriority.PRIMARY,
        normative_justification="Social foundation (Raworth 2017)",
        data_requirements=["boundary indicator reading"],
        meta={
            "framework": "doughnut",
            "boundary_group": "social",
            "boundary_name": name,
            "polarity": "shortfall",
            "social_value_dimension": SocialValueDimension.COMMUNITY_CONTINUITY.name,
            "indicator_type": IndicatorType.DASHBOARD_INDICATOR.name,
            "is_criterion": "true",
        },
    )


def _build_ecological_criterion(name: str) -> SFMCriteria:
    return SFMCriteria(
        id=_criterion_id(f"ecological:{name}"),
        label=f"Doughnut ecological ceiling: {name}",
        description=f"Maximum ecological pressure for {name}",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.MIXED,
        priority=CriteriaPriority.PRIMARY,
        normative_justification="Ecological ceiling (Raworth 2017)",
        data_requirements=["boundary indicator reading"],
        meta={
            "framework": "doughnut",
            "boundary_group": "ecological",
            "boundary_name": name,
            "polarity": "overshoot",
            "social_value_dimension": SocialValueDimension.ENVIRONMENTAL_INTEGRATION.name,
            "indicator_type": IndicatorType.DASHBOARD_INDICATOR.name,
            "is_criterion": "true",
        },
    )


def build_doughnut_criteria() -> List[SFMCriteria]:
    """Build the 21 Doughnut criteria nodes (12 social + 9 ecological)."""
    criteria = [_build_social_criterion(name) for name in _SOCIAL_BOUNDARIES]
    criteria.extend(_build_ecological_criterion(name) for name in _ECOLOGICAL_BOUNDARIES)
    return criteria
