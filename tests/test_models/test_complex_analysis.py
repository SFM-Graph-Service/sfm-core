"""
Unit tests for complex_analysis module.
"""

import pytest
import uuid
from models.complex_analysis import (
    DigraphAnalysis,
    CircularCausationProcess,
    ConflictDetection,
)
from models.sfm_enums import ConflictType


class TestDigraphAnalysis:
    def test_instantiation(self):
        da = DigraphAnalysis(label="Test Digraph")
        assert da.label == "Test Digraph"

    def test_with_stability(self):
        da = DigraphAnalysis(label="Stable", stability_score=0.85)
        assert da.stability_score == 0.85

    def test_with_complexity(self):
        da = DigraphAnalysis(label="Complex", complexity_measure=0.72)
        assert da.complexity_measure == 0.72

    def test_with_notes(self):
        da = DigraphAnalysis(label="Noted", methodology_notes="Three feedback loops")
        assert da.methodology_notes == "Three feedback loops"

    def test_complete(self):
        da = DigraphAnalysis(
            label="Complete",
            stability_score=0.9,
            complexity_measure=0.65,
            methodology_notes="Critical paths identified",
        )
        assert da.label == "Complete"


class TestCircularCausationProcess:
    def test_instantiation(self):
        ccp = CircularCausationProcess(label="Test Process")
        assert ccp.label == "Test Process"

    def test_with_process_type(self):
        ccp = CircularCausationProcess(label="Virtuous", process_type="virtuous")
        assert ccp.process_type == "virtuous"

    def test_with_feedback(self):
        ccp = CircularCausationProcess(label="Feedback", feedback_polarity="positive")
        assert ccp.feedback_polarity == "positive"

    def test_with_time_scale(self):
        ccp = CircularCausationProcess(label="Dynamic", time_scale="long-term")
        assert ccp.time_scale == "long-term"

    def test_complete(self):
        ccp = CircularCausationProcess(
            label="Complete",
            process_type="vicious",
            feedback_polarity="positive",
            time_scale="medium-term",
        )
        assert ccp.label == "Complete"


class TestConflictDetection:
    def test_instantiation(self):
        system_id = uuid.uuid4()
        cd = ConflictDetection(label="Test Conflict", analyzed_system_id=system_id)
        assert cd.label == "Test Conflict"
        assert cd.analyzed_system_id == system_id

    def test_with_type(self):
        system_id = uuid.uuid4()
        cd = ConflictDetection(
            label="Typed",
            analyzed_system_id=system_id,
            conflict_type=ConflictType.VALUE_CONFLICT,
        )
        assert cd.conflict_type == ConflictType.VALUE_CONFLICT

    def test_with_intensity(self):
        system_id = uuid.uuid4()
        conflict_id = "conf_1"
        cd = ConflictDetection(
            label="Intense",
            analyzed_system_id=system_id,
            conflict_intensity={conflict_id: 0.85},
        )
        assert cd.conflict_intensity[conflict_id] == 0.85

    def test_with_stakeholders(self):
        system_id = uuid.uuid4()
        conflict_id = "conf_1"
        stakeholder_ids = [uuid.uuid4(), uuid.uuid4()]
        cd = ConflictDetection(
            label="Affected",
            analyzed_system_id=system_id,
            affected_stakeholders={conflict_id: stakeholder_ids},
        )
        assert len(cd.affected_stakeholders[conflict_id]) == 2

    def test_complete(self):
        system_id = uuid.uuid4()
        conflict_id = "conf_1"
        cd = ConflictDetection(
            label="Complete",
            analyzed_system_id=system_id,
            conflict_type=ConflictType.RESOURCE_CONFLICT,
            conflict_intensity={conflict_id: 0.75},
            resolution_difficulty={conflict_id: 0.6},
        )
        assert cd.label == "Complete"
