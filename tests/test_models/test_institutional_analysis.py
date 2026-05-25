"""
Unit tests for institutional_analysis module.
"""

import pytest
import uuid
from models.institutional_analysis import InstitutionalStructure, PathDependencyAnalysis
from models.sfm_enums import InstitutionalScope, PathDependencyType, DependencyStrength


class TestInstitutionalStructure:
    """Test suite for InstitutionalStructure class."""

    def test_instantiation(self):
        """Test basic creation."""
        struct = InstitutionalStructure(label="Test Structure")
        assert struct.label == "Test Structure"

    def test_with_scope(self):
        """Test with institutional scope."""
        struct = InstitutionalStructure(
            label="Scoped",
            scope=InstitutionalScope.REGIONAL,
        )
        assert struct.scope == InstitutionalScope.REGIONAL

    def test_with_formal_rules(self):
        """Test with formal rules."""
        struct = InstitutionalStructure(
            label="Formal",
            formal_rules="Written constitution",
        )
        assert struct.formal_rules == "Written constitution"

    def test_with_informal_norms(self):
        """Test with informal norms."""
        struct = InstitutionalStructure(
            label="Informal",
            informal_norms="Cultural traditions",
        )
        assert struct.informal_norms == "Cultural traditions"

    def test_with_enforcement(self):
        """Test with enforcement mechanism."""
        struct = InstitutionalStructure(
            label="Enforced",
            enforcement_mechanism="Legal sanctions",
        )
        assert struct.enforcement_mechanism == "Legal sanctions"

    def test_complete(self):
        """Test complete structure."""
        struct = InstitutionalStructure(
            label="Complete",
            description="Full institution",
            scope=InstitutionalScope.NATIONAL,
            formal_rules="Legislation",
            informal_norms="Social norms",
            enforcement_mechanism="Regulatory agency",
        )
        assert struct.label == "Complete"


class TestPathDependencyAnalysis:
    """Test suite for PathDependencyAnalysis class."""

    def test_instantiation(self):
        """Test basic creation."""
        inst_id = uuid.uuid4()
        analysis = PathDependencyAnalysis(
            label="Test Path", analyzed_institution_id=inst_id
        )
        assert analysis.label == "Test Path"
        assert analysis.analyzed_institution_id == inst_id

    def test_with_type(self):
        """Test with path dependency type."""
        inst_id = uuid.uuid4()
        analysis = PathDependencyAnalysis(
            label="Lock-in",
            analyzed_institution_id=inst_id,
            dependency_strength=PathDependencyType.STRONG,
        )
        assert analysis.dependency_strength == PathDependencyType.STRONG

    def test_with_critical_junctures(self):
        """Test with critical junctures."""
        inst_id = uuid.uuid4()
        analysis = PathDependencyAnalysis(
            label="Juncture",
            analyzed_institution_id=inst_id,
            critical_junctures=["1980 policy reform"],
        )
        assert "1980 policy reform" in analysis.critical_junctures

    def test_with_lock_in(self):
        """Test with lock-in mechanisms."""
        inst_id = uuid.uuid4()
        analysis = PathDependencyAnalysis(
            label="Locked",
            analyzed_institution_id=inst_id,
            lock_in_mechanisms=["Network effects", "Sunk costs"],
        )
        assert len(analysis.lock_in_mechanisms) == 2

    def test_with_strength(self):
        """Test with dependency strength."""
        inst_id = uuid.uuid4()
        analysis = PathDependencyAnalysis(
            label="Moderate",
            analyzed_institution_id=inst_id,
            dependency_strength=PathDependencyType.MODERATE,
        )
        assert analysis.dependency_strength == PathDependencyType.MODERATE

    def test_complete(self):
        """Test complete analysis."""
        inst_id = uuid.uuid4()
        analysis = PathDependencyAnalysis(
            label="Complete Path",
            description="Full path analysis",
            analyzed_institution_id=inst_id,
            dependency_strength=PathDependencyType.LOCKED_IN,
            critical_junctures=["Founding moment"],
            lock_in_mechanisms=["Multiple mechanisms"],
        )
        assert analysis.label == "Complete Path"
        assert analysis.dependency_strength == PathDependencyType.LOCKED_IN
