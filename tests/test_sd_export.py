"""
Tests for System Dynamics XMILE export functionality.

Validates that SFM delivery matrices can be exported to XMILE format
per issue #26 requirements.
"""

import xml.etree.ElementTree as ET
from examples.hayden_case_studies.nebraska_k12_finance import (
    build_nebraska_k12_matrix,
)
from graph.exporters.system_dynamics_exporter import export_to_xmile


def test_export_to_xmile_creates_file(tmp_path):
    """Test that export creates an XMILE file."""
    matrix, service = build_nebraska_k12_matrix()

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Test Model"
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_export_to_xmile_valid_xml(tmp_path):
    """Test that exported file is valid XML."""
    matrix, service = build_nebraska_k12_matrix()

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Test Model"
    )

    # Should parse without errors
    tree = ET.parse(output_file)
    root = tree.getroot()

    # Root should be xmile element
    assert root.tag.endswith("xmile")


def test_export_to_xmile_has_required_structure(tmp_path):
    """Test that XMILE has required structure per OASIS standard."""
    matrix, service = build_nebraska_k12_matrix()

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Test Model",
        model_description="Test Description"
    )

    tree = ET.parse(output_file)
    root = tree.getroot()

    # Should have header element
    header = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}header")
    assert header is not None

    # Should have sim_specs element
    sim_specs = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}sim_specs")
    assert sim_specs is not None

    # Should have model element
    model = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}model")
    assert model is not None

    # Should have variables element
    variables = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}variables")
    assert variables is not None


def test_export_to_xmile_creates_stocks_for_components(tmp_path):
    """Test that SFM components become SD stocks."""
    matrix, service = build_nebraska_k12_matrix()

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Test Model"
    )

    tree = ET.parse(output_file)
    root = tree.getroot()

    # Find all stock elements
    stocks = root.findall(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}stock")

    # Should have stocks for matrix components
    assert len(stocks) > 0

    # Stocks should have names
    stock_names = [stock.get("name") for stock in stocks]
    assert all(name is not None for name in stock_names)


def test_export_to_xmile_creates_flows_for_quantified_deliveries(tmp_path):
    """Test that deliveries with quantities become SD flows."""
    matrix, service = build_nebraska_k12_matrix()

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Test Model"
    )

    tree = ET.parse(output_file)
    root = tree.getroot()

    # Find all flow elements
    flows = root.findall(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}flow")

    # Should have flows for quantified deliveries
    # Nebraska K-12 matrix has multiple deliveries with quantities
    assert len(flows) > 0

    # Flows should have names
    flow_names = [flow.get("name") for flow in flows]
    assert all(name is not None for name in flow_names)


def test_export_to_xmile_header_contains_metadata(tmp_path):
    """Test that XMILE header contains model metadata."""
    matrix, service = build_nebraska_k12_matrix()

    model_name = "Nebraska K-12 Test"
    model_description = "Test TEEOSA model"

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name=model_name,
        model_description=model_description
    )

    tree = ET.parse(output_file)
    root = tree.getroot()

    # Check header metadata
    header = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}header")
    assert header is not None

    # Should contain name
    name_elem = header.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}name")
    if name_elem is not None:
        assert model_name in name_elem.text


def test_export_to_xmile_sim_specs_has_time_parameters(tmp_path):
    """Test that sim_specs contains time simulation parameters."""
    matrix, service = build_nebraska_k12_matrix()

    output_file = tmp_path / "test_export.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Test Model"
    )

    tree = ET.parse(output_file)
    root = tree.getroot()

    sim_specs = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}sim_specs")
    assert sim_specs is not None

    # Should have time parameters
    start = sim_specs.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}start")
    stop = sim_specs.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}stop")
    dt = sim_specs.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}dt")

    # At least one time parameter should be present
    assert start is not None or stop is not None or dt is not None


def test_export_to_xmile_nebraska_case_study(tmp_path):
    """
    Smoke test: Validate SD export on Nebraska K-12 case study.

    Per issue #26 requirements:
    - Export Nebraska K-12 matrix via SD exporter
    - Verify XMILE artifact is created
    - Verify XMILE is parseable
    - Verify expected structure (stocks, flows, metadata)

    This validates the SFM → System Dynamics handoff per Hoffman & Hayden (2007).
    """
    # Create Nebraska K-12 matrix
    matrix, service = build_nebraska_k12_matrix()

    assert matrix is not None
    assert service is not None

    # Export to XMILE
    output_file = tmp_path / "nebraska_k12_finance.xmile"
    export_to_xmile(
        matrix,
        output_file,
        service,
        model_name="Nebraska K-12 Education Finance (TEEOSA)",
        model_description="System Dynamics model of Nebraska's TEEOSA formula per Hoffman & Hayden (2007)"
    )

    # Verify file created
    assert output_file.exists()
    assert output_file.stat().st_size > 0

    # Verify parseable XML
    tree = ET.parse(output_file)
    root = tree.getroot()

    # Verify XMILE structure
    assert root.tag.endswith("xmile")

    # Verify header present
    header = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}header")
    assert header is not None

    # Verify sim_specs present
    sim_specs = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}sim_specs")
    assert sim_specs is not None

    # Verify model present
    model = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}model")
    assert model is not None

    # Verify variables present
    variables = root.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}variables")
    assert variables is not None

    # Verify stocks created (components → stocks)
    stocks = root.findall(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}stock")
    assert len(stocks) > 0

    # Nebraska K-12 matrix has 10 components per build_nebraska_k12_matrix()
    # Should have 10 stocks (one per component)
    assert len(stocks) == 10

    # Verify flows created (deliveries with quantities → flows)
    flows = root.findall(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}flow")
    assert len(flows) > 0

    # Nebraska K-12 matrix has multiple quantified deliveries
    # Should have at least some flows created
    assert len(flows) >= 3

    # Verify stock names are component labels
    stock_names = [stock.get("name") for stock in stocks]
    assert "State_Legislature" in stock_names or "State Legislature" in stock_names
    assert "School_Districts" in stock_names or "School Districts" in stock_names
    assert "Students" in stock_names

    # Verify flows have names
    for flow in flows:
        name = flow.get("name")
        assert name is not None, "Flow missing name attribute"
