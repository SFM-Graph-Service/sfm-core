"""
Hayden-compliant Social Fabric Matrix delivery model.

Implements square N×N matrix structure where components appear on both axes.
Supports multiple heterogeneous deliveries per cell with required descriptions.

References:
- Hayden (2008): Multiple distinct deliveries per cell requirement
- Hayden (1987, 1993): Temporal modeling with rates and thresholds
- Hayden (2013): Cell descriptions as canonical deliverables
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid

from models.base_nodes import Node


@dataclass
class Delivery:
    """
    Single delivery within an SFM cell.

    Hayden allows multiple heterogeneous deliveries per (source, target) pair.
    A positive/negative sign is NOT sufficient per Hayden 2008.

    Attributes:
        delivery_type: Type of delivery (money, energy, pollution, rule, authority, information)
        delivery_content: Narrative description of what is delivered
        quantity: Optional numeric quantity
        units: Optional units for quantity
        temporal_rate: How often delivery occurs (annual, monthly, continuous, event-triggered)
        temporal_clock: Which clock governs timing (fiscal_year, legislative_cycle)
        threshold: Monitoring threshold value
        threshold_direction: Direction for threshold alert (above, below)
        last_threshold_check: Last time threshold was checked
        certainty: Confidence in this delivery (0.0-1.0)
        data_sources: Sources documenting this delivery
    """

    delivery_type: str
    delivery_content: str
    quantity: Optional[float] = None
    units: Optional[str] = None

    # Temporal modeling per Hayden 1987, 1993
    temporal_rate: Optional[str] = None
    temporal_clock: Optional[str] = None
    threshold: Optional[float] = None
    threshold_direction: Optional[str] = None
    last_threshold_check: Optional[datetime] = None

    # Quality metadata
    certainty: Optional[float] = None
    data_sources: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate delivery attributes."""
        if not self.delivery_type:
            raise ValueError("delivery_type is required")
        if not self.delivery_content:
            raise ValueError("delivery_content is required")

        if self.threshold_direction and self.threshold_direction not in ["above", "below"]:
            raise ValueError("threshold_direction must be 'above' or 'below'")

        if self.certainty is not None and not (0.0 <= self.certainty <= 1.0):
            raise ValueError("certainty must be between 0.0 and 1.0")


@dataclass
class SFMDeliveryCell(Node):
    """
    Cell (i,j) in Hayden's SFM showing ALL deliveries from component i → component j.

    Primary content is the delivery list and cell description (REQUIRED per Hayden).
    Hayden methodology treats cell descriptions as canonical deliverables, not optional metadata.

    Attributes:
        source_component_id: Source component UUID (row in matrix)
        target_component_id: Target component UUID (column in matrix)
        deliveries: List of all deliveries from source to target
        cell_description: Required narrative for non-empty cells
        net_correlation: Optional aggregate correlation type
        aggregate_strength: Optional aggregate strength measure
        cultural_values_influence: Cultural values affecting this cell
        ceremonial_component: Ceremonial (status-quo) component strength
        instrumental_component: Instrumental (problem-solving) component strength
    """

    source_component_id: Optional[uuid.UUID] = None
    target_component_id: Optional[uuid.UUID] = None

    # PRIMARY CONTENT per Hayden methodology
    deliveries: List[Delivery] = field(default_factory=list)
    cell_description: str = ""

    # Optional aggregate metrics
    net_correlation: Optional[Any] = None  # Optional CorrelationType from network_analysis
    aggregate_strength: Optional[float] = None

    # Integration with existing cultural framework
    cultural_values_influence: Dict[str, float] = field(default_factory=dict)
    ceremonial_component: Optional[float] = None
    instrumental_component: Optional[float] = None

    def __post_init__(self):
        """Validate per Hayden's SFM requirements."""
        # Validate required component IDs
        if self.source_component_id is None:
            raise ValueError("source_component_id is required")
        if self.target_component_id is None:
            raise ValueError("target_component_id is required")

        # CRITICAL: Non-empty cells require descriptions per Hayden methodology
        if self.deliveries and not self.cell_description:
            raise ValueError(
                "Non-empty SFM cells require cell_description per Hayden methodology. "
                "Cell descriptions are canonical SFM deliverables, not optional metadata."
            )

    def add_delivery(self, delivery: Delivery) -> None:
        """
        Add delivery to cell.

        Supports multiple deliveries per Hayden 2008 requirement.
        Validates that cell_description exists if this is the first delivery.

        Args:
            delivery: Delivery to add

        Raises:
            ValueError: If adding first delivery without cell_description
        """
        if not self.deliveries and not self.cell_description:
            raise ValueError(
                "Cannot add delivery to cell without cell_description. "
                "Set cell_description first per Hayden methodology."
            )

        self.deliveries.append(delivery)

    def get_deliveries_by_type(self, delivery_type: str) -> List[Delivery]:
        """
        Filter deliveries by type.

        Args:
            delivery_type: Type to filter (money, energy, pollution, etc.)

        Returns:
            List of deliveries matching type
        """
        return [d for d in self.deliveries if d.delivery_type == delivery_type]

    def get_total_quantity_by_type(self, delivery_type: str) -> Optional[float]:
        """
        Sum quantities for a delivery type.

        Args:
            delivery_type: Type to sum

        Returns:
            Total quantity or None if no quantities present
        """
        deliveries = self.get_deliveries_by_type(delivery_type)
        quantities = [d.quantity for d in deliveries if d.quantity is not None]

        if not quantities:
            return None

        return sum(quantities)


@dataclass
class SFMDeliveryMatrix(Node):
    """
    Square N×N Hayden-compliant SFM where components appear on BOTH axes.

    Non-symmetric: Cell (i,j) ≠ Cell (j,i)
    Implements Hayden's input-output style matrix structure.

    Attributes:
        components: Component UUIDs appearing on both row and column axes
        cells: Cells indexed by (source_id, target_id) tuple
        matrix_scope: Scope level (local, regional, national, global)
        temporal_scope: Time range for this matrix snapshot
    """

    # Same components on rows AND columns (square matrix requirement)
    components: List[uuid.UUID] = field(default_factory=list)

    # Cells indexed by (source_id, target_id) tuple
    cells: Dict[Tuple[uuid.UUID, uuid.UUID], SFMDeliveryCell] = field(default_factory=dict)

    # Matrix metadata
    matrix_scope: Optional[str] = None
    temporal_scope: Optional[Tuple[datetime, datetime]] = None

    def get_cell(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Optional[SFMDeliveryCell]:
        """
        Get cell at (i,j).

        Args:
            source_id: Row component (source)
            target_id: Column component (target)

        Returns:
            Cell or None if not exists
        """
        return self.cells.get((source_id, target_id))

    def set_cell(self, cell: SFMDeliveryCell) -> None:
        """
        Set cell at (source, target).

        Args:
            cell: Cell to set

        Raises:
            ValueError: If source or target not in matrix components
        """
        # Validate component membership
        if cell.source_component_id not in self.components:
            raise ValueError(
                f"Source component {cell.source_component_id} not in matrix. "
                f"Add component first with add_component()."
            )
        if cell.target_component_id not in self.components:
            raise ValueError(
                f"Target component {cell.target_component_id} not in matrix. "
                f"Add component first with add_component()."
            )

        self.cells[(cell.source_component_id, cell.target_component_id)] = cell

    def add_component(self, component_id: uuid.UUID) -> None:
        """
        Add component to both axes (maintains square structure).

        Args:
            component_id: Component UUID to add
        """
        if component_id not in self.components:
            self.components.append(component_id)

    def remove_component(self, component_id: uuid.UUID) -> None:
        """
        Remove component from matrix.

        Also removes all cells involving this component.

        Args:
            component_id: Component UUID to remove
        """
        if component_id in self.components:
            self.components.remove(component_id)

        # Remove cells involving this component
        cells_to_remove = [
            (src, tgt) for (src, tgt) in self.cells.keys()
            if src == component_id or tgt == component_id
        ]

        for key in cells_to_remove:
            del self.cells[key]

    def is_square(self) -> bool:
        """
        Verify matrix is square.

        Returns:
            Always True (square by design)
        """
        return True

    def get_non_empty_cells(self) -> List[SFMDeliveryCell]:
        """
        Get all cells with deliveries.

        Returns:
            List of non-empty cells
        """
        return [cell for cell in self.cells.values() if cell.deliveries]

    def get_component_outgoing_cells(self, component_id: uuid.UUID) -> List[SFMDeliveryCell]:
        """
        Get all cells where component is source (row).

        Args:
            component_id: Component UUID

        Returns:
            List of cells where this component delivers to others
        """
        return [
            cell for (src, _), cell in self.cells.items()
            if src == component_id
        ]

    def get_component_incoming_cells(self, component_id: uuid.UUID) -> List[SFMDeliveryCell]:
        """
        Get all cells where component is target (column).

        Args:
            component_id: Component UUID

        Returns:
            List of cells where this component receives from others
        """
        return [
            cell for (_, tgt), cell in self.cells.items()
            if tgt == component_id
        ]

    def validate_structure(self) -> List[str]:
        """
        Validate matrix structure per Hayden requirements.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check square structure
        if not self.is_square():
            errors.append("Matrix is not square")

        # Check non-empty cells have descriptions
        for (src, tgt), cell in self.cells.items():
            if cell.deliveries and not cell.cell_description:
                errors.append(
                    f"Cell ({src}, {tgt}) has deliveries but no description "
                    "(required per Hayden methodology)"
                )

        # Check all cells reference valid components
        for (src, tgt) in self.cells.keys():
            if src not in self.components:
                errors.append(f"Cell references invalid source component {src}")
            if tgt not in self.components:
                errors.append(f"Cell references invalid target component {tgt}")

        return errors
