import json
import os
import re
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional
from database import DatabaseManager

class TimeEntry:
    def __init__(self, start_time: datetime, end_time: Optional[datetime] = None, description: str = ""):
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TimeEntry':
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        return cls(start_time, end_time, data.get('description', ''))
    
    def duration_minutes(self) -> int:
        if not self.end_time:
            return 0
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def duration_hours(self) -> float:
        return self.duration_minutes() / 60

class TimesheetManager:
    def __init__(self, data_file: str = 'timesheet.db'):
        # Use SQLite database instead of JSON
        self.db = DatabaseManager(data_file)
        
        # Check for legacy JSON file and migrate if exists
        json_file = 'timesheet_data.json'
        if os.path.exists(json_file):
            self.db.migrate_from_json(json_file)
        
        # Maintain compatibility properties
        self.data_file = data_file
    
    @property
    def entries(self) -> List[TimeEntry]:
        """Get all entries for backward compatibility"""
        return self.db.get_all_entries()
    
    @property
    def current_session(self) -> Optional[TimeEntry]:
        """Get current session for backward compatibility"""
        session_data = self.db.get_current_session()
        if session_data:
            return TimeEntry(session_data[1], None, session_data[2])
        return None
    
    def load_data(self):
        """Legacy method - no longer needed with SQLite"""
        pass
    
    def save_data(self):
        """Legacy method - no longer needed with SQLite (auto-committed)"""
        pass
    
    def start_session(self, description: str = "") -> bool:
        """Start a new work session"""
        return self.db.start_session(description)
    
    def stop_session(self) -> Optional[TimeEntry]:
        """Stop the current work session"""
        return self.db.stop_session()
    
    def get_current_session_duration(self) -> int:
        """Get current session duration in minutes"""
        return self.db.get_current_session_duration()
    
    def get_entries_for_month(self, year: int, month: int) -> List[TimeEntry]:
        """Get all completed entries for a specific month"""
        return self.db.get_entries_for_month(year, month)
    
    def get_total_hours_for_month(self, year: int, month: int) -> float:
        """Get total hours worked in a specific month"""
        return self.db.get_total_hours_for_month(year, month)
    
    def add_manual_entry(self, date_obj: date, start_time_str: str, end_time_str: str, description: str = "") -> bool:
        """Add a manual time entry for a specific date"""
        return self.db.add_manual_entry(date_obj, start_time_str, end_time_str, description)
    
    def add_duration_entry(self, date_obj: date, duration_str: str, start_time_str: str = "09:00", description: str = "") -> bool:
        """Add a work entry using duration format (e.g., '5h 30m', '2h', '45m')"""
        return self.db.add_duration_entry(date_obj, duration_str, start_time_str, description)
    
    def _parse_duration(self, duration_str: str) -> tuple:
        """Parse duration string like '5h 30m', '2h', '45m' and return (hours, minutes)"""
        duration_str = duration_str.lower().strip()
        hours = 0
        minutes = 0
        
        # Pattern to match hours and minutes
        hour_match = re.search(r'(\d+)h', duration_str)
        minute_match = re.search(r'(\d+)m', duration_str)
        
        if hour_match:
            hours = int(hour_match.group(1))
        if minute_match:
            minutes = int(minute_match.group(1))
        
        # Validate reasonable values
        if hours > 24 or minutes > 59:
            return (0, 0)
        
        return (hours, minutes)
    
    def delete_entry(self, entry_index: int) -> bool:
        """Delete a work entry by index (1-based) - for backward compatibility"""
        # Get entries with IDs for proper deletion
        entries_with_ids = self.db.get_entries_with_ids()
        
        if 1 <= entry_index <= len(entries_with_ids):
            # Sort by start time to match display order
            sorted_entries = sorted(entries_with_ids, key=lambda x: x[1].start_time)
            entry_id = sorted_entries[entry_index - 1][0]
            return self.db.delete_entry_by_id(entry_id)
        return False
    
    def get_entries_with_index(self) -> List[tuple]:
        """Get all entries with their 1-based index for display"""
        entries = self.db.get_all_entries()
        # Sort by start time and add 1-based index
        sorted_entries = sorted(entries, key=lambda x: x.start_time)
        return [(i + 1, entry) for i, entry in enumerate(sorted_entries)]
    
    def get_daily_summary_for_month(self, year: int, month: int) -> Dict[int, float]:
        """Get daily hour totals for a specific month"""
        return self.db.get_daily_summary_for_month(year, month)
    
    # New methods for enhanced functionality
    def get_entries_for_date(self, target_date: date) -> List[TimeEntry]:
        """Get all entries for a specific date"""
        return self.db.get_entries_for_date(target_date)
    
    def get_entries_by_date(self, target_date: date) -> List[TimeEntry]:
        """Get all entries for a specific date (alias for API compatibility)"""
        return self.get_entries_for_date(target_date)
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        return self.db.get_stats()
    
    def get_recent_entries(self, limit: int = 20) -> List[TimeEntry]:
        """Get recent entries with limit"""
        return self.db.get_all_entries(limit=limit)
    
    # New methods for entry editing
    def get_entry_by_id(self, entry_id: int) -> Optional[TimeEntry]:
        """Get a specific entry by ID"""
        result = self.db.get_entry_by_id(entry_id)
        return result[1] if result else None
    
    def update_entry_by_id(self, entry_id: int, start_time: datetime, end_time: datetime, description: str = "") -> bool:
        """Update an existing entry"""
        return self.db.update_entry_by_id(entry_id, start_time, end_time, description)
    
    def get_entries_with_ids(self) -> List[tuple]:
        """Get all entries with their database IDs"""
        return self.db.get_entries_with_ids()
