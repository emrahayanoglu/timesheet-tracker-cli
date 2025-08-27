# Timesheet Tracker CLI

A simple command-line tool for tracking working time and generating monthly PDF reports.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ⏰ Start and stop work sessions
- 📊 Track time with descriptions  
- 📋 View work session history
- ➕ Add work sessions retroactively
- ⏱️ Add work sessions using duration format (5h 30m)
- 🗑️ Delete incorrect work sessions
- 📈 Generate monthly summaries
- 📄 Export monthly PDF reports
- 💾 Persistent data storage

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make the CLI executable:
```bash
chmod +x cli.py
```

## Usage

### Starting a work session
```bash
python cli.py start
python cli.py start -d "Working on project X"
```

### Adding work for a specific date
```bash
# Add a work session for yesterday
python cli.py add --date 2025-08-25 --start 09:00 --end 17:30 --description "Client work"

# Add a short session with minimal info
python cli.py add -d 2025-08-24 -s 14:00 -e 16:00

# Add overnight shift (end time is next day)
python cli.py add -d 2025-08-23 -s 22:00 -e 02:00 --desc "Night shift"
```

### Adding work using duration
```bash
# Add 5 hours 30 minutes (starts at 09:00 by default)
python cli.py addhours --date 2025-08-25 --duration "5h 30m" --description "Long coding session"

# Add 2 hours starting at 2 PM
python cli.py addhours -d 2025-08-24 -dur "2h" -s "14:00" --desc "Meeting"

# Add 45 minutes only
python cli.py addhours -d 2025-08-23 -dur "45m" --desc "Quick task"

# Add 1 hour 15 minutes
python cli.py addhours -d 2025-08-22 -dur "1h 15m" -s "16:00"
```

### Stopping a work session
```bash
python cli.py stop
```

### Check current status
```bash
python cli.py status
```

### View work sessions
```bash
# View recent sessions
python cli.py list

# View sessions for specific month
python cli.py list --month 8 --year 2025

# Limit number of entries shown
python cli.py list --limit 10
```

### Delete work sessions
```bash
# Interactive delete (shows list and prompts for index)
python cli.py delete

# Delete specific entry by index
python cli.py delete --index 5

# Delete without confirmation prompt
python cli.py delete --index 5 --confirm
```

### Generate monthly summary
```bash
python cli.py summary
```

### Generate PDF report
```bash
# Generate report for current month
python cli.py report --month 8 --year 2025

# Specify output filename
python cli.py report --month 8 --year 2025 --output my_timesheet.pdf
```

## Commands

- `start` - Start a new work session
- `stop` - Stop the current work session
- `add` - Add work session for a specific date (with start/end times)
- `addhours` - Add work session using duration format (e.g., "5h 30m")
- `delete` - Delete a work session by index
- `status` - Show current session status
- `list` - List work sessions
- `summary` - Show summary for current month
- `report` - Generate PDF report for specified month

## Data Storage

Work sessions are stored in `timesheet_data.json` in the current directory. This file contains:
- Completed work sessions
- Current active session (if any)

## Example Workflow

```bash
# Start working
python cli.py start -d "Development work"

# Check status
python cli.py status

# Stop working
python cli.py stop

# Add work from yesterday (forgot to track) - using time range
python cli.py add --date 2025-08-25 --start 09:00 --end 17:00 --description "Client work"

# Add work using duration format
python cli.py addhours --date 2025-08-24 --duration "5h 30m" --description "Coding session"

# Delete incorrect entry
python cli.py delete --index 3

# View current work
python cli.py list

# Generate monthly report
python cli.py report --month 8 --year 2025
```

## Requirements

- Python 3.6+
- click
- reportlab
- python-dateutil

## Installation Methods

### Method 1: Debian Package (Recommended for Debian/Ubuntu)
```bash
# Download or build the .deb package
sudo dpkg -i timesheet-tracker_*.deb
sudo apt install -f  # Install dependencies if needed
```

### Method 2: From Source
```bash
git clone https://github.com/yourusername/timesheet-tracker.git
cd timesheet-tracker
pip install -r requirements.txt
```

### Method 3: Using pip (if published)
```bash
pip install timesheet-tracker
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Building Debian Package

See [DEBIAN_PACKAGE.md](DEBIAN_PACKAGE.md) for detailed instructions on building and distributing the Debian package.
