"""
System Dynamics XMILE Exporter for Hayden-compliant Delivery Matrices.

Exports Social Fabric Matrix delivery matrices to XMILE format (System Dynamics
Interchange Standard) per Hayden's usage of system dynamics modeling.

Reference:
    Hoffman & Hayden (2007): Used ithink for Nebraska education finance modeling
    OASIS XMILE 1.0: https://www.oasis-open.org/committees/xmile/

Mapping:
    - Components → Stocks (levels)
    - Deliveries with quantities → Flows (rates)
    - Feedback loops → System dynamics loops
    - Temporal rates → Flow equations
"""

from pathlib import Path
from typing import Any, List, Optional
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def export_to_xmile(
    matrix: Any,  # SFMDeliveryMatrix type
    filepath: Path,
    service: Any,  # SFMService type
    model_name: Optional[str] = None,
    model_description: Optional[str] = None
) -> None:
    """
    Export delivery matrix to XMILE format.

    Creates a basic system dynamics model where:
    - Components become stocks
    - Deliveries with quantities become flows between stocks
    - Temporal rates inform flow equations

    Args:
        matrix: SFMDeliveryMatrix instance to export
        filepath: Path to save .xmile file
        service: SFMService instance for reading component nodes
        model_name: Name of the model (defaults to matrix label)
        model_description: Model description (defaults to matrix description)

    Example:
        >>> export_to_xmile(
        ...     matrix=matrix,
        ...     filepath=Path("nebraska_k12.xmile"),
        ...     service=service,
        ...     model_name="Nebraska K-12 Finance"
        ... )
    """
    # Build component label mapping
    component_labels = {}
    for comp_id in matrix.components:
        node = service.repository.read_node(comp_id)
        component_labels[comp_id] = node.label if node else str(comp_id)

    # Create XMILE root
    xmile = ET.Element("xmile", {
        "version": "1.0",
        "xmlns": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"
    })

    # Header
    header = ET.SubElement(xmile, "header")
    ET.SubElement(header, "vendor").text = "SFM Core"
    ET.SubElement(header, "product", {
        "version": "1.0",
        "lang": "en"
    }).text = "Social Fabric Matrix System Dynamics Exporter"
    ET.SubElement(header, "name").text = model_name or matrix.label or "SFM Model"

    # Simulation specs (default settings)
    sim_specs = ET.SubElement(xmile, "sim_specs", {
        "method": "Euler",
        "time_units": "year"
    })
    ET.SubElement(sim_specs, "start").text = "0"
    ET.SubElement(sim_specs, "stop").text = "10"
    ET.SubElement(sim_specs, "dt").text = "0.25"

    # Model
    model = ET.SubElement(xmile, "model")
    ET.SubElement(model, "name").text = model_name or matrix.label or "SFM Model"
    if model_description or matrix.description:
        ET.SubElement(model, "doc").text = model_description or matrix.description

    # Variables section
    variables = ET.SubElement(model, "variables")

    # Create stocks for each component
    stock_positions = _calculate_stock_positions(len(matrix.components))

    for idx, comp_id in enumerate(matrix.components):
        stock = ET.SubElement(variables, "stock", {
            "name": _sanitize_name(component_labels[comp_id])
        })
        ET.SubElement(stock, "doc").text = f"Component: {component_labels[comp_id]}"
        ET.SubElement(stock, "eqn").text = "0"  # Initial value

        # Display information (for visual layout)
        ET.SubElement(stock, "display", {
            "x": str(stock_positions[idx][0]),
            "y": str(stock_positions[idx][1]),
            "color": "blue"
        })

    # Create flows for deliveries with quantities
    flow_count = 0
    for (src_id, tgt_id), cell in matrix.cells.items():
        if not cell.deliveries:
            continue

        src_label = component_labels[src_id]
        tgt_label = component_labels[tgt_id]

        for delivery in cell.deliveries:
            if delivery.quantity is None:
                continue

            flow_count += 1
            flow_name = f"flow_{flow_count}_{delivery.delivery_type}"

            flow = ET.SubElement(variables, "flow", {
                "name": _sanitize_name(flow_name)
            })
            ET.SubElement(flow, "doc").text = f"{src_label} → {tgt_label}: {delivery.delivery_content[:100]}"

            # Flow equation based on quantity and temporal rate
            equation = _build_flow_equation(delivery)
            ET.SubElement(flow, "eqn").text = equation

            # Non-negative constraint
            ET.SubElement(flow, "non_negative")

            # Display information
            ET.SubElement(flow, "display", {
                "color": _get_flow_color(delivery.delivery_type)
            })

    # Auxiliaries for delivery types (informational only)
    delivery_type_counts = {}
    for cell in matrix.cells.values():
        for delivery in cell.deliveries:
            dtype = delivery.delivery_type
            delivery_type_counts[dtype] = delivery_type_counts.get(dtype, 0) + 1

    for dtype, count in delivery_type_counts.items():
        aux = ET.SubElement(variables, "aux", {
            "name": f"total_{dtype}_deliveries"
        })
        ET.SubElement(aux, "doc").text = f"Total number of {dtype} deliveries in matrix"
        ET.SubElement(aux, "eqn").text = str(count)

    # Write to file
    _write_pretty_xml(xmile, filepath)


def _sanitize_name(name: str) -> str:
    """
    Sanitize name for XMILE compatibility.

    Args:
        name: Original name

    Returns:
        Sanitized name (alphanumeric + underscores)
    """
    # Replace spaces and special chars with underscores
    sanitized = "".join(
        c if c.isalnum() or c == "_" else "_"
        for c in name
    )

    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")

    # Ensure doesn't start with number
    if sanitized and sanitized[0].isdigit():
        sanitized = "v_" + sanitized

    return sanitized or "unnamed"


def _build_flow_equation(delivery: Any) -> str:
    """
    Build flow equation from delivery attributes.

    Args:
        delivery: Delivery instance

    Returns:
        XMILE equation string
    """
    quantity = delivery.quantity or 0

    # Adjust for temporal rate
    if delivery.temporal_rate == "annual":
        # Annual flow, convert to per-timestep
        return f"{quantity}"
    elif delivery.temporal_rate == "monthly":
        # Monthly flow
        return f"{quantity * 12}"
    elif delivery.temporal_rate == "continuous":
        # Continuous flow
        return f"{quantity}"
    elif delivery.temporal_rate == "event-triggered":
        # Event-triggered, use PULSE or conditional
        return f"PULSE({quantity}, 1)"
    else:
        # Default: use raw quantity
        return f"{quantity}"


def _get_flow_color(delivery_type: str) -> str:
    """
    Get color for flow based on delivery type.

    Args:
        delivery_type: Type of delivery

    Returns:
        Color name for XMILE
    """
    color_map = {
        "money": "green",
        "rule": "red",
        "authority": "orange",
        "energy": "blue",
        "pollution": "brown",
        "information": "purple",
    }
    return color_map.get(delivery_type, "black")


def _calculate_stock_positions(n: int) -> List[tuple]:
    """
    Calculate positions for stocks in circular layout.

    Args:
        n: Number of stocks

    Returns:
        List of (x, y) position tuples
    """
    import math

    positions = []
    radius = 200
    center_x = 300
    center_y = 300

    for i in range(n):
        angle = (2 * math.pi * i) / n
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions.append((int(x), int(y)))

    return positions


def _write_pretty_xml(element: ET.Element, filepath: Path) -> None:
    """
    Write XML element to file with pretty formatting.

    Args:
        element: XML element to write
        filepath: Destination file path
    """
    # Convert to string
    xml_str = ET.tostring(element, encoding="unicode")

    # Pretty print
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split("\n") if line.strip()]
    pretty_xml = "\n".join(lines)

    # Write to file
    filepath.write_text(pretty_xml, encoding="utf-8")
