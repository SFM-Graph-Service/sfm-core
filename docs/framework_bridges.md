# Framework Bridges: SFM, Doughnut, and SES/IAD

## Positioning

SFM remains the institutional mechanism model (deliveries, dependencies, conflicts, feedback). The Doughnut model contributes boundary criteria and a dashboard framing of social shortfalls and ecological overshoots.

## Continuous indicator to delivery mapping

`boundary_state_to_delivery(indicator_value, threshold, polarity)` converts a continuous Doughnut reading into an SFM-compatible delivery state:

- `shortfall`: values below threshold are `undermines`, above threshold are `serves`
- `overshoot`: values above threshold are `undermines`, below threshold are `serves`
- equal to threshold is `neutral`

The output includes a normalized weight so boundary pressure can be compared across indicators.

## SES/IAD bridge

A minimal worked mapping is implemented in `build_ses_iad_example(service)`:

- Rules-in-use as institutional node(s)
- Action arena as a node cluster anchor
- Actor cluster linked to arena participation

This is intentionally small and testable, serving as a scaffold for richer SES/IAD encodings.

## Methodological caveat

The bridge itself is the research contribution: Doughnut indicators are continuous measurements, while many SFM deliveries are normative/structural links. Threshold and polarity choices must be explicit and justified in each applied study.
