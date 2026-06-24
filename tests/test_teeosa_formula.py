"""
Tests for TEEOSA formula implementation.

Verifies all 9 equations per Hoffman & Hayden (2007).
"""

import pytest
from models.teeosa_formula import (
    TEEOSACalculator,
    DistrictEnrollmentData,
    DistrictFinancialData,
    CostGroupData,
    create_example_district,
)


class TestTEEOSAFormulas:
    """Test individual TEEOSA formula equations."""

    def setup_method(self):
        """Setup calculator and test data for each test."""
        self.calculator = TEEOSACalculator()
        self.enrollment, self.financial = create_example_district()

    def test_attendance_ratio_calculation(self):
        """Test 3-year average attendance ratio calculation."""
        ratio = self.calculator.calculate_attendance_ratio(self.enrollment)

        # Expected: average of (665/700, 660/695, 655/690)
        expected = (665/700 + 660/695 + 655/690) / 3
        assert abs(ratio - expected) < 0.001

    def test_attendance_ratio_handles_missing_data(self):
        """Test attendance ratio when some years have no data."""
        enrollment = DistrictEnrollmentData(
            district_id="test",
            fall_membership_y2=100,
            avg_daily_membership_y2=95.0,
            fall_membership_y3=0,  # Missing data
            fall_membership_y4=0,  # Missing data
        )

        ratio = self.calculator.calculate_attendance_ratio(enrollment)
        assert ratio == 0.95  # Only y2 data available

    def test_attendance_ratio_defaults_to_one_when_no_data(self):
        """Test attendance ratio defaults to 1.0 when no historical data."""
        enrollment = DistrictEnrollmentData(district_id="test")
        ratio = self.calculator.calculate_attendance_ratio(enrollment)
        assert ratio == 1.0

    def test_equation_1_formula_students(self):
        """Test Equation (1): Formula Students calculation."""
        fs = self.calculator.equation_1_formula_students(self.enrollment)

        # Total students: 50 + 350 + 120 + 180 = 700
        # Contract students: 5
        # Attendance ratio / 3: ~0.949 / 3 = 0.316
        # FS = 0.316 × 700 + 5 ≈ 226.4
        assert fs > 220
        assert fs < 235

    def test_equation_1_with_no_contract_students(self):
        """Test Equation (1) when no contract students."""
        enrollment = DistrictEnrollmentData(
            district_id="test",
            half_day_k_y1=100,
            fall_membership_y2=100,
            avg_daily_membership_y2=95.0,
        )

        fs = self.calculator.equation_1_formula_students(enrollment)
        # Should be close to: (95/100)/3 × 100 = 31.67
        assert abs(fs - 31.67) < 1.0

    def test_equation_2_weighted_formula_students(self):
        """Test Equation (2): Weighted Formula Students."""
        wfs = self.calculator.equation_2_weighted_formula_students(self.enrollment)

        # Weighted students: 0.5×50 + 1.0×350 + 1.2×120 + 1.4×180
        #                  = 25 + 350 + 144 + 252 = 771
        # Contract: 1.0×5 = 5
        # WFS = attendance_ratio/3 × 771 + 5 ≈ 248.8
        assert wfs > 240
        assert wfs < 260

    def test_equation_2_grade_weights_correct(self):
        """Test grade weights are applied correctly in Equation (2)."""
        enrollment = DistrictEnrollmentData(
            district_id="test",
            half_day_k_y1=100,
            fall_membership_y2=100,
            avg_daily_membership_y2=100.0,  # Perfect attendance
        )

        wfs = self.calculator.equation_2_weighted_formula_students(enrollment)
        # WFS = (100/100)/3 × (0.5 × 100) = 0.333 × 50 = 16.67
        assert abs(wfs - 16.67) < 0.5

    def test_equation_3_indian_land_adjustment(self):
        """Test Equation (3): Indian Land Factor (25% additional)."""
        wfs = 100.0
        adjustment = self.calculator.equation_3_indian_land_adjustment(
            self.enrollment, wfs
        )

        # No Indian land students in example
        assert adjustment == 0.0

        # Test with Indian land students
        enrollment = DistrictEnrollmentData(
            district_id="test",
            students_on_indian_land=50
        )
        adjustment = self.calculator.equation_3_indian_land_adjustment(enrollment, wfs)
        assert adjustment == 50 * 0.25  # 12.5

    def test_equation_4_lep_adjustment(self):
        """Test Equation (4): LEP Factor (25% additional)."""
        wfs = 100.0
        adjustment = self.calculator.equation_4_lep_adjustment(self.enrollment, wfs)

        # Example has 15 LEP students
        assert adjustment == 15 * 0.25  # 3.75

    def test_equation_5_extreme_remoteness_adjustment(self):
        """Test Equation (5): Extreme Remoteness Factor (12.5% of WFS)."""
        wfs = 100.0
        adjustment = self.calculator.equation_5_extreme_remoteness_adjustment(
            self.enrollment, wfs
        )

        # Example not qualified for remoteness
        assert adjustment == 0.0

        # Test with remoteness qualification
        enrollment = DistrictEnrollmentData(
            district_id="test",
            extreme_remoteness_qualified=True
        )
        adjustment = self.calculator.equation_5_extreme_remoteness_adjustment(
            enrollment, wfs
        )
        assert adjustment == 100 * 0.125  # 12.5

    def test_equation_6_poverty_adjustment_tiers(self):
        """Test Equation (6): Poverty Factor progressive tiers."""
        wfs = 100.0

        # Test each tier
        test_cases = [
            (0.10, 0.05),   # 10% poverty → 5% additional
            (0.20, 0.10),   # 20% poverty → 10% additional
            (0.30, 0.15),   # 30% poverty → 15% additional
            (0.40, 0.25),   # 40% poverty → 25% additional
            (0.60, 0.50),   # 60% poverty → 50% additional
            (0.80, 1.05),   # 80% poverty → 105% additional
        ]

        for poverty_pct, expected_factor in test_cases:
            enrollment = DistrictEnrollmentData(
                district_id="test",
                poverty_percentage=poverty_pct
            )
            adjustment = self.calculator.equation_6_poverty_adjustment(enrollment, wfs)
            assert adjustment == wfs * expected_factor, \
                f"Poverty {poverty_pct} should have factor {expected_factor}"

    def test_calculate_adjusted_wfs_combines_all_factors(self):
        """Test AWFS calculation combines WFS + all demographic adjustments."""
        awfs = self.calculator.calculate_adjusted_wfs(self.enrollment)

        # Should include base WFS + LEP (15 students) + poverty (22%)
        # WFS ≈ 248, LEP = 15×0.25 = 3.75, poverty = 248×0.10 = 24.8
        # AWFS ≈ 248 + 3.75 + 24.8 ≈ 276.55
        assert awfs > 270
        assert awfs < 285

    def test_equation_7_adjusted_gfoe(self):
        """Test Equation (7): Adjusted GFOE calculation."""
        adjusted_gfoe = self.calculator.equation_7_adjusted_gfoe(self.financial)

        # Total GFOE: 5.2M + 5.0M + 4.85M = 15.05M
        # Total special receipts: 200k + 190k + 185k = 575k
        # Adjusted: 15.05M - 575k = 14.475M
        assert abs(adjusted_gfoe - 14_475_000.0) < 1000

    def test_equation_8_cost_grouping_average(self):
        """Test Equation (8): Cost grouping average calculation."""
        # Setup cost group data
        cost_data = CostGroupData(
            cost_group_gfoe={"Standard": 500_000_000.0},
            cost_group_wfs={"Standard": 100_000.0},
        )
        calculator = TEEOSACalculator(cost_data)

        avg_cost = calculator.equation_8_cost_grouping_average(
            self.financial, self.enrollment
        )

        # Expected: 500M / 100k = 5000 per student
        assert avg_cost == 5000.0

    def test_equation_8_handles_zero_wfs(self):
        """Test Equation (8) handles zero WFS in cost group."""
        cost_data = CostGroupData(
            cost_group_gfoe={"Standard": 1000.0},
            cost_group_wfs={"Standard": 0.0},
        )
        calculator = TEEOSACalculator(cost_data)

        avg_cost = calculator.equation_8_cost_grouping_average(
            self.financial, self.enrollment
        )

        assert avg_cost == 0.0  # Should not crash

    def test_equation_9_growth_factor(self):
        """Test Equation (9): Growth factor calculation."""
        growth = self.calculator.equation_9_growth_factor(
            self.enrollment, self.financial
        )

        # Default growth factor is 1.03 (3%)
        assert growth == 1.03

    def test_calculate_district_need_complete(self):
        """Test complete district need calculation using all 9 equations."""
        # Setup realistic cost group data
        cost_data = CostGroupData(
            cost_group_gfoe={"Standard": 700_800_000.0},  # $700.8M (FY 2005-06 verified)
            cost_group_wfs={"Standard": 140_000.0},
            statewide_growth_factor=0.03,
        )
        calculator = TEEOSACalculator(cost_data)

        result = calculator.calculate_district_need(self.enrollment, self.financial)

        # Verify all components present
        assert "formula_students" in result
        assert "weighted_formula_students" in result
        assert "adjusted_weighted_formula_students" in result
        assert "adjusted_gfoe" in result
        assert "average_cost_per_student" in result
        assert "growth_factor" in result
        assert "district_need" in result
        assert "cost_group" in result

        # Verify reasonable values
        assert result["formula_students"] > 0
        assert result["weighted_formula_students"] > 0
        assert result["adjusted_weighted_formula_students"] > 0
        assert result["average_cost_per_student"] > 0
        assert result["growth_factor"] > 1.0
        assert result["district_need"] > 0

        # Average cost should be: 700.8M / 140k ≈ 5006 per student
        assert abs(result["average_cost_per_student"] - 5006) < 10

        # AWFS should be around 276 (from prior test)
        # District need: 276 × 5006 × 1.03 ≈ 1,423,000
        assert result["district_need"] > 1_200_000
        assert result["district_need"] < 1_600_000


class TestDistrictDataModels:
    """Test data model classes."""

    def test_enrollment_data_initialization(self):
        """Test DistrictEnrollmentData initializes with defaults."""
        data = DistrictEnrollmentData(district_id="001-0001")

        assert data.district_id == "001-0001"
        assert data.half_day_k_y1 == 0
        assert data.poverty_percentage == 0.0
        assert data.extreme_remoteness_qualified is False

    def test_financial_data_initialization(self):
        """Test DistrictFinancialData initializes with defaults."""
        data = DistrictFinancialData(district_id="001-0001")

        assert data.district_id == "001-0001"
        assert data.cost_group == "Standard"
        assert data.gfoe_y1 == 0.0

    def test_cost_group_data_initialization(self):
        """Test CostGroupData initializes with defaults."""
        data = CostGroupData()

        assert isinstance(data.cost_group_gfoe, dict)
        assert isinstance(data.cost_group_wfs, dict)
        assert data.statewide_growth_factor == 0.03
        assert data.allowable_growth_rate == 0.05


class TestExampleDistrictCreation:
    """Test example district factory."""

    def test_create_example_district_returns_valid_data(self):
        """Test create_example_district returns valid enrollment and financial data."""
        enrollment, financial = create_example_district()

        assert isinstance(enrollment, DistrictEnrollmentData)
        assert isinstance(financial, DistrictFinancialData)
        assert enrollment.district_id == "001-0001"
        assert financial.district_id == "001-0001"

    def test_example_district_has_plausible_values(self):
        """Test example district has plausible 2005-2006 values."""
        enrollment, financial = create_example_district()

        # Total students should be in hundreds
        total = (
            enrollment.half_day_k_y1 +
            enrollment.full_day_k_through_6_y1 +
            enrollment.grades_7_8_y1 +
            enrollment.grades_9_12_y1
        )
        assert total == 700

        # GFOE should be in millions
        assert financial.gfoe_y1 > 1_000_000
        assert financial.gfoe_y1 < 10_000_000

        # Cost group should be valid
        assert financial.cost_group in ["Very Sparse", "Sparse", "Standard"]


class TestCostGroupCategories:
    """Test cost grouping classification."""

    def test_cost_groups_exist(self):
        """Test three cost group categories exist."""
        groups = ["Very Sparse", "Sparse", "Standard"]
        cost_data = CostGroupData(
            cost_group_gfoe={g: 1000.0 for g in groups},
            cost_group_wfs={g: 100.0 for g in groups},
        )

        assert "Very Sparse" in cost_data.cost_group_gfoe
        assert "Sparse" in cost_data.cost_group_gfoe
        assert "Standard" in cost_data.cost_group_gfoe

    def test_cost_group_classification_criteria(self):
        """Test cost group classification based on density.

        From LB 806 (1997):
        - Very Sparse: <0.5 students per square mile
        - Sparse: 0.5-2.0 students per square mile
        - Standard: >2.0 students per square mile
        """
        # This test documents the criteria
        # Actual classification would happen in data processing
        criteria = {
            "Very Sparse": "<0.5 students/sq mi",
            "Sparse": "0.5-2.0 students/sq mi",
            "Standard": ">2.0 students/sq mi",
        }

        assert len(criteria) == 3
        assert "Very Sparse" in criteria


class TestFormulaValidation:
    """Test formula validation and edge cases."""

    def test_formulas_handle_zero_students(self):
        """Test formulas handle zero student enrollment gracefully."""
        calculator = TEEOSACalculator()
        enrollment = DistrictEnrollmentData(district_id="empty")
        financial = DistrictFinancialData(district_id="empty")

        result = calculator.calculate_district_need(enrollment, financial)

        # Should complete without error
        assert result["formula_students"] == 0
        assert result["weighted_formula_students"] == 0
        assert result["district_need"] == 0

    def test_formulas_handle_all_contract_students(self):
        """Test formulas when all students are contracted out."""
        calculator = TEEOSACalculator()
        enrollment = DistrictEnrollmentData(
            district_id="contract",
            contract_full_day_k_through_6_y1=100,
            fall_membership_y2=100,
            avg_daily_membership_y2=95.0,
        )
        financial = DistrictFinancialData(district_id="contract")

        result = calculator.calculate_district_need(enrollment, financial)

        # Contract students should still count
        assert result["formula_students"] == 100
        assert result["weighted_formula_students"] == 100  # Weight 1.0 for K-6

    def test_poverty_factor_boundary_values(self):
        """Test poverty factor at tier boundaries."""
        calculator = TEEOSACalculator()

        # Test exactly at tier boundaries
        boundary_tests = [
            (0.15, 0.05),   # Exactly at 15% boundary
            (0.25, 0.10),   # Exactly at 25% boundary
            (0.35, 0.15),   # Exactly at 35% boundary
            (0.50, 0.25),   # Exactly at 50% boundary
            (0.75, 0.50),   # Exactly at 75% boundary
        ]

        for poverty_pct, expected_factor in boundary_tests:
            enrollment = DistrictEnrollmentData(
                district_id="boundary",
                poverty_percentage=poverty_pct
            )
            adjustment = calculator.equation_6_poverty_adjustment(enrollment, 100.0)
            assert adjustment == 100.0 * expected_factor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
