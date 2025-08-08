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
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
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
    
    return styles

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
    
    # Create table
    table = Table(table_data, colWidths=[2.5*inch, 1.5*inch])
    
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
    
    table = Table(table_data, colWidths=col_widths)
    
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

def create_district_pdf_report(district, district_data, df, output_path, date_range_info="", matching_stats=None):
    """Create a professional PDF report for a district"""
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=0.75*inch, leftMargin=0.75*inch,
                          topMargin=1*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    story = []
    styles = create_custom_styles()
    
    # Title
    title = Paragraph(f"NYC Department of Education<br/>District {int(district)} Substitute Paraprofessional Report", 
                     styles['CustomTitle'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Date and range info
    date_text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
    if date_range_info:
        date_text += f"<br/>Data Period: {date_range_info}"
    
    date_para = Paragraph(date_text, styles['CenterNormal'])
    story.append(date_para)
    story.append(Spacer(1, 20))
    
    # District Summary
    story.append(Paragraph("District Summary", styles['CustomHeading']))
    
    # Calculate district totals
    district_totals = {
        'Total Jobs': int(district_data['Total'].sum()),
        'Total Filled': int((district_data['Vacancy_Filled'] + district_data['Absence_Filled']).sum()),
        'Total Vacancies': int(district_data['Total_Vacancy'].sum()),
        'Total Absences': int(district_data['Total_Absence'].sum()),
        'Vacancy Fill Rate': ((district_data['Vacancy_Filled'].sum() / 
                              max(district_data['Total_Vacancy'].sum(), 1)) * 100),
        'Absence Fill Rate': ((district_data['Absence_Filled'].sum() / 
                              max(district_data['Total_Absence'].sum(), 1)) * 100),
        'Overall Fill Rate': (((district_data['Vacancy_Filled'] + district_data['Absence_Filled']).sum() / 
                             max(district_data['Total'].sum(), 1)) * 100)
    }
    
    summary_table = create_summary_table(district_totals, "District Summary")
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Statistics by Classification
    story.append(Paragraph("Statistics by Classification", styles['CustomHeading']))
    
    # Prepare classification data - simplified combined stats
    class_data = []
    for _, row in district_data.iterrows():
        total_filled = row['Vacancy_Filled'] + row['Absence_Filled']
        total_unfilled = row['Vacancy_Unfilled'] + row['Absence_Unfilled']
        overall_fill_pct = (total_filled / max(row['Total'], 1)) * 100
        
        class_data.append({
            'Classification': row['Classification'],
            'Jobs Filled': int(total_filled),
            'Jobs Unfilled': int(total_unfilled),
            'Total Jobs': int(row['Total']),
            'Fill Rate %': overall_fill_pct
        })
    
    class_df = pd.DataFrame(class_data)
    class_table = create_data_table(class_df, "Classification Statistics")
    story.append(class_table)
    story.append(Spacer(1, 20))
    
    # Schools in District
    story.append(Paragraph(f"Schools in District {int(district)}", styles['CustomHeading']))
    
    district_schools = df[df['District'] == district]['Location'].unique()
    school_data = []
    
    # Import the create_summary_stats function to get proper school statistics
    try:
        from data_processing import create_summary_stats
        
        # Create school-level summary
        district_df = df[df['District'] == district]
        school_summary = create_summary_stats(district_df, ['Location'])
        school_summary = school_summary.groupby('Location', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
        
        for _, row in school_summary.iterrows():
            total_filled = row['Vacancy_Filled'] + row['Absence_Filled']
            fill_rate = (total_filled / max(row['Total'], 1)) * 100
            
            school_data.append({
                'School': row['Location'],
                'Total Jobs': int(row['Total']),
                'Jobs Filled': int(total_filled),
                'Jobs Unfilled': int(row['Total'] - total_filled),
                'Fill Rate %': fill_rate
            })
            
    except Exception as e:
        print(f"Warning: Could not create detailed school statistics: {e}")
        # Fallback to simple counting
        for location in sorted(district_schools):
            school_df = df[(df['District'] == district) & (df['Location'] == location)]
            if not school_df.empty:
                total_jobs = len(school_df)
                filled_jobs = len(school_df[school_df['Fill_Status'] == 'Filled'])
                fill_rate = (filled_jobs / max(total_jobs, 1)) * 100
                
                school_data.append({
                    'School': location,
                    'Total Jobs': total_jobs,
                    'Jobs Filled': filled_jobs,
                    'Jobs Unfilled': total_jobs - filled_jobs,
                    'Fill Rate %': fill_rate
                })
    
    if school_data:
        schools_df = pd.DataFrame(school_data)
        schools_table = create_data_table(schools_df, "Schools")
        story.append(schools_table)
    else:
        story.append(Paragraph("No school data available", styles['Normal']))
    
    # Add matching analysis if available
    if matching_stats is not None and not matching_stats.empty:
        story.append(PageBreak())
        story.append(Paragraph("Payroll Data Matching Analysis", styles['CustomHeading']))
        
        district_matching = matching_stats[matching_stats['Location'].isin(district_schools)]
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
            
            # Create summary with available data
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
            
            # Detailed matching table for schools - only show available columns with simplified headers
            story.append(Paragraph("School-Level Matching Details", styles['CustomSubheading']))
            
            # Select only the columns that exist for the detailed table
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
            
            # Create table with only available columns and simplified headers
            display_matching = district_matching[available_cols].copy()
            display_matching = display_matching.rename(columns=column_renames)
            match_detail_table = create_data_table(display_matching, "School Matching")
            story.append(match_detail_table)
        else:
            story.append(Paragraph("No payroll matching data available for this district.", styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = Paragraph("NYC Department of Education - SubCentral System<br/>For questions: SubCentral@schools.nyc.gov",
                           styles['CenterNormal'])
    story.append(footer_text)
    
    # Build PDF
    doc.build(story)
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
        matching_stats = create_matching_analysis(df, srepp_df) if not srepp_df.empty else None
        
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
