#!/usr/bin/env python3

"""
Test Edit Functionality
======================
"""

from timesheet_sqlite import TimesheetManager
from datetime import datetime, date, time

print("Testing edit functionality...")

# Create test manager
manager = TimesheetManager('test_edit_timesheet.db')

# Add a test entry
test_date = date(2025, 8, 30)
success = manager.add_manual_entry(test_date, "09:00", "17:00", "Original description")
print(f"✅ Added test entry: {success}")

# Get the entry ID
entries_with_ids = manager.get_entries_with_ids()
if entries_with_ids:
    entry_id, entry = entries_with_ids[0]
    print(f"✅ Retrieved entry ID: {entry_id}")
    print(f"   Original: {entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')} ({entry.duration_hours():.1f}h)")
    print(f"   Description: {entry.description}")
    
    # Test updating the entry
    new_start = datetime.combine(test_date, time(10, 0))
    new_end = datetime.combine(test_date, time(18, 30))
    new_description = "Updated description"
    
    success = manager.update_entry_by_id(entry_id, new_start, new_end, new_description)
    print(f"✅ Updated entry: {success}")
    
    # Verify the update
    updated_entry = manager.get_entry_by_id(entry_id)
    if updated_entry:
        print(f"   Updated: {updated_entry.start_time.strftime('%H:%M')} - {updated_entry.end_time.strftime('%H:%M')} ({updated_entry.duration_hours():.1f}h)")
        print(f"   Description: {updated_entry.description}")
    
    # Test deletion
    success = manager.db.delete_entry_by_id(entry_id)
    print(f"✅ Deleted entry: {success}")
    
else:
    print("❌ No entries found")

# Cleanup
import os
if os.path.exists('test_edit_timesheet.db'):
    os.remove('test_edit_timesheet.db')
    print("🧹 Test database cleaned up")

print("\n🎉 Edit functionality test completed!")
print("\nWeb interface features:")
print("1. Edit button on each entry in /entries page")
print("2. Edit form at /edit_entry/<id>")
print("3. Real-time duration calculation")
print("4. Quick duration buttons")
print("5. Delete functionality from edit page")
