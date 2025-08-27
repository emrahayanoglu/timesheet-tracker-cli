#!/bin/bash

# Simple Debian package builder for Timesheet Tracker

set -e

echo "Building Timesheet Tracker Debian package (simple method)..."

# Check if we're in the right directory
if [ ! -f "cli.py" ] || [ ! -f "debian/control" ]; then
    echo "Error: Must be run from the timesheet-tracker source directory"
    exit 1
fi

# Create build directory structure
BUILD_DIR="timesheet-tracker_1.0.0-1"
mkdir -p "$BUILD_DIR/usr/lib/python3/dist-packages/timesheet_tracker"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/doc/timesheet-tracker"
mkdir -p "$BUILD_DIR/DEBIAN"

# Copy Python files
cp timesheet.py "$BUILD_DIR/usr/lib/python3/dist-packages/timesheet_tracker/"
cp pdf_generator.py "$BUILD_DIR/usr/lib/python3/dist-packages/timesheet_tracker/"
cp __init__.py "$BUILD_DIR/usr/lib/python3/dist-packages/timesheet_tracker/"

# Create CLI wrapper
cat > "$BUILD_DIR/usr/bin/timesheet-tracker" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/usr/lib/python3/dist-packages/timesheet_tracker')
from cli import cli
if __name__ == '__main__':
    cli()
EOF

# Copy CLI module with proper imports
sed 's/from timesheet import TimesheetManager/from timesheet_tracker.timesheet import TimesheetManager/' cli.py | \
sed 's/from pdf_generator import PDFGenerator/from timesheet_tracker.pdf_generator import PDFGenerator/' > \
"$BUILD_DIR/usr/lib/python3/dist-packages/timesheet_tracker/cli.py"

chmod +x "$BUILD_DIR/usr/bin/timesheet-tracker"

# Copy documentation
cp README.md "$BUILD_DIR/usr/share/doc/timesheet-tracker/"

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << 'EOF'
Package: timesheet-tracker
Version: 1.0.0-1
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-click, python3-reportlab, python3-dateutil
Maintainer: Your Name <your.email@example.com>
Description: Simple CLI tool for tracking working time
 A command-line tool for tracking working time and generating monthly PDF reports.
 .
 Features:
  * Start and stop work sessions
  * Track time with descriptions
  * Add work sessions retroactively
  * Add work sessions using duration format (5h 30m)
  * Delete incorrect work sessions
  * View work session history
  * Generate monthly summaries
  * Export monthly PDF reports
  * Persistent data storage
EOF

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
case "$1" in
    configure)
        if [ ! -e /usr/local/bin/timesheet ]; then
            ln -sf /usr/bin/timesheet-tracker /usr/local/bin/timesheet
        fi
        echo "Timesheet Tracker installed successfully!"
        echo "Use 'timesheet-tracker --help' or 'timesheet --help' to get started."
        ;;
esac
exit 0
EOF

# Create postrm script
cat > "$BUILD_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
case "$1" in
    remove|purge)
        if [ -L /usr/local/bin/timesheet ]; then
            rm -f /usr/local/bin/timesheet
        fi
        ;;
esac
exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/postinst"
chmod +x "$BUILD_DIR/DEBIAN/postrm"

# Build the package
echo "Building .deb package..."
dpkg-deb --build "$BUILD_DIR"

echo ""
echo "Package built successfully: ${BUILD_DIR}.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${BUILD_DIR}.deb"
echo "  sudo apt install -f  # if there are dependency issues"
echo ""
echo "To test before installing:"
echo "  dpkg-deb -I ${BUILD_DIR}.deb  # Show package info"
echo "  dpkg-deb -c ${BUILD_DIR}.deb  # List package contents"
