"""
Tests for System Dynamics XMILE export.

Tests cover:
- XMILE format generation
- Stocks (components) creation
- Flows (deliveries) creation
- XML structure validation
"""

import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from graph.exporters import export_to_xmile


class TestXMILEExporter:
    """Test XMILE export for delivery matrices."""

    def setup_method(self):
        """Setup test service and sample delivery matrix."""
        # Create service
        self.service = SFMService()

        # Create sample components
        self.comp_a = Node(label="Component A", description="First component")
        self.comp_b = Node(label="Component B", description="Second component")
        self.comp_c = Node(label="Component C", description="Third component")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)
        self.service.create_node(self.comp_c)

        # Create delivery matrix
        self.matrix = self.service.create_delivery_matrix(
            label="Test SD Model",
            description="Test System Dynamics Model",
            components=[self.comp_a.id, self.comp_b.id, self.comp_c.id]
        )

        # Add quantified delivery: A → B
        money_delivery = Delivery(
            delivery_type="money",
            delivery_content="Annual funding",
            quantity=1_000_000,
            units="USD/year",
            temporal_rate="annual"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            money_delivery,
            cell_description="A funds B annually"
        )

        # Add quantified delivery: B → C
        energy_delivery = Delivery(
            delivery_type="energy",
            delivery_content="Service delivery",
            quantity=500,
            units="hours/month",
            temporal_rate="monthly"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_b.id,
            self.comp_c.id,
            energy_delivery,
            cell_description="B provides services to C"
        )

        # Add non-quantified delivery: A → C (should be ignored in flows)
        rule_delivery = Delivery(
            delivery_type="rule",
            delivery_content="Regulations"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_c.id,
            rule_delivery,
            cell_description="A regulates C"
        )

    def test_export_creates_file(self):
        """Test XMILE file is created."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            assert tmp_path.exists()
            assert tmp_path.stat().st_size > 0

        finally:
            tmp_path.unlink()

    def test_xmile_has_valid_root(self):
        """Test XMILE has valid root element."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            assert root.tag == "{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}xmile"
            assert root.get("version") == "1.0"

        finally:
            tmp_path.unlink()

    def test_xmile_has_header(self):
        """Test XMILE has header section."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service,
                model_name="Test Model"
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            # Find header (namespace aware)
            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            header = root.find("xmile:header", ns)

            assert header is not None

            name = header.find("xmile:name", ns)
            assert name is not None
            assert name.text == "Test Model"

        finally:
            tmp_path.unlink()

    def test_xmile_has_sim_specs(self):
        """Test XMILE has simulation specifications."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            sim_specs = root.find("xmile:sim_specs", ns)

            assert sim_specs is not None
            assert sim_specs.get("method") == "Euler"
            assert sim_specs.get("time_units") == "year"

            start = sim_specs.find("xmile:start", ns)
            stop = sim_specs.find("xmile:stop", ns)
            dt = sim_specs.find("xmile:dt", ns)

            assert start is not None
            assert stop is not None
            assert dt is not None

        finally:
            tmp_path.unlink()

    def test_xmile_has_stocks_for_components(self):
        """Test XMILE creates stocks for each component."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            model = root.find("xmile:model", ns)
            variables = model.find("xmile:variables", ns)

            stocks = variables.findall("xmile:stock", ns)

            # Should have 3 stocks (one per component)
            assert len(stocks) >= 3

            stock_names = [s.get("name") for s in stocks]
            assert "Component_A" in stock_names
            assert "Component_B" in stock_names
            assert "Component_C" in stock_names

        finally:
            tmp_path.unlink()

    def test_xmile_has_flows_for_quantified_deliveries(self):
        """Test XMILE creates flows for quantified deliveries."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            model = root.find("xmile:model", ns)
            variables = model.find("xmile:variables", ns)

            flows = variables.findall("xmile:flow", ns)

            # Should have 2 flows (only quantified deliveries)
            assert len(flows) == 2

            # Check flow names contain type
            flow_names = [f.get("name") for f in flows]
            assert any("money" in name for name in flow_names)
            assert any("energy" in name for name in flow_names)

        finally:
            tmp_path.unlink()

    def test_xmile_flow_equations(self):
        """Test XMILE flows have equations."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            model = root.find("xmile:model", ns)
            variables = model.find("xmile:variables", ns)

            flows = variables.findall("xmile:flow", ns)

            for flow in flows:
                eqn = flow.find("xmile:eqn", ns)
                assert eqn is not None
                assert eqn.text is not None
                # Should contain numeric value
                assert any(char.isdigit() for char in eqn.text)

        finally:
            tmp_path.unlink()

    def test_xmile_auxiliaries_for_delivery_counts(self):
        """Test XMILE creates auxiliaries for delivery type counts."""
        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                self.matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            model = root.find("xmile:model", ns)
            variables = model.find("xmile:variables", ns)

            auxs = variables.findall("xmile:aux", ns)

            # Should have auxiliaries for delivery type counts
            assert len(auxs) >= 3  # money, energy, rule

            aux_names = [a.get("name") for a in auxs]
            assert any("total_money" in name for name in aux_names)
            assert any("total_energy" in name for name in aux_names)
            assert any("total_rule" in name for name in aux_names)

        finally:
            tmp_path.unlink()

    def test_xmile_with_empty_matrix(self):
        """Test XMILE export with empty matrix (no deliveries)."""
        empty_matrix = self.service.create_delivery_matrix(
            label="Empty Model",
            components=[self.comp_a.id, self.comp_b.id]
        )

        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                empty_matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            model = root.find("xmile:model", ns)
            variables = model.find("xmile:variables", ns)

            # Should have stocks but no flows
            stocks = variables.findall("xmile:stock", ns)
            flows = variables.findall("xmile:flow", ns)

            assert len(stocks) == 2
            assert len(flows) == 0

        finally:
            tmp_path.unlink()

    def test_xmile_sanitizes_names(self):
        """Test XMILE sanitizes component names for XML compliance."""
        # Create component with special characters
        special_comp = Node(label="Component (A) - Special!", description="Test")
        self.service.create_node(special_comp)

        matrix = self.service.create_delivery_matrix(
            label="Test",
            components=[special_comp.id]
        )

        with tempfile.NamedTemporaryFile(suffix=".xmile", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            export_to_xmile(
                matrix,
                tmp_path,
                self.service
            )

            tree = ET.parse(tmp_path)
            root = tree.getroot()

            ns = {"xmile": "http://docs.oasis-open.org/xmile/ns/XMILE/v1.0"}
            model = root.find("xmile:model", ns)
            variables = model.find("xmile:variables", ns)

            stocks = variables.findall("xmile:stock", ns)

            # Should have sanitized name (only alphanumeric + underscores)
            stock_name = stocks[0].get("name")
            assert all(c.isalnum() or c == "_" for c in stock_name)

        finally:
            tmp_path.unlink()
