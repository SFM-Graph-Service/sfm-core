"""
Criteria Evaluation Module - Assesses deliveries against normative criteria.

Implements Hayden's normative SFM framework by evaluating how system deliveries
serve or undermine specified social criteria.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
from enum import Enum

from models import SFMCriteria
from models.delivery_matrix import SFMDeliveryMatrix, SFMDeliveryCell


class EvaluationAlignment(Enum):
    """How a delivery aligns with a criterion."""
    SERVES = "serves"  # Delivery positively serves the criterion
    UNDERMINES = "undermines"  # Delivery negatively undermines the criterion
    NEUTRAL = "neutral"  # Delivery has no significant impact
    UNKNOWN = "unknown"  # Alignment cannot be determined


@dataclass
class DeliveryEvaluation:
    """Evaluation of a single delivery against a criterion."""
    delivery_id: uuid.UUID
    delivery_type: str
    delivery_content: str
    alignment: EvaluationAlignment
    alignment_strength: float  # 0.0 to 1.0
    rationale: str

    # Performance metrics
    delivery_quality: Optional[float] = None
    delivery_reliability: Optional[float] = None
    delivery_efficiency: Optional[float] = None

    # Impact assessment
    positive_impacts: List[str] = field(default_factory=list)
    negative_impacts: List[str] = field(default_factory=list)
    improvement_opportunities: List[str] = field(default_factory=list)


@dataclass
class CriterionEvaluationResult:
    """Results of evaluating all deliveries against a criterion."""
    criterion_id: uuid.UUID
    criterion_label: str
    criterion_type: str
    priority: str

    # Delivery evaluations
    serving_deliveries: List[DeliveryEvaluation] = field(default_factory=list)
    undermining_deliveries: List[DeliveryEvaluation] = field(default_factory=list)
    neutral_deliveries: List[DeliveryEvaluation] = field(default_factory=list)
    unknown_deliveries: List[DeliveryEvaluation] = field(default_factory=list)

    # Aggregate scores
    overall_alignment_score: float = 0.0  # -1.0 (all undermine) to +1.0 (all serve)
    serving_delivery_count: int = 0
    undermining_delivery_count: int = 0

    # Analysis
    key_strengths: List[str] = field(default_factory=list)
    key_weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def calculate_aggregates(self) -> None:
        """Calculate aggregate scores and analysis."""
        self.serving_delivery_count = len(self.serving_deliveries)
        self.undermining_delivery_count = len(self.undermining_deliveries)

        # Calculate weighted alignment score
        total_weight = 0.0
        weighted_sum = 0.0

        for delivery_eval in self.serving_deliveries:
            weight = delivery_eval.alignment_strength
            total_weight += weight
            weighted_sum += weight

        for delivery_eval in self.undermining_deliveries:
            weight = delivery_eval.alignment_strength
            total_weight += weight
            weighted_sum -= weight

        if total_weight > 0:
            self.overall_alignment_score = weighted_sum / total_weight

        # Generate key strengths
        if self.serving_delivery_count > 0:
            self.key_strengths.append(
                f"{self.serving_delivery_count} deliveries actively serve this criterion"
            )

            high_quality_serves = [
                d for d in self.serving_deliveries
                if d.delivery_quality and d.delivery_quality >= 0.8
            ]
            if high_quality_serves:
                self.key_strengths.append(
                    f"{len(high_quality_serves)} high-quality deliveries provide strong support"
                )

        # Generate key weaknesses
        if self.undermining_delivery_count > 0:
            self.key_weaknesses.append(
                f"{self.undermining_delivery_count} deliveries undermine this criterion"
            )

            strong_undermining = [
                d for d in self.undermining_deliveries
                if d.alignment_strength >= 0.7
            ]
            if strong_undermining:
                self.key_weaknesses.append(
                    f"{len(strong_undermining)} deliveries create significant conflicts"
                )

        # Generate recommendations
        if self.overall_alignment_score < 0:
            self.recommendations.append(
                "Overall alignment is negative - consider redesigning undermining deliveries"
            )

        low_quality_serves = [
            d for d in self.serving_deliveries
            if d.delivery_quality and d.delivery_quality < 0.6
        ]
        if low_quality_serves:
            self.recommendations.append(
                f"Improve quality of {len(low_quality_serves)} serving deliveries"
            )

        for delivery_eval in self.serving_deliveries + self.undermining_deliveries:
            if delivery_eval.improvement_opportunities:
                self.recommendations.extend(delivery_eval.improvement_opportunities)


def evaluate_against_criteria(service: Any) -> Dict[uuid.UUID, CriterionEvaluationResult]:
    """
    Evaluate all deliveries against defined criteria.

    Traverses the SFM graph to find:
    1. All SFMCriteria nodes
    2. All SFMDeliveryMatrix nodes and their cells
    3. Relationships connecting deliveries to criteria

    Returns a dictionary mapping criterion_id to evaluation results.

    Args:
        service: SFMService instance with loaded graph

    Returns:
        Dict mapping criterion UUID to CriterionEvaluationResult
    """
    results: Dict[uuid.UUID, CriterionEvaluationResult] = {}

    # Get all criteria nodes
    criteria_nodes: List[SFMCriteria] = []
    for node in service.list_nodes():
        if isinstance(node, SFMCriteria):
            criteria_nodes.append(node)

    if not criteria_nodes:
        return results  # No criteria to evaluate against

    # Get all delivery matrix cells from SFMDeliveryMatrix nodes
    delivery_cells: List[SFMDeliveryCell] = []
    for node in service.list_nodes():
        if isinstance(node, SFMDeliveryMatrix):
            # Extract cells from matrix
            for cell in node.cells.values():
                if cell.deliveries:  # Only include cells with deliveries
                    delivery_cells.append(cell)

    if not delivery_cells:
        return results  # No deliveries to evaluate

    # Evaluate each criterion
    for criterion in criteria_nodes:
        result = CriterionEvaluationResult(
            criterion_id=criterion.id,
            criterion_label=criterion.label,
            criterion_type=str(criterion.criteria_type.value),
            priority=str(criterion.priority.value)
        )

        # Find delivery cells linked to this criterion
        # Look for relationships where the criterion is source or target
        all_relationships = service.list_relationships()
        criterion_relationships = [
            rel for rel in all_relationships
            if criterion.id in (rel.source_id, rel.target_id)
        ]

        linked_delivery_cell_ids: set[uuid.UUID] = set()
        for rel in criterion_relationships:
            # If criterion is source, target might be delivery cell
            if rel.source_id == criterion.id:
                linked_delivery_cell_ids.add(rel.target_id)
            # If criterion is target, source might be delivery cell
            if rel.target_id == criterion.id:
                linked_delivery_cell_ids.add(rel.source_id)

        # Evaluate each linked delivery cell
        for cell in delivery_cells:
            if cell.id not in linked_delivery_cell_ids:
                continue

            # Evaluate each delivery in the cell
            for delivery in cell.deliveries:
                # Determine alignment based on relationship attributes
                alignment, strength, rationale = _evaluate_delivery_cell_alignment(
                    cell, delivery, criterion, service, criterion_relationships
                )

                delivery_eval = DeliveryEvaluation(
                    delivery_id=cell.id,  # Use cell ID since deliveries don't have individual IDs
                    delivery_type=delivery.delivery_type or "unknown",
                    delivery_content=delivery.delivery_content or "unspecified delivery",
                    alignment=alignment,
                    alignment_strength=strength,
                    rationale=rationale,
                    delivery_quality=None,  # Delivery dataclass doesn't have quality fields
                    delivery_reliability=None,
                    delivery_efficiency=None
                )

                # Categorize by alignment
                if alignment == EvaluationAlignment.SERVES:
                    result.serving_deliveries.append(delivery_eval)
                elif alignment == EvaluationAlignment.UNDERMINES:
                    result.undermining_deliveries.append(delivery_eval)
                elif alignment == EvaluationAlignment.NEUTRAL:
                    result.neutral_deliveries.append(delivery_eval)
                else:
                    result.unknown_deliveries.append(delivery_eval)

        # Calculate aggregates and analysis
        result.calculate_aggregates()
        results[criterion.id] = result

    return results


def _evaluate_delivery_cell_alignment(
    cell: SFMDeliveryCell,
    delivery: Any,  # Delivery dataclass from delivery_matrix
    criterion: SFMCriteria,
    service: Any,
    criterion_relationships: List[Any]
) -> tuple[EvaluationAlignment, float, str]:
    """
    Determine how a delivery cell's delivery aligns with a criterion.

    Returns:
        (alignment, strength, rationale) tuple
    """
    # Find the relationship linking delivery cell to criterion
    linking_rel = None
    for rel in criterion_relationships:
        if cell.id in (rel.source_id, rel.target_id):
            linking_rel = rel
            break

    if not linking_rel:
        return (
            EvaluationAlignment.UNKNOWN,
            0.0,
            "No direct relationship found between delivery cell and criterion"
        )

    # Check relationship weight (positive = serves, negative = undermines)
    weight = linking_rel.weight if hasattr(linking_rel, 'weight') and linking_rel.weight else 0.0

    if weight > 0.1:
        # Positive relationship - delivery serves criterion
        strength = min(abs(weight), 1.0)

        # Build rationale
        rationale_parts = [f"Delivery supports criterion (relationship weight: {weight:.2f})"]

        # Check delivery certainty if available
        if hasattr(delivery, 'certainty') and delivery.certainty and delivery.certainty >= 0.9:
            rationale_parts.append("High certainty strengthens support")

        # Check quantity if available
        if hasattr(delivery, 'quantity') and delivery.quantity:
            rationale_parts.append(f"Quantified delivery ({delivery.quantity} {delivery.units or ''})")

        return (
            EvaluationAlignment.SERVES,
            strength,
            "; ".join(rationale_parts)
        )

    elif weight < -0.1:
        # Negative relationship - delivery undermines criterion
        strength = min(abs(weight), 1.0)

        rationale_parts = [f"Delivery conflicts with criterion (relationship weight: {weight:.2f})"]

        # Check certainty
        if hasattr(delivery, 'certainty') and delivery.certainty and delivery.certainty >= 0.9:
            rationale_parts.append("High certainty confirms conflict")

        return (
            EvaluationAlignment.UNDERMINES,
            strength,
            "; ".join(rationale_parts)
        )

    else:
        # Near-zero weight or no weight - neutral or unknown
        if weight != 0:
            return (
                EvaluationAlignment.NEUTRAL,
                abs(weight),
                f"Weak relationship (weight: {weight:.2f}) indicates minimal impact"
            )
        else:
            return (
                EvaluationAlignment.UNKNOWN,
                0.0,
                "Relationship exists but alignment is unspecified"
            )


def format_evaluation_report(
    results: Dict[uuid.UUID, CriterionEvaluationResult],
    include_details: bool = True
) -> str:
    """
    Format criterion evaluation results as human-readable report.

    Args:
        results: Evaluation results from evaluate_against_criteria
        include_details: Whether to include detailed delivery listings

    Returns:
        Formatted text report
    """
    if not results:
        return "No criteria evaluation results available."

    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("CRITERIA EVALUATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    # Sort criteria by overall alignment (worst first to highlight problems)
    sorted_results = sorted(
        results.values(),
        key=lambda r: r.overall_alignment_score
    )

    for result in sorted_results:
        lines.append(f"Criterion: {result.criterion_label}")
        lines.append(f"  Type: {result.criterion_type}, Priority: {result.priority}")
        lines.append(f"  Overall Alignment Score: {result.overall_alignment_score:+.3f}")
        lines.append(f"  Serving Deliveries: {result.serving_delivery_count}")
        lines.append(f"  Undermining Deliveries: {result.undermining_delivery_count}")

        if result.key_strengths:
            lines.append("")
            lines.append("  Strengths:")
            for strength in result.key_strengths:
                lines.append(f"    • {strength}")

        if result.key_weaknesses:
            lines.append("")
            lines.append("  Weaknesses:")
            for weakness in result.key_weaknesses:
                lines.append(f"    ⚠ {weakness}")

        if result.recommendations:
            lines.append("")
            lines.append("  Recommendations:")
            for rec in result.recommendations:
                lines.append(f"    → {rec}")

        if include_details:
            if result.serving_deliveries:
                lines.append("")
                lines.append("  Serving Deliveries:")
                for delivery_eval in result.serving_deliveries[:3]:  # Limit to top 3
                    lines.append(
                        f"    ✓ {delivery_eval.delivery_type}: {delivery_eval.delivery_content[:60]}"
                    )
                    lines.append(f"      Strength: {delivery_eval.alignment_strength:.2f}")
                    if delivery_eval.delivery_quality:
                        lines.append(f"      Quality: {delivery_eval.delivery_quality:.2f}")

            if result.undermining_deliveries:
                lines.append("")
                lines.append("  Undermining Deliveries:")
                for delivery_eval in result.undermining_deliveries[:3]:  # Limit to top 3
                    lines.append(
                        f"    ✗ {delivery_eval.delivery_type}: {delivery_eval.delivery_content[:60]}"
                    )
                    lines.append(f"      Strength: {delivery_eval.alignment_strength:.2f}")

        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    return "\n".join(lines)
