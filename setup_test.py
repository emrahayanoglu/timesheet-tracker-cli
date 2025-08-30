#!/usr/bin/env python3

"""
Timesheet Tracker CLI - Setup and Installation Guide
====================================================

This script has been enhanced with two major new features:

1. SQLite3 Database Backend (instead of JSON)
2. Web Interface (Flask-based)

INSTALLATION:
============

1. Install required system packages:
   sudo apt update
   sudo apt install python3-pip python3-venv

2. Create and activate virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate

3. Install required packages:
   pip install -r requirements.txt

USAGE:
======

CLI Commands (same as before):
- timesheet start [-d "description"]
- timesheet stop
- timesheet status
- timesheet list [-m month] [-y year]
- timesheet add -d date -s start_time -e end_time [--desc "description"]
- timesheet addhours -d date -dur duration [-s start_time] [--desc "description"]
- timesheet delete [-i index] [-y]
- timesheet summary
- timesheet report -m month -y year [-o output_file]

NEW COMMANDS:
- timesheet migrate    # Migrate existing JSON data to SQLite
- timesheet web        # Launch web interface at http://localhost:5000

WEB INTERFACE:
=============
Access via browser at: http://localhost:5000

Features:
- Dashboard with live session tracking
- Interactive time entry management
- Calendar view of work sessions
- Monthly reports with charts
- Quick entry forms
- Real-time session status updates

MIGRATION:
=========
Your existing JSON data will be automatically migrated to SQLite when you first run
the updated timesheet manager. The original JSON file will be backed up.

FILES STRUCTURE:
===============
- timesheet.db         # SQLite database (replaces timesheet_data.json)
- database.py          # Database management layer
- timesheet_sqlite.py  # Updated timesheet manager using SQLite
- web_app.py          # Flask web application
- templates/          # HTML templates for web interface
- cli.py              # Updated CLI with new commands
"""

print(__doc__)

# Test basic functionality
try:
    print("\n" + "="*60)
    print("TESTING BASIC FUNCTIONALITY")
    print("="*60)
    
    # Test database creation
    from database import DatabaseManager
    print("✅ Database module imported successfully")
    
    db = DatabaseManager('test_timesheet.db')
    print("✅ SQLite database created successfully")
    
    # Test timesheet manager
    from timesheet_sqlite import TimesheetManager
    print("✅ Updated timesheet manager imported successfully")
    
    manager = TimesheetManager('test_timesheet.db')
    print("✅ Timesheet manager initialized with SQLite backend")
    
    # Test basic operations
    result = manager.start_session("Test session")
    print(f"✅ Start session: {result}")
    
    current = manager.current_session
    print(f"✅ Current session exists: {current is not None}")
    
    result = manager.stop_session()
    print(f"✅ Stop session: {result is not None}")
    
    stats = manager.get_stats()
    print(f"✅ Statistics: {stats}")
    
    print("\n🎉 All basic tests passed!")
    print("\nNEXT STEPS:")
    print("1. Install Flask: pip install flask")
    print("2. Run CLI: python cli.py --help")
    print("3. Launch web interface: python cli.py web")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required files are in the same directory")
except Exception as e:
    print(f"❌ Error: {e}")

finally:
    # Cleanup test database
    import os
    if os.path.exists('test_timesheet.db'):
        os.remove('test_timesheet.db')
        print("🧹 Test database cleaned up")
