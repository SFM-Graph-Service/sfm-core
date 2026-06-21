"""
Unit tests for Doughnut-SFM bridge functionality.

Tests the conversion of continuous Doughnut boundary indicators
to discrete SFM delivery weights per issue #27 requirements.
"""

import pytest
from graph.doughnut_bridge import boundary_state_to_delivery, get_delivery_state


class TestBoundaryStateToDelivery:
    """Test boundary_state_to_delivery helper function."""

    # -------------------------------------------------------------------------
    # Shortfall boundaries (social foundation) tests
    # -------------------------------------------------------------------------

    def test_shortfall_below_threshold(self):
        """Test shortfall boundary below threshold (negative weight)."""
        # Social foundation: 65% have adequate income, target 95%
        weight = boundary_state_to_delivery(
            indicator_value=0.65,
            threshold=0.95,
            polarity="shortfall"
        )

        # Should be negative (shortfall)
        assert weight < 0
        # Should be approximately -0.316 ((0.65 - 0.95) / 0.95)
        assert -0.32 <= weight <= -0.31

    def test_shortfall_at_threshold(self):
        """Test shortfall boundary exactly at threshold (neutral)."""
        weight = boundary_state_to_delivery(
            indicator_value=0.95,
            threshold=0.95,
            polarity="shortfall"
        )

        # Should be zero (at threshold)
        assert weight == 0.0

    def test_shortfall_above_threshold(self):
        """Test shortfall boundary above threshold (positive weight)."""
        # Social foundation: 98% have adequate income, target 95%
        weight = boundary_state_to_delivery(
            indicator_value=0.98,
            threshold=0.95,
            polarity="shortfall"
        )

        # Should be positive (exceeding foundation)
        assert weight > 0
        # Should be approximately +0.032 ((0.98 - 0.95) / 0.95)
        assert 0.03 <= weight <= 0.04

    def test_shortfall_severe_below_threshold(self):
        """Test shortfall boundary severely below threshold (large negative weight)."""
        # Extreme shortfall: 10% have adequate income, target 95%
        weight = boundary_state_to_delivery(
            indicator_value=0.10,
            threshold=0.95,
            polarity="shortfall"
        )

        # Should be large negative weight (approximately -0.89)
        assert weight < -0.8
        assert weight >= -1.0  # Clamped at -1.0

    def test_shortfall_severe_above_threshold(self):
        """Test shortfall boundary severely above threshold (clamped to +1.0)."""
        # Extreme excess: 200% of target (e.g., normalized indicator)
        weight = boundary_state_to_delivery(
            indicator_value=2.00,
            threshold=0.95,
            polarity="shortfall"
        )

        # Should be clamped to +1.0
        assert weight == 1.0

    # -------------------------------------------------------------------------
    # Overshoot boundaries (ecological ceiling) tests
    # -------------------------------------------------------------------------

    def test_overshoot_above_threshold(self):
        """Test overshoot boundary above threshold (negative weight)."""
        # Ecological ceiling: CO2 at 420 ppm, safe threshold 350 ppm
        weight = boundary_state_to_delivery(
            indicator_value=420,
            threshold=350,
            polarity="overshoot"
        )

        # Should be negative (overshoot)
        assert weight < 0
        # Should be approximately -0.20 (-(420 - 350) / 350)
        assert -0.21 <= weight <= -0.19

    def test_overshoot_at_threshold(self):
        """Test overshoot boundary exactly at threshold (neutral)."""
        weight = boundary_state_to_delivery(
            indicator_value=350,
            threshold=350,
            polarity="overshoot"
        )

        # Should be zero (at threshold)
        assert weight == 0.0

    def test_overshoot_below_threshold(self):
        """Test overshoot boundary below threshold (positive weight)."""
        # Ecological ceiling: CO2 at 300 ppm, safe threshold 350 ppm
        weight = boundary_state_to_delivery(
            indicator_value=300,
            threshold=350,
            polarity="overshoot"
        )

        # Should be positive (within safe zone)
        assert weight > 0
        # Should be approximately +0.14 (-(300 - 350) / 350)
        assert 0.13 <= weight <= 0.15

    def test_overshoot_severe_above_threshold(self):
        """Test overshoot boundary severely above threshold (clamped to -1.0)."""
        # Extreme overshoot: CO2 at 700 ppm, safe threshold 350 ppm
        weight = boundary_state_to_delivery(
            indicator_value=700,
            threshold=350,
            polarity="overshoot"
        )

        # Should be clamped to -1.0
        assert weight == -1.0

    def test_overshoot_severe_below_threshold(self):
        """Test overshoot boundary severely below threshold (large positive weight)."""
        # Far below threshold (e.g., pre-industrial CO2 levels)
        weight = boundary_state_to_delivery(
            indicator_value=100,
            threshold=350,
            polarity="overshoot"
        )

        # Should be large positive weight (approximately 0.71)
        assert weight > 0.7
        assert weight <= 1.0  # Clamped at +1.0

    # -------------------------------------------------------------------------
    # Edge cases and error handling
    # -------------------------------------------------------------------------

    def test_zero_threshold_raises_error(self):
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="Threshold cannot be zero"):
            boundary_state_to_delivery(
                indicator_value=100,
                threshold=0,
                polarity="overshoot"
            )

    def test_invalid_polarity_raises_error(self):
        """Test that invalid polarity raises ValueError."""
        with pytest.raises(ValueError, match="Invalid polarity"):
            boundary_state_to_delivery(
                indicator_value=100,
                threshold=350,
                polarity="invalid"
            )

    def test_negative_threshold_shortfall(self):
        """Test shortfall boundary with negative threshold."""
        # Edge case: negative threshold (e.g., temperature anomaly)
        weight = boundary_state_to_delivery(
            indicator_value=-2.0,
            threshold=-1.0,
            polarity="shortfall"
        )

        # -2.0 is below -1.0 threshold, so shortfall (negative weight)
        assert weight < 0

    def test_negative_threshold_overshoot(self):
        """Test overshoot boundary with negative threshold."""
        # Edge case: negative threshold
        weight = boundary_state_to_delivery(
            indicator_value=-0.5,
            threshold=-1.0,
            polarity="overshoot"
        )

        # -0.5 is above -1.0 threshold, so overshoot (negative weight)
        assert weight < 0

    # -------------------------------------------------------------------------
    # Real-world examples from Doughnut literature
    # -------------------------------------------------------------------------

    def test_health_social_foundation_example(self):
        """Test Health boundary (social foundation) with realistic data."""
        # Example: 85% of population has access to healthcare, target 95%
        weight = boundary_state_to_delivery(
            indicator_value=0.85,
            threshold=0.95,
            polarity="shortfall"
        )

        # Should be negative (shortfall)
        assert weight < 0
        # Should be approximately -0.105 ((0.85 - 0.95) / 0.95)
        assert -0.11 <= weight <= -0.10

    def test_air_pollution_ecological_ceiling_example(self):
        """Test Air Pollution boundary (ecological ceiling) with realistic data."""
        # Example: PM2.5 at 15 μg/m³, safe threshold 10 μg/m³
        weight = boundary_state_to_delivery(
            indicator_value=15,
            threshold=10,
            polarity="overshoot"
        )

        # Should be negative (overshoot)
        assert weight < 0
        # Should be approximately -0.5 (-(15 - 10) / 10)
        assert -0.51 <= weight <= -0.49

    def test_water_social_foundation_example(self):
        """Test Water boundary (social foundation) with realistic data."""
        # Example: 70% have access to clean water, target 90%
        weight = boundary_state_to_delivery(
            indicator_value=0.70,
            threshold=0.90,
            polarity="shortfall"
        )

        # Should be negative (shortfall)
        assert weight < 0
        # Should be approximately -0.222 ((0.70 - 0.90) / 0.90)
        assert -0.23 <= weight <= -0.21


class TestGetDeliveryState:
    """Test get_delivery_state helper function."""

    def test_positive_state(self):
        """Test weight > 0.05 classified as positive."""
        assert get_delivery_state(0.1) == "positive"
        assert get_delivery_state(0.5) == "positive"
        assert get_delivery_state(1.0) == "positive"

    def test_negative_state(self):
        """Test weight < -0.05 classified as negative."""
        assert get_delivery_state(-0.1) == "negative"
        assert get_delivery_state(-0.5) == "negative"
        assert get_delivery_state(-1.0) == "negative"

    def test_neutral_state(self):
        """Test abs(weight) <= 0.05 classified as neutral."""
        assert get_delivery_state(0.0) == "neutral"
        assert get_delivery_state(0.02) == "neutral"
        assert get_delivery_state(-0.03) == "neutral"
        assert get_delivery_state(0.05) == "neutral"
        assert get_delivery_state(-0.05) == "neutral"

    def test_boundary_cases(self):
        """Test boundary cases at +/- 0.05 threshold."""
        # Exactly at threshold should be neutral
        assert get_delivery_state(0.05) == "neutral"
        assert get_delivery_state(-0.05) == "neutral"

        # Just above threshold should be positive/negative
        assert get_delivery_state(0.051) == "positive"
        assert get_delivery_state(-0.051) == "negative"


class TestBoundaryStateToDeliveryIntegration:
    """Integration tests for boundary_state_to_delivery with real scenarios."""

    def test_clean_air_act_co2_reduction(self):
        """Test EPA standards reducing CO2 overshoot."""
        # Scenario: EPA standards reduce CO2 from 420 ppm to 300 ppm
        # Threshold: 350 ppm

        # Before EPA standards (overshoot)
        weight_before = boundary_state_to_delivery(420, 350, "overshoot")
        assert weight_before < 0  # Negative (overshoot)

        # After EPA standards (within safe zone)
        weight_after = boundary_state_to_delivery(300, 350, "overshoot")
        assert weight_after > 0  # Positive (helping meet boundary)

        # Net improvement
        improvement = weight_after - weight_before
        assert improvement > 0

    def test_teeosa_education_access(self):
        """Test TEEOSA formula improving education access."""
        # Scenario: TEEOSA increases education access from 75% to 92%
        # Threshold: 95%

        # Before TEEOSA (shortfall)
        weight_before = boundary_state_to_delivery(0.75, 0.95, "shortfall")
        assert weight_before < 0  # Negative (shortfall)

        # After TEEOSA (still shortfall but improved)
        weight_after = boundary_state_to_delivery(0.92, 0.95, "shortfall")
        assert weight_after < 0  # Still negative but closer to zero

        # Net improvement (both negative, but after is less negative)
        assert weight_after > weight_before

    def test_boundary_met_from_both_sides(self):
        """Test that approaching threshold from either side converges to zero."""
        threshold = 100

        # Approaching from below (shortfall)
        weights_below = [
            boundary_state_to_delivery(val, threshold, "shortfall")
            for val in [50, 75, 90, 95, 99, 100]
        ]
        # Should monotonically increase toward zero
        for i in range(len(weights_below) - 1):
            assert weights_below[i] < weights_below[i + 1]
        assert weights_below[-1] == 0.0

        # Approaching from above (overshoot)
        weights_above = [
            boundary_state_to_delivery(val, threshold, "overshoot")
            for val in [200, 150, 120, 110, 105, 100]
        ]
        # Should monotonically increase toward zero
        for i in range(len(weights_above) - 1):
            assert weights_above[i] < weights_above[i + 1]
        assert weights_above[-1] == 0.0
