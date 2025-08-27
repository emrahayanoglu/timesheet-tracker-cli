#!/bin/bash

# Setup script for Timesheet Tracker CLI
echo "🔧 Setting up Timesheet Tracker CLI..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
echo "📋 Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

# Make scripts executable
chmod +x timesheet
chmod +x timesheet.sh

echo "✅ Setup complete!"
echo ""
echo "Usage examples:"
echo "  ./timesheet.sh start -d 'Working on project'"
echo "  ./timesheet.sh stop"
echo "  ./timesheet.sh status"
echo "  ./timesheet.sh list"
echo "  ./timesheet.sh report --month 8 --year 2025"
echo ""
echo "Or use the Python script directly:"
echo "  .venv/bin/python cli.py start -d 'Working on project'"
