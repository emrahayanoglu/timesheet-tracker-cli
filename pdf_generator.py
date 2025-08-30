from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime, date
import calendar
from typing import List

# Import both timesheet managers for compatibility
try:
    from timesheet_sqlite import TimesheetManager, TimeEntry
except ImportError:
    from timesheet import TimesheetManager, TimeEntry

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
    
    def generate_monthly_report(self, manager: TimesheetManager, year: int, month: int, output_file: str):
        """Generate a PDF report for the specified month"""
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        story = []
        
        # Title
        month_name = calendar.month_name[month]
        title = Paragraph(f"Timesheet Report - {month_name} {year}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Summary section
        entries = manager.get_entries_for_month(year, month)
        total_hours = manager.get_total_hours_for_month(year, month)
        daily_summary = manager.get_daily_summary_for_month(year, month)
        
        summary_heading = Paragraph("Summary", self.heading_style)
        story.append(summary_heading)
        
        summary_data = [
            ["Total Hours Worked:", f"{total_hours:.2f}"],
            ["Total Days Worked:", str(len(daily_summary))],
            ["Average Hours/Day:", f"{total_hours/len(daily_summary):.2f}" if daily_summary else "0.00"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Daily breakdown
        if daily_summary:
            daily_heading = Paragraph("Daily Breakdown", self.heading_style)
            story.append(daily_heading)
            
            daily_data = [["Date", "Hours Worked"]]
            for day in sorted(daily_summary.keys()):
                date_str = f"{year}-{month:02d}-{day:02d}"
                hours = f"{daily_summary[day]:.2f}"
                daily_data.append([date_str, hours])
            
            daily_table = Table(daily_data, colWidths=[2.5*inch, 2.5*inch])
            daily_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(daily_table)
            story.append(Spacer(1, 30))
        
        # Detailed entries
        if entries:
            details_heading = Paragraph("Detailed Time Entries", self.heading_style)
            story.append(details_heading)
            
            details_data = [["Date", "Start Time", "End Time", "Duration (h)", "Description"]]
            
            for entry in sorted(entries, key=lambda x: x.start_time):
                date_str = entry.start_time.strftime("%Y-%m-%d")
                start_time = entry.start_time.strftime("%H:%M")
                end_time = entry.end_time.strftime("%H:%M") if entry.end_time else "N/A"
                duration = f"{entry.duration_hours():.2f}"
                description = entry.description[:30] + "..." if len(entry.description) > 30 else entry.description
                
                details_data.append([date_str, start_time, end_time, duration, description])
            
            details_table = Table(details_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 2.3*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(details_table)
        
        # Footer
        story.append(Spacer(1, 50))
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        return output_file
