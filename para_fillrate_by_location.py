import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import plotly.io as pio
import numpy as np
import os
import re
import time

# === GLOBAL CONSTANTS ===
DISPLAY_COLS = [
    'Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
    'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct'
]

DISPLAY_COLS_RENAME = {
    'Classification': 'Classification',
    'Vacancy_Filled': 'Vacancy Filled',
    'Vacancy_Unfilled': 'Vacancy Unfilled',
    'Total_Vacancy': 'Total Vacancy',
    'Vacancy_Fill_Pct': 'Vacancy Fill %',
    'Absence_Filled': 'Absence Filled',
    'Absence_Unfilled': 'Absence Unfilled',
    'Total_Absence': 'Total Absence',
    'Absence_Fill_Pct': 'Absence Fill %',
    'Total': 'Total',
    'Overall_Fill_Pct': 'Overall Fill %'
}

def format_pct(x):
    return f"{x:.1f}%" if isinstance(x, (int, float)) else str(x)

def format_int(x):
    return f"{int(x):,}" if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else str(x)

def load_and_process_data(csv_file_path):
    """
    Load CSV data and process it for dashboard display
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # Parse Job Start dates (convert from Excel serial date format)
    if 'Job Start' in df.columns:
        # Convert Excel serial date to datetime (Excel serial dates start from 1900-01-01)
        df['Job Start'] = pd.to_datetime(df['Job Start'] - 1, unit='D', origin='1900-01-01')
    
    # Clean Classification names to remove newlines and extra spaces
    df['Classification'] = df['Classification'].str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
    df['Classification'] = df['Classification'].str.replace(r'\s+', ' ', regex=True)
    
    # Create District code (ensure it's an integer and remove rows with NaN districts)
    df = df.dropna(subset=['District'])  # Remove rows where District is NaN
    df['District'] = df['District'].astype(int)

    # Add column for boroughs
    df['Borough'] = df['Location'].apply(get_borough_from_location)
    
    # Clean Location names for folder creation
    df['Location_Clean'] = df['Location'].str.replace(r'[<>:"/\\|?*]', '_', regex=True)
    df['Type'] = df['Type'].str.strip().str.title()
    
    # Define filled vs unfilled status
    filled_statuses = [
        'Finished/Admin Assigned',
        'Finished/IVR Assigned', 
        'Finished/Pre Arranged',
        'Finished/Web Sub Search'
    ]
    
    # Create fill status column
    df['Fill_Status'] = df['Status'].apply(
        lambda x: 'Filled' if x in filled_statuses else 'Unfilled'
    )
    
    # Create combined category for Type + Fill Status
    df['Type_Fill_Status'] = df['Type'] + '_' + df['Fill_Status']
    
    return df

def get_borough_from_location(location):
    """
    Extract borough from location based on first letter
    """

    if pd.isna(location) or not location:
        return 'Unknown'
    
    first_char = location.strip()[0].upper()
    borough_map = {
        'M': 'Manhattan', 
        'K': 'Brooklyn',
        'Q': 'Queens',
        'X': 'Bronx',
        'R': 'Staten Island'
    }

    return borough_map.get(first_char, 'Unknown')

def get_data_date_range(df):
    """
    Get the date range from Job Start column
    """
    if 'Job Start' not in df.columns:
        return "Date range not available"
    
    try:
        # Get min and max dates, excluding NaT (Not a Time) values
        valid_dates = df['Job Start'].dropna()
        if len(valid_dates) == 0:
            return "Date range not available"
        
        min_date = valid_dates.min()
        max_date = valid_dates.max()
        
        # Format dates as readable strings
        min_date_str = min_date.strftime('%B %d, %Y')
        max_date_str = max_date.strftime('%B %d, %Y')
        
        if min_date.date() == max_date.date():
            return f"Data from: {min_date_str}"
        else:
            return f"Data period: {min_date_str} to {max_date_str}"
    except Exception as e:
        print(f"Warning: Could not parse date range - {e}")
        return "Date range not available"

def create_borough_summary_stats(df):
    """
    Create summary statistics by borough
    """
    return create_summary_stats(df, ['Borough'])

def create_summary_stats(df, group_cols):
    """
    Create summary statistics by specified grouping columns
    """
    # Group by specified columns and Type_Fill_Status
    summary = df.groupby(group_cols + ['Classification', 'Type_Fill_Status']).size().reset_index(name='Count')
    
    # Pivot to get all combinations
    summary_pivot = summary.pivot_table(
        index=group_cols + ['Classification'],
        columns='Type_Fill_Status',
        values='Count',
        fill_value=0
    )
    # Flatten columns if pivot_table creates a MultiIndex
    if isinstance(summary_pivot.columns, pd.MultiIndex):
        summary_pivot.columns = summary_pivot.columns.get_level_values(-1)
    summary_pivot = summary_pivot.reset_index()
    summary_pivot.columns.name = None
    
    # Ensure all possible columns exist
    expected_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled']
    for col in expected_cols:
        if col not in summary_pivot.columns:
            summary_pivot[col] = 0
    
    # Calculate totals and percentages
    summary_pivot['Total_Vacancy'] = summary_pivot['Vacancy_Filled'] + summary_pivot['Vacancy_Unfilled']
    summary_pivot['Total_Absence'] = summary_pivot['Absence_Filled'] + summary_pivot['Absence_Unfilled']
    summary_pivot['Total'] = summary_pivot['Total_Vacancy'] + summary_pivot['Total_Absence']
    
    # Calculate percentages
    summary_pivot['Vacancy_Fill_Pct'] = np.where(
        summary_pivot['Total_Vacancy'] > 0,
        (summary_pivot['Vacancy_Filled'] / summary_pivot['Total_Vacancy'] * 100).round(1),
        0
    )
    summary_pivot['Absence_Fill_Pct'] = np.where(
        summary_pivot['Total_Absence'] > 0,
        (summary_pivot['Absence_Filled'] / summary_pivot['Total_Absence'] * 100).round(1),
        0
    )
    summary_pivot['Overall_Fill_Pct'] = np.where(
        summary_pivot['Total'] > 0,
        ((summary_pivot['Vacancy_Filled'] + summary_pivot['Absence_Filled']) / summary_pivot['Total'] * 100).round(1),
        0
    )

    # Remove 'Type_Fill_Status' if present
    if 'Type_Fill_Status' in summary_pivot.columns:
        summary_pivot = summary_pivot.drop(columns=['Type_Fill_Status'])

    # Only keep the columns needed for display
    display_cols = group_cols + [
        'Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct'
    ]
    summary_pivot = summary_pivot[[col for col in display_cols if col in summary_pivot.columns]]
    return summary_pivot

def clean_classification_for_display(classification):
    """
    Clean classification names for display in bar charts
    """
    return classification.replace(' SPEAKING PARA', '')

def create_school_report(district, location, location_clean, school_data, output_dir, date_range_info):
    """
    Create a comprehensive report for a single school
    """
    # Create subfolder for school if it doesn't exist
    school_dir = os.path.join(output_dir, f"District_{int(district)}", "Schools", f"School_{location_clean}")
    os.makedirs(school_dir, exist_ok=True)
    
    # Create summary table as HTML
    table_html = df_with_pretty_columns(school_data[DISPLAY_COLS]).to_html(
        index=False,
        table_id='summary-table',
        classes='table table-striped',
        formatters={
            DISPLAY_COLS_RENAME.get(col, col): format_pct if 'Pct' in col else format_int
            for col in DISPLAY_COLS
        }
    )

    
    # --- Key Insights Section ---
    # Compute key metrics for the summary box (use first row, as school_data is per school)
    key_row = school_data.iloc[0]
    key_insights_html = f'''
    <div class="summary-box">
        <h3>Key Insights</h3>
        <ul>
            <li><strong>Total Jobs:</strong> {format_int(school_data["Total"].sum())}</li>
            <li><strong>Total Vacancies:</strong> {format_int(school_data["Total_Vacancy"].sum())} ({format_pct((school_data["Total_Vacancy"].sum()/school_data["Total"].sum()*100) if school_data["Total"].sum() > 0 else 0)})</li>
            <li><strong>Total Absences:</strong> {format_int(school_data["Total_Absence"].sum())} ({format_pct((school_data["Total_Absence"].sum()/school_data["Total"].sum()*100) if school_data["Total"].sum() > 0 else 0)})</li>
            <li><strong>Overall Fill Rate:</strong> {format_pct((school_data["Vacancy_Filled"].sum() + school_data["Absence_Filled"].sum())/school_data["Total"].sum()*100 if school_data["Total"].sum() > 0 else 0)}</li>
            <li><strong>Vacancy Fill Rate:</strong> {format_pct((school_data["Vacancy_Filled"].sum()/school_data["Total_Vacancy"].sum()*100) if school_data["Total_Vacancy"].sum() > 0 else 0)}</li>
            <li><strong>Absence Fill Rate:</strong> {format_pct((school_data["Absence_Filled"].sum()/school_data["Total_Absence"].sum()*100) if school_data["Total_Absence"].sum() > 0 else 0)}</li>
            <li><strong>Classifications:</strong> {', '.join(school_data['Classification'].unique())}</li>
        </ul>
    </div>
    '''
    # Create grouped bar chart
    fig_bar = go.Figure()
    # Add bars for each category
    fig_bar.add_trace(go.Bar(
        name='Vacancy Filled',
        x=school_data['Classification'].apply(clean_classification_for_display),
        y=school_data['Vacancy_Filled'],
        marker_color='darkgreen',
        text=[f"{val:,}" for val in school_data['Vacancy_Filled']],
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=school_data['Classification'].apply(clean_classification_for_display),
        y=school_data['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=[f"{val:,}" for val in school_data['Vacancy_Unfilled']],
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Absence Filled',
        x=school_data['Classification'].apply(clean_classification_for_display),
        y=school_data['Absence_Filled'],
        marker_color='forestgreen',
        text=[f"{val:,}" for val in school_data['Absence_Filled']],
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Absence Unfilled',
        x=school_data['Classification'].apply(clean_classification_for_display),
        y=school_data['Absence_Unfilled'],
        marker_color='red',
        text=[f"{val:,}" for val in school_data['Absence_Unfilled']],
        textposition='auto'
    ))
    
    fig_bar.update_layout(
        title=f'Jobs by Classification and Type - {location}',
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=500,
        width=1200
    )
    
    # Save bar chart
    # Further sanitize the location_clean for filename to ensure Windows compatibility
    safe_location_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(location_clean)).strip()
    # Remove multiple consecutive underscores for cleaner filenames
    safe_location_name = re.sub(r'_+', '_', safe_location_name)
    if len(safe_location_name) > 200:  # Prevent long filenames
        safe_location_name = safe_location_name[:200]
    bar_chart_file = os.path.join(school_dir, f'{safe_location_name}_bar_chart.html')
    # Ensure the directory exists
    os.makedirs(os.path.dirname(bar_chart_file), exist_ok=True)
    
    # Generate HTML and write to file
    html_str = pio.to_html(fig_bar, include_plotlyjs='cdn', div_id=f"{safe_location_name}_bar_chart")
    with open(bar_chart_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    # Create pie charts for each classification
    pie_charts_html = ""
    for idx, (_, row) in enumerate(school_data.iterrows()):
        if row['Total'] > 0:  # Only create pie chart if there are jobs
            # Sanitize both location_clean and classification for filename with comprehensive approach
            safe_location = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(location_clean)).strip()
            safe_classification = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(row['Classification'])).strip()
            
            # Remove multiple consecutive underscores for cleaner filenames
            safe_location = re.sub(r'_+', '_', safe_location)
            safe_classification = re.sub(r'_+', '_', safe_classification)
            
            # Ensure filename isn't too long (Windows has 260 char limit for full path)
            base_name = f'{safe_location}_{safe_classification}_pie'
            if len(base_name) > 200:  # Leave room for directory path and extension
                base_name = base_name[:200]
            pie_fig = go.Figure(data=[go.Pie(
                labels=['Vacancy Filled', 'Vacancy Unfilled', 'Absence Filled', 'Absence Unfilled'],
                values=[row['Vacancy_Filled'], row['Vacancy_Unfilled'], row['Absence_Filled'], row['Absence_Unfilled']],
                hole=0.3,
                marker_colors=['darkgreen', 'lightcoral', 'forestgreen', 'red'],
                textinfo='value+percent',
                textposition='inside',
                textfont=dict(size=14),
                texttemplate='%{value:,}<br>%{percent}'
            )])
            pie_fig.update_layout(
                title=dict(
                    text=f"{row['Classification']}<br>({int(row['Total']):,} total jobs)",
                    y=0.95,
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=16)
                ),
                height=450,
                width=400,
                showlegend=True,
                margin=dict(t=60, b=40, l=40, r=40)
            )
            
            pie_file = os.path.join(school_dir, f'{base_name}.html')
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(pie_file), exist_ok=True)
            pyo.plot(pie_fig, filename=pie_file, auto_open=False)
            
            pie_charts_html += f'<iframe src="{os.path.basename(pie_file)}" width="420" height="470" frameborder="0"></iframe>\n'
    
    # Calculate key insights for the school
    total_jobs = int(school_data['Total'].sum())
    total_vacancy = int(school_data['Total_Vacancy'].sum())
    total_absence = int(school_data['Total_Absence'].sum())
    vacancy_filled = int(school_data['Vacancy_Filled'].sum())
    absence_filled = int(school_data['Absence_Filled'].sum())
    overall_fill_pct = (vacancy_filled + absence_filled) / total_jobs * 100 if total_jobs > 0 else 0
    vacancy_fill_pct = (vacancy_filled / total_vacancy * 100) if total_vacancy > 0 else 0
    absence_fill_pct = (absence_filled / total_absence * 100) if total_absence > 0 else 0

    key_insights_html = f"""
        <div class=\"summary-box\" style=\"background-color:#f8f9fa;padding:15px;border-radius:5px;margin:10px 0;\">
            <h3>Key Insights</h3>
            <ul>
                <li><strong>Total Jobs:</strong> {total_jobs}</li>
                <li><strong>Total Vacancies:</strong> {total_vacancy} ({(total_vacancy/total_jobs*100) if total_jobs > 0 else 0:.1f}%)</li>
                <li><strong>Total Absences:</strong> {total_absence} ({(total_absence/total_jobs*100) if total_jobs > 0 else 0:.1f}%)</li>
                <li><strong>Overall Fill Rate:</strong> {overall_fill_pct:.1f}%</li>
                <li><strong>Vacancy Fill Rate:</strong> {vacancy_fill_pct:.1f}%</li>
                <li><strong>Absence Fill Rate:</strong> {absence_fill_pct:.1f}%</li>
            </ul>
        </div>
    """
    # Create comprehensive HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYCDOE Jobs Report - {location}</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
        <style>
            :root {{
                --primary-color: #2E86AB;
                --secondary-color: #A23B72;
                --success-color: #2ca02c;
                --warning-color: #ff7f0e;
                --danger-color: #d62728;
                --light-bg: #f5f5f5;
                --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
                --hover-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }}

            .header {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white; 
                text-align: center; 
                padding: 40px 20px; 
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="80" r="2.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                opacity: 0.3;
            }}

            .header h1 {{
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }}

            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }}

            .content {{
                padding: 30px;
            }}

            .section {{ 
                background: white;
                margin: 30px 0; 
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }}

            .section:hover {{
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }}

            .section h2, .section h3 {{ 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.8em;
            }}

            .section h3 {{
                font-size: 1.5em;
            }}

            .navigation {{ 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 20px; 
                border-radius: 15px; 
                margin: 20px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
            }}

            .navigation a {{
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                display: inline-block;
                margin: 5px;
            }}

            .navigation a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(46, 134, 171, 0.3);
            }}

            .summary-box {{ 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 25px; 
                border-radius: 15px; 
                margin: 25px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
            }}

            .summary-box h3 {{
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.4em;
            }}

            .summary-box ul {{
                list-style: none;
                padding: 0;
            }}

            .summary-box li {{
                padding: 8px 0;
                border-bottom: 1px solid rgba(46, 134, 171, 0.1);
                font-size: 1.1em;
            }}

            .summary-box li:last-child {{
                border-bottom: none;
            }}

            .summary-box strong {{
                color: var(--primary-color);
            }}

            .table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 25px 0; 
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .table-responsive {{
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .table th, .table td {{ 
                padding: 15px 12px; 
                text-align: center; 
                border-bottom: 1px solid #e0e0e0;
            }}

            .table th {{ 
                background: var(--primary-color);
                color: white;
                font-weight: 600;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .table tbody tr {{
                transition: all 0.3s ease;
            }}

            .table tbody tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}

            .table tbody tr:hover {{
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .pie-container {{ 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin: 25px 0;
            }}

            .chart-container {{ 
                margin: 25px 0; 
                text-align: center;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .footer {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                text-align: center;
                padding: 30px;
                margin-top: 40px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .footer a {{ 
                color: #FFD700; 
                text-decoration: none; 
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .footer a:hover {{ 
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                transform: scale(1.05);
            }}

            iframe {{
                border: none;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
            }}

            iframe:hover {{
                box-shadow: var(--hover-shadow);
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                }}

                .header {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                .content {{
                    padding: 15px;
                }}

                .section {{
                    padding: 20px;
                    margin: 15px 0;
                }}

                .pie-container {{
                    grid-template-columns: 1fr;
                    gap: 15px;
                }}

                iframe {{
                    width: 100% !important;
                    height: 400px !important;
                }}
            }}

            /* Loading Animation */
            .loading {{
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(46, 134, 171, 0.3);
                border-radius: 50%;
                border-top-color: var(--primary-color);
                animation: spin 1s ease-in-out infinite;
            }}

            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}

            /* Print Styles */
            @media print {{
                body {{
                    background: white;
                }}

                .section {{
                    break-inside: avoid;
                    page-break-inside: avoid;
                    box-shadow: none;
                    border: 1px solid #ddd;
                }}

                .header {{
                    background: white !important;
                    color: black !important;
                    border: 2px solid var(--primary-color);
                }}

                iframe {{
                    display: none;
                }}
            }}
        </style>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {{
                $('.table').DataTable({{
                    paging: false, 
                    searching: false, 
                    info: false, 
                    order: [],
                    responsive: true
                }});
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NYCDOE Substitute Paraprofessional Jobs Report</h1>
                <p>School: {location} (District {int(district)})</p>
                <p>{date_range_info}</p>
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>

            <div class="content">
                <div class="navigation">
                    <a href="../../../index.html">← Back to Overall Summary</a> | 
                    <a href="../../{int(district)}_report.html">← Back to District {int(district)}</a>
                </div>
                
                <div class="section">
                    <h2>Key Insights</h2>
                    {key_insights_html}
                </div>

                <div class="section">
                    <h3>Summary Statistics</h3>
                    <div class="table-responsive">
                        {table_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Jobs by Classification and Type</h3>
                    <div class="chart-container">
                        <iframe src="{safe_location_name}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                    </div>
                </div>

                <div class="section">
                    <h3>Breakdown by Classification</h3>
                    <div class="pie-container">
                        {pie_charts_html}
                    </div>
                </div>
            </div>
            
            {get_professional_footer()}
        </div>
    </body>
    </html>
    """
    # Save main report
    report_file = os.path.join(school_dir, f'{safe_location_name}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file

def create_district_report(district, district_data, df, output_dir, summary_stats, date_range_info):
    """
    Create a comprehensive report for a single District including school summaries
    """
    # Create subfolder for District if it doesn't exist
    district_dir = os.path.join(output_dir, f"District_{int(district)}")
    os.makedirs(district_dir, exist_ok=True)
    
    # Get the borough for this district
    district_borough = df[df['District'] == district]['Borough'].iloc[0]
    borough_name_clean = district_borough.replace(' ', '_').replace('/', '_')
    # Get borough data for comparison
    borough_data = create_summary_stats(df[df['Borough'] == district_borough], ['Borough'])
    # Create summary table as HTML
    table_html = df_with_pretty_columns(district_data[DISPLAY_COLS]).to_html(
        index=False,
        table_id='summary-table',
        classes='table table-striped',
        formatters={
            DISPLAY_COLS_RENAME.get(col, col): format_pct if 'Pct' in col else format_int
            for col in DISPLAY_COLS
        }
    )

    
    # --- Summary by School Table ---
    df_district = df[df['District'] == district]
    summary_by_school = create_summary_stats(df_district, ['Location'])
    summary_by_school = summary_by_school.groupby('Location', as_index=False).agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    })
    summary_by_school['Vacancy_Fill_Pct'] = np.where(
        summary_by_school['Total_Vacancy'] > 0,
        (summary_by_school['Vacancy_Filled'] / summary_by_school['Total_Vacancy'] * 100).round(1),
        0
    )
    summary_by_school['Absence_Fill_Pct'] = np.where(
        summary_by_school['Total_Absence'] > 0,
        (summary_by_school['Absence_Filled'] / summary_by_school['Total_Absence'] * 100).round(1),
        0
    )
    summary_by_school['Overall_Fill_Pct'] = np.where(
        summary_by_school['Total'] > 0,
        ((summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']) / summary_by_school['Total'] * 100).round(1),
        0
    )
    school_display_cols = ['Location', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct']
    summary_by_school = summary_by_school[[col for col in school_display_cols if col in summary_by_school.columns]]
    # Sort by school name alphabetically
    summary_by_school = summary_by_school.sort_values('Location')
    summary_by_school_html = df_with_pretty_columns(summary_by_school.rename(columns={'Location': 'School'})).to_html(
        index=False,
        classes='table',
        formatters={
            'School': str,
            'Vacancy Filled': format_int,
            'Vacancy Unfilled': format_int,
            'Total Vacancy': format_int,
            'Vacancy Fill %': format_pct,
            'Absence Filled': format_int,
            'Absence Unfilled': format_int,
            'Total Absence': format_int,
            'Absence Fill %': format_pct,
            'Total': format_int,
            'Overall Fill %': format_pct
        }
    )
    # Generate school reports and links
    district_schools = df[df['District'] == district]['Location'].unique()
    school_links = ""
    school_reports = []
    for location in sorted(district_schools):
        location_clean = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(location)).strip()
        # Ensure the clean location name isn't too long
        if len(location_clean) > 200:
            location_clean = location_clean[:200]
        
        # Create safe location name for file paths (additional sanitization)
        safe_location_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(location_clean)).strip()
        if len(safe_location_name) > 200:
            safe_location_name = safe_location_name[:200]
        
        school_df = df[(df['District'] == district) & (df['Location'] == location)]
        school_summary = create_summary_stats(school_df, ['District', 'Location'])
        if len(school_summary) > 0:
            school_report = create_school_report(district, location, location_clean, school_summary, output_dir, date_range_info)
            school_reports.append(school_report)
            school_links += f'<li><a href="Schools/School_{location_clean}/{safe_location_name}_report.html">{location}</a> - {school_summary["Total"].sum().astype(int)} total jobs</li>\n'
    # Calculate summary stats for comparison with district stats
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    })
    overall_stats = {
        'Total': int(overall_totals['Total']),
        'Total_Vacancy': int(overall_totals['Total_Vacancy']),
        'Total_Absence': int(overall_totals['Total_Absence']),
        'Vacancy_Filled': int(overall_totals['Vacancy_Filled']),
        'Absence_Filled': int(overall_totals['Absence_Filled'])
    }
    # Create grouped bar chart
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name='Vacancy Filled',
        x=district_data['Classification'].apply(clean_classification_for_display),
        y=district_data['Vacancy_Filled'],
        marker_color='darkgreen',
        text=[f"{val:,}" for val in district_data['Vacancy_Filled']],
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=district_data['Classification'].apply(clean_classification_for_display),
        y=district_data['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=[f"{val:,}" for val in district_data['Vacancy_Unfilled']],
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Absence Filled',
        x=district_data['Classification'].apply(clean_classification_for_display),
        y=district_data['Absence_Filled'],
        marker_color='forestgreen',
        text=[f"{val:,}" for val in district_data['Absence_Filled']],
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Absence Unfilled',
        x=district_data['Classification'].apply(clean_classification_for_display),
        y=district_data['Absence_Unfilled'],
        marker_color='red',
        text=[f"{val:,}" for val in district_data['Absence_Unfilled']],
        textposition='auto'
    ))
    
    fig_bar.update_layout(
        title=f'Jobs by Classification and Type - District {int(district)}',
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=500,
        width=1200
    )
    
    # Save bar chart
    bar_chart_file = os.path.join(district_dir, f'{int(district)}_bar_chart.html')
    
    # Generate HTML and write to file
    html_str = pio.to_html(fig_bar, include_plotlyjs='cdn', div_id=f"district_{int(district)}_bar_chart")
    with open(bar_chart_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    # Create pie charts for each classification
    pie_charts_html = ""
    for idx, (_, row) in enumerate(district_data.iterrows()):
        if row['Total'] > 0:  # Only create pie chart if there are jobs
            pie_fig = go.Figure(data=[go.Pie(
                labels=['Vacancy Filled', 'Vacancy Unfilled', 'Absence Filled', 'Absence Unfilled'],
                values=[row['Vacancy_Filled'], row['Vacancy_Unfilled'], row['Absence_Filled'], row['Absence_Unfilled']],
                hole=0.3,
                marker_colors=['darkgreen', 'lightcoral', 'forestgreen', 'red'],
                textinfo='value+percent',
                textposition='inside',
                textfont=dict(size=14),
                texttemplate='%{value:,}<br>%{percent}'
            )])
            pie_fig.update_layout(
                title=dict(
                    text=f"{row['Classification']}<br>({int(row['Total']):,} total jobs)",
                    y=0.95,
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=16)
                ),
                height=450,
                width=400,
                showlegend=True,
                margin=dict(t=60, b=40, l=40, r=40)
            )
            
            safe_classification = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(row["Classification"])).strip()
            # Remove multiple consecutive underscores and ensure reasonable length
            safe_classification = re.sub(r'_+', '_', safe_classification)
            # Ensure filename isn't too long
            base_name = f'{int(district)}_{safe_classification}_pie'
            if len(base_name) > 200:
                base_name = base_name[:200]
            pie_file = os.path.join(district_dir, f'{base_name}.html')
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(pie_file), exist_ok=True)
            pyo.plot(pie_fig, filename=pie_file, auto_open=False)
            
            pie_charts_html += f'<iframe src="{os.path.basename(pie_file)}" width="420" height="470" frameborder="0"></iframe>\n'
    
    # Create comprehensive HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYCDOE Jobs Report - District {int(district)}</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
        <style>
            :root {{
                --primary-color: #2E86AB;
                --secondary-color: #A23B72;
                --success-color: #2ca02c;
                --warning-color: #ff7f0e;
                --danger-color: #d62728;
                --light-bg: #f5f5f5;
                --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
                --hover-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }}

            .header {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white; 
                text-align: center; 
                padding: 40px 20px; 
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="80" r="2.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                opacity: 0.3;
            }}

            .header h1 {{
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }}

            .header h2 {{
                font-size: 1.5em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
                margin-bottom: 10px;
            }}

            .content {{
                padding: 30px;
            }}

            .section {{ 
                background: white;
                margin: 30px 0; 
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }}

            .section:hover {{
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }}

            .section h3 {{ 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.5em;
            }}

            .navigation {{ 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 20px; 
                border-radius: 15px; 
                margin: 20px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
            }}

            .navigation a {{
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                display: inline-block;
                margin: 5px;
            }}

            .navigation a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(46, 134, 171, 0.3);
            }}

            .table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 25px 0; 
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .table th, .table td {{ 
                padding: 15px 12px; 
                text-align: center; 
                border-bottom: 1px solid #e0e0e0;
            }}

            .table th {{ 
                background: var(--primary-color);
                color: white;
                font-weight: 600;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .table tbody tr {{
                transition: all 0.3s ease;
            }}

            .table tbody tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}

            .table tbody tr:hover {{
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .pie-container {{ 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin: 25px 0;
            }}

            .comparison-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}

            .comparison-card {{
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }}

            .comparison-card:hover {{
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }}

            .comparison-card.citywide {{
                background: linear-gradient(135deg, #e8f4f8, #d6eaf8);
            }}

            .comparison-card.borough {{
                background: linear-gradient(135deg, #f4e8f8, #e8d6f8);
            }}

            .comparison-card.district {{
                background: linear-gradient(135deg, #f0f8e8, #e8f8d6);
            }}

            .comparison-card h4 {{
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }}

            .comparison-card ul {{
                list-style: none;
                padding: 0;
            }}

            .comparison-card li {{
                padding: 8px 0;
                border-bottom: 1px solid rgba(46, 134, 171, 0.1);
                font-size: 1.1em;
            }}

            .comparison-card li:last-child {{
                border-bottom: none;
            }}

            .school-links {{
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .school-links ul {{
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 30px;
            }}

            .school-links li {{
                padding: 8px 0;
                break-inside: avoid;
            }}

            .school-links a {{
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }}

            .school-links a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }}

            .chart-container {{ 
                margin: 25px 0; 
                text-align: center;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .footer {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                text-align: center;
                padding: 30px;
                margin-top: 40px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .footer a {{ 
                color: #FFD700; 
                text-decoration: none; 
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .footer a:hover {{ 
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                transform: scale(1.05);
            }}

            iframe {{
                border: none;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
            }}

            iframe:hover {{
                box-shadow: var(--hover-shadow);
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                }}

                .header {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                .content {{
                    padding: 15px;
                }}

                .section {{
                    padding: 20px;
                    margin: 15px 0;
                }}

                .comparison-grid {{
                    grid-template-columns: 1fr;
                }}

                .school-links ul {{
                    columns: 1;
                }}

                iframe {{
                    width: 100% !important;
                    height: 400px !important;
                }}
            }}

            .table-responsive {{
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

        </style>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {{
                $('.table').DataTable({{
                    paging: false, 
                    searching: false, 
                    info: false, 
                    order: [],
                    responsive: true
                }});
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NYCDOE Substitute Paraprofessional Jobs Report</h1>
                <h2>District: {int(district)}</h2>
                <p>{date_range_info}</p>
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>

            <div class="content">
                <div class="navigation">
                    <a href="../index.html">← Back to Overall Summary</a> | 
                    <a href="../Borough_{borough_name_clean}/{borough_name_clean}_report.html">← Back to {district_borough}</a>
                </div>
                
                <div class="section">
                    <h3>Summary Statistics</h3>
                    <div class="table-responsive">
                        {table_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Summary by School</h3>
                    <div class="table-responsive">
                        {summary_by_school_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Jobs by Classification and Type</h3>
                    <div class="chart-container">
                        <iframe src="{int(district)}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                    </div>
                </div>

                <div class="section">
                    <h3>Breakdown by Classification</h3>
                    <div class="pie-container">
                        {pie_charts_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Comparison: Citywide vs Borough vs District</h3>
                    <div class="comparison-grid">
                        <div class="comparison-card citywide">
                            <h4>Citywide Statistics</h4>
                            <ul>
                                <li><strong>Total Jobs:</strong> {overall_stats['Total']:,}</li>
                                <li><strong>Total Vacancies:</strong> {overall_stats['Total_Vacancy']:,} ({(overall_stats['Total_Vacancy'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)</li>
                                <li><strong>Total Absences:</strong> {overall_stats['Total_Absence']:,} ({(overall_stats['Total_Absence'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)</li>
                                <li><strong>Overall Fill Rate:</strong> {((overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']) / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%</li>
                                <li><strong>Vacancy Fill Rate:</strong> {(overall_stats['Vacancy_Filled'] / overall_stats['Total_Vacancy'] * 100) if overall_stats['Total_Vacancy'] > 0 else 0:.1f}%</li>
                                <li><strong>Absence Fill Rate:</strong> {(overall_stats['Absence_Filled'] / overall_stats['Total_Absence'] * 100) if overall_stats['Total_Absence'] > 0 else 0:.1f}%</li>
                                <li><strong>Number of Schools:</strong> {len(df['Location'].unique())}</li>
                            </ul>
                        </div>
                        <div class="comparison-card borough">
                            <h4>{district_borough} Statistics</h4>
                            <ul>
                                <li><strong>Total Jobs:</strong> {int(borough_data['Total'].sum()):,}</li>
                                <li><strong>Total Vacancies:</strong> {int(borough_data['Total_Vacancy'].sum()):,} ({(borough_data['Total_Vacancy'].sum() / borough_data['Total'].sum() * 100) if borough_data['Total'].sum() > 0 else 0:.1f}%)</li>
                                <li><strong>Total Absences:</strong> {int(borough_data['Total_Absence'].sum()):,} ({(borough_data['Total_Absence'].sum() / borough_data['Total'].sum() * 100) if borough_data['Total'].sum() > 0 else 0:.1f}%)</li>
                                <li><strong>Overall Fill Rate:</strong> {((borough_data['Vacancy_Filled'].sum() + borough_data['Absence_Filled'].sum()) / borough_data['Total'].sum() * 100) if borough_data['Total'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Vacancy Fill Rate:</strong> {(borough_data['Vacancy_Filled'].sum() / borough_data['Total_Vacancy'].sum() * 100) if borough_data['Total_Vacancy'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Absence Fill Rate:</strong> {(borough_data['Absence_Filled'].sum() / borough_data['Total_Absence'].sum() * 100) if borough_data['Total_Absence'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Number of Schools:</strong> {len(df[df['Borough'] == district_borough]['Location'].unique())}</li>
                            </ul>
                        </div>
                        <div class="comparison-card district">
                            <h4>District {int(district)} Statistics</h4>
                            <ul>
                                <li><strong>Total Jobs:</strong> {int(district_data['Total'].sum()):,}</li>
                                <li><strong>Total Vacancies:</strong> {int(district_data['Total_Vacancy'].sum()):,} ({(district_data['Total_Vacancy'].sum() / district_data['Total'].sum() * 100) if district_data['Total'].sum() > 0 else 0:.1f}%)</li>
                                <li><strong>Total Absences:</strong> {int(district_data['Total_Absence'].sum()):,} ({(district_data['Total_Absence'].sum() / district_data['Total'].sum() * 100) if district_data['Total'].sum() > 0 else 0:.1f}%)</li>
                                <li><strong>Overall Fill Rate:</strong> {((district_data['Vacancy_Filled'].sum() + district_data['Absence_Filled'].sum()) / district_data['Total'].sum() * 100) if district_data['Total'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Vacancy Fill Rate:</strong> {(district_data['Vacancy_Filled'].sum() / district_data['Total_Vacancy'].sum() * 100) if district_data['Total_Vacancy'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Absence Fill Rate:</strong> {(district_data['Absence_Filled'].sum() / district_data['Total_Absence'].sum() * 100) if district_data['Total_Absence'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Number of Schools:</strong> {len(df[(df['District'] == district)]['Location'].unique())}</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>Individual School Reports</h3>
                    <div class="school-links">
                        <ul>
                            {school_links}
                        </ul>
                    </div>
                </div>
            </div>
            
            {get_professional_footer()}
        </div>
    </body>
    </html>
    """
    
    # Save main report
    report_file = os.path.join(district_dir, f'{int(district)}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file, school_reports

def create_borough_report(borough, borough_data, df, output_dir, summary_stats, date_range_info):
    """
    Create a comprehensive report for a single Borough including district summaries
    """
    # Create subfolder for Borough if it doesn't exist
    borough_clean = borough.replace(' ', '_').replace('/', '_')
    borough_dir = os.path.join(output_dir, f"Borough_{borough_clean}")
    os.makedirs(borough_dir, exist_ok=True)
    
    # Create summary table as HTML
    table_html = df_with_pretty_columns(borough_data[DISPLAY_COLS]).to_html(
        index=False,
        table_id='summary-table',
        classes='table table-striped',
        formatters={
            DISPLAY_COLS_RENAME.get(col, col): format_pct if 'Pct' in col else format_int
            for col in DISPLAY_COLS
        }
    )
    
    # Create grouped bar chart
    fig_bar = go.Figure()
    # Add bars for each category
    fig_bar.add_trace(go.Bar(
        name='Vacancy Filled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Vacancy_Filled'],
        marker_color='darkgreen',
        text=borough_data['Vacancy_Filled'],
        textposition='auto'
    ))

    fig_bar.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=borough_data['Vacancy_Unfilled'],
        textposition='auto'
    ))

    fig_bar.add_trace(go.Bar(
        name='Absence Filled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Absence_Filled'],
        marker_color='forestgreen',
        text=borough_data['Absence_Filled'],
        textposition='auto'
    ))

    fig_bar.add_trace(go.Bar(
        name='Absence Unfilled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Absence_Unfilled'],
        marker_color='red',
        text=borough_data['Absence_Unfilled'],
        textposition='auto'
    ))

    fig_bar.update_layout(
        title=f'Jobs by Classification and Type - {borough}',
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=500,
        width=1200
    )
    
    # Save bar chart
    bar_chart_file = os.path.join(borough_dir, f'{borough_clean}_bar_chart.html')
    
    # Generate HTML and write to file
    html_str = pio.to_html(fig_bar, include_plotlyjs='cdn', div_id=f"borough_{borough_clean}_bar_chart")
    with open(bar_chart_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    # Create pie charts for each classification
    pie_charts_html = ""
    for idx, (_, row) in enumerate(borough_data.iterrows()):
        if row['Total'] > 0:  # Only create pie chart if there are jobs
            pie_fig = go.Figure(data=[go.Pie(
                labels=['Vacancy Filled', 'Vacancy Unfilled', 'Absence Filled', 'Absence Unfilled'],
                values=[row['Vacancy_Filled'], row['Vacancy_Unfilled'], row['Absence_Filled'], row['Absence_Unfilled']],
                hole=0.3,
                marker_colors=['darkgreen', 'lightcoral', 'forestgreen', 'red'],
                textinfo='value+percent',
                textposition='inside',
                textfont=dict(size=14),
                texttemplate='%{value:,}<br>%{percent}'
            )])
            pie_fig.update_layout(
                title=dict(
                    text=f"{row['Classification']}<br>({int(row['Total']):,} total jobs)",
                    y=0.95,
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=16)
                ),
                height=450,
                width=400,
                showlegend=True,
                margin=dict(t=60, b=40, l=40, r=40)
            )
            
            pie_file = os.path.join(borough_dir, f'{borough_clean}_{row["Classification"].replace("/", "_")}_pie.html')
            pyo.plot(pie_fig, filename=pie_file, auto_open=False)
            
            pie_charts_html += f'<iframe src="{os.path.basename(pie_file)}" width="420" height="470" frameborder="0"></iframe>\n'
    
    # --- Summary by District Table ---
    df_borough = df[df['Borough'] == borough]
    summary_by_district = create_summary_stats(df_borough, ['District'])
    summary_by_district = summary_by_district.groupby('District', as_index=False).agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    })
    summary_by_district['Vacancy_Fill_Pct'] = np.where(
        summary_by_district['Total_Vacancy'] > 0,
        (summary_by_district['Vacancy_Filled'] / summary_by_district['Total_Vacancy'] * 100).round(1),
        0
    )
    summary_by_district['Absence_Fill_Pct'] = np.where(
        summary_by_district['Total_Absence'] > 0,
        (summary_by_district['Absence_Filled'] / summary_by_district['Total_Absence'] * 100).round(1),
        0
    )
    summary_by_district['Overall_Fill_Pct'] = np.where(
        summary_by_district['Total'] > 0,
        ((summary_by_district['Vacancy_Filled'] + summary_by_district['Absence_Filled']) / summary_by_district['Total'] * 100).round(1),
        0
    )
    district_display_cols = ['District', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct']
    summary_by_district = summary_by_district[[col for col in district_display_cols if col in summary_by_district.columns]]
    summary_by_district_html = df_with_pretty_columns(summary_by_district).to_html(
        index=False,
        classes='table',
        formatters={
            'District': lambda x: f"D{int(x)}" if pd.notna(x) else x,
            'Vacancy Filled': format_int,
            'Vacancy Unfilled': format_int,
            'Total Vacancy': format_int,
            'Vacancy Fill %': format_pct,
            'Absence Filled': format_int,
            'Absence Unfilled': format_int,
            'Total Absence': format_int,
            'Absence Fill %': format_pct,
            'Total': format_int,
            'Overall Fill %': format_pct
        }
    )
    # Get districts in this borough and create links
    borough_districts = sorted(df[df['Borough'] == borough]['District'].unique())
    district_links = ""
    for district in borough_districts:
        district_data_subset = summary_stats[summary_stats['District'] == district]
        if len(district_data_subset) > 0:
            total_jobs = district_data_subset['Total'].sum()
            district_links += f'<li><a href="../District_{int(district)}/{int(district)}_report.html">District {int(district)} Report</a> - {int(total_jobs)} total jobs</li>\n'
    # Calculate summary stats for comparison with citywide stats
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    })
    overall_stats = {
        'Total': int(overall_totals['Total']),
        'Total_Vacancy': int(overall_totals['Total_Vacancy']),
        'Total_Absence': int(overall_totals['Total_Absence']),
        'Vacancy_Filled': int(overall_totals['Vacancy_Filled']),
        'Absence_Filled': int(overall_totals['Absence_Filled'])
    }
    # Create grouped bar chart
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name='Vacancy Filled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Vacancy_Filled'],
        marker_color='darkgreen',
        text=borough_data['Vacancy_Filled'],
        textposition='auto'
    ))

    fig_bar.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=borough_data['Vacancy_Unfilled'],
        textposition='auto'
    ))

    fig_bar.add_trace(go.Bar(
        name='Absence Filled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Absence_Filled'],
        marker_color='forestgreen',
        text=borough_data['Absence_Filled'],
        textposition='auto'
    ))

    fig_bar.add_trace(go.Bar(
        name='Absence Unfilled',
        x=borough_data['Classification'].apply(clean_classification_for_display),
        y=borough_data['Absence_Unfilled'],
        marker_color='red',
        text=borough_data['Absence_Unfilled'],
        textposition='auto'
    ))

    fig_bar.update_layout(
        title=f'Jobs by Classification and Type - {borough}',
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=500,
        width=1200
    )
    
    # Save bar chart
    bar_chart_file = os.path.join(borough_dir, f'{borough_clean}_bar_chart.html')
    
    # Generate HTML and write to file (second instance)
    html_str = pio.to_html(fig_bar, include_plotlyjs='cdn', div_id=f"borough_{borough_clean}_bar_chart_2")
    with open(bar_chart_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    # Create pie charts for each classification
    pie_charts_html = ""
    for idx, (_, row) in enumerate(borough_data.iterrows()):
        if row['Total'] > 0:  # Only create pie chart if there are jobs
            pie_fig = go.Figure(data=[go.Pie(
                labels=['Vacancy Filled', 'Vacancy Unfilled', 'Absence Filled', 'Absence Unfilled'],
                values=[row['Vacancy_Filled'], row['Vacancy_Unfilled'], row['Absence_Filled'], row['Absence_Unfilled']],
                hole=0.3,
                marker_colors=['darkgreen', 'lightcoral', 'forestgreen', 'red'],
                textinfo='value+percent',
                textposition='inside',
                textfont=dict(size=14),
                texttemplate='%{value:,}<br>%{percent}'
            )])
            pie_fig.update_layout(
                title=dict(
                    text=f"{row['Classification']}<br>({int(row['Total']):,} total jobs)",
                    y=0.95,
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=16)
                ),
                height=450,
                width=400,
                showlegend=True,
                margin=dict(t=60, b=40, l=40, r=40)
            )
            
            pie_file = os.path.join(borough_dir, f'{borough_clean}_{row["Classification"].replace("/", "_")}_pie.html')
            pyo.plot(pie_fig, filename=pie_file, auto_open=False)
            
            pie_charts_html += f'<iframe src="{os.path.basename(pie_file)}" width="420" height="470" frameborder="0"></iframe>\n'
    
    # --- Summary by District Table ---
    df_borough = df[df['Borough'] == borough]
    summary_by_district = create_summary_stats(df_borough, ['District'])
    summary_by_district = summary_by_district.groupby('District', as_index=False).agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    })
    summary_by_district['Vacancy_Fill_Pct'] = np.where(
        summary_by_district['Total_Vacancy'] > 0,
        (summary_by_district['Vacancy_Filled'] / summary_by_district['Total_Vacancy'] * 100).round(1),
        0
    )
    summary_by_district['Absence_Fill_Pct'] = np.where(
        summary_by_district['Total_Absence'] > 0,
        (summary_by_district['Absence_Filled'] / summary_by_district['Total_Absence'] * 100).round(1),
        0
    )
    summary_by_district['Overall_Fill_Pct'] = np.where(
        summary_by_district['Total'] > 0,
        ((summary_by_district['Vacancy_Filled'] + summary_by_district['Absence_Filled']) / summary_by_district['Total'] * 100).round(1),
        0
    )
    district_display_cols = ['District', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct']
    summary_by_district = summary_by_district[[col for col in district_display_cols if col in summary_by_district.columns]]
    summary_by_district_html = df_with_pretty_columns(summary_by_district).to_html(
        index=False,
        classes='table',
        formatters={
            'District': lambda x: f"D{int(x)}" if pd.notna(x) else x,
            'Vacancy Filled': format_int,
            'Vacancy Unfilled': format_int,
            'Total Vacancy': format_int,
            'Vacancy Fill %': format_pct,
            'Absence Filled': format_int,
            'Absence Unfilled': format_int,
            'Total Absence': format_int,
            'Absence Fill %': format_pct,
            'Total': format_int,
            'Overall Fill %': format_pct
        }
    )
    # Calculate key insights for the borough
    total_jobs = int(borough_data['Total'].sum())
    total_vacancy = int(borough_data['Total_Vacancy'].sum())
    total_absence = int(borough_data['Total_Absence'].sum())
    vacancy_filled = int(borough_data['Vacancy_Filled'].sum())
    absence_filled = int(borough_data['Absence_Filled'].sum())
    overall_fill_pct = (vacancy_filled + absence_filled) / total_jobs * 100 if total_jobs > 0 else 0
    vacancy_fill_pct = (vacancy_filled / total_vacancy * 100) if total_vacancy > 0 else 0
    absence_fill_pct = (absence_filled / total_absence * 100) if total_absence > 0 else 0

    key_insights_html = f"""
        <div class=\"summary-box\" style=\"background-color:#f8f9fa;padding:15px;border-radius:5px;margin:10px 0;\">
            <h3>Key Insights</h3>
            <ul>
                <li><strong>Total Jobs:</strong> {total_jobs}</li>
                <li><strong>Total Vacancies:</strong> {total_vacancy} ({(total_vacancy/total_jobs*100) if total_jobs > 0 else 0:.1f}%)</li>
                <li><strong>Total Absences:</strong> {total_absence} ({(total_absence/total_jobs*100) if total_jobs > 0 else 0:.1f}%)</li>
                <li><strong>Overall Fill Rate:</strong> {overall_fill_pct:.1f}%</li>
                <li><strong>Vacancy Fill Rate:</strong> {vacancy_fill_pct:.1f}%</li>
                <li><strong>Absence Fill Rate:</strong> {absence_fill_pct:.1f}%</li>
            </ul>
        </div>
    """
    # Create comprehensive HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYCDOE Jobs Report - {borough}</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
        <style>
            :root {{
                --primary-color: #2E86AB;
                --secondary-color: #A23B72;
                --success-color: #2ca02c;
                --warning-color: #ff7f0e;
                --danger-color: #d62728;
                --light-bg: #f5f5f5;
                --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
                --hover-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }}

            .header {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white; 
                text-align: center; 
                padding: 40px 20px; 
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="80" r="2.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                opacity: 0.3;
            }}

            .header h1 {{
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }}

            .header h2 {{
                font-size: 1.5em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
                margin-bottom: 10px;
            }}

            .content {{
                padding: 30px;
            }}

            .section {{ 
                background: white;
                margin: 30px 0; 
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }}

            .section:hover {{
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }}

            .section h3 {{ 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.5em;
            }}

            .navigation {{ 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 20px; 
                border-radius: 15px; 
                margin: 20px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
            }}

            .navigation a {{
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                display: inline-block;
                margin: 5px;
            }}

            .navigation a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(46, 134, 171, 0.3);
            }}

            .table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 25px 0; 
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .table-responsive {{
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .table th, .table td {{ 
                padding: 15px 12px; 
                text-align: center; 
                border-bottom: 1px solid #e0e0e0;
            }}

            .table th {{ 
                background: var(--primary-color);
                color: white;
                font-weight: 600;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .table tbody tr {{
                transition: all 0.3s ease;
            }}

            .table tbody tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}

            .table tbody tr:hover {{
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .pie-container {{ 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin: 25px 0;
            }}

            .comparison-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}

            .comparison-card {{
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }}

            .comparison-card:hover {{
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }}

            .comparison-card.citywide {{
                background: linear-gradient(135deg, #e8f4f8, #d6eaf8);
            }}

            .comparison-card.borough {{
                background: linear-gradient(135deg, #f0f8e8, #e8f8d6);
            }}

            .comparison-card h4 {{
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }}

            .comparison-card ul {{
                list-style: none;
                padding: 0;
            }}

            .comparison-card li {{
                padding: 8px 0;
                border-bottom: 1px solid rgba(46, 134, 171, 0.1);
                font-size: 1.1em;
            }}

            .comparison-card li:last-child {{
                border-bottom: none;
            }}

            .district-links {{
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .district-links ul {{
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 30px;
            }}

            .district-links li {{
                padding: 8px 0;
                break-inside: avoid;
            }}

            .district-links a {{
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }}

            .district-links a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }}

            .chart-container {{ 
                margin: 25px 0; 
                text-align: center;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .footer {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                text-align: center;
                padding: 30px;
                margin-top: 40px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .footer a {{ 
                color: #FFD700; 
                text-decoration: none; 
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .footer a:hover {{ 
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                transform: scale(1.05);
            }}

            iframe {{
                border: none;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
            }}

            iframe:hover {{
                box-shadow: var(--hover-shadow);
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                }}

                .header {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                .content {{
                    padding: 15px;
                }}

                .section {{
                    padding: 20px;
                    margin: 15px 0;
                }}

                .comparison-grid {{
                    grid-template-columns: 1fr;
                }}

                .district-links ul {{
                    columns: 1;
                }}

                iframe {{
                    width: 100% !important;
                    height: 400px !important;
                }}
            }}
        </style>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {{
                $('.table').DataTable({{
                    paging: false, 
                    searching: false, 
                    info: false, 
                    order: [],
                    responsive: true
                }});
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NYCDOE Substitute Paraprofessional Jobs Report</h1>
                <h2>Borough: {borough}</h2>
                <p>{date_range_info}</p>
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>

            <div class="content">
                <div class="navigation">
                    <a href="../index.html">← Back to Overall Summary</a>
                </div>
                
                <div class="section">
                    <h3>Summary Statistics</h3>
                    <div class="table-responsive">
                        {table_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Summary by District</h3>
                    <div class="table-responsive">
                        {summary_by_district_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Jobs by Classification and Type</h3>
                    <div class="chart-container">
                        <iframe src="{borough_clean}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                    </div>
                </div>

                <div class="section">
                    <h3>Breakdown by Classification</h3>
                    <div class="pie-container">
                        {pie_charts_html}
                    </div>
                </div>

                <div class="section">
                    <h3>Comparison: {borough} vs. Citywide</h3>
                    <div class="comparison-grid">
                        <div class="comparison-card citywide">
                            <h4>Citywide Statistics</h4>
                            <ul>
                                <li><strong>Total Jobs:</strong> {overall_stats['Total']:,}</li>
                                <li><strong>Total Vacancies:</strong> {overall_stats['Total_Vacancy']:,} ({(overall_stats['Total_Vacancy'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)</li>
                                <li><strong>Total Absences:</strong> {overall_stats['Total_Absence']:,} ({(overall_stats['Total_Absence'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)</li>
                                <li><strong>Overall Fill Rate:</strong> {((overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']) / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%</li>
                                <li><strong>Vacancy Fill Rate:</strong> {(overall_stats['Vacancy_Filled'] / overall_stats['Total_Vacancy'] * 100) if overall_stats['Total_Vacancy'] > 0 else 0:.1f}%</li>
                                <li><strong>Absence Fill Rate:</strong> {(overall_stats['Absence_Filled'] / overall_stats['Total_Absence'] * 100) if overall_stats['Total_Absence'] > 0 else 0:.1f}%</li>
                                <li><strong>Number of Schools:</strong> {len(df['Location'].unique())}</li>
                            </ul>
                        </div>
                        <div class="comparison-card borough">
                            <h4>This Borough</h4>
                            <ul>
                                <li><strong>Total Jobs:</strong> {int(borough_data['Total'].sum()):,}</li>
                                <li><strong>Total Vacancies:</strong> {int(borough_data['Total_Vacancy'].sum()):,} ({(borough_data['Total_Vacancy'].sum() / borough_data['Total'].sum() * 100) if borough_data['Total'].sum() > 0 else 0:.1f}%)</li>
                                <li><strong>Total Absences:</strong> {int(borough_data['Total_Absence'].sum()):,} ({(borough_data['Total_Absence'].sum() / borough_data['Total'].sum() * 100) if borough_data['Total'].sum() > 0 else 0:.1f}%)</li>
                                <li><strong>Overall Fill Rate:</strong> {((borough_data['Vacancy_Filled'].sum() + borough_data['Absence_Filled'].sum()) / borough_data['Total'].sum() * 100) if borough_data['Total'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Vacancy Fill Rate:</strong> {(borough_data['Vacancy_Filled'].sum() / borough_data['Total_Vacancy'].sum() * 100) if borough_data['Total_Vacancy'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Absence Fill Rate:</strong> {(borough_data['Absence_Filled'].sum() / borough_data['Total_Absence'].sum() * 100) if borough_data['Total_Absence'].sum() > 0 else 0:.1f}%</li>
                                <li><strong>Number of Schools:</strong> {len(df[df['Borough'] == borough]['Location'].unique())}</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>Individual District Reports</h3>
                    <div class="district-links">
                        <ul>
                            {district_links}
                        </ul>
                    </div>
                </div>
            </div>
            
            {get_professional_footer()}
        </div>
    </body>
    </html>
    """
    
    # Save main report
    report_file = os.path.join(borough_dir, f'{borough_clean}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file


def create_overall_summary(df, summary_stats, borough_stats, output_dir, date_range_info):
    """
    Create an overall summary report across all districts
    """
    # Overall statistics by classification
    overall_stats = summary_stats.groupby('Classification').agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    }).reset_index()
    
    # Recalculate percentages
    overall_stats['Vacancy_Fill_Pct'] = np.where(
        overall_stats['Total_Vacancy'] > 0,
        (overall_stats['Vacancy_Filled'] / overall_stats['Total_Vacancy'] * 100).round(1),
        0
    )
    overall_stats['Absence_Fill_Pct'] = np.where(
        overall_stats['Total_Absence'] > 0,
        (overall_stats['Absence_Filled'] / overall_stats['Total_Absence'] * 100).round(1),
        0
    )
    overall_stats['Overall_Fill_Pct'] = np.where(
        overall_stats['Total'] > 0,
        ((overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']) / overall_stats['Total'] * 100).round(1),
        0
    )
    
    print(overall_stats['Classification'].unique())

    # Create overall bar chart
    fig_overall = go.Figure()

    # Filter out PARAPROFESSIONAL from the dataset
    filtered_stats = overall_stats[overall_stats['Classification'] != 'PARAPROFESSIONAL']

    fig_overall.add_trace(go.Bar(
        name='Vacancy Filled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Vacancy_Filled'],
        marker_color='darkgreen',
        text=[f"{val:,}" for val in filtered_stats['Vacancy_Filled']],
        textposition='auto'
    ))

    fig_overall.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=[f"{val:,}" for val in filtered_stats['Vacancy_Unfilled']],
        textposition='auto'
    ))

    fig_overall.add_trace(go.Bar(
        name='Absence Filled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Absence_Filled'],
        marker_color='forestgreen',
        text=[f"{val:,}" for val in filtered_stats['Absence_Filled']],
        textposition='auto'
    ))

    fig_overall.add_trace(go.Bar(
        name='Absence Unfilled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Absence_Unfilled'],
        marker_color='red',
        text=[f"{val:,}" for val in filtered_stats['Absence_Unfilled']],
        textposition='auto'
    ))

    fig_overall.update_layout(
        title='Overall Jobs by Classification and Type - All Districts',
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=500,
        width=1400
    )
    
    overall_chart_file = os.path.join(output_dir, 'overall_bar_chart.html')
    
    # Generate HTML and write to file
    html_str = pio.to_html(fig_overall, include_plotlyjs='cdn', div_id="overall_bar_chart")
    with open(overall_chart_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    # Create District summary table
    district_summary = summary_stats.groupby('District').agg({
        'Vacancy_Filled': 'sum',
        'Vacancy_Unfilled': 'sum',
        'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum',
        'Total_Vacancy': 'sum',
        'Total_Absence': 'sum',
        'Total': 'sum'
    }).reset_index()
    
    # Recalculate percentages for district summary
    district_summary['Vacancy_Fill_Pct'] = np.where(
        district_summary['Total_Vacancy'] > 0,
        (district_summary['Vacancy_Filled'] / district_summary['Total_Vacancy'] * 100).round(1),
        0
    )
    district_summary['Absence_Fill_Pct'] = np.where(
        district_summary['Total_Absence'] > 0,
        (district_summary['Absence_Filled'] / district_summary['Total_Absence'] * 100).round(1),
        0
    )
    district_summary['Overall_Fill_Pct'] = np.where(
        district_summary['Total'] > 0,
        ((district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']) / district_summary['Total'] * 100).round(1),
        0
    )
    district_summary = district_summary.sort_values('Total', ascending=False)
    
    # Generate links to individual District reports
    district_links = ""
    for _, row in district_summary.sort_values('District').iterrows():
        district_num = row['District']
        district_links += f'<li><a href="District_{int(district_num)}/{int(district_num)}_report.html">District {int(district_num)} Report</a> - {int(row["Total"])} total jobs</li>\n'

    borough_links = ""
    for borough in sorted(df['Borough'].unique()):
        if borough != 'Unknown':
            borough_data = borough_stats[borough_stats['Borough'] == borough]
            if len(borough_data) > 0:
                total_jobs = borough_data['Total'].sum()
                borough_name_clean = borough.replace(' ', '_').replace('/', '_')
                borough_links += f'<li><a href="Borough_{borough_name_clean}/{borough_name_clean}_report.html">{borough} Report</a> - {int(total_jobs)} total jobs</li>\n'
    
    
    # Calculate overall statistics
    total_jobs = len(df)
    total_filled = len(df[df['Fill_Status'] == 'Filled'])
    total_vacancies = len(df[df['Type'] == 'Vacancy'])
    total_absences = len(df[df['Type'] == 'Absence'])
    
    # Create main index HTML
    display_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                   'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct']
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYCDOE Jobs Dashboard - Overall Summary</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
        <style>
            :root {{
                --primary-color: #2E86AB;
                --secondary-color: #A23B72;
                --success-color: #2ca02c;
                --warning-color: #ff7f0e;
                --danger-color: #d62728;
                --light-bg: #f5f5f5;
                --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
                --hover-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }}

            .header {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white; 
                text-align: center; 
                padding: 40px 20px; 
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="80" r="2.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                opacity: 0.3;
            }}

            .header h1 {{
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }}

            .header h2 {{
                font-size: 1.5em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
                margin-bottom: 10px;
            }}

            .content {{
                padding: 30px;
            }}

            .section {{ 
                background: white;
                margin: 30px 0; 
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }}

            .section:hover {{
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }}

            .section h3 {{ 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.5em;
            }}

            .summary-box {{ 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 25px; 
                border-radius: 15px; 
                margin: 25px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
            }}

            .summary-box h3 {{
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.4em;
            }}

            .summary-box ul {{
                list-style: none;
                padding: 0;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }}

            .summary-box li {{
                padding: 15px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.7);
                font-size: 1.1em;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}

            .summary-box li:hover {{
                transform: translateY(-2px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.15);
            }}

            .summary-box strong {{
                color: var(--primary-color);
                display: block;
                font-size: 0.9em;
                margin-bottom: 5px;
            }}

            .table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 25px 0; 
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .table-responsive {{
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .table th, .table td {{ 
                padding: 15px 12px; 
                text-align: center; 
                border-bottom: 1px solid #e0e0e0;
            }}

            .table th {{ 
                background: var(--primary-color);
                color: white;
                font-weight: 600;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .table tbody tr {{
                transition: all 0.3s ease;
            }}

            .table tbody tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}

            .table tbody tr:hover {{
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .links-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}

            .links-section {{
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .links-section h4 {{
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }}

            .links-section ul {{
                list-style: none;
                padding: 0;
            }}

            .links-section li {{
                padding: 8px 0;
                break-inside: avoid;
            }}

            .links-section a {{
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }}

            .links-section a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }}

            .chart-container {{ 
                margin: 25px 0; 
                text-align: center;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }}

            .footer {{ 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                text-align: center;
                padding: 30px;
                margin-top: 40px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            .footer a {{ 
                color: #FFD700; 
                text-decoration: none; 
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .footer a:hover {{ 
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                transform: scale(1.05);
            }}

            iframe {{
                border: none;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
            }}

            iframe:hover {{
                box-shadow: var(--hover-shadow);
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                }}

                .header {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                .content {{
                    padding: 15px;
                }}

                .section {{
                    padding: 20px;
                    margin: 15px 0;
                }}

                .summary-box ul {{
                    grid-template-columns: 1fr;
                }}

                .links-grid {{
                    grid-template-columns: 1fr;
                }}

                iframe {{
                    width: 100% !important;
                    height: 400px !important;
                }}
            }}
        </style>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {{
                $('.table').DataTable({{
                    paging: false, 
                    searching: false, 
                    info: false, 
                    order: [],
                    responsive: true
                }});
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NYCDOE Substitute Paraprofessional Jobs Dashboard</h1>
                <h2>Citywide Summary Report</h2>
                <p>{date_range_info}</p>
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>

            <div class="content">
                <div class="section">
                    <div class="summary-box">
                        <h3>Key Statistics</h3>
                        <ul>
                            <li><strong>Total Jobs</strong>{total_jobs:,}</li>
                            <li><strong>Total Vacancies</strong>{total_vacancies:,} ({(total_vacancies/total_jobs*100):.1f}%)</li>
                            <li><strong>Total Absences</strong>{total_absences:,} ({(total_absences/total_jobs*100):.1f}%)</li>
                            <li><strong>Total Filled</strong>{total_filled:,} ({(total_filled/total_jobs*100):.1f}%)</li>
                            <li><strong>Total Districts</strong>{len(df['District'].unique())}</li>
                            <li><strong>Total Schools</strong>{len(df['Location'].unique())}</li>
                            <li><strong>Total Classifications</strong>{len(df['Classification'].unique())}</li>
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h3>Overall Jobs by Classification and Type</h3>
                    <div class="chart-container">
                        <iframe src="overall_bar_chart.html" width="1420" height="520" frameborder="0"></iframe>
                    </div>
                </div>
                
                <div class="section">
                    <h3>Summary by Classification (All Districts)</h3>
                    <div class="table-responsive">
                        {df_with_pretty_columns(overall_stats[display_cols]).to_html(
        index=False,
        classes='table',
        formatters={
            DISPLAY_COLS_RENAME.get(col, col): format_pct if 'Pct' in col else format_int
            for col in display_cols
        }
    )}
                    </div>
                </div>
                
                <div class="section">
                    <h3>Summary by District</h3>
                    <div class="table-responsive">
                        {district_summary[['District'] + display_cols[1:]].sort_values('District').rename(columns=DISPLAY_COLS_RENAME).to_html(
        index=False,
        classes='table',
        formatters={
            'District': lambda x: f"D{int(x)}" if pd.notna(x) else x,
            **{
                DISPLAY_COLS_RENAME.get(col, col): format_pct if 'Pct' in col else format_int
                for col in display_cols
            }
        }
    )}
                    </div>
                </div>

                <div class="section">
                    <h3>Detailed Reports</h3>
                    <div class="links-grid">
                        <div class="links-section">
                            <h4>Borough Reports</h4>
                            <ul>
                                {borough_links}
                            </ul>
                        </div>
                        <div class="links-section">
                            <h4>District Reports</h4>
                            <ul>
                                {district_links}
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <p style="text-align: center; font-style: italic; color: #666; font-size: 1.1em;">
                        Generated from data containing {len(df):,} job records
                    </p>
                </div>
            </div>
            
            {get_professional_footer()}
        </div>
    </body>
    </html>
    """
    
    index_file = os.path.join(output_dir, 'index.html')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return index_file

def get_professional_footer():
    """Return the professional footer HTML"""
    return f"""
    <div class="footer">
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">Created by HR School Support</div>
        <div style="margin-bottom:6px;">For internal use only.</div>
        <div style="margin-bottom:6px;">For inquiries, please contact <a href="mailto:SubCentral@schools.nyc.gov">SubCentral@schools.nyc.gov</a>.</div>
        <div style="font-size:13px; color:#e0e0e0;">&copy; {pd.Timestamp.now().year} Property of the NYCDOE</div>
    </div>
    """

def df_with_pretty_columns(df):
    """
    Return a copy of df with columns renamed for display.
    """
    return df.rename(columns=DISPLAY_COLS_RENAME)

def main():
    """
    Main function to generate static reports
    """
    # Replace with your CSV file path
    csv_file_path = 'Fill Rate Data/mayjobs.csv'
    output_directory = 'nycdoe_reports'
    
   

    
    
    start_time = time.time()
    print("Starting report generation...")
    try:
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Load and process data
        print("Loading and processing data...")
        df = load_and_process_data(csv_file_path)
        
        # Get date range information
        date_range_info = get_data_date_range(df)
        print(f"Data range: {date_range_info}")
        
        summary_stats = create_summary_stats(df, ['District'])
        # Remove 'Type_Fill_Status' if present
        if 'Type_Fill_Status' in summary_stats.columns:
            summary_stats = summary_stats.drop(columns=['Type_Fill_Status'])

        # Convert to int to avoid float display issues
        int_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled', 
                   'Total_Vacancy', 'Total_Absence', 'Total']
        for col in int_cols:
            summary_stats[col] = summary_stats[col].astype(int)

        #Create borough-level statistics
        print("Creating borough-level statistics...")
        borough_stats = create_borough_summary_stats(df)
        if 'Type_Fill_Status' in borough_stats.columns:
            borough_stats = borough_stats.drop(columns=['Type_Fill_Status'])
        # Create reports for each District
        districts = sorted(df['District'].unique())
        print(f"Creating reports for {len(districts)} districts...")
        report_files = []
        all_school_reports = []
        
        for district in districts:
            district_data = summary_stats[summary_stats['District'] == district].copy()
            if len(district_data) > 0:
                report_file, school_reports = create_district_report(district, district_data, df, output_directory, summary_stats, date_range_info)
                report_files.append(report_file)
                all_school_reports.extend(school_reports)
                print(f"District {int(district)} report finished.")
        
        #Create reports for each borough
        boroughs = sorted(df['Borough'].unique())
        print(f"Creating reports for {len(boroughs)} boroughs...")
        borough_report_files = []

        for borough in boroughs:
            if borough != 'Unknown': # Skip if no valid borough found
                borough_data = borough_stats[borough_stats['Borough'] == borough].copy()
                if len(borough_data) > 0:
                    borough_report = create_borough_report(borough, borough_data, df, output_directory, summary_stats, date_range_info)
                    borough_report_files.append(borough_report)
                    print(f"Borough {borough} report finished.")
        
        # Create overall summary
        index_file = create_overall_summary(df, summary_stats, borough_stats, output_directory, date_range_info)
        
        print(f"Reports generated successfully!")
        print(f"Main report: {index_file}")
        print(f"Individual District reports: {len(report_files)} files created")
        print(f"Individual School reports: {len(all_school_reports)} files created")
        print(f"Open '{index_file}' in your web browser to view the dashboard")
        
        elapsed = time.time() - start_time
        print(f"Total run time: {elapsed:.2f} seconds")
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_file_path}'")
        print("Please make sure the file exists and update the csv_file_path variable.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()