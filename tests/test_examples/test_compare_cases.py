"""
Smoke test for compare_cases.py cross-case comparison script.

Verifies that compare_cases.py runs successfully and produces a comparison
table with expected structure.
"""

import subprocess
import sys
from pathlib import Path


def test_compare_cases_runs_successfully():
    """Test that compare_cases.py executes without errors."""
    script_path = Path(__file__).parent.parent.parent / "examples" / "hayden_case_studies" / "compare_cases.py"

    assert script_path.exists(), f"compare_cases.py not found at {script_path}"

    # Run the script
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=120  # 2 minute timeout
    )

    # Should exit successfully
    assert result.returncode == 0, f"compare_cases.py failed with:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    # Check for expected output
    output = result.stdout

    # Should contain comparison table header
    assert "HAYDEN CASE STUDIES COMPARISON TABLE" in output, "Missing comparison table header"

    # Should contain expected case study names
    assert "Clean Air Act 1970" in output, "Missing Clean Air Act case study"
    assert "Corporate Director Networks" in output, "Missing Director Networks case study"
    assert "Low-Level Radioactive Waste" in output, "Missing Radioactive Waste case study"
    assert "Nebraska K-12 Finance" in output, "Missing Nebraska K-12 case study"

    # Should contain column headers
    expected_columns = ["Comp", "Cells", "Deliv", "Types", "Quant%", "Circ", "C/I", "Levels", "Conf", "Feed", "Crit", "Multi"]
    for column in expected_columns:
        assert column in output, f"Missing expected column: {column}"

    # Should contain insights section
    assert "CROSS-CASE INSIGHTS" in output, "Missing insights section"
    assert "Most Complex:" in output, "Missing complexity insight"
    assert "Most Quantified:" in output, "Missing quantification insight"

    # Should contain legend
    assert "Column Legend:" in output, "Missing column legend"

    print("✓ compare_cases.py runs successfully and produces expected output")


def test_compare_cases_produces_valid_metrics():
    """Test that compare_cases.py produces valid metric values."""
    script_path = Path(__file__).parent.parent.parent / "examples" / "hayden_case_studies" / "compare_cases.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, "Script should run successfully"

    output = result.stdout

    # Extract table section (between COMPARISON TABLE header and Column Legend)
    table_start = output.find("Case Study")
    table_end = output.find("Column Legend:")
    assert table_start > 0 and table_end > table_start, "Could not find table section"

    table_section = output[table_start:table_end]

    # Check that each case study has a row with numeric values
    # Expected: Component count > 0, Cell count > 0, Delivery count > 0
    for case_name in ["Clean Air Act 1970", "Corporate Director Networks", "Low-Level Radioactive Waste", "Nebraska K-12 Finance"]:
        assert case_name in table_section, f"Case {case_name} not in table"

        # Find the row for this case
        row_start = table_section.find(case_name)
        row_end = table_section.find("\n", row_start)
        row = table_section[row_start:row_end]

        # Split by whitespace and check that we have numeric values
        parts = row.split()

        # After case name, we should have numeric columns
        # Index 0-2: Case name (may be split), then numeric values start
        # Looking for component count (should be >= 5)
        numeric_parts = [p for p in parts if p.replace(".", "").replace("-", "").isdigit() or p == "N/A"]

        assert len(numeric_parts) >= 10, f"Row for {case_name} doesn't have enough numeric columns: {row}"

    print("✓ compare_cases.py produces valid metrics for all case studies")


def test_compare_cases_identifies_most_complex():
    """Test that compare_cases.py correctly identifies the most complex case."""
    script_path = Path(__file__).parent.parent.parent / "examples" / "hayden_case_studies" / "compare_cases.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, "Script should run successfully"

    output = result.stdout

    # Check insights section
    insights_start = output.find("CROSS-CASE INSIGHTS")
    assert insights_start > 0, "Insights section not found"

    insights_section = output[insights_start:]

    # Should identify a specific case as most complex
    assert "Most Complex:" in insights_section, "Most Complex designation missing"

    # Should have details about complexity
    assert "deliveries" in insights_section.lower(), "Missing delivery count in insights"
    assert "cells" in insights_section.lower(), "Missing cell count in insights"

    print("✓ compare_cases.py provides meaningful cross-case insights")
