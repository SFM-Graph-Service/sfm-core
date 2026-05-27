#!/bin/bash
# Quick script to run all Hayden case study examples
set -e

echo "=========================================="
echo "Running SFM Core Example Demonstrations"
echo "=========================================="
echo ""
echo "Based on Hayden's published research:"
echo "  - Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix"
echo "    Approach to Policy Analysis and Program Evaluation. Springer."
echo ""

EXAMPLES_DIR="examples/hayden_case_studies"

# Function to run an example
run_example() {
    local script=$1
    local name=$2

    echo "=========================================="
    echo "Running: $name"
    echo "=========================================="

    if python "$script" 2>&1; then
        echo ""
        echo "✓ $name completed successfully"

        # Show generated file
        local xlsx_file="${script%.py}.xlsx"
        if [ -f "$xlsx_file" ]; then
            local size=$(du -h "$xlsx_file" | cut -f1)
            echo "  Generated: $xlsx_file ($size)"
        fi
    else
        echo ""
        echo "✗ $name failed"
        return 1
    fi
    echo ""
}

# Check if examples directory exists
if [ ! -d "$EXAMPLES_DIR" ]; then
    echo "✗ Examples directory not found: $EXAMPLES_DIR"
    exit 1
fi

# Track results
PASSED=0
FAILED=0

# Run each example
echo "Running examples from: $EXAMPLES_DIR"
echo ""

if run_example "$EXAMPLES_DIR/nebraska_k12_finance.py" "Nebraska K-12 Education Finance"; then
    ((PASSED++))
else
    ((FAILED++))
fi

if run_example "$EXAMPLES_DIR/radioactive_waste.py" "Low-Level Radioactive Waste Policy"; then
    ((PASSED++))
else
    ((FAILED++))
fi

if run_example "$EXAMPLES_DIR/director_networks.py" "Corporate Director Networks"; then
    ((PASSED++))
else
    ((FAILED++))
fi

if run_example "$EXAMPLES_DIR/clean_air_act_1970.py" "Clean Air Act 1970"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Summary
echo "=========================================="
echo "Example Demonstrations Summary"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ All examples completed successfully!"
    echo ""
    echo "Generated files:"
    ls -lh $EXAMPLES_DIR/*.xlsx 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    echo ""
    echo "Open Excel files to view:"
    echo "  - Matrix View (N×N delivery matrix)"
    echo "  - Cell Descriptions (narrative deliverables)"
    echo "  - Delivery Details (tabular data)"
    exit 0
else
    echo "⚠ Some examples failed"
    exit 1
fi
