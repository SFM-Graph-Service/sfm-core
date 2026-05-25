"""
Unit tests for technology_integration module.
"""

import pytest
import uuid
from models.technology_integration import ToolSkillTechnologyComplex, EcologicalSystem
from models.sfm_enums import ToolSkillTechnologyType


class TestToolSkillTechnologyComplex:
    def test_instantiation(self):
        tstc = ToolSkillTechnologyComplex(label="Test Complex")
        assert tstc.label == "Test Complex"

    def test_with_technology_type(self):
        tstc = ToolSkillTechnologyComplex(
            label="Physical", technology_type=ToolSkillTechnologyType.PHYSICAL_TOOL
        )
        assert tstc.technology_type == ToolSkillTechnologyType.PHYSICAL_TOOL

    def test_with_integration(self):
        tstc = ToolSkillTechnologyComplex(label="Integrated", integration_level=0.85)
        assert tstc.integration_level == 0.85

    def test_with_capacity(self):
        tstc = ToolSkillTechnologyComplex(
            label="Capable", problem_solving_capacity=0.75
        )
        assert tstc.problem_solving_capacity == 0.75

    def test_complete(self):
        tstc = ToolSkillTechnologyComplex(
            label="Complete",
            technology_type=ToolSkillTechnologyType.PHYSICAL_TOOL,
            integration_level=0.9,
            problem_solving_capacity=0.8,
        )
        assert tstc.label == "Complete"


class TestEcologicalSystem:
    def test_instantiation(self):
        es = EcologicalSystem(label="Test Ecosystem")
        assert es.label == "Test Ecosystem"

    def test_with_type(self):
        es = EcologicalSystem(label="Forest", ecosystem_type="forest")
        assert es.ecosystem_type == "forest"

    def test_with_health(self):
        es = EcologicalSystem(label="Healthy", environmental_health=0.85)
        assert es.environmental_health == 0.85

    def test_with_biodiversity(self):
        es = EcologicalSystem(label="Diverse", biodiversity_index=0.9)
        assert es.biodiversity_index == 0.9

    def test_complete(self):
        es = EcologicalSystem(
            label="Complete",
            ecosystem_type="wetland",
            environmental_health=0.75,
            biodiversity_index=0.8,
        )
        assert es.label == "Complete"
