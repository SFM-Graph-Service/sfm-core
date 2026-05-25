"""
Unit tests for cultural_analysis module.
"""

import pytest
import uuid
from models.cultural_analysis import (
    CeremonialInstrumentalClassification,
    ValueSystem,
    SocialBelief,
    CulturalAttitude,
)
from models.sfm_enums import CeremonialInstrumentalType, ValueSystemType


class TestCeremonialInstrumentalClassification:
    def test_instantiation(self):
        cic = CeremonialInstrumentalClassification(label="Test Classification")
        assert cic.label == "Test Classification"

    def test_with_type(self):
        cic = CeremonialInstrumentalClassification(
            label="Ceremonial", classification=CeremonialInstrumentalType.CEREMONIAL
        )
        assert cic.classification == CeremonialInstrumentalType.CEREMONIAL

    def test_with_rationale(self):
        cic = CeremonialInstrumentalClassification(
            label="Reasoned", classification_rationale="Past-binding"
        )
        assert cic.classification_rationale == "Past-binding"

    def test_complete(self):
        cic = CeremonialInstrumentalClassification(
            label="Complete",
            classification=CeremonialInstrumentalType.INSTRUMENTAL,
            classification_rationale="Problem-solving",
        )
        assert cic.label == "Complete"


class TestValueSystem:
    def test_instantiation(self):
        vs = ValueSystem(label="Test Values")
        assert vs.label == "Test Values"

    def test_with_type(self):
        vs = ValueSystem(
            label="Cultural", system_type=ValueSystemType.CULTURAL_DOMINANT
        )
        assert vs.system_type == ValueSystemType.CULTURAL_DOMINANT

    def test_with_core_values(self):
        vs = ValueSystem(label="Valued", core_values=["Equity", "sustainability"])
        assert vs.core_values == ["Equity", "sustainability"]

    def test_complete(self):
        vs = ValueSystem(
            label="Complete",
            system_type=ValueSystemType.INSTITUTIONAL_EMBEDDED,
            core_values=["Justice", "fairness"],
        )
        assert vs.label == "Complete"


class TestSocialBelief:
    def test_instantiation(self):
        sb = SocialBelief(label="Test Belief")
        assert sb.label == "Test Belief"

    def test_with_type(self):
        sb = SocialBelief(label="Factual", belief_type="factual")
        assert sb.belief_type == "factual"

    def test_with_strength(self):
        sb = SocialBelief(label="Strong", belief_strength=0.85)
        assert sb.belief_strength == 0.85

    def test_complete(self):
        sb = SocialBelief(
            label="Complete", belief_type="normative", belief_strength=0.9
        )
        assert sb.label == "Complete"


class TestCulturalAttitude:
    def test_instantiation(self):
        ca = CulturalAttitude(label="Test Attitude")
        assert ca.label == "Test Attitude"

    def test_with_strength(self):
        ca = CulturalAttitude(label="Strong", attitude_strength=0.8)
        assert ca.attitude_strength == 0.8

    def test_with_tendency(self):
        ca = CulturalAttitude(label="Behavioral", behavioral_tendency="proactive")
        assert ca.behavioral_tendency == "proactive"

    def test_complete(self):
        ca = CulturalAttitude(
            label="Complete",
            attitude_strength=0.75,
            behavioral_tendency="Conservation practices",
        )
        assert ca.label == "Complete"
