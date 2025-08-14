"""
NYC DOE Paraprofessional Jobs - ReportLab PDF Generator

Creates professional PDF reports directly from data using ReportLab
"""

import os
import time
import pandas as pd
from datetime import datetime

# Check if ReportLab is installed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, PageTemplate, Frame
    from reportlab.platypus.flowables import Flowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not found. Installing...")

def install_reportlab():
    """Install ReportLab if not available"""
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        print("✅ ReportLab installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install ReportLab: {e}")
        return False

def create_custom_styles():
    """Create custom styles for the PDF reports"""
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#004080'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#004080'),
        spaceBefore=15,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceBefore=10,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='CenterNormal',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor('#666666')
    ))
    
    styles.add(ParagraphStyle(
        name='ItalicStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#666666')
    ))
    
    styles.add(ParagraphStyle(
        name='AlertStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#d32f2f'),
        fontName='Helvetica-Bold'
    ))
    
    return styles

def draw_banner_on_first_page(canvas, doc, title_text, logo_path):
    """Draw banner on first page only, ignoring margins"""
    if doc.page == 1:  # Only draw on first page
        # Save canvas state
        canvas.saveState()
        
        # Get page dimensions
        page_width, page_height = letter
        
        # Banner dimensions
        banner_height = 1.2 * inch
        
        # Draw blue background across full page width at top
        canvas.setFillColor(colors.HexColor('#004080'))
        canvas.rect(0, page_height - banner_height, page_width, banner_height, fill=1, stroke=0)
        
        # Add logo on the right side if available
        if logo_path and os.path.exists(logo_path):
            try:
                # Scale logo to fit banner height with some padding
                logo_height = banner_height * 0.6
                logo_width = logo_height * 3  # Assuming horizontal logo is roughly 3:1 ratio
                
                # Position logo on the right side with margin
                logo_x = page_width - 0.75*inch - logo_width
                logo_y = page_height - banner_height + (banner_height - logo_height) / 2
                
                canvas.drawImage(logo_path, logo_x, logo_y, 
                               width=logo_width, height=logo_height,
                               preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Add white text on the left side
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 16)
        
        # Position title text on the left side with margin
        text_x = 0.7 * inch
        
        # Split title into lines and center vertically
        lines = title_text.split('\n')
        line_height = 18
        total_text_height = len(lines) * line_height
        start_y = page_height - banner_height + (banner_height + total_text_height) / 2 - line_height
        
        for i, line in enumerate(lines):
            y_pos = start_y - (i * line_height)
            canvas.drawString(text_x, y_pos, line.strip())
            
        # Restore canvas state
        canvas.restoreState()

class BlueBanner(Flowable):
    """Custom flowable for blue banner with white text and logo that extends full page width"""
    
    def __init__(self, title_text, logo_path=None, width=8.5*inch, height=1.2*inch):
        self.title_text = title_text
        self.logo_path = logo_path
        self.width = width
        self.height = height
        
    def wrap(self, availWidth, availHeight):
        return (self.width, self.height)
        
    def draw(self):
        # NYC DOE Blue background - draw rectangle extending to page edges with normal height
        self.canv.setFillColor(colors.HexColor('#004080'))
        # Extend left and right to page edges but keep normal height to avoid clipping text
        self.canv.rect(-1*inch, 0, 9.5*inch, self.height, fill=1, stroke=0)
        
        # Add white text on the left side
        self.canv.setFillColor(colors.white)
        self.canv.setFont('Helvetica-Bold', 16)
        
        # Position title text on the left side with margin
        text_x = -0.75*inch + 0.7 * inch
        
        # Split title into lines and center vertically
        lines = self.title_text.split('<br/>')
        if len(lines) == 1:
            lines = self.title_text.split('\n')
        
        line_height = 18
        total_text_height = len(lines) * line_height
        start_y = (self.height + total_text_height) / 2 - line_height
        
        for i, line in enumerate(lines):
            y_pos = start_y - (i * line_height)
            self.canv.drawString(text_x, y_pos, line.strip())
        
        # Add logo on the right side if available
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Scale logo to fit banner height with some padding
                logo_height = self.height * 0.6
                logo_width = logo_height * 3  # Assuming horizontal logo is roughly 3:1 ratio
                
                # Position logo on the right side with margin
                # Calculate position from right edge of page
                page_width = 8.5 * inch
                logo_x = page_width - 0.75*inch - logo_width - 0.5*inch  # Right margin + logo width + padding
                logo_y = (self.height - logo_height) / 2
                
                self.canv.drawImage(self.logo_path, logo_x, logo_y, 
                                  width=logo_width, height=logo_height,
                                  preserveAspectRatio=True, mask='auto')
            except:
                # If logo fails, just show text
                pass

def create_summary_table(data, title="Summary"):
    """Create a formatted summary table"""
    # Prepare data for table
    table_data = [['Metric', 'Value']]
    
    for key, value in data.items():
        if isinstance(value, (int, float)):
            if 'Pct' in key or 'Rate' in key or '%' in key or 'Percentage' in key:
                if value != 'N/A' and pd.notna(value):
                    formatted_value = f"{value:.1f}%"
                else:
                    formatted_value = "N/A"
            else:
                if value != 'N/A' and pd.notna(value):
                    formatted_value = f"{value:,}"
                else:
                    formatted_value = "N/A"
        else:
            formatted_value = str(value) if value != 'N/A' else "N/A"
        
        # Clean up key names
        clean_key = key.replace('_', ' ').title()
        table_data.append([clean_key, formatted_value])
    
    # Create table with repeating headers
    table = Table(table_data, colWidths=[2.5*inch, 1.5*inch], repeatRows=1)
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    return table

def create_data_table(df, title="Data Table"):
    """Create a formatted data table from DataFrame"""
    if df.empty:
        return Paragraph("No data available", getSampleStyleSheet()['Normal'])
    
    # Convert DataFrame to list of lists
    table_data = [list(df.columns)]
    
    for _, row in df.iterrows():
        formatted_row = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                formatted_row.append('')
            elif isinstance(value, (int, float)):
                if 'Pct' in col or '%' in col or 'Rate' in col or 'Percentage' in col:
                    formatted_row.append(f"{value:.1f}%")
                else:
                    formatted_row.append(f"{value:,}")
            else:
                formatted_row.append(str(value)[:30])  # Truncate long strings
        table_data.append(formatted_row)
    
    # Calculate column widths
    num_cols = len(df.columns)
    available_width = 6.5 * inch
    
    # Adjust column widths based on content
    if num_cols <= 4:
        col_width = available_width / num_cols
        col_widths = [col_width] * num_cols
    else:
        # For many columns, make some wider/narrower based on content
        col_widths = []
        for col in df.columns:
            if 'School' in col or 'Location' in col or 'Classification' in col:
                col_widths.append(available_width * 0.3)  # Wider for names
            elif 'Pct' in col or '%' in col:
                col_widths.append(available_width * 0.12)  # Narrower for percentages
            else:
                col_widths.append(available_width * 0.15)  # Medium for numbers
        
        # Normalize to fit available width
        total_width = sum(col_widths)
        col_widths = [w * available_width / total_width for w in col_widths]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    return table

def create_matching_table_with_colors(df, title="Data Table"):
    """Create a formatted matching data table with conditional formatting for Match %"""
    if df.empty:
        return Paragraph("No data available", getSampleStyleSheet()['Normal'])
    
    # Convert DataFrame to list of lists
    table_data = [list(df.columns)]
    match_col_index = None
    
    # Find the Match % column index
    for i, col in enumerate(df.columns):
        if 'Match' in col and '%' in col:
            match_col_index = i
            break
    
    for _, row in df.iterrows():
        formatted_row = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                formatted_row.append('')
            elif isinstance(value, (int, float)):
                if 'Pct' in col or '%' in col or 'Rate' in col or 'Percentage' in col:
                    formatted_row.append(f"{value:.1f}%")
                else:
                    formatted_row.append(f"{value:,}")
            else:
                formatted_row.append(str(value)[:30])  # Truncate long strings
        table_data.append(formatted_row)
    
    # Calculate column widths
    num_cols = len(df.columns)
    available_width = 6.5 * inch
    
    # Adjust column widths based on content
    col_widths = []
    for col in df.columns:
        if 'School' in col or 'Location' in col:
            col_widths.append(available_width * 0.4)  # Wider for school names
        elif 'Match' in col and '%' in col:
            col_widths.append(available_width * 0.15)  # Medium for match percentage
        else:
            col_widths.append(available_width * 0.225)  # Medium for other columns
    
    # Normalize to fit available width
    total_width = sum(col_widths)
    col_widths = [w * available_width / total_width for w in col_widths]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Base table style
    table_style = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Base background (will be overridden by conditional formatting)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]
    
    # Add conditional formatting for Match % column if it exists
    if match_col_index is not None:
        for row_idx, (_, row) in enumerate(df.iterrows(), start=1):  # Start at 1 to skip header
            match_value = row.iloc[match_col_index] if match_col_index < len(row) else None
            
            if pd.notna(match_value) and isinstance(match_value, (int, float)):
                if match_value < 70:
                    # Red for poor performance
                    bg_color = colors.HexColor('#ffebee')  # Light red
                    text_color = colors.HexColor('#c62828')  # Dark red
                elif match_value < 90:
                    # Orange for needs improvement
                    bg_color = colors.HexColor('#fff3e0')  # Light orange
                    text_color = colors.HexColor('#ef6c00')  # Dark orange
                else:
                    # Green for meets benchmark
                    bg_color = colors.HexColor('#e8f5e8')  # Light green
                    text_color = colors.HexColor('#2e7d32')  # Dark green
                
                # Apply background color to the Match % cell
                table_style.append(('BACKGROUND', (match_col_index, row_idx), (match_col_index, row_idx), bg_color))
                table_style.append(('TEXTCOLOR', (match_col_index, row_idx), (match_col_index, row_idx), text_color))
                table_style.append(('FONTNAME', (match_col_index, row_idx), (match_col_index, row_idx), 'Helvetica-Bold'))
    
    table.setStyle(TableStyle(table_style))
    return table

def create_district_pdf_report(district, district_data, df, output_path, date_range_info="", matching_stats=None):
    """Create a professional PDF report for a district"""
    
    print(f"🔍 DEBUG: Starting PDF generation for District {district}")
    print(f"  - Output path: {output_path}")
    print(f"  - District data shape: {district_data.shape if hasattr(district_data, 'shape') else type(district_data)}")
    print(f"  - DataFrame shape: {df.shape if hasattr(df, 'shape') else type(df)}")
    print(f"  - Matching stats: {type(matching_stats)} - {matching_stats.shape if hasattr(matching_stats, 'shape') else 'N/A'}")
    
    print("🔧 DEBUG: Setting up banner and document...")
    
    # Title Banner data
    logo_path = os.path.join(os.path.dirname(__file__), "Horizontal_logo_White_PublicSchools.png")
    banner_text = f"NYC Department of Education\nSubstitute Paraprofessional Report\nDistrict {int(district)}"
    
    # Create custom page template function
    def first_page(canvas, doc):
        draw_banner_on_first_page(canvas, doc, banner_text, logo_path)
    
    # Create the PDF document with normal top margin
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=0.75*inch, leftMargin=0.75*inch,
                          topMargin=1*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    story = []
    styles = create_custom_styles()
    
    # Add spacing to account for banner (no longer adding banner as flowable)
    story.append(Spacer(1, 60))  # Extra space for banner area
    
    # Date and range info
    date_text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
    if date_range_info:
        date_text += f"<br/>{date_range_info}"
    
    date_para = Paragraph(date_text, styles['CenterNormal'])
    story.append(date_para)
    story.append(Spacer(1, 20))
    
    # FIRST: District Summary (moved to top per feedback)
    story.append(Paragraph("District Overview", styles['CustomHeading']))
    
    # Calculate overall fill rate for summary sentence
    total_filled = (district_data['Vacancy_Filled'] + district_data['Absence_Filled']).sum()
    total_jobs = district_data['Total'].sum()
    overall_fill_rate = (total_filled / max(total_jobs, 1)) * 100
    
    # Brief summary sentence per feedback
    summary_text = f"Schools in District {int(district)} have an overall fill rate of {overall_fill_rate:.1f}% from SubCentral data."
    story.append(Paragraph(summary_text, styles['Normal']))
    
    # Add match percentage info if available
    district_schools = df[df['District'] == district]['Location'].unique()
    if matching_stats is not None and not matching_stats.empty:
        district_matching = matching_stats[matching_stats['Location'].isin(district_schools)]
        if not district_matching.empty:
            # Calculate average match percentage for the district
            match_pct_col = None
            for col in district_matching.columns:
                if 'Match' in col and ('Percentage' in col or '%' in col):
                    match_pct_col = col
                    break
            
            if match_pct_col and match_pct_col in district_matching.columns:
                avg_match_pct = district_matching[match_pct_col].mean()
                schools_below_90 = len(district_matching[district_matching[match_pct_col] < 90])
                total_schools_with_data = len(district_matching)
                
                match_summary_text = f"The district has an average payroll matching rate of {avg_match_pct:.1f}% across {total_schools_with_data} schools with data."
                if schools_below_90 > 0:
                    match_summary_text += f" {schools_below_90} schools are below the 90% benchmark and may need attention for proper SubCentral usage."
                else:
                    match_summary_text += " All schools meet the 90% matching benchmark."
                
                story.append(Spacer(1, 10))
                story.append(Paragraph(match_summary_text, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # SECOND: Payroll Data Matching Analysis
    print(f"🔧 DEBUG: Checking matching stats - Type: {type(matching_stats)}")
    if matching_stats is not None:
        print(f"  - matching_stats is not None, shape: {matching_stats.shape if hasattr(matching_stats, 'shape') else 'no shape'}")
        print(f"  - empty check: {matching_stats.empty if hasattr(matching_stats, 'empty') else 'no empty attr'}")
        
    if matching_stats is not None and not matching_stats.empty:
        story.append(Paragraph("Payroll Data Matching Analysis", styles['CustomHeading']))
        
        # Add detailed explanation text like the original version
        explanation_text = """This analysis matches individual jobs using <strong>Location + EIS ID + Date</strong> between SubCentral and SREPP payroll systems. 
        The Match Percentage shows what percentage of payroll records have corresponding SubCentral records for each school. 
        Higher percentages indicate better data consistency between the two systems."""
        
        explanation_para = Paragraph(explanation_text, styles['Normal'])
        story.append(explanation_para)
        story.append(Spacer(1, 10))
        
        # Add matching benchmark explanation
        story.append(Paragraph(
            "Schools should aim for a Match % of 90% or higher to ensure proper use of SubCentral for paraprofessional job tracking.",
            styles['Normal']
        ))
        story.append(Spacer(1, 10))
        
        # Get schools in this district first
        district_schools = df[df['District'] == district]['Location'].unique()
        print(f"🔧 DEBUG: Found {len(district_schools)} schools in district {district}")
        
        # Filter matching stats by schools in this district (like the original version)
        district_matching = matching_stats[matching_stats['Location'].isin(district_schools)]
        print(f"🔧 DEBUG: Filtered matching_stats to {len(district_matching)} rows for district schools")
        
        if not district_matching.empty:
            # Check what columns are available and handle missing ones
            subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in district_matching.columns else 'SubCentral_Count'
            payroll_col = 'Payroll Job Days' if 'Payroll Job Days' in district_matching.columns else 'Payroll_Count'
            matched_col = None
            match_pct_col = None
            
            # Look for matched jobs column
            for col in district_matching.columns:
                if 'Matched' in col and 'Job' in col:
                    matched_col = col
                    break
            
            # Look for match percentage column
            for col in district_matching.columns:
                if 'Match' in col and ('Percentage' in col or '%' in col):
                    match_pct_col = col
                    break
            
            # Create summary with available data (like original version)
            match_summary = {
                'Schools with Data': len(district_matching),
                'Total SubCentral Records': int(district_matching[subcentral_col].sum()) if subcentral_col in district_matching.columns else 'N/A',
                'Total Payroll Records': int(district_matching[payroll_col].sum()) if payroll_col in district_matching.columns else 'N/A'
            }
            
            if matched_col and matched_col in district_matching.columns:
                match_summary['Total Matched Records'] = int(district_matching[matched_col].sum())
                
            if match_pct_col and match_pct_col in district_matching.columns:
                match_summary['Average Match Rate'] = district_matching[match_pct_col].mean()
            elif matched_col and subcentral_col in district_matching.columns:
                # Calculate match percentage if we have the data
                total_matched = district_matching[matched_col].sum()
                total_subcentral = district_matching[subcentral_col].sum()
                if total_subcentral > 0:
                    match_summary['Average Match Rate'] = (total_matched / total_subcentral) * 100
            
            match_table = create_summary_table(match_summary, "Matching Summary")
            story.append(match_table)
            story.append(Spacer(1, 15))
            
            # Detailed matching table for schools - like original version
            story.append(Paragraph("School-Level Matching Details", styles['CustomSubheading']))
            
            # Select only the columns that exist for the detailed table (like original)
            available_cols = ['Location']
            column_renames = {'Location': 'School'}
            
            if subcentral_col in district_matching.columns:
                available_cols.append(subcentral_col)
                column_renames[subcentral_col] = 'SubCentral'
            if payroll_col in district_matching.columns:
                available_cols.append(payroll_col)
                column_renames[payroll_col] = 'Payroll'
            if matched_col and matched_col in district_matching.columns:
                available_cols.append(matched_col)
                column_renames[matched_col] = 'Matched'
            if match_pct_col and match_pct_col in district_matching.columns:
                available_cols.append(match_pct_col)
                column_renames[match_pct_col] = 'Match %'
            
            print(f"🔧 DEBUG: Creating matching table with columns: {available_cols}")
            
            # Create table with only available columns and simplified headers (like original)
            display_matching = district_matching[available_cols].copy()
            display_matching = display_matching.rename(columns=column_renames)
            
            # Sort by Match % if available (lowest to highest)
            if 'Match %' in display_matching.columns:
                display_matching = display_matching.sort_values('Match %', ascending=True)
            
            # Use the color-coded table function for matching data
            match_detail_table = create_matching_table_with_colors(display_matching, "School Matching Analysis")
            story.append(match_detail_table)
            
            # Add color legend with proper formatting for ReportLab
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Color Legend:</b>", styles['Normal']))
            story.append(Spacer(1, 5))
            
            # Create legend table with colored cells
            legend_data = [
                ['', 'Performance Level', 'Match % Range'],
                ['', 'Meets Benchmark', '≥90%'],
                ['', 'Needs Improvement', '70-89%'],
                ['', 'Poor Performance', '<70%']
            ]
            
            legend_table = Table(legend_data, colWidths=[0.3*inch, 1.5*inch, 1*inch])
            legend_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                
                # Color indicators
                ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#e8f5e8')),  # Green
                ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#fff3e0')),  # Orange  
                ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#ffebee')),  # Red
                
                # Text formatting
                ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (1, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            story.append(legend_table)
            story.append(PageBreak())
        else:
            story.append(Paragraph("No payroll matching data available for this district.", styles['Normal']))
            story.append(PageBreak())
    
    # THIRD: Job Classifications (moved back to end per feedback)
    story.append(Paragraph("Job Classifications", styles['CustomHeading']))
    story.append(Paragraph("Data source: SubCentral", styles['ItalicStyle'] if hasattr(styles, 'ItalicStyle') else styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Prepare classification data - sort by total jobs (highest to lowest)
    class_data = []
    for _, row in district_data.iterrows():
        total_filled = row['Vacancy_Filled'] + row['Absence_Filled']
        total_unfilled = row['Vacancy_Unfilled'] + row['Absence_Unfilled']
        overall_fill_pct = (total_filled / max(row['Total'], 1)) * 100
        
        class_data.append({
            'Classification': row['Classification'],
            'Total Jobs': int(row['Total']),
            'Jobs Filled': int(total_filled),
            'Jobs Unfilled': int(total_unfilled),
            'Fill Rate %': overall_fill_pct
        })
    
    # Sort by total jobs (highest to lowest) per feedback
    class_df = pd.DataFrame(class_data).sort_values('Total Jobs', ascending=False)
    class_table = create_data_table(class_df, "Classification Statistics")
    story.append(class_table)
    story.append(Spacer(1, 20))
    
    # Footer
    # Footer
    story.append(Spacer(1, 30))
    footer_text = Paragraph("NYC Department of Education - SubCentral System<br/>For questions: SubCentral@schools.nyc.gov",
                           styles['CenterNormal'])
    story.append(footer_text)
    
    print("🔧 DEBUG: Building PDF document...")
    # Build PDF with custom page template for first page banner
    doc.build(story, onFirstPage=first_page)
    print(f"✅ DEBUG: Successfully created PDF for District {district}")
    return output_path

def main_reportlab_compiler():
    """Main function using ReportLab to generate PDFs"""
    # Check if ReportLab is available
    if not REPORTLAB_AVAILABLE:
        if not install_reportlab():
            return
        # Re-import after installation
        global colors, letter, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        global getSampleStyleSheet, ParagraphStyle, inch, canvas, TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    
    try:
        from data_processing import load_and_process_data, create_summary_stats, create_matching_analysis, get_data_date_range
    except ImportError as e:
        print(f"❌ Error importing data processing modules: {e}")
        print("Make sure data_processing.py is in the same directory")
        return
    
    # Configuration
    csv_files = [
        'Fill Rate Data/mayjobs.csv',
        'Fill Rate Data/junejobs.csv',
        'Fill Rate Data/apriljobs.csv',
        'Fill Rate Data/febmarchjobs.csv',
        'Fill Rate Data/decjanjobs.csv',
        'Fill Rate Data/sepoctnovjobs.csv',
        'SREPP1.csv',
        'SREPP2.csv',
    ]
    
    output_directory = 'district_reportlab_pdfs'
    os.makedirs(output_directory, exist_ok=True)
    
    start_time = time.time()
    print("Loading data for ReportLab PDF generation...")
    
    try:
        df, srepp_df = load_and_process_data(csv_files)
        
        if df.empty:
            print("❌ No data loaded! Check your CSV files.")
            return
        
        print(f"✅ Loaded {len(df)} records from SubCentral data")
        if not srepp_df.empty:
            print(f"✅ Loaded {len(srepp_df)} records from SREPP payroll data")
        else:
            print("⚠️ No SREPP payroll data loaded - matching analysis will be skipped")
            
        # Debug: Check what columns are available in the main dataframe
        print(f"🔧 DEBUG: SubCentral data columns: {list(df.columns)[:10]}...")  # Show first 10 columns
        print(f"🔧 DEBUG: Sample districts in data: {sorted(df['District'].unique())[:5]}")  # Show first 5 districts
        
        # Get date range information
        date_range_info = get_data_date_range(df)
        print(f"Data range: {date_range_info}")
        
        # Create summary statistics
        summary_stats = create_summary_stats(df, ['District'])
        if 'Type_Fill_Status' in summary_stats.columns:
            summary_stats = summary_stats.drop(columns=['Type_Fill_Status'])
        
        # Convert to int to avoid float display issues
        int_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled', 
                   'Total_Vacancy', 'Total_Absence', 'Total']
        for col in int_cols:
            if col in summary_stats.columns:
                summary_stats[col] = summary_stats[col].astype(int)
        
        # Create matching analysis
        print(f"🔧 DEBUG: SREPP data empty: {srepp_df.empty}")
        print(f"🔧 DEBUG: SREPP data shape: {srepp_df.shape if hasattr(srepp_df, 'shape') else 'no shape'}")
        
        if not srepp_df.empty:
            matching_stats = create_matching_analysis(df, srepp_df)
            print(f"🔧 DEBUG: Matching analysis result type: {type(matching_stats)}")
            print(f"🔧 DEBUG: Matching analysis shape: {matching_stats.shape if hasattr(matching_stats, 'shape') else 'no shape'}")
        else:
            matching_stats = None
            print("🔧 DEBUG: No SREPP data available, matching_stats set to None")
        
        # Generate PDFs for each district
        districts = sorted(df['District'].unique())
        created_files = []
        failed_files = []
        
        print(f"Creating ReportLab PDFs for {len(districts)} districts...")
        
        for district in districts:
            district_data = summary_stats[summary_stats['District'] == district].copy()
            if len(district_data) > 0:
                pdf_filename = f"District_{int(district)}_Report.pdf"
                pdf_path = os.path.join(output_directory, pdf_filename)
                
                try:
                    create_district_pdf_report(
                        district, district_data, df, pdf_path, 
                        date_range_info, matching_stats
                    )
                    created_files.append(pdf_path)
                    print(f"✅ Created: {pdf_filename}")
                except Exception as e:
                    failed_files.append((district, str(e)))
                    print(f"❌ Failed District {district}: {e}")
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"REPORTLAB PDF GENERATION COMPLETED")
        print(f"{'='*60}")
        print(f"✅ Created {len(created_files)} PDF reports")
        if failed_files:
            print(f"❌ Failed: {len(failed_files)} reports")
            for district, error in failed_files:
                print(f"  - District {district}: {error}")
        print(f"📁 Output directory: {output_directory}")
        print(f"⏱️  Total time: {elapsed:.2f} seconds")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find one or more CSV files")
        print("Please make sure all files exist in the specified paths.")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"❌ Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_reportlab_compiler()
