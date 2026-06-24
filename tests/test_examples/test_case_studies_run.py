"""
Smoke tests for Hayden case studies.

Verifies each case study builder runs end-to-end and produces a non-empty
AnalysisReport with expected keys. No network or Neo4j dependencies.

Tests for issue #19: Run analysis battery in all four Hayden case studies.
"""

import unittest

from examples.hayden_case_studies import clean_air_act_1970
from examples.hayden_case_studies import director_networks
from examples.hayden_case_studies import nebraska_k12
from examples.hayden_case_studies import radioactive_waste
from graph.analysis_report import run_analysis_battery, AnalysisReport


class TestCleanAirActCaseStudy(unittest.TestCase):
    """Smoke test for Clean Air Act 1970 case study."""

    def test_clean_air_act_matrix_builds_and_analyzes(self):
        """Clean Air Act matrix builder should complete and produce valid analysis report."""
        # Build matrix
        matrix, service = clean_air_act_1970.create_clean_air_act_matrix()

        # Verify matrix created
        self.assertIsNotNone(matrix)
        self.assertIsNotNone(service)

        # Run analysis battery
        report = run_analysis_battery(service)

        # Verify report structure
        self.assertIsInstance(report, AnalysisReport)
        self.assertIsInstance(report.ceremonial_nodes, list)
        self.assertIsInstance(report.instrumental_nodes, list)
        self.assertIsInstance(report.circular_causation_paths, list)
        self.assertIsInstance(report.holarchy_levels, dict)
        self.assertIsInstance(report.feedback_cycles, list)
        self.assertIsInstance(report.conflicts, list)
        self.assertIsInstance(report.ceremonial_ratio, float)
        self.assertIsInstance(report.node_count, int)

        # Verify non-empty graph
        self.assertGreater(report.node_count, 0, "Clean Air Act matrix should have nodes")

        # Verify at least one analysis ran
        has_results = (
            len(report.ceremonial_nodes) > 0 or
            len(report.instrumental_nodes) > 0 or
            len(report.circular_causation_paths) > 0 or
            len(report.holarchy_levels) > 0 or
            len(report.feedback_cycles) > 0 or
            len(report.conflicts) > 0 or
            report.temporal_snapshots is not None
        )
        self.assertTrue(has_results, "Analysis battery should produce some results")


class TestDirectorNetworksCaseStudy(unittest.TestCase):
    """Smoke test for director networks case study."""

    def test_director_networks_matrix_builds_and_analyzes(self):
        """Director networks matrix builder should complete and produce valid analysis report."""
        # Build matrix
        matrix, service = director_networks.create_director_network_matrix()

        # Verify matrix created
        self.assertIsNotNone(matrix)
        self.assertIsNotNone(service)

        # Run analysis battery
        report = run_analysis_battery(service)

        # Verify report structure
        self.assertIsInstance(report, AnalysisReport)
        self.assertIsInstance(report.ceremonial_nodes, list)
        self.assertIsInstance(report.instrumental_nodes, list)
        self.assertIsInstance(report.circular_causation_paths, list)
        self.assertIsInstance(report.holarchy_levels, dict)
        self.assertIsInstance(report.feedback_cycles, list)
        self.assertIsInstance(report.conflicts, list)

        # Verify non-empty graph
        self.assertGreater(report.node_count, 0, "Director networks matrix should have nodes")

        # Verify at least one analysis ran
        has_results = (
            len(report.ceremonial_nodes) > 0 or
            len(report.instrumental_nodes) > 0 or
            len(report.circular_causation_paths) > 0 or
            len(report.holarchy_levels) > 0 or
            len(report.feedback_cycles) > 0 or
            len(report.conflicts) > 0
        )
        self.assertTrue(has_results, "Analysis battery should produce some results")


class TestNebraskaK12CaseStudy(unittest.TestCase):
    """Smoke test for Nebraska K-12 finance case study."""

    def test_nebraska_k12_matrix_builds_and_analyzes(self):
        """Nebraska K-12 matrix builder should complete and produce valid analysis report."""
        # Import service
        from api.sfm_service import SFMService
        service = SFMService()

        # Build matrix
        matrix, components = nebraska_k12.create_nebraska_k12_matrix(service)

        # Verify matrix created
        self.assertIsNotNone(matrix)
        self.assertIsNotNone(service)

        # Run analysis battery
        report = run_analysis_battery(service)

        # Verify report structure
        self.assertIsInstance(report, AnalysisReport)
        self.assertIsInstance(report.ceremonial_nodes, list)
        self.assertIsInstance(report.instrumental_nodes, list)
        self.assertIsInstance(report.circular_causation_paths, list)
        self.assertIsInstance(report.holarchy_levels, dict)
        self.assertIsInstance(report.feedback_cycles, list)
        self.assertIsInstance(report.conflicts, list)

        # Verify non-empty graph
        self.assertGreater(report.node_count, 0, "Nebraska K-12 matrix should have nodes")

        # Verify at least one analysis ran
        has_results = (
            len(report.ceremonial_nodes) > 0 or
            len(report.instrumental_nodes) > 0 or
            len(report.circular_causation_paths) > 0 or
            len(report.holarchy_levels) > 0 or
            len(report.feedback_cycles) > 0 or
            len(report.conflicts) > 0
        )
        self.assertTrue(has_results, "Analysis battery should produce some results")


class TestRadioactiveWasteCaseStudy(unittest.TestCase):
    """Smoke test for radioactive waste case study."""

    def test_radioactive_waste_matrix_builds_and_analyzes(self):
        """Radioactive waste matrix builder should complete and produce valid analysis report."""
        # Build matrix
        matrix, service = radioactive_waste.create_llrw_matrix()

        # Verify matrix created
        self.assertIsNotNone(matrix)
        self.assertIsNotNone(service)

        # Run analysis battery
        report = run_analysis_battery(service)

        # Verify report structure
        self.assertIsInstance(report, AnalysisReport)
        self.assertIsInstance(report.ceremonial_nodes, list)
        self.assertIsInstance(report.instrumental_nodes, list)
        self.assertIsInstance(report.circular_causation_paths, list)
        self.assertIsInstance(report.holarchy_levels, dict)
        self.assertIsInstance(report.feedback_cycles, list)
        self.assertIsInstance(report.conflicts, list)

        # Verify non-empty graph
        self.assertGreater(report.node_count, 0, "Radioactive waste matrix should have nodes")

        # Verify at least one analysis ran
        has_results = (
            len(report.ceremonial_nodes) > 0 or
            len(report.instrumental_nodes) > 0 or
            len(report.circular_causation_paths) > 0 or
            len(report.holarchy_levels) > 0 or
            len(report.feedback_cycles) > 0 or
            len(report.conflicts) > 0
        )
        self.assertTrue(has_results, "Analysis battery should produce some results")


if __name__ == "__main__":
    unittest.main()
