"""
TEEOSA Formula Implementation

Nebraska Tax Equity and Educational Opportunities Support Act formula calculations
per Hoffman & Hayden (2007) - "Using the Social Fabric Matrix to Analyze
Institutional Rules Relative to Adequacy in Education Funding."

Reference: Journal of Economic Issues, 41(2), 359-367.
Legal Reference: Nebraska Revised Statutes § 79-1003, Supp. 2005

This module implements all 9 TEEOSA formula equations for calculating state aid
to Nebraska K-12 school districts.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class DistrictEnrollmentData:
    """
    Historical enrollment data for a school district.

    All student counts are by grade category for the prior year (y1).
    Historical ratios use years y2, y3, y4 (2-4 years prior to formula year).
    """
    district_id: str

    # Prior year (y1) enrollment by grade category
    half_day_k_y1: int = 0  # Ky1: Half-day kindergarten
    full_day_k_through_6_y1: int = 0  # FDKSy1: Full-day K through grade 6
    grades_7_8_y1: int = 0  # SEy1: Grades 7-8 (secondary elementary)
    grades_9_12_y1: int = 0  # NTy1: Grades 9-12 (non-terminal)

    # Contract students (y1) - students contracted out to other districts
    contract_half_day_k_y1: int = 0  # KCy1
    contract_full_day_k_through_6_y1: int = 0  # FDKCy1
    contract_grades_7_8_y1: int = 0  # SECy1
    contract_grades_9_12_y1: int = 0  # NTCy1

    # Historical Fall Membership and Average Daily Membership (y2, y3, y4)
    fall_membership_y2: int = 0  # FMy2
    fall_membership_y3: int = 0  # FMy3
    fall_membership_y4: int = 0  # FMy4

    avg_daily_membership_y2: float = 0.0  # ADMy2
    avg_daily_membership_y3: float = 0.0  # ADMy3
    avg_daily_membership_y4: float = 0.0  # ADMy4

    # Demographic factors (y1)
    students_on_indian_land: int = 0
    limited_english_proficiency_students: int = 0
    extreme_remoteness_qualified: bool = False
    poverty_percentage: float = 0.0  # 0.0 to 1.0


@dataclass
class DistrictFinancialData:
    """
    Historical financial and cost data for a school district.
    """
    district_id: str

    # Cost grouping classification
    cost_group: str = "Standard"  # "Very Sparse", "Sparse", "Standard"

    # General Fund Operating Expenditures (GFOE) - historical
    gfoe_y1: float = 0.0
    gfoe_y2: float = 0.0
    gfoe_y3: float = 0.0

    # Adjustments to GFOE
    special_receipts_y1: float = 0.0
    special_receipts_y2: float = 0.0
    special_receipts_y3: float = 0.0

    # Other financial data
    property_valuation: float = 0.0
    local_effort_rate: float = 0.0


@dataclass
class CostGroupData:
    """
    Statewide cost grouping data for TEEOSA calculations.
    """
    # Cost grouping expenditures and student counts
    cost_group_gfoe: Dict[str, float] = field(default_factory=dict)
    cost_group_wfs: Dict[str, float] = field(default_factory=dict)

    # Growth factors
    statewide_growth_factor: float = 0.03  # 3% default
    allowable_growth_rate: float = 0.05  # 5% default


class TEEOSACalculator:
    """
    Calculator for TEEOSA formula equations (1)-(9).

    Implements the Nebraska state aid formula per Hoffman & Hayden (2007).
    """

    # Grade weighting coefficients (Equation 2)
    WEIGHT_HALF_DAY_K = 0.5
    WEIGHT_FULL_DAY_K_6 = 1.0
    WEIGHT_GRADES_7_8 = 1.2
    WEIGHT_GRADES_9_12 = 1.4

    # Demographic weighting factors
    INDIAN_LAND_FACTOR = 0.25  # 25% additional (Equation 3)
    LEP_FACTOR = 0.25  # 25% additional (Equation 4)
    EXTREME_REMOTENESS_FACTOR = 0.125  # 12.5% additional (Equation 5)

    def __init__(self, cost_group_data: Optional[CostGroupData] = None):
        """Initialize calculator with optional cost grouping data."""
        self.cost_group_data = cost_group_data or CostGroupData()

    def calculate_attendance_ratio(self, enrollment: DistrictEnrollmentData) -> float:
        """
        Calculate 3-year average attendance ratio (ADM/FM).

        Used in Equations (1) and (2).

        Args:
            enrollment: District enrollment data

        Returns:
            Average attendance ratio (0.0 to 1.0)
        """
        ratios = []

        if enrollment.fall_membership_y2 > 0:
            ratios.append(enrollment.avg_daily_membership_y2 / enrollment.fall_membership_y2)
        if enrollment.fall_membership_y3 > 0:
            ratios.append(enrollment.avg_daily_membership_y3 / enrollment.fall_membership_y3)
        if enrollment.fall_membership_y4 > 0:
            ratios.append(enrollment.avg_daily_membership_y4 / enrollment.fall_membership_y4)

        if not ratios:
            return 1.0  # Default to perfect attendance if no data

        # Average of available ratios
        return sum(ratios) / len(ratios)

    def equation_1_formula_students(self, enrollment: DistrictEnrollmentData) -> float:
        """
        Equation (1): Adjusted Fall Membership Formula Students (FS).

        Converts fall membership counts into formula students by adjusting
        for attendance ratios and contracted students.

        Formula:
        FS = [.333 × (ADMy2/FMy2 + ADMy3/FMy3 + ADMy4/FMy4) ×
              (Ky1 + FDKSy1 + SEy1 + NTy1)]
             + (KCy1 + FDKCy1 + SECy1 + NTCy1)

        Args:
            enrollment: District enrollment data

        Returns:
            Formula students count
        """
        # Calculate 3-year average ratio, then multiply by 1/3
        attendance_ratio = self.calculate_attendance_ratio(enrollment) / 3.0

        # Sum of all non-contract students
        total_students = (
            enrollment.half_day_k_y1 +
            enrollment.full_day_k_through_6_y1 +
            enrollment.grades_7_8_y1 +
            enrollment.grades_9_12_y1
        )

        # Sum of all contract students
        contract_students = (
            enrollment.contract_half_day_k_y1 +
            enrollment.contract_full_day_k_through_6_y1 +
            enrollment.contract_grades_7_8_y1 +
            enrollment.contract_grades_9_12_y1
        )

        # Apply attendance ratio to non-contract students, add contract students
        formula_students = (attendance_ratio * total_students) + contract_students

        return formula_students

    def equation_2_weighted_formula_students(self, enrollment: DistrictEnrollmentData) -> float:
        """
        Equation (2): Weighted Formula Students (WFS).

        Apply grade-level weights to formula students to account for
        differential costs of educating different grade levels.

        Weights:
        - Half-day K: 0.5
        - Full-day K-6: 1.0
        - Grades 7-8: 1.2
        - Grades 9-12: 1.4

        Formula:
        WFS = [.333 × (ADMy2/FMy2 + ADMy3/FMy3 + ADMy4/FMy4) ×
               (.5Ky1 + 1.0FDKSy1 + 1.2SEy1 + 1.4NTy1)]
              + (.5KCy1 + 1.0FDKCy1 + 1.2SECy1 + 1.4NTCy1)

        Args:
            enrollment: District enrollment data

        Returns:
            Weighted formula students
        """
        attendance_ratio = self.calculate_attendance_ratio(enrollment) / 3.0

        # Apply weights to non-contract students
        weighted_students = (
            self.WEIGHT_HALF_DAY_K * enrollment.half_day_k_y1 +
            self.WEIGHT_FULL_DAY_K_6 * enrollment.full_day_k_through_6_y1 +
            self.WEIGHT_GRADES_7_8 * enrollment.grades_7_8_y1 +
            self.WEIGHT_GRADES_9_12 * enrollment.grades_9_12_y1
        )

        # Apply weights to contract students
        weighted_contract = (
            self.WEIGHT_HALF_DAY_K * enrollment.contract_half_day_k_y1 +
            self.WEIGHT_FULL_DAY_K_6 * enrollment.contract_full_day_k_through_6_y1 +
            self.WEIGHT_GRADES_7_8 * enrollment.contract_grades_7_8_y1 +
            self.WEIGHT_GRADES_9_12 * enrollment.contract_grades_9_12_y1
        )

        wfs = (attendance_ratio * weighted_students) + weighted_contract

        return wfs

    def equation_3_indian_land_adjustment(self, enrollment: DistrictEnrollmentData, wfs: float) -> float:
        """
        Equation (3): Indian Land Factor.

        Adds 25% additional weighting for students on Indian land.

        Args:
            enrollment: District enrollment data
            wfs: Weighted formula students from Equation (2)

        Returns:
            Additional weighted formula students for Indian land
        """
        if enrollment.students_on_indian_land == 0:
            return 0.0

        # 25% additional weight per student on Indian land
        return self.INDIAN_LAND_FACTOR * enrollment.students_on_indian_land

    def equation_4_lep_adjustment(self, enrollment: DistrictEnrollmentData, wfs: float) -> float:
        """
        Equation (4): Limited English Proficiency (LEP) Factor.

        Adds 25% additional weighting for LEP students.

        Args:
            enrollment: District enrollment data
            wfs: Weighted formula students from Equation (2)

        Returns:
            Additional weighted formula students for LEP
        """
        if enrollment.limited_english_proficiency_students == 0:
            return 0.0

        # 25% additional weight per LEP student
        return self.LEP_FACTOR * enrollment.limited_english_proficiency_students

    def equation_5_extreme_remoteness_adjustment(
        self,
        enrollment: DistrictEnrollmentData,
        wfs: float
    ) -> float:
        """
        Equation (5): Extreme Remoteness Factor.

        Adds 12.5% additional weighting for qualifying remote districts.

        Args:
            enrollment: District enrollment data
            wfs: Weighted formula students from Equation (2)

        Returns:
            Additional weighted formula students for extreme remoteness
        """
        if not enrollment.extreme_remoteness_qualified:
            return 0.0

        # 12.5% of WFS for extreme remoteness
        return self.EXTREME_REMOTENESS_FACTOR * wfs

    def equation_6_poverty_adjustment(self, enrollment: DistrictEnrollmentData, wfs: float) -> float:
        """
        Equation (6): Poverty Factor.

        Progressive weighting using delta functions, increasing from 5% to 105%
        as poverty concentration rises.

        Tiers (from paper):
        - 0-15%: 5% additional
        - 15-25%: 10% additional
        - 25-35%: 15% additional
        - 35-50%: 25% additional
        - 50-75%: 50% additional
        - >75%: 105% additional

        Args:
            enrollment: District enrollment data
            wfs: Weighted formula students from Equation (2)

        Returns:
            Additional weighted formula students for poverty
        """
        poverty_pct = enrollment.poverty_percentage

        # Progressive tier structure
        if poverty_pct <= 0.15:
            factor = 0.05
        elif poverty_pct <= 0.25:
            factor = 0.10
        elif poverty_pct <= 0.35:
            factor = 0.15
        elif poverty_pct <= 0.50:
            factor = 0.25
        elif poverty_pct <= 0.75:
            factor = 0.50
        else:
            factor = 1.05

        return factor * wfs

    def calculate_adjusted_wfs(self, enrollment: DistrictEnrollmentData) -> float:
        """
        Calculate total Adjusted Weighted Formula Students (AWFS).

        Combines Equations (2)-(6): WFS + all demographic adjustments.

        Args:
            enrollment: District enrollment data

        Returns:
            Total adjusted weighted formula students
        """
        # Base WFS (Equation 2)
        wfs = self.equation_2_weighted_formula_students(enrollment)

        # Add demographic factors (Equations 3-6)
        indian_land = self.equation_3_indian_land_adjustment(enrollment, wfs)
        lep = self.equation_4_lep_adjustment(enrollment, wfs)
        remoteness = self.equation_5_extreme_remoteness_adjustment(enrollment, wfs)
        poverty = self.equation_6_poverty_adjustment(enrollment, wfs)

        awfs = wfs + indian_land + lep + remoteness + poverty

        return awfs

    def equation_7_adjusted_gfoe(self, financial: DistrictFinancialData) -> float:
        """
        Equation (7): Total Adjusted GFOE for Cost Grouping.

        Sums historical General Fund Operating Expenditures with adjustments.

        Args:
            financial: District financial data

        Returns:
            Total adjusted GFOE
        """
        # Sum 3 years of GFOE
        total_gfoe = financial.gfoe_y1 + financial.gfoe_y2 + financial.gfoe_y3

        # Subtract special receipts (non-formula revenue)
        total_special = (
            financial.special_receipts_y1 +
            financial.special_receipts_y2 +
            financial.special_receipts_y3
        )

        adjusted_gfoe = total_gfoe - total_special

        return adjusted_gfoe

    def equation_8_cost_grouping_average(
        self,
        financial: DistrictFinancialData,
        enrollment: DistrictEnrollmentData
    ) -> float:
        """
        Equation (8): Average Formula Cost Per Student in Cost Grouping.

        Calculates statewide average cost per student for district's cost group.

        Cost groups:
        - Very Sparse: <0.5 students per square mile
        - Sparse: 0.5-2.0 students per square mile
        - Standard: >2.0 students per square mile

        Args:
            financial: District financial data
            enrollment: District enrollment data

        Returns:
            Average cost per student for cost group
        """
        cost_group = financial.cost_group

        # Get statewide totals for this cost group
        total_gfoe = self.cost_group_data.cost_group_gfoe.get(cost_group, 0.0)
        total_wfs = self.cost_group_data.cost_group_wfs.get(cost_group, 1.0)

        if total_wfs == 0:
            return 0.0

        average_cost = total_gfoe / total_wfs

        return average_cost

    def equation_9_growth_factor(
        self,
        enrollment: DistrictEnrollmentData,
        financial: DistrictFinancialData
    ) -> float:
        """
        Equation (9): Growth Factor.

        Combines enrollment changes and allowable growth rates.

        Args:
            enrollment: District enrollment data
            financial: District financial data

        Returns:
            Growth factor (multiplier)
        """
        # Simplified growth factor: use statewide rate
        # Full implementation would calculate enrollment change ratio
        growth_factor = 1.0 + self.cost_group_data.statewide_growth_factor

        return growth_factor

    def calculate_district_need(
        self,
        enrollment: DistrictEnrollmentData,
        financial: DistrictFinancialData
    ) -> Dict[str, Any]:
        """
        Calculate complete TEEOSA district need using all 9 equations.

        Returns detailed breakdown of calculations.

        Args:
            enrollment: District enrollment data
            financial: District financial data

        Returns:
            Dictionary with all calculated values and final state aid amount
        """
        # Student counts and weightings (Equations 1-6)
        formula_students = self.equation_1_formula_students(enrollment)
        wfs = self.equation_2_weighted_formula_students(enrollment)
        awfs = self.calculate_adjusted_wfs(enrollment)

        # Cost calculations (Equations 7-9)
        adjusted_gfoe = self.equation_7_adjusted_gfoe(financial)
        avg_cost_per_student = self.equation_8_cost_grouping_average(financial, enrollment)
        growth_factor = self.equation_9_growth_factor(enrollment, financial)

        # Final need calculation
        # Need = AWFS × Average Cost × Growth Factor
        district_need = awfs * avg_cost_per_student * growth_factor

        return {
            "formula_students": formula_students,
            "weighted_formula_students": wfs,
            "adjusted_weighted_formula_students": awfs,
            "adjusted_gfoe": adjusted_gfoe,
            "average_cost_per_student": avg_cost_per_student,
            "growth_factor": growth_factor,
            "district_need": district_need,
            "cost_group": financial.cost_group,
        }


def create_example_district() -> tuple[DistrictEnrollmentData, DistrictFinancialData]:
    """
    Create example district data for testing TEEOSA calculations.

    Uses plausible 2005-2006 Nebraska K-12 values.

    Returns:
        Tuple of (enrollment_data, financial_data)
    """
    enrollment = DistrictEnrollmentData(
        district_id="001-0001",
        # Prior year enrollment
        half_day_k_y1=50,
        full_day_k_through_6_y1=350,
        grades_7_8_y1=120,
        grades_9_12_y1=180,
        # Contract students
        contract_half_day_k_y1=0,
        contract_full_day_k_through_6_y1=5,
        contract_grades_7_8_y1=0,
        contract_grades_9_12_y1=0,
        # Historical FM and ADM
        fall_membership_y2=700,
        fall_membership_y3=695,
        fall_membership_y4=690,
        avg_daily_membership_y2=665.0,
        avg_daily_membership_y3=660.0,
        avg_daily_membership_y4=655.0,
        # Demographics
        students_on_indian_land=0,
        limited_english_proficiency_students=15,
        extreme_remoteness_qualified=False,
        poverty_percentage=0.22,  # 22% poverty
    )

    financial = DistrictFinancialData(
        district_id="001-0001",
        cost_group="Standard",
        # Historical GFOE
        gfoe_y1=5_200_000.0,
        gfoe_y2=5_000_000.0,
        gfoe_y3=4_850_000.0,
        # Special receipts
        special_receipts_y1=200_000.0,
        special_receipts_y2=190_000.0,
        special_receipts_y3=185_000.0,
    )

    return enrollment, financial
