#!/usr/bin/env python3
import click
from datetime import datetime, date, time, timedelta
import calendar
from timesheet_sqlite import TimesheetManager
import subprocess
import sys
import os

@click.group()
def cli():
    """Simple timesheet tracking CLI tool
    
    Track your working time with start/stop commands or add work sessions for specific dates.
    Generate monthly PDF reports at the end of each month.
    """
    pass

@cli.command()
@click.option('--description', '-d', default='', help='Description of the work session')
def start(description):
    """Start a new work session"""
    manager = TimesheetManager()
    
    if manager.start_session(description):
        click.echo(f"✅ Work session started at {datetime.now().strftime('%H:%M:%S')}")
        if description:
            click.echo(f"   Description: {description}")
    else:
        click.echo("❌ A work session is already active. Stop it first with 'timesheet stop'")

@cli.command()
def stop():
    """Stop the current work session"""
    manager = TimesheetManager()
    
    session = manager.stop_session()
    if session:
        duration = session.duration_hours()
        click.echo(f"✅ Work session stopped at {session.end_time.strftime('%H:%M:%S')}")
        click.echo(f"   Duration: {duration:.2f} hours ({session.duration_minutes()} minutes)")
        if session.description:
            click.echo(f"   Description: {session.description}")
    else:
        click.echo("❌ No active work session to stop")

@cli.command()
def status():
    """Show current session status"""
    manager = TimesheetManager()
    
    if manager.current_session:
        start_time = manager.current_session.start_time
        duration = manager.get_current_session_duration()
        hours = duration / 60
        
        click.echo("🟢 Work session is ACTIVE")
        click.echo(f"   Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"   Duration: {hours:.2f} hours ({duration} minutes)")
        if manager.current_session.description:
            click.echo(f"   Description: {manager.current_session.description}")
    else:
        click.echo("🔴 No active work session")

@cli.command()
@click.option('--month', '-m', type=int, help='Month (1-12)')
@click.option('--year', '-y', type=int, help='Year')
@click.option('--limit', '-l', default=20, help='Maximum number of entries to show')
def list(month, year, limit):
    """List work sessions"""
    manager = TimesheetManager()
    
    if month and year:
        entries = manager.get_entries_for_month(year, month)
        month_name = calendar.month_name[month]
        click.echo(f"\n📋 Work sessions for {month_name} {year}:")
        total_hours = manager.get_total_hours_for_month(year, month)
        click.echo(f"   Total hours: {total_hours:.2f}")
    else:
        entries = manager.entries[-limit:] if len(manager.entries) > limit else manager.entries
        click.echo(f"\n📋 Recent work sessions (last {len(entries)}):")
    
    if not entries:
        click.echo("   No work sessions found")
        return
    
    click.echo()
    
    # Get absolute indices for proper deletion reference
    if month and year:
        # For month view, show sequential numbering
        for i, entry in enumerate(sorted(entries, key=lambda x: x.start_time), 1):
            start_date = entry.start_time.strftime('%Y-%m-%d')
            start_time = entry.start_time.strftime('%H:%M')
            end_time = entry.end_time.strftime('%H:%M') if entry.end_time else 'N/A'
            duration = f"{entry.duration_hours():.2f}h"
            
            click.echo(f"{i:2d}. {start_date} {start_time} - {end_time} ({duration})")
            if entry.description:
                click.echo(f"     📝 {entry.description}")
    else:
        # For recent view, show absolute indices for deletion
        start_index = len(manager.entries) - len(entries)
        for i, entry in enumerate(sorted(entries, key=lambda x: x.start_time)):
            absolute_index = start_index + i + 1
            start_date = entry.start_time.strftime('%Y-%m-%d')
            start_time = entry.start_time.strftime('%H:%M')
            end_time = entry.end_time.strftime('%H:%M') if entry.end_time else 'N/A'
            duration = f"{entry.duration_hours():.2f}h"
            
            click.echo(f"{absolute_index:2d}. {start_date} {start_time} - {end_time} ({duration})")
            if entry.description:
                click.echo(f"     📝 {entry.description}")
        
        if len(manager.entries) > limit:
            click.echo(f"\n   (Showing last {len(entries)} of {len(manager.entries)} total entries)")
            click.echo(f"   Use 'delete' command with the index numbers shown above")

@cli.command()
@click.option('--month', '-m', type=int, required=True, help='Month (1-12)')
@click.option('--year', '-y', type=int, required=True, help='Year')
@click.option('--output', '-o', help='Output PDF filename')
def report(month, year, output):
    """Generate a PDF report for the specified month"""
    
    if month < 1 or month > 12:
        click.echo("❌ Month must be between 1 and 12")
        return
    
    manager = TimesheetManager()
    entries = manager.get_entries_for_month(year, month)
    
    if not entries:
        month_name = calendar.month_name[month]
        click.echo(f"❌ No work sessions found for {month_name} {year}")
        return
    
    if not output:
        month_name = calendar.month_name[month].lower()
        output = f"timesheet_{month_name}_{year}.pdf"
    
    try:
        from pdf_generator import PDFGenerator
        generator = PDFGenerator()
        generator.generate_monthly_report(manager, year, month, output)
        
        total_hours = manager.get_total_hours_for_month(year, month)
        month_name = calendar.month_name[month]
        
        click.echo(f"✅ PDF report generated: {output}")
        click.echo(f"   Month: {month_name} {year}")
        click.echo(f"   Total hours: {total_hours:.2f}")
        click.echo(f"   Total entries: {len(entries)}")
        
    except ImportError:
        click.echo("❌ PDF generation requires reportlab. Install with: pip install reportlab")
    except Exception as e:
        click.echo(f"❌ Error generating PDF: {str(e)}")

@cli.command()
@click.option('--date', '-d', required=True, help='Date in YYYY-MM-DD format')
@click.option('--start', '-s', required=True, help='Start time in HH:MM format')
@click.option('--end', '-e', required=True, help='End time in HH:MM format')
@click.option('--description', '--desc', default='', help='Description of the work session')
def add(date, start, end, description):
    """Add work session for a specific date"""
    manager = TimesheetManager()
    
    try:
        # Parse the date
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Validate that the date is not in the future
        if date_obj > datetime.now().date():
            click.echo("❌ Cannot add work session for future dates")
            return
        
        # Add the manual entry
        if manager.add_manual_entry(date_obj, start, end, description):
            duration_hours = 0
            # Calculate duration for display
            try:
                start_hour, start_min = map(int, start.split(':'))
                end_hour, end_min = map(int, end.split(':'))
                start_minutes = start_hour * 60 + start_min
                end_minutes = end_hour * 60 + end_min
                
                # Handle next day case
                if end_minutes <= start_minutes:
                    end_minutes += 24 * 60
                
                duration_minutes = end_minutes - start_minutes
                duration_hours = duration_minutes / 60
            except:
                pass
            
            click.echo(f"✅ Work session added for {date}")
            click.echo(f"   Time: {start} - {end} ({duration_hours:.2f} hours)")
            if description:
                click.echo(f"   Description: {description}")
        else:
            click.echo("❌ Invalid time format. Use HH:MM format (e.g., 09:30)")
            
    except ValueError:
        click.echo("❌ Invalid date format. Use YYYY-MM-DD format (e.g., 2025-08-26)")

@cli.command()
@click.option('--date', '-d', required=True, help='Date in YYYY-MM-DD format')
@click.option('--duration', '-dur', required=True, help='Duration like "5h 30m", "2h", or "45m"')
@click.option('--start', '-s', default='09:00', help='Start time in HH:MM format (default: 09:00)')
@click.option('--description', '--desc', default='', help='Description of the work session')
def addhours(date, duration, start, description):
    """Add work session using duration (e.g., 5h 30m)"""
    manager = TimesheetManager()
    
    try:
        # Parse the date
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Validate that the date is not in the future
        if date_obj > datetime.now().date():
            click.echo("❌ Cannot add work session for future dates")
            return
        
        # Add the duration entry
        if manager.add_duration_entry(date_obj, duration, start, description):
            # Parse duration for display
            hours, minutes = manager._parse_duration(duration)
            total_hours = hours + minutes / 60
            
            # Calculate end time for display
            start_hour, start_min = map(int, start.split(':'))
            start_dt = datetime.combine(date_obj, time(start_hour, start_min))
            end_dt = start_dt + timedelta(hours=hours, minutes=minutes)
            end_time = end_dt.strftime('%H:%M')
            
            click.echo(f"✅ Work session added for {date}")
            click.echo(f"   Duration: {duration} ({total_hours:.2f} hours)")
            click.echo(f"   Time: {start} - {end_time}")
            if description:
                click.echo(f"   Description: {description}")
        else:
            click.echo("❌ Invalid duration format. Use formats like '5h 30m', '2h', or '45m'")
            
    except ValueError:
        click.echo("❌ Invalid date format. Use YYYY-MM-DD format (e.g., 2025-08-26)")

@cli.command()
@click.option('--index', '-i', type=int, help='Index of the entry to delete (see with "list" command)')
@click.option('--confirm', '-y', is_flag=True, help='Skip confirmation prompt')
def delete(index, confirm):
    """Delete a work session by index"""
    manager = TimesheetManager()
    
    if not manager.entries:
        click.echo("❌ No work sessions to delete")
        return
    
    # If no index provided, show list and ask for index
    if index is None:
        click.echo("\n📋 Current work sessions:")
        entries_with_index = manager.get_entries_with_index()
        
        # Show entries in chronological order with absolute indices
        for idx, entry in sorted(entries_with_index, key=lambda x: x[1].start_time):
            start_date = entry.start_time.strftime('%Y-%m-%d')
            start_time = entry.start_time.strftime('%H:%M')
            end_time = entry.end_time.strftime('%H:%M') if entry.end_time else 'N/A'
            duration = f"{entry.duration_hours():.2f}h"
            
            click.echo(f"{idx:2d}. {start_date} {start_time} - {end_time} ({duration})")
            if entry.description:
                click.echo(f"     📝 {entry.description}")
        
        click.echo(f"\nTotal entries: {len(manager.entries)}")
        try:
            index = click.prompt("Enter the index to delete", type=int)
        except click.Abort:
            click.echo("Cancelled")
            return
    
    # Validate index
    if not (1 <= index <= len(manager.entries)):
        click.echo(f"❌ Invalid index. Must be between 1 and {len(manager.entries)}")
        return
    
    # Get the entry to delete for confirmation
    entry_to_delete = manager.entries[index - 1]
    start_date = entry_to_delete.start_time.strftime('%Y-%m-%d')
    start_time = entry_to_delete.start_time.strftime('%H:%M')
    end_time = entry_to_delete.end_time.strftime('%H:%M') if entry_to_delete.end_time else 'N/A'
    duration = f"{entry_to_delete.duration_hours():.2f}h"
    
    click.echo(f"\n🗑️  Entry to delete:")
    click.echo(f"   {index}. {start_date} {start_time} - {end_time} ({duration})")
    if entry_to_delete.description:
        click.echo(f"      📝 {entry_to_delete.description}")
    
    # Confirmation
    if not confirm:
        if not click.confirm("\nAre you sure you want to delete this entry?"):
            click.echo("Cancelled")
            return
    
    # Delete the entry
    if manager.delete_entry(index):
        click.echo("✅ Work session deleted successfully")
    else:
        click.echo("❌ Failed to delete work session")

@cli.command()
@click.option('--index', '-i', type=int, help='Index of the entry to edit (see with "list" command)')
def edit(index):
    """Edit an existing work session"""
    manager = TimesheetManager()
    
    if not manager.entries:
        click.echo("❌ No work sessions to edit")
        return
    
    # If no index provided, show list and ask for index
    if index is None:
        click.echo("\n📋 Current work sessions:")
        entries_with_index = manager.get_entries_with_index()
        
        # Show entries in chronological order with absolute indices
        for idx, entry in sorted(entries_with_index, key=lambda x: x[1].start_time):
            start_date = entry.start_time.strftime('%Y-%m-%d')
            start_time = entry.start_time.strftime('%H:%M')
            end_time = entry.end_time.strftime('%H:%M') if entry.end_time else 'N/A'
            duration = f"{entry.duration_hours():.2f}h"
            
            click.echo(f"{idx:2d}. {start_date} {start_time} - {end_time} ({duration})")
            if entry.description:
                click.echo(f"     📝 {entry.description}")
        
        click.echo(f"\nTotal entries: {len(manager.entries)}")
        try:
            index = click.prompt("Enter the index to edit", type=int)
        except click.Abort:
            click.echo("Cancelled")
            return
    
    # Validate index
    entries_with_ids = manager.get_entries_with_ids()
    if not (1 <= index <= len(entries_with_ids)):
        click.echo(f"❌ Invalid index. Must be between 1 and {len(entries_with_ids)}")
        return
    
    # Get the entry to edit
    sorted_entries = sorted(entries_with_ids, key=lambda x: x[1].start_time)
    entry_id, entry_to_edit = sorted_entries[index - 1]
    
    click.echo(f"\n✏️  Editing entry:")
    click.echo(f"   Date: {entry_to_edit.start_time.strftime('%Y-%m-%d')}")
    click.echo(f"   Time: {entry_to_edit.start_time.strftime('%H:%M')} - {entry_to_edit.end_time.strftime('%H:%M')}")
    click.echo(f"   Duration: {entry_to_edit.duration_hours():.2f}h")
    click.echo(f"   Description: {entry_to_edit.description}")
    
    click.echo("\nEnter new values (press Enter to keep current value):")
    
    # Get new values
    new_date_str = click.prompt("Date (YYYY-MM-DD)", default=entry_to_edit.start_time.strftime('%Y-%m-%d'))
    new_start_str = click.prompt("Start time (HH:MM)", default=entry_to_edit.start_time.strftime('%H:%M'))
    new_end_str = click.prompt("End time (HH:MM)", default=entry_to_edit.end_time.strftime('%H:%M'))
    new_description = click.prompt("Description", default=entry_to_edit.description)
    
    try:
        # Parse new values
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        start_hour, start_min = map(int, new_start_str.split(':'))
        end_hour, end_min = map(int, new_end_str.split(':'))
        
        new_start_time = datetime.combine(new_date, time(start_hour, start_min))
        new_end_time = datetime.combine(new_date, time(end_hour, end_min))
        
        # Handle next day case
        if new_end_time <= new_start_time:
            new_end_time += timedelta(days=1)
        
        # Update the entry
        if manager.update_entry_by_id(entry_id, new_start_time, new_end_time, new_description):
            new_duration = (new_end_time - new_start_time).total_seconds() / 3600
            click.echo(f"\n✅ Entry updated successfully:")
            click.echo(f"   Date: {new_date}")
            click.echo(f"   Time: {new_start_str} - {new_end_str}")
            click.echo(f"   Duration: {new_duration:.2f}h")
            click.echo(f"   Description: {new_description}")
        else:
            click.echo("❌ Failed to update entry")
            
    except (ValueError, IndexError) as e:
        click.echo(f"❌ Invalid input: {str(e)}")

@cli.command()
def summary():
    """Show summary of current month"""
    manager = TimesheetManager()
    now = datetime.now()
    
    entries = manager.get_entries_for_month(now.year, now.month)
    total_hours = manager.get_total_hours_for_month(now.year, now.month)
    daily_summary = manager.get_daily_summary_for_month(now.year, now.month)
    
    month_name = calendar.month_name[now.month]
    click.echo(f"\n📊 Summary for {month_name} {now.year}:")
    click.echo(f"   Total hours worked: {total_hours:.2f}")
    click.echo(f"   Total work sessions: {len(entries)}")
    click.echo(f"   Days worked: {len(daily_summary)}")
    
    if daily_summary:
        avg_hours = total_hours / len(daily_summary)
        click.echo(f"   Average hours/day: {avg_hours:.2f}")
    
    # Show current session if active
    if manager.current_session:
        duration = manager.get_current_session_duration()
        hours = duration / 60
        click.echo(f"\n🟢 Current session: {hours:.2f} hours ({duration} minutes)")

@cli.command()
def web():
    """Launch the web interface"""
    try:
        # Check if Flask is installed
        import flask
        click.echo("🌐 Starting web interface...")
        click.echo("   URL: http://localhost:5000")
        click.echo("   Press Ctrl+C to stop")
        
        # Run the web app
        from web_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except ImportError:
        click.echo("❌ Flask is not installed. Install with: pip install flask")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error starting web interface: {str(e)}")
        sys.exit(1)

@cli.command()
def migrate():
    """Migrate existing JSON data to SQLite database"""
    manager = TimesheetManager()
    click.echo("✅ Migration complete! Your data is now stored in SQLite database.")
    click.echo("   Database file: timesheet.db")
    
    # Show stats
    stats = manager.get_stats()
    click.echo(f"   Total entries: {stats['total_entries']}")
    click.echo(f"   Total hours: {stats['total_hours']}")

if __name__ == '__main__':
    cli()
