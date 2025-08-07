"""
Chart generation utilities for NYC DOE Reports
"""

import plotly.graph_objects as go
import plotly.io as pio
import plotly.offline as pyo
import os
import re

def clean_classification_for_display(classification):
    """
    Clean classification names for display in bar charts
    """
    return classification.replace(' SPEAKING PARA', '')

def create_bar_chart(data, title, output_file, div_id=None):
    """
    Create a grouped bar chart for job data
    
    Args:
        data: DataFrame with job data
        title: Chart title
        output_file: Path to save the chart HTML
        div_id: HTML div ID for the chart
    """
    fig = go.Figure()
    
    # Add bars for each category
    fig.add_trace(go.Bar(
        name='Vacancy Filled',
        x=data['Classification'].apply(clean_classification_for_display),
        y=data['Vacancy_Filled'],
        marker_color='darkgreen',
        text=[f"{int(val):,}" for val in data['Vacancy_Filled']],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=data['Classification'].apply(clean_classification_for_display),
        y=data['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=[f"{int(val):,}" for val in data['Vacancy_Unfilled']],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Absence Filled',
        x=data['Classification'].apply(clean_classification_for_display),
        y=data['Absence_Filled'],
        marker_color='forestgreen',
        text=[f"{int(val):,}" for val in data['Absence_Filled']],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Absence Unfilled',
        x=data['Classification'].apply(clean_classification_for_display),
        y=data['Absence_Unfilled'],
        marker_color='red',
        text=[f"{int(val):,}" for val in data['Absence_Unfilled']],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=500,
        width=1200
    )
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Generate HTML and write to file
    html_str = pio.to_html(fig, include_plotlyjs=True, div_id=div_id)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    return output_file

def sanitize_filename(name):
    """
    Enhanced filename sanitization for Windows compatibility
    """
    if not name:
        return "unknown"
    
    # Convert to string and remove/replace problematic characters
    # Windows invalid: < > : " | ? * \ / and control chars
    sanitized = re.sub(r'[<>:"|?*\\/\x00-\x1f\x7f-\x9f]', '_', str(name))
    
    # Replace multiple underscores/spaces with single underscore
    sanitized = re.sub(r'[_\s]+', '_', sanitized)
    
    # Remove leading/trailing underscores, periods, and spaces
    sanitized = sanitized.strip('_. ')
    
    # Handle Windows reserved names
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
    
    if sanitized.upper() in reserved:
        sanitized = f"file_{sanitized}"
    
    # Ensure it's not empty and not too long
    if not sanitized:
        sanitized = "unknown"
    if len(sanitized) > 50:
        sanitized = sanitized[:50].rstrip('_.')
    
    return sanitized

def create_pie_chart(classification, data_row, location_clean, output_dir):
    """
    Create a pie chart for a specific classification
    
    Args:
        classification: Classification name
        data_row: Pandas Series with job data for this classification
        location_clean: Clean location name for file naming
        output_dir: Directory to save the chart
    
    Returns:
        Tuple of (pie_file_path, iframe_html)
    """
    if data_row['Total'] <= 0:
        return None, ""
    
    # Use enhanced sanitization with additional safety
    safe_location = sanitize_filename(location_clean)
    safe_classification = sanitize_filename(classification)
    
    # Create progressively simpler filenames until one works
    filename_attempts = [
        f'{safe_location}_{safe_classification}_pie.html',
        f'{safe_location[:20]}_pie.html',
        f'school_{abs(hash(location_clean)) % 10000}_pie.html',
        f'chart_{abs(hash(str(data_row))) % 10000}.html'
    ]
    
    pie_file = None
    for attempt in filename_attempts:
        try:
            test_path = os.path.join(output_dir, attempt)
            # Test if we can create this file
            os.makedirs(output_dir, exist_ok=True)
            with open(test_path, 'w') as test_f:
                test_f.write('test')
            os.remove(test_path)
            pie_file = test_path
            break
        except Exception:
            continue
    
    if pie_file is None:
        print(f"Warning: Could not create valid filename for {location_clean} {classification}")
        return None, ""
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=['Vacancy Filled', 'Vacancy Unfilled', 'Absence Filled', 'Absence Unfilled'],
        values=[data_row['Vacancy_Filled'], data_row['Vacancy_Unfilled'], 
                data_row['Absence_Filled'], data_row['Absence_Unfilled']],
        hole=0.3,
        marker_colors=['darkgreen', 'lightcoral', 'forestgreen', 'red'],
        textinfo='value+percent',
        textposition='inside',
        textfont=dict(size=14),
        texttemplate='%{value:,}<br>%{percent}'
    )])
    
    pie_fig.update_layout(
        title=dict(
            text=f"{classification}<br>({int(data_row['Total']):,} total jobs)",
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
    
    try:
        pyo.plot(pie_fig, filename=pie_file, auto_open=False)
        base_filename = os.path.basename(pie_file)
        iframe_html = f'<iframe src="{base_filename}" width="450" height="500" frameborder="0"></iframe>'
        return pie_file, iframe_html
    except Exception as e:
        print(f"Error creating pie chart file '{pie_file}': {e}")
        return None, ""
        fallback_name = f"chart_{abs(hash(f'{location_clean}_{classification}')) % 100000}.html"
def create_pie_charts_for_data(data, location_clean, output_dir):
    """
    Create pie charts for all classifications in the data
    
    Args:
        data: DataFrame with job data
        location_clean: Clean location name for file naming
        output_dir: Directory to save the charts
    
    Returns:
        HTML string containing all pie chart iframes
    """
    pie_charts_html = ""
    
    for idx, (_, row) in enumerate(data.iterrows()):
        if row['Total'] > 0:  # Only create pie chart if there are jobs
            pie_file, iframe_html = create_pie_chart(
                row['Classification'], row, location_clean, output_dir
            )
            if iframe_html:
                pie_charts_html += iframe_html
    
    return pie_charts_html

def create_overall_bar_chart(overall_stats, output_file):
    """
    Create the overall citywide bar chart
    
    Args:
        overall_stats: DataFrame with overall statistics
        output_file: Path to save the chart HTML
    """
    # Filter out PARAPROFESSIONAL from the dataset
    filtered_stats = overall_stats[overall_stats['Classification'] != 'PARAPROFESSIONAL']
    
    fig_overall = go.Figure()
    
    fig_overall.add_trace(go.Bar(
        name='Vacancy Filled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Vacancy_Filled'],
        marker_color='darkgreen',
        text=[f"{int(val):,}" for val in filtered_stats['Vacancy_Filled']],
        textposition='auto'
    ))

    fig_overall.add_trace(go.Bar(
        name='Vacancy Unfilled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Vacancy_Unfilled'],
        marker_color='lightcoral',
        text=[f"{int(val):,}" for val in filtered_stats['Vacancy_Unfilled']],
        textposition='auto'
    ))

    fig_overall.add_trace(go.Bar(
        name='Absence Filled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Absence_Filled'],
        marker_color='forestgreen',
        text=[f"{int(val):,}" for val in filtered_stats['Absence_Filled']],
        textposition='auto'
    ))

    fig_overall.add_trace(go.Bar(
        name='Absence Unfilled',
        x=[clean_classification_for_display(x) for x in filtered_stats['Classification']],
        y=filtered_stats['Absence_Unfilled'],
        marker_color='red',
        text=[f"{int(val):,}" for val in filtered_stats['Absence_Unfilled']],
        textposition='auto'
    ))

    fig_overall.update_layout(
        title='Overall Jobs by Classification and Type - All Districts',
        xaxis_title='Classification',
        yaxis_title='Number of Jobs',
        barmode='group',
        height=550,
        width=1400
    )
    
    # Generate HTML and write to file
    html_str = pio.to_html(fig_overall, include_plotlyjs=True, div_id="overall_bar_chart")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    return output_file
