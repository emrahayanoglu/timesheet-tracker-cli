#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple
from timesheet import TimeEntry

class DatabaseManager:
    def __init__(self, db_path: str = 'timesheet.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create time_entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    description TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create current_session table for tracking active session
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS current_session (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    start_time TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_time_entries_start_time 
                ON time_entries(start_time)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_time_entries_date 
                ON time_entries(date(start_time))
            ''')
            
            conn.commit()
    
    def migrate_from_json(self, json_file: str = 'timesheet_data.json'):
        """Migrate existing JSON data to SQLite database"""
        if not os.path.exists(json_file):
            return False
        
        try:
            import json
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Migrate completed entries
            entries = data.get('entries', [])
            for entry_data in entries:
                entry = TimeEntry.from_dict(entry_data)
                if entry.end_time:  # Only migrate completed entries
                    self.add_completed_entry(entry)
            
            # Migrate current session if exists
            current_data = data.get('current_session')
            if current_data:
                current_entry = TimeEntry.from_dict(current_data)
                self.start_session(current_entry.description, current_entry.start_time)
            
            # Backup the original JSON file
            backup_file = f"{json_file}.backup"
            os.rename(json_file, backup_file)
            print(f"✅ Migrated data from {json_file} to SQLite. Original file backed up as {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error migrating from JSON: {str(e)}")
            return False
    
    def add_completed_entry(self, entry: TimeEntry):
        """Add a completed time entry to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO time_entries (start_time, end_time, description)
                VALUES (?, ?, ?)
            ''', (
                entry.start_time.isoformat(),
                entry.end_time.isoformat() if entry.end_time else None,
                entry.description
            ))
            conn.commit()
            return cursor.lastrowid
    
    def start_session(self, description: str = "", start_time: datetime = None) -> bool:
        """Start a new work session"""
        if self.get_current_session():
            return False  # Session already active
        
        if start_time is None:
            start_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO current_session (id, start_time, description)
                VALUES (1, ?, ?)
            ''', (start_time.isoformat(), description))
            conn.commit()
        
        return True
    
    def stop_session(self) -> Optional[TimeEntry]:
        """Stop the current work session and move it to completed entries"""
        current_session = self.get_current_session()
        if not current_session:
            return None
        
        end_time = datetime.now()
        entry = TimeEntry(current_session[1], end_time, current_session[2])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add to completed entries
            cursor.execute('''
                INSERT INTO time_entries (start_time, end_time, description)
                VALUES (?, ?, ?)
            ''', (
                entry.start_time.isoformat(),
                entry.end_time.isoformat(),
                entry.description
            ))
            
            # Remove from current session
            cursor.execute('DELETE FROM current_session WHERE id = 1')
            conn.commit()
        
        return entry
    
    def get_current_session(self) -> Optional[Tuple[int, datetime, str]]:
        """Get the current active session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, start_time, description FROM current_session WHERE id = 1
            ''')
            row = cursor.fetchone()
            
            if row:
                return (row[0], datetime.fromisoformat(row[1]), row[2])
            return None
    
    def get_current_session_duration(self) -> int:
        """Get current session duration in minutes"""
        session = self.get_current_session()
        if not session:
            return 0
        return int((datetime.now() - session[1]).total_seconds() / 60)
    
    def get_all_entries(self, limit: int = None, offset: int = 0) -> List[TimeEntry]:
        """Get all completed time entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT start_time, end_time, description 
                FROM time_entries 
                WHERE end_time IS NOT NULL
                ORDER BY start_time DESC
            '''
            
            if limit:
                query += f' LIMIT {limit} OFFSET {offset}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                start_time = datetime.fromisoformat(row[0])
                end_time = datetime.fromisoformat(row[1]) if row[1] else None
                entries.append(TimeEntry(start_time, end_time, row[2]))
            
            return entries
    
    def get_entries_for_month(self, year: int, month: int) -> List[TimeEntry]:
        """Get all completed entries for a specific month"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create date range for the month
            start_date = f"{year:04d}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1:04d}-01-01"
            else:
                end_date = f"{year:04d}-{month+1:02d}-01"
            
            cursor.execute('''
                SELECT start_time, end_time, description 
                FROM time_entries 
                WHERE end_time IS NOT NULL
                AND date(start_time) >= ? 
                AND date(start_time) < ?
                ORDER BY start_time
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            entries = []
            for row in rows:
                start_time = datetime.fromisoformat(row[0])
                end_time = datetime.fromisoformat(row[1]) if row[1] else None
                entries.append(TimeEntry(start_time, end_time, row[2]))
            
            return entries
    
    def get_entries_for_date(self, target_date: date) -> List[TimeEntry]:
        """Get all entries for a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            date_str = target_date.strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT start_time, end_time, description 
                FROM time_entries 
                WHERE date(start_time) = ?
                ORDER BY start_time
            ''', (date_str,))
            
            rows = cursor.fetchall()
            entries = []
            for row in rows:
                start_time = datetime.fromisoformat(row[0])
                end_time = datetime.fromisoformat(row[1]) if row[1] else None
                entries.append(TimeEntry(start_time, end_time, row[2]))
            
            return entries
    
    def get_total_hours_for_month(self, year: int, month: int) -> float:
        """Get total hours worked in a specific month"""
        entries = self.get_entries_for_month(year, month)
        return sum(entry.duration_hours() for entry in entries)
    
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
                end_datetime += timedelta(days=1)
            
            # Create and add the entry
            entry = TimeEntry(start_datetime, end_datetime, description)
            self.add_completed_entry(entry)
            return True
            
        except (ValueError, IndexError):
            return False
    
    def add_duration_entry(self, date_obj: date, duration_str: str, start_time_str: str = "09:00", description: str = "") -> bool:
        """Add a work entry using duration format (e.g., '5h 30m', '2h', '45m')"""
        try:
            from timesheet import TimesheetManager
            # Parse duration string using existing method
            temp_manager = TimesheetManager()
            hours, minutes = temp_manager._parse_duration(duration_str)
            if hours == 0 and minutes == 0:
                return False
            
            # Parse start time
            start_hour, start_min = map(int, start_time_str.split(':'))
            start_datetime = datetime.combine(date_obj, time(start_hour, start_min))
            
            # Calculate end time
            end_datetime = start_datetime + timedelta(hours=hours, minutes=minutes)
            
            # Create and add the entry
            entry = TimeEntry(start_datetime, end_datetime, description)
            self.add_completed_entry(entry)
            return True
            
        except (ValueError, IndexError):
            return False
    
    def delete_entry_by_id(self, entry_id: int) -> bool:
        """Delete a time entry by database ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM time_entries WHERE rowid = ?', (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_entry_by_id(self, entry_id: int, start_time: datetime, end_time: datetime, description: str = "") -> bool:
        """Update a time entry by database ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE time_entries 
                SET start_time = ?, end_time = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE rowid = ?
            ''', (start_time.isoformat(), end_time.isoformat(), description, entry_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_entry_by_id(self, entry_id: int) -> Optional[Tuple[int, TimeEntry]]:
        """Get a specific entry by database ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT rowid, start_time, end_time, description 
                FROM time_entries 
                WHERE rowid = ?
            ''', (entry_id,))
            row = cursor.fetchone()
            
            if row:
                entry_id = row[0]
                start_time = datetime.fromisoformat(row[1])
                end_time = datetime.fromisoformat(row[2]) if row[2] else None
                entry = TimeEntry(start_time, end_time, row[3])
                return (entry_id, entry)
            return None
    
    def get_entries_with_ids(self, limit: int = None) -> List[Tuple[int, TimeEntry]]:
        """Get all entries with their database IDs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT rowid, start_time, end_time, description 
                FROM time_entries 
                WHERE end_time IS NOT NULL
                ORDER BY start_time DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                entry_id = row[0]
                start_time = datetime.fromisoformat(row[1])
                end_time = datetime.fromisoformat(row[2]) if row[2] else None
                entry = TimeEntry(start_time, end_time, row[3])
                entries.append((entry_id, entry))
            
            return entries
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM time_entries WHERE end_time IS NOT NULL')
            total_entries = cursor.fetchone()[0]
            
            # Total hours
            cursor.execute('''
                SELECT SUM(
                    (julianday(end_time) - julianday(start_time)) * 24
                ) FROM time_entries WHERE end_time IS NOT NULL
            ''')
            total_hours = cursor.fetchone()[0] or 0
            
            # This month stats
            now = datetime.now()
            start_of_month = f"{now.year:04d}-{now.month:02d}-01"
            if now.month == 12:
                start_of_next_month = f"{now.year+1:04d}-01-01"
            else:
                start_of_next_month = f"{now.year:04d}-{now.month+1:02d}-01"
            
            cursor.execute('''
                SELECT COUNT(*), SUM(
                    (julianday(end_time) - julianday(start_time)) * 24
                ) FROM time_entries 
                WHERE end_time IS NOT NULL
                AND date(start_time) >= ? 
                AND date(start_time) < ?
            ''', (start_of_month, start_of_next_month))
            
            month_result = cursor.fetchone()
            month_entries = month_result[0] or 0
            month_hours = month_result[1] or 0
            
            return {
                'total_entries': total_entries,
                'total_hours': round(total_hours, 2),
                'month_entries': month_entries,
                'month_hours': round(month_hours, 2),
                'current_month': now.month,
                'current_year': now.year
            }
