#!/bin/bash
# Test script to validate fresh installation following README instructions
set -e

echo "=========================================="
echo "Testing SFM Core Fresh Installation"
echo "=========================================="

# Test 1: Check Python version
echo ""
echo "Test 1: Checking Python version..."
python3 --version
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✓ Python 3.10+ detected"
else
    echo "✗ Python 3.10+ required"
    exit 1
fi

# Test 2: Check system dependencies
echo ""
echo "Test 2: Checking system dependencies..."
if command -v dot >/dev/null 2>&1; then
    echo "✓ graphviz installed"
else
    echo "⚠ graphviz not installed (optional for visualization)"
fi

# Test 3: Verify requirements.txt exists
echo ""
echo "Test 3: Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "✓ requirements.txt found"
    echo "  Dependencies: $(wc -l < requirements.txt | tr -d ' ') lines"
else
    echo "✗ requirements.txt not found"
    exit 1
fi

# Test 4: Verify setup.py exists
echo ""
echo "Test 4: Checking setup.py..."
if [ -f "setup.py" ]; then
    echo "✓ setup.py found"
else
    echo "✗ setup.py not found"
    exit 1
fi

# Test 5: Check if already in venv
echo ""
echo "Test 5: Checking virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ Already in virtual environment: $VIRTUAL_ENV"
    VENV_ACTIVE=1
else
    echo "⚠ Not in virtual environment (will use current Python)"
    VENV_ACTIVE=0
fi

# Test 6: Verify import works
echo ""
echo "Test 6: Testing basic import..."
if python3 -c "from api.sfm_service import SFMService; print('✓ Import successful')"; then
    echo "✓ SFM service importable"
else
    echo "✗ Cannot import SFM service - check installation"
    exit 1
fi

# Test 7: Verify models import
echo ""
echo "Test 7: Testing models import..."
if python3 -c "from models import Node; from models.delivery_matrix import Delivery, SFMDeliveryMatrix; print('✓ Models import successful')"; then
    echo "✓ Core models importable"
else
    echo "✗ Cannot import models"
    exit 1
fi

# Test 8: Quick functional test
echo ""
echo "Test 8: Quick functional test..."
python3 << 'EOF'
from api.sfm_service import SFMService
from models import Node

service = SFMService()
node = service.create_node(Node(label="Test Node", description="Test"))
assert node.id is not None, "Node creation failed"
stats = service.get_statistics()
assert stats.total_nodes >= 1, "Statistics not working"
print("✓ Basic functionality working")
EOF

# Test 9: Check example files exist
echo ""
echo "Test 9: Checking example files..."
EXAMPLES_DIR="examples/hayden_case_studies"
if [ -d "$EXAMPLES_DIR" ]; then
    EXAMPLE_COUNT=$(find "$EXAMPLES_DIR" -name "*.py" | wc -l)
    echo "✓ Examples directory found: $EXAMPLE_COUNT Python files"
else
    echo "⚠ Examples directory not found"
fi

# Test 10: Test suite availability
echo ""
echo "Test 10: Checking test suite..."
if [ -d "tests" ]; then
    TEST_COUNT=$(find tests -name "test_*.py" | wc -l)
    echo "✓ Tests directory found: $TEST_COUNT test files"
else
    echo "⚠ Tests directory not found"
fi

echo ""
echo "=========================================="
echo "Installation Validation Summary"
echo "=========================================="
echo "✓ All critical tests passed"
echo ""
echo "Next steps:"
echo "  1. Run test suite: pytest tests/"
echo "  2. Run examples: python examples/hayden_case_studies/nebraska_k12_finance.py"
echo "  3. Start API server: uvicorn api.rest.app:app --reload"
echo ""
