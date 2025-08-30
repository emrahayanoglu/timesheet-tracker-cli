#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from datetime import datetime, date, timedelta, time
import calendar
import os
import tempfile
from timesheet_sqlite import TimesheetManager

app = Flask(__name__)

# Initialize the timesheet manager with SQLite backend
timesheet_manager = TimesheetManager()

@app.route('/')
def index():
    """Main dashboard page"""
    # Get current session info
    current_session = timesheet_manager.current_session
    current_duration = timesheet_manager.get_current_session_duration()
    
    # Get this month's stats
    now = datetime.now()
    month_entries = timesheet_manager.get_entries_for_month(now.year, now.month)
    month_hours = timesheet_manager.get_total_hours_for_month(now.year, now.month)
    
    # Get recent entries
    recent_entries = timesheet_manager.get_recent_entries(limit=10)
    
    # Get overall stats
    stats = timesheet_manager.get_stats()
    
    return render_template('index.html', 
                         current_session=current_session,
                         current_duration=current_duration,
                         month_entries=len(month_entries),
                         month_hours=month_hours,
                         recent_entries=recent_entries,
                         stats=stats,
                         current_month=calendar.month_name[now.month],
                         current_year=now.year)

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new work session"""
    data = request.get_json()
    description = data.get('description', '')
    
    if timesheet_manager.start_session(description):
        return jsonify({'success': True, 'message': 'Session started successfully'})
    else:
        return jsonify({'success': False, 'message': 'A session is already active'}), 400

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop the current work session"""
    session = timesheet_manager.stop_session()
    if session:
        return jsonify({
            'success': True, 
            'message': 'Session stopped successfully',
            'duration': session.duration_hours(),
            'duration_minutes': session.duration_minutes()
        })
    else:
        return jsonify({'success': False, 'message': 'No active session to stop'}), 400

@app.route('/api/session/status')
def session_status():
    """Get current session status"""
    current_session = timesheet_manager.current_session
    if current_session:
        duration = timesheet_manager.get_current_session_duration()
        return jsonify({
            'active': True,
            'start_time': current_session.start_time.isoformat(),
            'description': current_session.description,
            'duration_minutes': duration,
            'duration_hours': round(duration / 60, 2)
        })
    else:
        return jsonify({'active': False})

@app.route('/entries')
def entries():
    """List all entries with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get entries with their database IDs
    entries_with_ids = timesheet_manager.get_entries_with_ids()
    total_entries = len(entries_with_ids)
    
    # Calculate pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    entries_page = entries_with_ids[start_idx:end_idx]
    
    # Calculate pagination info
    total_pages = (total_entries + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('entries.html',
                         entries_with_ids=entries_page,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         total_entries=total_entries)

@app.route('/add_entry')
def add_entry():
    """Form to add a new entry"""
    # Check if a specific date is requested
    requested_date = request.args.get('date')
    if requested_date:
        try:
            # Validate the date format
            datetime.strptime(requested_date, '%Y-%m-%d')
            today = requested_date
        except ValueError:
            today = datetime.now().strftime('%Y-%m-%d')
    else:
        today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('add_entry.html', today=today)

@app.route('/api/entry/add', methods=['POST'])
def api_add_entry():
    """Add a new time entry"""
    data = request.get_json()
    
    try:
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = data['start_time']
        description = data.get('description', '')
        
        if 'end_time' in data and data['end_time']:
            # Time range entry
            end_time = data['end_time']
            success = timesheet_manager.add_manual_entry(entry_date, start_time, end_time, description)
        elif 'duration' in data and data['duration']:
            # Duration entry
            duration = data['duration']
            success = timesheet_manager.add_duration_entry(entry_date, duration, start_time, description)
        else:
            return jsonify({'success': False, 'message': 'Either end_time or duration is required'}), 400
        
        if success:
            return jsonify({'success': True, 'message': 'Entry added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add entry. Check your input.'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/reports')
def reports():
    """Reports page"""
    # Get current month by default
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Get entries for the selected month
    entries = timesheet_manager.get_entries_for_month(year, month)
    total_hours = timesheet_manager.get_total_hours_for_month(year, month)
    daily_summary = timesheet_manager.get_daily_summary_for_month(year, month)
    
    # Generate calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Calculate stats
    working_days = len(daily_summary)
    avg_hours_per_day = total_hours / working_days if working_days > 0 else 0
    
    return render_template('reports.html',
                         entries=entries,
                         total_hours=total_hours,
                         daily_summary=daily_summary,
                         calendar_weeks=cal,
                         month=month,
                         year=year,
                         month_name=month_name,
                         working_days=working_days,
                         avg_hours_per_day=avg_hours_per_day)

@app.route('/api/entry/<int:entry_id>/delete', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete a time entry"""
    if timesheet_manager.db.delete_entry_by_id(entry_id):
        return jsonify({'success': True, 'message': 'Entry deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Entry not found'}), 404

@app.route('/api/entry/<int:entry_id>')
def get_entry(entry_id):
    """Get a specific entry for editing"""
    result = timesheet_manager.db.get_entry_by_id(entry_id)
    if result:
        entry_id, entry = result
        return jsonify({
            'success': True,
            'entry': {
                'id': entry_id,
                'date': entry.start_time.strftime('%Y-%m-%d'),
                'start_time': entry.start_time.strftime('%H:%M'),
                'end_time': entry.end_time.strftime('%H:%M') if entry.end_time else '',
                'description': entry.description,
                'duration_hours': entry.duration_hours()
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Entry not found'}), 404

@app.route('/api/entry/<int:entry_id>/update', methods=['PUT'])
def update_entry(entry_id):
    """Update an existing entry"""
    data = request.get_json()
    
    try:
        # Parse the input data
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time_str = data['start_time']
        end_time_str = data['end_time']
        description = data.get('description', '')
        
        # Parse time strings
        start_hour, start_min = map(int, start_time_str.split(':'))
        end_hour, end_min = map(int, end_time_str.split(':'))
        
        # Create datetime objects
        start_datetime = datetime.combine(entry_date, time(start_hour, start_min))
        end_datetime = datetime.combine(entry_date, time(end_hour, end_min))
        
        # Handle next day case
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)
        
        # Update the entry
        if timesheet_manager.update_entry_by_id(entry_id, start_datetime, end_datetime, description):
            return jsonify({'success': True, 'message': 'Entry updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Entry not found or update failed'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid data: {str(e)}'}), 400

@app.route('/edit_entry/<int:entry_id>')
def edit_entry_page(entry_id):
    """Edit entry page"""
    result = timesheet_manager.db.get_entry_by_id(entry_id)
    if not result:
        return redirect(url_for('entries'))
    
    entry_id, entry = result
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('edit_entry.html', 
                         entry_id=entry_id, 
                         entry=entry, 
                         today=today)

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    return jsonify(timesheet_manager.get_stats())

@app.route('/api/day-details/<date_str>')
def api_day_details(date_str):
    """API endpoint to get detailed information for a specific day"""
    try:
        # Parse the date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get entries for the day
        entries = timesheet_manager.get_entries_by_date(date_obj)
        
        # Convert entries to JSON-serializable format
        entries_data = []
        total_hours = 0
        
        for entry in entries:
            entry_data = {
                'id': entry.id,
                'start_time': entry.start_time.isoformat(),
                'end_time': entry.end_time.isoformat() if entry.end_time else None,
                'description': entry.description,
                'duration_hours': entry.duration_hours()
            }
            entries_data.append(entry_data)
            if entry.duration_hours():
                total_hours += entry.duration_hours()
        
        return jsonify({
            'date': date_str,
            'entries': entries_data,
            'total_hours': total_hours,
            'entries_count': len(entries_data)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calendar')
def calendar_view():
    """Enhanced calendar view of entries with daily hours"""
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Validate month and year
    if not (1 <= month <= 12):
        month = now.month
    if year < 2000 or year > 2100:
        year = now.year
    
    # Get entries for the month
    entries = timesheet_manager.get_entries_for_month(year, month)
    daily_summary = timesheet_manager.get_daily_summary_for_month(year, month)
    
    # Group entries by date for detailed view
    entries_by_date = {}
    daily_details = {}
    
    for entry in entries:
        day = entry.start_time.day
        if day not in entries_by_date:
            entries_by_date[day] = []
            daily_details[day] = {
                'total_hours': 0,
                'entries_count': 0,
                'earliest_start': None,
                'latest_end': None,
                'descriptions': []
            }
        
        entries_by_date[day].append(entry)
        daily_details[day]['total_hours'] += entry.duration_hours()
        daily_details[day]['entries_count'] += 1
        
        # Track earliest start and latest end
        if daily_details[day]['earliest_start'] is None or entry.start_time.time() < daily_details[day]['earliest_start']:
            daily_details[day]['earliest_start'] = entry.start_time.time()
        
        if entry.end_time and (daily_details[day]['latest_end'] is None or entry.end_time.time() > daily_details[day]['latest_end']):
            daily_details[day]['latest_end'] = entry.end_time.time()
        
        # Collect unique descriptions
        if entry.description and entry.description not in daily_details[day]['descriptions']:
            daily_details[day]['descriptions'].append(entry.description)
    
    # Generate calendar with weeks starting on Monday
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # Calculate month statistics
    total_hours = sum(daily_summary.values())
    working_days = len(daily_summary)
    avg_hours_per_day = total_hours / working_days if working_days > 0 else 0
    
    # Find the most productive day
    most_productive_day = max(daily_summary.items(), key=lambda x: x[1]) if daily_summary else None
    
    # Calculate week totals
    week_totals = []
    for week in cal:
        week_total = 0
        for day in week:
            if day != 0 and day in daily_summary:
                week_total += daily_summary[day]
        week_totals.append(week_total)
    
    return render_template('calendar.html',
                         calendar_weeks=cal,
                         entries_by_date=entries_by_date,
                         daily_summary=daily_summary,
                         daily_details=daily_details,
                         week_totals=week_totals,
                         month=month,
                         year=year,
                         month_name=month_name,
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year,
                         total_hours=total_hours,
                         working_days=working_days,
                         avg_hours_per_day=avg_hours_per_day,
                         most_productive_day=most_productive_day,
                         current_month=now.month,
                         current_year=now.year,
                         current_day=now.day)

@app.route('/api/report/pdf')
def generate_pdf_report():
    """Generate and download PDF report"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # Validate month and year
        if not (1 <= month <= 12):
            return jsonify({'success': False, 'message': 'Invalid month'}), 400
        
        # Check if we have entries for this month
        entries = timesheet_manager.get_entries_for_month(year, month)
        if not entries:
            month_name = calendar.month_name[month]
            return jsonify({'success': False, 'message': f'No entries found for {month_name} {year}'}), 404
        
        # Try to import and use PDF generator
        try:
            from pdf_generator import PDFGenerator
            
            # Create temporary file
            month_name = calendar.month_name[month].lower()
            filename = f"timesheet_{month_name}_{year}.pdf"
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            
            # Generate PDF
            generator = PDFGenerator()
            generator.generate_monthly_report(timesheet_manager, year, month, temp_path)
            
            # Send file and clean up
            return send_file(temp_path, 
                           as_attachment=True, 
                           download_name=filename,
                           mimetype='application/pdf')
            
        except ImportError:
            return jsonify({'success': False, 'message': 'PDF generation requires reportlab. Install with: pip install reportlab'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error generating PDF: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Read debug and host from environment variables, defaulting to safe values
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
