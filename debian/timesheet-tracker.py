#!/usr/bin/env python3
"""
Timesheet Tracker CLI entry point for Debian package
"""

import sys
import os

# Add the package directory to Python path
sys.path.insert(0, '/usr/lib/python3/dist-packages/timesheet_tracker')

# Import and run the CLI
try:
    from cli import cli
    if __name__ == '__main__':
        cli()
except ImportError as e:
    print(f"Error importing timesheet tracker: {e}")
    print("Please ensure the package is properly installed.")
    sys.exit(1)
