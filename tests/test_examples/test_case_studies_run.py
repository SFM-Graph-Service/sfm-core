"""Smoke tests for Hayden case studies with analysis battery integration."""

from graph.analysis_report import run_analysis_battery
from examples.hayden_case_studies.clean_air_act_1970 import (
    create_clean_air_act_matrix,
    create_clean_air_temporal_clock,
)
from examples.hayden_case_studies.clean_air_act_doughnut import (
    create_clean_air_act_doughnut_case,
)
from examples.hayden_case_studies.compare_cases import compare_cases, format_comparison_table
from examples.hayden_case_studies.director_networks import create_director_network_matrix
from examples.hayden_case_studies.nebraska_k12_finance import build_nebraska_k12_matrix
from examples.hayden_case_studies.radioactive_waste import create_llrw_matrix


def _assert_report_shape(report):
    assert isinstance(report.ceremonial_nodes, list)
    assert isinstance(report.instrumental_nodes, list)
    assert isinstance(report.feedback_cycles, list)
    assert isinstance(report.conflicts, list)
    assert report.node_count > 0


def test_clean_air_case_runs_with_analysis_report():
    _, service = create_clean_air_act_matrix()
    create_clean_air_temporal_clock(service)
    report = run_analysis_battery(service)
    _assert_report_shape(report)


def test_director_network_case_runs_with_analysis_report():
    _, service = create_director_network_matrix()
    report = run_analysis_battery(service)
    _assert_report_shape(report)


def test_nebraska_case_runs_with_analysis_report():
    _, service = build_nebraska_k12_matrix()
    report = run_analysis_battery(service)
    _assert_report_shape(report)


def test_radioactive_waste_case_runs_with_analysis_report():
    _, service = create_llrw_matrix()
    report = run_analysis_battery(service)
    _assert_report_shape(report)


def test_doughnut_coupled_case_runs_end_to_end():
    _, _, report, doughnut_report = create_clean_air_act_doughnut_case()
    _assert_report_shape(report)
    assert doughnut_report.boundaries
    boundary_names = [b.boundary_label.lower() for b in doughnut_report.boundaries]
    assert any("air pollution" in name for name in boundary_names)


def test_compare_cases_outputs_expected_columns():
    rows = compare_cases()
    assert len(rows) == 4
    table = format_comparison_table(rows)
    assert "study" in table
    assert "cycles" in table
    assert "ci_ratio" in table
    assert "levels" in table
    assert "conflicts" in table
