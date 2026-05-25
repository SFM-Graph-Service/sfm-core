"""
Unit tests for matrix_components module.
"""

import pytest
import uuid
from models.matrix_components import MatrixCell, SFMCriteria, SFMMatrix
from models.sfm_enums import (
    CriteriaType,
    CorrelationScale,
    MeasurementApproach,
    CriteriaPriority,
)


class TestMatrixCell:
    """Test suite for MatrixCell class."""

    def test_matrix_cell_instantiation(self):
        """Test basic MatrixCell creation."""
        cell = MatrixCell(
            label="Test Cell", institution_id=uuid.uuid4(), criteria_id=uuid.uuid4()
        )
        assert cell.label == "Test Cell"
        assert isinstance(cell.institution_id, uuid.UUID)
        assert isinstance(cell.criteria_id, uuid.UUID)

    def test_matrix_cell_with_strength(self):
        """Test MatrixCell with correlation strength."""
        cell = MatrixCell(
            label="Cell",
            institution_id=uuid.uuid4(),
            criteria_id=uuid.uuid4(),
            correlation_strength=0.75,
        )
        assert cell.correlation_strength == 0.75

    def test_matrix_cell_with_correlation(self):
        """Test MatrixCell with correlation scale."""
        cell = MatrixCell(
            label="Cell",
            institution_id=uuid.uuid4(),
            criteria_id=uuid.uuid4(),
            correlation_scale=CorrelationScale.STRONGLY_POSITIVE,
        )
        assert cell.correlation_scale == CorrelationScale.STRONGLY_POSITIVE

    def test_matrix_cell_with_justification(self):
        """Test MatrixCell with justification and confidence."""
        cell = MatrixCell(
            label="Cell",
            institution_id=uuid.uuid4(),
            criteria_id=uuid.uuid4(),
            justification="Empirical study",
            confidence_level=0.85,
        )
        assert cell.justification == "Empirical study"
        assert cell.confidence_level == 0.85

    def test_matrix_cell_complete(self):
        """Test MatrixCell with all fields."""
        inst_id = uuid.uuid4()
        crit_id = uuid.uuid4()
        cell = MatrixCell(
            label="Complete Cell",
            description="Fully specified cell",
            institution_id=inst_id,
            criteria_id=crit_id,
            correlation_strength=0.9,
            correlation_scale=CorrelationScale.MODERATELY_POSITIVE,
            justification="Strong theoretical basis",
            confidence_level=0.9,
        )
        assert cell.label == "Complete Cell"
        assert cell.institution_id == inst_id
        assert cell.criteria_id == crit_id


class TestSFMCriteria:
    """Test suite for SFMCriteria class."""

    def test_criteria_instantiation(self):
        """Test basic SFMCriteria creation."""
        criteria = SFMCriteria(label="Test Criteria")
        assert criteria.label == "Test Criteria"

    def test_criteria_with_type(self):
        """Test SFMCriteria with criteria type."""
        criteria = SFMCriteria(
            label="Social Criterion", criteria_type=CriteriaType.SOCIAL
        )
        assert criteria.criteria_type == CriteriaType.SOCIAL

    def test_criteria_with_measurement(self):
        """Test SFMCriteria with measurement details."""
        criteria = SFMCriteria(
            label="Measurable",
            measurement_approach=MeasurementApproach.QUANTITATIVE,
        )
        assert criteria.measurement_approach == MeasurementApproach.QUANTITATIVE

    def test_criteria_with_priority(self):
        """Test SFMCriteria with priority level."""
        criteria = SFMCriteria(
            label="Primary Criterion", priority=CriteriaPriority.PRIMARY
        )
        assert criteria.priority == CriteriaPriority.PRIMARY

    def test_criteria_complete(self):
        """Test SFMCriteria with all fields."""
        criteria = SFMCriteria(
            label="Complete Criteria",
            description="Fully specified criteria",
            criteria_type=CriteriaType.ECONOMIC,
            measurement_approach=MeasurementApproach.MIXED,
            priority=CriteriaPriority.PRIMARY,
        )
        assert criteria.label == "Complete Criteria"
        assert criteria.criteria_type == CriteriaType.ECONOMIC


class TestSFMMatrix:
    """Test suite for SFMMatrix class."""

    def test_matrix_instantiation(self):
        """Test basic SFMMatrix creation."""
        matrix = SFMMatrix(label="Test Matrix")
        assert matrix.label == "Test Matrix"
        assert matrix.institutions == []
        assert matrix.criteria == []
        assert matrix.matrix_cells == []

    def test_matrix_with_criteria(self):
        """Test SFMMatrix with institutions and criteria."""
        inst_ids = [uuid.uuid4(), uuid.uuid4()]
        crit_ids = [uuid.uuid4(), uuid.uuid4()]
        matrix = SFMMatrix(
            label="Criteria Matrix", institutions=inst_ids, criteria=crit_ids
        )
        assert len(matrix.institutions) == 2
        assert len(matrix.criteria) == 2

    def test_matrix_with_cells(self):
        """Test SFMMatrix with populated cells."""
        cell_ids = [uuid.uuid4(), uuid.uuid4()]
        matrix = SFMMatrix(label="Populated", matrix_cells=cell_ids)
        assert len(matrix.matrix_cells) == 2

    def test_matrix_with_purpose(self):
        """Test SFMMatrix with purpose."""
        matrix = SFMMatrix(
            label="Purposeful",
            matrix_purpose="Analyze policy impacts",
        )
        assert matrix.matrix_purpose == "Analyze policy impacts"

    def test_matrix_complete(self):
        """Test SFMMatrix with all fields."""
        inst_ids = [uuid.uuid4() for _ in range(3)]
        crit_ids = [uuid.uuid4() for _ in range(3)]
        cell_ids = [uuid.uuid4() for _ in range(5)]

        matrix = SFMMatrix(
            label="Complete Matrix",
            description="Fully specified matrix",
            institutions=inst_ids,
            criteria=crit_ids,
            matrix_cells=cell_ids,
            matrix_purpose="Comprehensive analysis",
            completeness_score=0.9,
            consistency_score=0.85,
        )
        assert matrix.label == "Complete Matrix"
        assert len(matrix.institutions) == 3
        assert len(matrix.criteria) == 3
        assert len(matrix.matrix_cells) == 5


class TestMatrixIntegration:
    """Integration tests for matrix components."""

    def test_criteria_with_all_types(self):
        """Test criteria with different types."""
        for ctype in [
            CriteriaType.SOCIAL,
            CriteriaType.ECONOMIC,
            CriteriaType.ENVIRONMENTAL,
        ]:
            crit = SFMCriteria(label=f"Criteria {ctype}", criteria_type=ctype)
            assert crit.criteria_type == ctype

    def test_criteria_priority_levels(self):
        """Test criteria with different priorities."""
        for priority in [
            CriteriaPriority.PRIMARY,
            CriteriaPriority.SECONDARY,
            CriteriaPriority.TERTIARY,
        ]:
            crit = SFMCriteria(label=f"Priority {priority}", priority=priority)
            assert crit.priority == priority

    def test_cell_correlation_scales(self):
        """Test all correlation scale values."""
        scales = [
            CorrelationScale.STRONGLY_POSITIVE,
            CorrelationScale.MODERATELY_POSITIVE,
            CorrelationScale.WEAKLY_POSITIVE,
            CorrelationScale.NEUTRAL,
        ]
        for scale in scales:
            cell = MatrixCell(
                label=f"Cell {scale}",
                institution_id=uuid.uuid4(),
                criteria_id=uuid.uuid4(),
                correlation_scale=scale,
            )
            assert cell.correlation_scale == scale

    def test_criteria_measurement_approaches(self):
        """Test different measurement approaches."""
        approaches = [
            MeasurementApproach.QUANTITATIVE,
            MeasurementApproach.QUALITATIVE,
            MeasurementApproach.MIXED,
        ]
        for approach in approaches:
            crit = SFMCriteria(
                label=f"Measure {approach}", measurement_approach=approach
            )
            assert crit.measurement_approach == approach

    def test_matrix_empty_vs_populated(self):
        """Test empty matrix vs populated matrix."""
        empty = SFMMatrix(label="Empty")
        assert len(empty.matrix_cells) == 0
        assert len(empty.institutions) == 0

        populated = SFMMatrix(
            label="Populated",
            institutions=[uuid.uuid4()],
            criteria=[uuid.uuid4()],
            matrix_cells=[uuid.uuid4()],
        )
        assert len(populated.matrix_cells) == 1
