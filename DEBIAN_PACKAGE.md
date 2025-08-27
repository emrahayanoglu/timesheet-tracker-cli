# Timesheet Tracker - Debian Package

This document describes how to build, install, and use the Timesheet Tracker Debian package.

## Building the Package

### Prerequisites

Install build dependencies:
```bash
sudo apt update
sudo apt install build-essential debhelper python3-all python3-setuptools dh-python
```

### Simple Build Method (Recommended)

Use the included build script:
```bash
./build-simple.sh
```

This creates `timesheet-tracker_1.0.0-1.deb` in the current directory.

### Advanced Build Method

For a more traditional Debian package build:
```bash
./build-deb.sh
```

This requires additional packages like `devscripts` and uses `debuild`.

## Installing the Package

### Install the .deb package:
```bash
sudo dpkg -i timesheet-tracker_1.0.0-1.deb
```

### Install dependencies if needed:
```bash
sudo apt install -f
```

### Alternative: Install dependencies first:
```bash
sudo apt install python3-click python3-reportlab python3-dateutil
sudo dpkg -i timesheet-tracker_1.0.0-1.deb
```

## Usage

After installation, you can use the tool with either command:
- `timesheet-tracker` (full name)
- `timesheet` (symlink for convenience)

### Basic Commands:
```bash
# Start work session
timesheet start -d "Working on project"

# Check status
timesheet status

# Stop work session
timesheet stop

# List recent sessions
timesheet list

# Add work for specific date
timesheet add --date 2025-08-25 --start 09:00 --end 17:30 --description "Client work"

# Add work using duration
timesheet addhours --date 2025-08-24 --duration "5h 30m" --description "Development"

# Delete incorrect entries
timesheet delete --index 5

# Generate monthly summary
timesheet summary

# Generate PDF report
timesheet report --month 8 --year 2025
```

## Package Information

- **Package Name**: timesheet-tracker
- **Version**: 1.0.0-1
- **Architecture**: all (pure Python)
- **Dependencies**: python3, python3-click, python3-reportlab, python3-dateutil

## Files Installed

- `/usr/bin/timesheet-tracker` - Main CLI executable
- `/usr/local/bin/timesheet` - Convenience symlink
- `/usr/lib/python3/dist-packages/timesheet_tracker/` - Python modules
- `/usr/share/doc/timesheet-tracker/README.md` - Documentation

## Uninstalling

```bash
sudo dpkg -r timesheet-tracker
```

Or to remove configuration files too:
```bash
sudo dpkg -P timesheet-tracker
```

## Package Contents Verification

Check package info:
```bash
dpkg-deb -I timesheet-tracker_1.0.0-1.deb
```

List package contents:
```bash
dpkg-deb -c timesheet-tracker_1.0.0-1.deb
```

## Distribution

The .deb package can be:
- Shared directly for manual installation
- Added to a personal APT repository
- Distributed via file sharing or internal repositories
- Installed on multiple Debian/Ubuntu systems

## Troubleshooting

### Import Errors
If you get import errors, ensure all dependencies are installed:
```bash
sudo apt install python3-click python3-reportlab python3-dateutil
```

### Permission Issues
The package should install with proper permissions, but if needed:
```bash
sudo chmod +x /usr/bin/timesheet-tracker
```

### Data Location
Work session data is stored as `timesheet_data.json` in the directory where you run the command.
