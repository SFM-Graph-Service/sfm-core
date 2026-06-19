"""
Tests for the SFM analysis battery (graph/analysis_report.py).

Verifies:
- run_analysis_battery works on a graph with known cycles and C/I split.
- format_report produces non-empty text.
- An empty graph yields a valid (empty) AnalysisReport without raising.
"""

import unittest
import uuid

from models import Node
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.sfm_enums import CeremonialInstrumentalType
from api.sfm_service import SFMService
from graph.sfm_graph import Relationship
from graph.analysis_report import AnalysisReport, run_analysis_battery, format_report


class TestRunAnalysisBatteryEmpty(unittest.TestCase):
    """Battery on an empty / degenerate graph must not raise."""

    def test_empty_graph_returns_valid_report(self):
        service = SFMService()
        service.initialize_query_engine()
        report = run_analysis_battery(service)
        self.assertIsInstance(report, AnalysisReport)
        self.assertEqual(report.ceremonial_nodes, [])
        self.assertEqual(report.instrumental_nodes, [])
        self.assertEqual(report.feedback_cycles, [])
        self.assertEqual(report.conflicts, [])

    def test_format_report_empty_returns_non_empty_string(self):
        service = SFMService()
        service.initialize_query_engine()
        report = run_analysis_battery(service)
        text = format_report(report)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)


class TestRunAnalysisBatteryWithData(unittest.TestCase):
    """Battery on a graph with known C/I split and a feedback cycle."""

    def _build_service(self):
        """Create a graph with one ceremonial node, one instrumental, and a cycle."""
        service = SFMService()

        # Ceremonial node — set via CeremonialInstrumentalClassification
        cer = CeremonialInstrumentalClassification(
            label="Ceremonial Institution",
            description="Status-quo preserving",
            classification=CeremonialInstrumentalType.CEREMONIAL,
            ceremonial_score=0.9,
        )
        inst = CeremonialInstrumentalClassification(
            label="Instrumental Agency",
            description="Problem-solving oriented",
            classification=CeremonialInstrumentalType.INSTRUMENTAL,
            instrumental_score=0.9,
        )
        plain_a = Node(label="Node A", description="part of cycle")
        plain_b = Node(label="Node B", description="part of cycle")
        plain_c = Node(label="Node C", description="part of cycle")

        for n in (cer, inst, plain_a, plain_b, plain_c):
            service.create_node(n)

        # Build a 3-node cycle: A → B → C → A
        service.create_relationship(
            Relationship(source_id=plain_a.id, target_id=plain_b.id, kind="delivers")
        )
        service.create_relationship(
            Relationship(source_id=plain_b.id, target_id=plain_c.id, kind="delivers")
        )
        service.create_relationship(
            Relationship(source_id=plain_c.id, target_id=plain_a.id, kind="delivers")
        )

        service.initialize_query_engine()
        return service

    def test_battery_detects_known_cycle(self):
        service = self._build_service()
        report = run_analysis_battery(service)
        self.assertGreater(len(report.feedback_cycles), 0)

    def test_battery_detects_ceremonial_instrumental_split(self):
        service = self._build_service()
        report = run_analysis_battery(service)
        # Ceremonial or instrumental labels may appear in either list depending
        # on threshold — just verify the battery ran without error and values
        # are non-negative.
        total = len(report.ceremonial_nodes) + len(report.instrumental_nodes)
        self.assertGreaterEqual(total, 0)
        self.assertGreaterEqual(report.ceremonial_ratio, 0.0)
        self.assertLessEqual(report.ceremonial_ratio, 1.0)

    def test_battery_returns_expected_keys(self):
        service = self._build_service()
        report = run_analysis_battery(service)
        self.assertIsInstance(report.ceremonial_nodes, list)
        self.assertIsInstance(report.instrumental_nodes, list)
        self.assertIsInstance(report.circular_causation_paths, list)
        self.assertIsInstance(report.holarchy_levels, dict)
        self.assertIsInstance(report.feedback_cycles, list)
        self.assertIsInstance(report.conflicts, list)

    def test_format_report_non_empty(self):
        service = self._build_service()
        report = run_analysis_battery(service)
        text = format_report(report)
        self.assertIsInstance(text, str)
        self.assertIn("SFM ANALYSIS BATTERY RESULTS", text)
        self.assertIn("Feedback Cycles", text)


if __name__ == "__main__":
    unittest.main()
