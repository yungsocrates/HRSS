"""
District Choropleth Mapping for NYC DOE Paraprofessional Jobs Dashboard

This module creates interactive choropleth maps showing district-level fill rates
using NYC School District geographic boundaries.
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot

def load_district_geojson():
    """Load the NYC School Districts GeoJSON file"""
    try:
        with open('NYC_School_Districts_-2063935521060471505.geojson', 'r') as f:
            geojson_data = json.load(f)
        return geojson_data
    except FileNotFoundError:
        print("Warning: NYC School Districts GeoJSON file not found")
        return None
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return None

def prepare_district_data(district_summary):
    """
    Prepare district summary data for choropleth mapping
    
    Args:
        district_summary: DataFrame with district-level statistics
        
    Returns:
        DataFrame: Prepared data with district IDs and fill rates
    """
    # Create a copy to avoid modifying original data
    map_data = district_summary.copy()
    
    # Ensure District column is integer for matching with GeoJSON
    map_data['District'] = map_data['District'].astype(int)
    
    # Create a text column for hover information
    map_data['hover_text'] = map_data.apply(lambda row: 
        f"District {int(row['District'])}<br>" +
        f"Overall Fill Rate: {row['Overall_Fill_Pct']:.1f}%<br>" +
        f"Total Jobs: {int(row['Total']):,}<br>" +
        f"Filled: {int(row['Total_Filled']):,}<br>" +
        f"Unfilled: {int(row['Total_Unfilled']):,}<br>" +
        f"Vacancy Fill Rate: {row['Vacancy_Fill_Pct']:.1f}%<br>" +
        f"Absence Fill Rate: {row['Absence_Fill_Pct']:.1f}%",
        axis=1
    )
    
    return map_data

def create_district_choropleth(district_summary, output_file):
    """
    Create an interactive choropleth map of district fill rates
    
    Args:
        district_summary: DataFrame with district-level statistics
        output_file: Path to save the HTML map file
        
    Returns:
        str: HTML content of the map, or None if creation failed
    """
    # Load GeoJSON data
    geojson_data = load_district_geojson()
    if geojson_data is None:
        return None
    
    # Prepare data for mapping - no filtering, let the map show what it can
    map_data = prepare_district_data(district_summary)
    
    # Create the choropleth map with mapbox background
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson_data,
        locations=map_data['District'],
        z=map_data['Overall_Fill_Pct'],
        colorscale=[[0, 'red'], [0.5, 'yellow'], [1, 'green']],  # Red at 60%, Green at 100%
        zmin=60,  # Set minimum color scale to 60%
        zmax=100, # Set maximum color scale to 100%
        marker_line_width=1,
        marker_line_color='black',
        featureidkey="properties.SchoolDist",
        colorbar_title="Fill Rate (%)",
        text=map_data['hover_text'],  # Use the detailed hover text
        hoverinfo="text"
    ))
    
    # Update layout with Carto Positron background
    fig.update_layout(
        title={
            'text': 'NYC School Districts - Overall Fill Rate by District',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial, sans-serif'}
        },
        mapbox=dict(
            style='carto-positron',
            center=dict(lat=40.7128, lon=-73.9060),  # NYC center
            zoom=9.5
        ),
        width=1300,
        height=800,
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Save the map
    try:
        html_content = plot(fig, output_type='div', include_plotlyjs=True)
        
        # Create a complete HTML file
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYC Districts Fill Rate Map</title>
            <meta charset="utf-8">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    background-color: #f8f9fa;
                }}
                .map-container {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin: 0 auto;
                    max-width: 1440px;
                }}
                .map-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="map-container">
                <div class="map-info">
                    <p>Interactive map showing overall fill rates by NYC school district. 
                    Hover over districts to see detailed statistics.</p>
                </div>
                {html_content}
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"District choropleth map saved to: {output_file}")
        return html_content
        
    except Exception as e:
        print(f"Error creating choropleth map: {e}")
        return None

def create_district_map_summary_stats(district_summary):
    """
    Create summary statistics for the district map
    
    Args:
        district_summary: DataFrame with district-level statistics
        
    Returns:
        dict: Summary statistics for display
    """
    stats = {
        'total_districts': len(district_summary),
        'avg_fill_rate': district_summary['Overall_Fill_Pct'].mean(),
        'highest_fill_rate': district_summary['Overall_Fill_Pct'].max(),
        'lowest_fill_rate': district_summary['Overall_Fill_Pct'].min(),
        'best_district': district_summary.loc[district_summary['Overall_Fill_Pct'].idxmax(), 'District'],
        'worst_district': district_summary.loc[district_summary['Overall_Fill_Pct'].idxmin(), 'District'],
        'total_jobs': district_summary['Total'].sum(),
        'total_filled': district_summary['Total_Filled'].sum(),
        'districts_above_90': len(district_summary[district_summary['Overall_Fill_Pct'] >= 90]),
        'districts_below_70': len(district_summary[district_summary['Overall_Fill_Pct'] < 70])
    }
    
    return stats

def get_district_map_section_html(district_summary, map_file_path):
    """
    Generate HTML section content for the district map
    
    Args:
        district_summary: DataFrame with district-level statistics
        map_file_path: Relative path to the map HTML file
        
    Returns:
        str: HTML content for the district map section
    """
    # Get summary statistics
    stats = create_district_map_summary_stats(district_summary)
    
    # Create the HTML section
    html_content = f"""
    <div class="section">
        <h3>Geographic Distribution - District Fill Rates</h3>
        
        <div class="map-summary">
            <div class="summary-stats-grid">
                <div class="stat-card">
                    <h4>Average Fill Rate</h4>
                    <div class="stat-value">{stats['avg_fill_rate']:.1f}%</div>
                </div>
                <div class="stat-card">
                    <h4>Highest Fill Rate District</h4>
                    <div class="stat-value">D{int(stats['best_district'])} ({stats['highest_fill_rate']:.1f}%)</div>
                </div>
                <div class="stat-card">
                    <h4>Districts ≥90%</h4>
                    <div class="stat-value">{stats['districts_above_90']} of {stats['total_districts']}</div>
                </div>
                <div class="stat-card">
                    <h4>Districts <70%</h4>
                    <div class="stat-value">{stats['districts_below_70']} of {stats['total_districts']}</div>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <iframe src="{map_file_path}" width="1400" height="950" frameborder="0"></iframe>
        </div>
        
        <div class="map-notes">
            <p style="font-style: italic; color: #666; text-align: center; margin-top: 15px;">
                Districts are colored by overall fill rate: 
                <span style="color: #d62728;">Red (low)</span> → 
                <span style="color: #ff7f0e;">Orange</span> → 
                <span style="color: #ffff99;">Yellow</span> → 
                <span style="color: #98df8a;">Light Green</span> → 
                <span style="color: #2ca02c;">Green (high)</span>
            </p>
        </div>
    </div>
    """
    
    return html_content
