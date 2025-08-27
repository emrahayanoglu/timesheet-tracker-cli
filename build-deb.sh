#!/bin/bash

# Build script for Timesheet Tracker Debian package

set -e

echo "Building Timesheet Tracker Debian package..."

# Check if we're in the right directory
if [ ! -f "cli.py" ] || [ ! -f "timesheet.py" ]; then
    echo "Error: Must be run from the timesheet-tracker source directory"
    exit 1
fi

# Check for required build dependencies
echo "Checking build dependencies..."
BUILD_DEPS="debhelper python3-all python3-setuptools dh-python"
missing_deps=""

for dep in $BUILD_DEPS; do
    if ! dpkg -l "$dep" >/dev/null 2>&1; then
        missing_deps="$missing_deps $dep"
    fi
done

if [ -n "$missing_deps" ]; then
    echo "Missing build dependencies:$missing_deps"
    echo "Install them with: sudo apt install$missing_deps"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf debian/timesheet-tracker/
rm -f ../timesheet-tracker_*.deb
rm -f ../timesheet-tracker_*.changes
rm -f ../timesheet-tracker_*.buildinfo

# Build the package
echo "Building package..."
debuild -us -uc -b

echo ""
echo "Package built successfully!"
echo "Install with: sudo dpkg -i ../timesheet-tracker_*.deb"
echo "Or install dependencies first: sudo apt install -f"
