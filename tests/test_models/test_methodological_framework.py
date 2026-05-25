"""
Unit tests for methodological_framework module.
"""

import pytest
from models.methodological_framework import (
    InstrumentalistInquiryFramework,
    NormativeSystemsAnalysis,
    PolicyRelevanceIntegration,
    DatabaseIntegrationCapability,
)


class TestInstrumentalistInquiryFramework:
    def test_instantiation(self):
        iif = InstrumentalistInquiryFramework(label="Test Framework")
        assert iif.label == "Test Framework"

    def test_with_question(self):
        iif = InstrumentalistInquiryFramework(
            label="Question", inquiry_purpose="What is the impact?"
        )
        assert iif.inquiry_purpose == "What is the impact?"

    def test_with_application(self):
        iif = InstrumentalistInquiryFramework(
            label="Applied", normative_orientation="Pragmatic approach"
        )
        assert iif.normative_orientation == "Pragmatic approach"

    def test_complete(self):
        iif = InstrumentalistInquiryFramework(
            label="Complete",
            description="Full inquiry framework",
            inquiry_purpose="Research question",
            problem_context="Policy context",
            normative_orientation="Value-based",
        )
        assert iif.label == "Complete"


class TestNormativeSystemsAnalysis:
    def test_instantiation(self):
        nsa = NormativeSystemsAnalysis(label="Test Analysis")
        assert nsa.label == "Test Analysis"

    def test_with_criteria(self):
        nsa = NormativeSystemsAnalysis(
            label="Criteria", normative_criteria=["Equity", "Efficiency"]
        )
        assert len(nsa.normative_criteria) == 2

    def test_with_prioritization(self):
        nsa = NormativeSystemsAnalysis(
            label="Prioritized", value_hierarchy={"equity": 0.6, "efficiency": 0.4}
        )
        assert nsa.value_hierarchy["equity"] == 0.6

    def test_complete(self):
        nsa = NormativeSystemsAnalysis(
            label="Complete",
            description="Full normative analysis",
            normative_criteria=["Justice", "Sustainability"],
            value_hierarchy={"justice": 0.7, "sustainability": 0.3},
            ethical_framework="Utilitarian",
        )
        assert nsa.label == "Complete"


class TestPolicyRelevanceIntegration:
    def test_instantiation(self):
        pri = PolicyRelevanceIntegration(label="Test Integration")
        assert pri.label == "Test Integration"

    def test_with_policies(self):
        pri = PolicyRelevanceIntegration(
            label="Targeted", policy_context="Healthcare reform"
        )
        assert pri.policy_context == "Healthcare reform"

    def test_with_pathways(self):
        pri = PolicyRelevanceIntegration(
            label="Pathway", description="Implementation strategies"
        )
        assert pri.description == "Implementation strategies"

    def test_complete(self):
        pri = PolicyRelevanceIntegration(
            label="Complete",
            description="Full policy integration",
            policy_context="Education policy",
            political_feasibility=0.75,
            implementation_capacity=0.65,
        )
        assert pri.label == "Complete"


class TestDatabaseIntegrationCapability:
    def test_instantiation(self):
        dic = DatabaseIntegrationCapability(label="Test Database")
        assert dic.label == "Test Database"

    def test_with_sources(self):
        dic = DatabaseIntegrationCapability(label="Sources", database_type="PostgreSQL")
        assert dic.database_type == "PostgreSQL"

    def test_with_capabilities(self):
        dic = DatabaseIntegrationCapability(
            label="Capable", data_architecture="Star schema"
        )
        assert dic.data_architecture == "Star schema"

    def test_complete(self):
        dic = DatabaseIntegrationCapability(
            label="Complete",
            description="Full database integration",
            database_type="MongoDB",
            data_architecture="Document-based",
            integration_level=0.85,
        )
        assert dic.label == "Complete"
