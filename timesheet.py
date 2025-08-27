import json
import os
import re
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional

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
    def __init__(self, data_file: str = 'timesheet_data.json'):
        self.data_file = data_file
        self.entries: List[TimeEntry] = []
        self.current_session: Optional[TimeEntry] = None
        self.load_data()
    
    def load_data(self):
        """Load timesheet data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.entries = [TimeEntry.from_dict(entry) for entry in data.get('entries', [])]
                    
                    # Check for ongoing session
                    current_data = data.get('current_session')
                    if current_data:
                        self.current_session = TimeEntry.from_dict(current_data)
            except (json.JSONDecodeError, KeyError):
                self.entries = []
                self.current_session = None
    
    def save_data(self):
        """Save timesheet data to JSON file"""
        data = {
            'entries': [entry.to_dict() for entry in self.entries],
            'current_session': self.current_session.to_dict() if self.current_session else None
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_session(self, description: str = "") -> bool:
        """Start a new work session"""
        if self.current_session:
            return False  # Session already active
        
        self.current_session = TimeEntry(datetime.now(), description=description)
        self.save_data()
        return True
    
    def stop_session(self) -> Optional[TimeEntry]:
        """Stop the current work session"""
        if not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        self.entries.append(self.current_session)
        completed_session = self.current_session
        self.current_session = None
        self.save_data()
        return completed_session
    
    def get_current_session_duration(self) -> int:
        """Get current session duration in minutes"""
        if not self.current_session:
            return 0
        return int((datetime.now() - self.current_session.start_time).total_seconds() / 60)
    
    def get_entries_for_month(self, year: int, month: int) -> List[TimeEntry]:
        """Get all completed entries for a specific month"""
        return [
            entry for entry in self.entries
            if entry.end_time and entry.start_time.year == year and entry.start_time.month == month
        ]
    
    def get_total_hours_for_month(self, year: int, month: int) -> float:
        """Get total hours worked in a specific month"""
        entries = self.get_entries_for_month(year, month)
        return sum(entry.duration_hours() for entry in entries)
    
    def add_manual_entry(self, date_obj: date, start_time_str: str, end_time_str: str, description: str = "") -> bool:
        """Add a manual time entry for a specific date"""
        try:
            # Parse time strings (format: HH:MM)
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))
            
            # Create datetime objects for the specified date
            start_datetime = datetime.combine(date_obj, time(start_hour, start_min))
            end_datetime = datetime.combine(date_obj, time(end_hour, end_min))
            
            # Handle case where end time is next day (e.g., night shift)
            if end_datetime <= start_datetime:
                from datetime import timedelta
                end_datetime += timedelta(days=1)
            
            # Create and add the entry
            entry = TimeEntry(start_datetime, end_datetime, description)
            self.entries.append(entry)
            self.save_data()
            return True
            
        except (ValueError, IndexError):
            return False
    
    def add_duration_entry(self, date_obj: date, duration_str: str, start_time_str: str = "09:00", description: str = "") -> bool:
        """Add a work entry using duration format (e.g., '5h 30m', '2h', '45m')"""
        try:
            # Parse duration string
            hours, minutes = self._parse_duration(duration_str)
            if hours == 0 and minutes == 0:
                return False
            
            # Parse start time
            start_hour, start_min = map(int, start_time_str.split(':'))
            start_datetime = datetime.combine(date_obj, time(start_hour, start_min))
            
            # Calculate end time
            end_datetime = start_datetime + timedelta(hours=hours, minutes=minutes)
            
            # Create and add the entry
            entry = TimeEntry(start_datetime, end_datetime, description)
            self.entries.append(entry)
            self.save_data()
            return True
            
        except (ValueError, IndexError):
            return False
    
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
        """Delete a work entry by index (1-based)"""
        if 1 <= entry_index <= len(self.entries):
            self.entries.pop(entry_index - 1)
            self.save_data()
            return True
        return False
    
    def get_entries_with_index(self) -> List[tuple]:
        """Get all entries with their 1-based index for display"""
        return [(i + 1, entry) for i, entry in enumerate(self.entries)]
    
    def get_daily_summary_for_month(self, year: int, month: int) -> Dict[int, float]:
        """Get daily hour totals for a specific month"""
        entries = self.get_entries_for_month(year, month)
        daily_hours = {}
        
        for entry in entries:
            day = entry.start_time.day
            if day not in daily_hours:
                daily_hours[day] = 0
            daily_hours[day] += entry.duration_hours()
        
        return daily_hours
