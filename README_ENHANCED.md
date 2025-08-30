# Timesheet Tracker CLI - Enhanced Version

A powerful command-line and web-based time tracking application with SQLite3 backend.

## 🚀 NEW FEATURES

### 1. SQLite3 Database Backend
- **Replaced JSON with SQLite3** for better performance, reliability, and data integrity
- Automatic migration from existing JSON data
- Better query performance for large datasets
- Support for complex operations and reporting

### 2. Web Interface
- **Modern web dashboard** accessible at `http://localhost:5000`
- **Real-time session tracking** with live updates
- **Interactive calendar view** of work sessions
- **Visual reports** with charts and statistics
- **Quick entry forms** for adding time entries
- **Mobile-responsive design** with Bootstrap

## 📦 Installation

### Prerequisites
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

### Setup
```bash
# Clone or navigate to the project directory
cd timesheet-tracker-cli

# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies
- `click>=8.0.0` - CLI framework
- `reportlab>=3.6.0` - PDF generation
- `python-dateutil>=2.8.0` - Date utilities
- `flask>=2.0.0` - Web framework (NEW)

## 🔄 Migration from JSON

Your existing JSON data will be automatically migrated when you first run the application:

```bash
python3 cli.py migrate
```

The original `timesheet_data.json` will be backed up as `timesheet_data.json.backup`.

## 📋 CLI Usage

### Basic Commands (Enhanced)
```bash
# Session management
python3 cli.py start [-d "description"]
python3 cli.py stop
python3 cli.py status

# Entry management
python3 cli.py list [-m month] [-y year] [-l limit]
python3 cli.py add -d YYYY-MM-DD -s HH:MM -e HH:MM [--desc "description"]
python3 cli.py addhours -d YYYY-MM-DD -dur "8h 30m" [-s HH:MM] [--desc "description"]
python3 cli.py delete [-i index] [-y]

# Reporting
python3 cli.py summary
python3 cli.py report -m month -y year [-o output.pdf]

# NEW COMMANDS
python3 cli.py migrate    # Migrate JSON data to SQLite
python3 cli.py web        # Launch web interface
```

## 🌐 Web Interface

### Launch Web Interface
```bash
python3 cli.py web
```

Then open your browser to: `http://localhost:5000`

### Web Features

#### Dashboard
- **Live session status** with real-time duration updates
- **Monthly statistics** and overview cards
- **Recent entries** quick view
- **Start/Stop sessions** with description support

#### Entries Management
- **List all entries** with pagination
- **Add new entries** using time ranges or duration
- **Quick duration buttons** (4h, 6h, 8h, etc.)
- **Entry deletion** with confirmation

#### Calendar View
- **Monthly calendar** with color-coded work days
- **Daily hour totals** displayed on each date
- **Entry details** on hover/click
- **Navigation** between months

#### Reports & Analytics
- **Visual charts** showing daily and weekly patterns
- **Detailed entry tables** with export options
- **Monthly summaries** with statistics
- **PDF generation** (when reportlab is installed)

### API Endpoints

The web interface provides a REST API:

```
GET  /api/session/status      # Get current session status
POST /api/session/start       # Start new session
POST /api/session/stop        # Stop current session
POST /api/entry/add          # Add new entry
DELETE /api/entry/<id>/delete # Delete entry
GET  /api/stats              # Get statistics
```

## 📁 File Structure

```
timesheet-tracker-cli/
├── cli.py                  # Enhanced CLI with new commands
├── timesheet.py           # Original timesheet manager (legacy)
├── timesheet_sqlite.py    # NEW: SQLite-based timesheet manager
├── database.py            # NEW: Database management layer
├── web_app.py            # NEW: Flask web application
├── pdf_generator.py      # PDF report generator
├── requirements.txt      # Updated dependencies
├── timesheet.db          # NEW: SQLite database file
├── templates/            # NEW: HTML templates
│   ├── base.html
│   ├── index.html        # Dashboard
│   ├── entries.html      # Entry list
│   ├── add_entry.html    # Add entry form
│   ├── calendar.html     # Calendar view
│   └── reports.html      # Reports page
└── setup_test.py         # NEW: Setup verification script
```

## 🔧 Architecture Changes

### Database Layer
- **DatabaseManager class** handles all SQLite operations
- **Automatic table creation** and indexing
- **Migration utilities** for JSON data
- **Optimized queries** for performance

### Backward Compatibility
- **Existing CLI commands** work unchanged
- **Automatic JSON migration** on first run
- **Same data structures** in Python code
- **PDF generation** still supported

### Web Layer
- **Flask application** with RESTful API
- **Bootstrap 5** for responsive design
- **Chart.js** for data visualization
- **Real-time updates** via JavaScript

## 🚀 Quick Start

1. **Test the basic functionality:**
   ```bash
   python3 setup_test.py
   ```

2. **Start tracking time (CLI):**
   ```bash
   python3 cli.py start -d "Working on project"
   # Do some work...
   python3 cli.py stop
   ```

3. **Launch web interface:**
   ```bash
   python3 cli.py web
   ```

4. **View your data:**
   - CLI: `python3 cli.py list`
   - Web: Open `http://localhost:5000`

## 📊 Benefits of SQLite3 Migration

1. **Performance**: Faster queries, especially for large datasets
2. **Reliability**: ACID transactions, data integrity
3. **Scalability**: Better handling of concurrent access
4. **Features**: Complex queries, aggregations, indexing
5. **Standards**: SQL-based, widely supported format

## 🌟 Web Interface Benefits

1. **Visual Overview**: Dashboard with charts and statistics
2. **Easy Entry**: Quick forms for adding time entries
3. **Calendar View**: See your work patterns at a glance
4. **Real-time Updates**: Live session tracking
5. **Mobile Friendly**: Works on phones and tablets
6. **No Setup**: Just run `python3 cli.py web` and go

## 🔮 Future Enhancements

- **Multi-user support** with authentication
- **Project/category tracking** for better organization
- **Time tracking integrations** (GitHub, Jira, etc.)
- **Advanced reporting** with custom date ranges
- **Data export** in multiple formats
- **API authentication** for third-party integrations

## 🐛 Troubleshooting

### Common Issues

1. **Flask not found**: Install with `pip install flask`
2. **Permission errors**: Use virtual environment
3. **Port already in use**: Web interface uses port 5000
4. **Database locked**: Only one active session at a time

### Getting Help

1. Check the setup test: `python3 setup_test.py`
2. Verify dependencies: `pip list`
3. Check database: `python3 cli.py migrate`

---

**Enjoy your enhanced timesheet tracking experience!** 🎉
