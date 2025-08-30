#!/usr/bin/env python3

"""
Test PDF Generation with Web Interface
=====================================
"""

import sys
import os

# Add test data
print("Setting up test data...")

# Import the managers
from timesheet_sqlite import TimesheetManager
from datetime import datetime, date

# Create test manager
manager = TimesheetManager('test_pdf_timesheet.db')

# Add some test entries for current month
current_date = datetime.now().date()
manager.add_manual_entry(current_date, "09:00", "17:00", "Test work session 1")
manager.add_manual_entry(current_date.replace(day=current_date.day-1 if current_date.day > 1 else 1), 
                        "10:00", "18:00", "Test work session 2")

print("✅ Test data created")

# Test PDF generation
try:
    from pdf_generator import PDFGenerator
    
    generator = PDFGenerator()
    output_file = "test_report.pdf"
    
    generator.generate_monthly_report(manager, current_date.year, current_date.month, output_file)
    
    if os.path.exists(output_file):
        print(f"✅ PDF generated successfully: {output_file}")
        print(f"   File size: {os.path.getsize(output_file)} bytes")
        
        # Clean up
        os.remove(output_file)
        print("🧹 Test PDF cleaned up")
    else:
        print("❌ PDF file was not created")
        
except Exception as e:
    print(f"❌ Error generating PDF: {e}")

finally:
    # Clean up test database
    if os.path.exists('test_pdf_timesheet.db'):
        os.remove('test_pdf_timesheet.db')
        print("🧹 Test database cleaned up")

print("\n🎉 PDF generation test completed!")
print("\nNow you can:")
print("1. Run the web interface: python3 cli.py web")
print("2. Go to Reports page")
print("3. Click 'Generate PDF' button")
