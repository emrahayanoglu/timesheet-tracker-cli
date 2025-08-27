#!/bin/bash

# Timesheet CLI wrapper script
# This script makes it easier to run the timesheet tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
CLI_SCRIPT="$SCRIPT_DIR/cli.py"

# Check if virtual environment exists
if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Run the CLI with all arguments
cd "$SCRIPT_DIR"
"$PYTHON_CMD" "$CLI_SCRIPT" "$@"
