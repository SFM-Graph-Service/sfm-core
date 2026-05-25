"""
Unit tests for specialized_components module.
"""

import pytest
from uuid import uuid4
from models.specialized_components import (
    SocialIndicatorSystem,
    EvolutionaryPathway,
    SocialProvisioningMatrix,
)
from models.sfm_enums import EvolutionaryStage


class TestSocialIndicatorSystem:
    def test_instantiation(self):
        sis = SocialIndicatorSystem(label="Test System")
        assert sis.label == "Test System"

    def test_with_indicators(self):
        sis = SocialIndicatorSystem(label="Indicators", indicator_category="Health")
        assert sis.indicator_category == "Health"

    def test_with_framework(self):
        sis = SocialIndicatorSystem(label="Framework", measurement_framework="SDGs")
        assert sis.measurement_framework == "SDGs"

    def test_with_aggregation(self):
        sis = SocialIndicatorSystem(label="Aggregated", data_collection_method="Survey")
        assert sis.data_collection_method == "Survey"

    def test_complete(self):
        sis = SocialIndicatorSystem(
            label="Complete",
            indicator_category="Wellbeing",
            measurement_framework="Custom",
            data_collection_method="Mixed methods",
        )
        assert sis.label == "Complete"


class TestEvolutionaryPathway:
    def test_instantiation(self):
        ep = EvolutionaryPathway(label="Test Pathway")
        assert ep.label == "Test Pathway"

    def test_with_stages(self):
        ep = EvolutionaryPathway(
            label="Stages", pathway_stage=EvolutionaryStage.EMERGENCE
        )
        assert ep.pathway_stage == EvolutionaryStage.EMERGENCE

    def test_with_trajectory(self):
        ep = EvolutionaryPathway(
            label="Trajectory", development_trajectory=["Initial", "Growth", "Maturity"]
        )
        assert len(ep.development_trajectory) == 3

    def test_with_drivers(self):
        ep = EvolutionaryPathway(
            label="Driven", evolutionary_pressures=["Technology", "Policy"]
        )
        assert len(ep.evolutionary_pressures) == 2

    def test_complete(self):
        ep = EvolutionaryPathway(
            label="Complete",
            pathway_stage=EvolutionaryStage.MATURATION,
            development_trajectory=["Emergence", "Growth"],
            evolutionary_pressures=["Innovation", "Competition"],
        )
        assert ep.label == "Complete"


class TestSocialProvisioningMatrix:
    def test_instantiation(self):
        spm = SocialProvisioningMatrix(label="Test Matrix")
        assert spm.label == "Test Matrix"
        assert spm.provisioning_categories == []

    def test_with_stages(self):
        spm = SocialProvisioningMatrix(
            label="Stages", provisioning_categories=["Production", "Distribution"]
        )
        assert len(spm.provisioning_categories) == 2

    def test_with_actors(self):
        actor_ids = [uuid4(), uuid4()]
        spm = SocialProvisioningMatrix(label="Actors", beneficiary_groups=actor_ids)
        assert len(spm.beneficiary_groups) == 2

    def test_with_flows(self):
        spm = SocialProvisioningMatrix(
            label="Flows",
            provision_mechanisms={
                "goods": ["Food", "Shelter"],
                "services": ["Healthcare"],
            },
        )
        assert "goods" in spm.provision_mechanisms

    def test_complete(self):
        actor_ids = [uuid4()]
        spm = SocialProvisioningMatrix(
            label="Complete",
            provisioning_categories=["Production", "Consumption"],
            beneficiary_groups=actor_ids,
            provision_mechanisms={"all": ["Complete chain"]},
        )
        assert spm.label == "Complete"
