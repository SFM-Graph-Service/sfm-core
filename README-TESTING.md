# Testing Guide for sfm-core

## Quick Start

### Option 1: Use the helper script (Recommended) ✅
```bash
cd /home/gdabbs/repos/sfm-core

# Run all tests
./run_tests.sh

# Run with verbose output
./run_tests.sh -v

# Run with coverage
./run_tests.sh --cov=models --cov=graph --cov=api --cov=data --cov-report=term-missing

# Run specific tests
./run_tests.sh tests/test_models/
./run_tests.sh tests/test_models/test_base_nodes.py
```

The script automatically:
- Activates the `.venv` virtual environment
- Sets the PYTHONPATH correctly
- Runs pytest with your arguments

### Option 2: Activate venv manually
```bash
cd /home/gdabbs/repos/sfm-core
source .venv/bin/activate
export PYTHONPATH=/home/gdabbs/repos/sfm-core:$PYTHONPATH
pytest
```

### Option 3: Add alias to your shell profile
Add this line to your `~/.bashrc` or `~/.zshrc`:
```bash
alias sfm-test='cd /home/gdabbs/repos/sfm-core && source .venv/bin/activate && export PYTHONPATH=/home/gdabbs/repos/sfm-core:$PYTHONPATH && pytest'
```

Reload your shell, then run:
```bash
sfm-test
sfm-test -v
sfm-test --cov=models
```

## Common Test Commands

```bash
# Run all tests
./run_tests.sh

# Run all tests with verbose output
./run_tests.sh -v

# Run with coverage report
./run_tests.sh --cov=models --cov=graph --cov=api --cov=data --cov-report=term-missing

# Run only Phase 1 (model) tests
./run_tests.sh tests/test_models/ -v

# Run only Phase 2 (graph/service) tests
./run_tests.sh tests/test_graph/ tests/test_service/ -v

# Run a specific test file
./run_tests.sh tests/test_models/test_base_nodes.py -v

# Run a specific test
./run_tests.sh tests/test_models/test_base_nodes.py::test_node_creation -v

# Stop at first failure
./run_tests.sh -x

# Run tests matching a keyword
./run_tests.sh -k "ceremonial" -v

# Generate HTML coverage report
./run_tests.sh --cov=. --cov-report=html
# Then open htmlcov/index.html in your browser
```

## Current Test Status

**Total: 349 tests**
- ✅ Passing: 316 (91%)
- ❌ Failing: 33 (9%)

**Phase 1 (Models):** 238/238 passing ✅
**Phase 2 (Graph/Service):** 78/111 (70%)

Most failures are due to test fixtures needing updates to match model validation requirements (e.g., MatrixCell requires institution_id).

## Troubleshooting

### "ModuleNotFoundError: No module named 'networkx'"
- Install dependencies: `pip install -r requirements.txt`

### "ModuleNotFoundError: No module named 'graph'"
- Use the `./run_tests.sh` script OR
- Set PYTHONPATH: `export PYTHONPATH=/home/gdabbs/repos/sfm-core:$PYTHONPATH`

### "ModuleNotFoundError: No module named 'models'"
- Same as above - PYTHONPATH needs to be set to the project root
