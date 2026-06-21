"""
Doughnut-SFM Bridge: Converting continuous indicators to discrete deliveries.

This module addresses the core methodological challenge of integrating
Raworth's Doughnut Economics (continuous indicators) with Hayden's
Social Fabric Matrix (discrete deliveries).

Methodological Context
----------------------
- **Doughnut Economics**: Uses continuous metrics (e.g., CO2 ppm, income ratios,
  access percentages) measured against scientific/normative thresholds
- **Social Fabric Matrix**: Uses Boolean/weighted deliveries between institutions
  representing presence/absence/strength of transactions

The bridge translates continuous boundary states into delivery weights,
preserving both the quantitative precision of Doughnut indicators and
the institutional focus of SFM analysis.

**Research Contribution**: The mapping itself is a methodological contribution.
It demonstrates how global sustainability frameworks (planetary boundaries,
social foundations) can be operationalized at the institutional level through
SFM delivery chain analysis.

References
----------
- Raworth, K. (2017). *Doughnut Economics: Seven Ways to Think Like a
  21st-Century Economist*. Chelsea Green Publishing.
- Hayden, F. G. (2006). *Policymaking for a Good Society*. Springer.
- Steffen et al. (2015). *Planetary boundaries: Guiding human development
  on a changing planet*. Science, 347(6223), 1259855.

Examples
--------
>>> # CO2 concentration (ecological ceiling, overshoot polarity)
>>> delivery_weight = boundary_state_to_delivery(
...     indicator_value=420,  # ppm CO2
...     threshold=350,        # safe boundary
...     polarity="overshoot"
... )
>>> print(delivery_weight)  # Negative weight (driving overshoot)
-0.7

>>> # Income access (social foundation, shortfall polarity)
>>> delivery_weight = boundary_state_to_delivery(
...     indicator_value=0.65,  # 65% have adequate income
...     threshold=0.95,        # 95% target
...     polarity="shortfall"
... )
>>> print(delivery_weight)  # Negative weight (driving shortfall)
-0.316
"""

from typing import Literal

__all__ = [
    "boundary_state_to_delivery",
    "DeliveryState",
]

# Type alias for delivery state
DeliveryState = Literal["positive", "negative", "neutral"]


def boundary_state_to_delivery(
    indicator_value: float,
    threshold: float,
    polarity: Literal["shortfall", "overshoot"]
) -> float:
    """
    Convert continuous Doughnut boundary state to SFM delivery weight.

    Maps a continuous indicator reading to a delivery weight in [-1.0, +1.0]
    based on distance from threshold and boundary polarity.

    Parameters
    ----------
    indicator_value : float
        Current measured value of the boundary indicator.
        Examples:
        - CO2 concentration in ppm
        - Percentage of population with adequate income (0.0-1.0)
        - Biodiversity loss rate
    threshold : float
        Safe/desirable threshold for the boundary.
        For shortfall boundaries: minimum acceptable level
        For overshoot boundaries: maximum sustainable level
    polarity : {"shortfall", "overshoot"}
        Boundary type:
        - "shortfall": social foundation (below = bad, above = good)
        - "overshoot": ecological ceiling (above = bad, below = good)

    Returns
    -------
    float
        Delivery weight in [-1.0, +1.0]:
        - **Positive weights**: Delivery helps meet boundary
          (reduces overshoot or addresses shortfall)
        - **Negative weights**: Delivery undermines boundary
          (drives overshoot or contributes to shortfall)
        - **Zero**: Delivery is neutral or at threshold

    Weight Calculation
    ------------------
    The weight magnitude is proportional to distance from threshold,
    normalized to produce weights in [-1.0, +1.0]:

    For **shortfall** boundaries (social foundation):
        - indicator_value < threshold → negative weight (shortfall)
        - indicator_value >= threshold → positive weight (met/exceeded)
        - weight = (indicator_value - threshold) / threshold

    For **overshoot** boundaries (ecological ceiling):
        - indicator_value > threshold → negative weight (overshoot)
        - indicator_value <= threshold → positive weight (within safe zone)
        - weight = (threshold - indicator_value) / threshold

    Clamping: Extreme values are clamped to [-1.0, +1.0] to prevent
    unbounded weights.

    Examples
    --------
    **Ecological Ceiling Example: CO2 Emissions**

    >>> # Current CO2: 420 ppm, Safe threshold: 350 ppm (overshoot)
    >>> weight = boundary_state_to_delivery(420, 350, "overshoot")
    >>> print(f"{weight:.2f}")  # -0.20 (20% overshoot)
    -0.20

    **Social Foundation Example: Income Access**

    >>> # Current: 65% have adequate income, Target: 95% (shortfall)
    >>> weight = boundary_state_to_delivery(0.65, 0.95, "shortfall")
    >>> print(f"{weight:.2f}")  # -0.32 (32% shortfall)
    -0.32

    **At Threshold (Met Boundary)**

    >>> # Exactly at threshold
    >>> weight = boundary_state_to_delivery(350, 350, "overshoot")
    >>> print(f"{weight:.2f}")  # 0.00 (at threshold)
    0.00

    **Positive Delivery (Helping Meet Boundary)**

    >>> # EPA standards reduce emissions below threshold
    >>> weight = boundary_state_to_delivery(300, 350, "overshoot")
    >>> print(f"{weight:.2f}")  # +0.14 (within safe zone)
    0.14

    Notes
    -----
    - Threshold values must be non-zero to avoid division errors
    - The mapping assumes linear scaling; non-linear thresholds
      (e.g., tipping points) may require custom transforms
    - Weights represent institutional impact direction, not
      absolute quantitative contributions
    - For multi-delivery cells, weights can be aggregated to show
      net institutional impact on boundary

    Raises
    ------
    ValueError
        If threshold is zero or polarity is invalid

    See Also
    --------
    graph.doughnut_evaluation.evaluate_doughnut : Evaluates all boundaries
    graph.doughnut_evaluation.BoundaryEvaluation : Boundary evaluation container
    """
    # Validate inputs
    if threshold == 0:
        raise ValueError("Threshold cannot be zero (would cause division by zero)")

    if polarity not in ["shortfall", "overshoot"]:
        raise ValueError(f"Invalid polarity '{polarity}'. Must be 'shortfall' or 'overshoot'")

    # Calculate distance from threshold
    distance = indicator_value - threshold

    # Convert to weight based on polarity
    if polarity == "shortfall":
        # Social foundation: below threshold is bad (negative weight)
        # above threshold is good (positive weight)
        weight = distance / abs(threshold)

    else:  # polarity == "overshoot"
        # Ecological ceiling: above threshold is bad (negative weight)
        # below threshold is good (positive weight)
        weight = -distance / abs(threshold)

    # Clamp to [-1.0, +1.0] to prevent unbounded weights
    weight = max(-1.0, min(1.0, weight))

    return weight


def get_delivery_state(weight: float) -> DeliveryState:
    """
    Classify delivery weight into discrete state.

    Parameters
    ----------
    weight : float
        Delivery weight from boundary_state_to_delivery()

    Returns
    -------
    DeliveryState
        "positive" if weight > 0.05,
        "negative" if weight < -0.05,
        "neutral" if abs(weight) <= 0.05

    Examples
    --------
    >>> get_delivery_state(0.3)
    'positive'
    >>> get_delivery_state(-0.7)
    'negative'
    >>> get_delivery_state(0.02)
    'neutral'

    Notes
    -----
    The 0.05 threshold provides a small dead zone around zero
    to avoid treating tiny numerical differences as meaningful.
    """
    if weight > 0.05:
        return "positive"
    elif weight < -0.05:
        return "negative"
    else:
        return "neutral"
