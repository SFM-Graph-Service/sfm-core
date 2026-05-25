#!/bin/bash
# Helper script to run sfm-core tests with virtual environment

# Activate the virtual environment
source /home/gdabbs/repos/sfm-core/.venv/bin/activate

# Set PYTHONPATH to include the current directory
export PYTHONPATH=/home/gdabbs/repos/sfm-core:$PYTHONPATH

# Run pytest with any arguments passed to this script
pytest "$@"
