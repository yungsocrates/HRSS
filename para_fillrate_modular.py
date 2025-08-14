"""
NYC DOE Paraprofessional Jobs Dashboard - Main Script (Modularized)

This is the main entry point for generating the NYC DOE reports dashboard.
The heavy lifting is now done by imported modules for better maintainability.
"""

import os
import time
import pandas as pd
import numpy as np
import re

# Import our custom modules
from data_processing import (
    load_and_process_data, get_data_date_range, create_summary_stats, 
    copy_logo_to_output, df_with_pretty_columns,
    DISPLAY_COLS, format_pct, format_int, create_matching_analysis
)
from report_generators import create_district_report
from chart_utils import create_overall_bar_chart
from templates import get_html_template, get_header_html, get_professional_footer, create_classification_tabbed_tables, create_school_tabbed_tables, create_district_tabbed_tables, create_borough_tabbed_tables, create_simple_table_with_tabbed_styling, create_conditional_formatted_table

def create_borough_report(borough, borough_data, df, output_dir, district_stats, date_range_info, matching_stats=None):
    """
    Create a comprehensive report for a single borough with restructured sections per feedback:
    1. Overall Summary (Borough vs Citywide) with Average Match %
    2. Match Payroll Analysis (sorted lowest to highest Match %)
    3. Classification Information (sorted highest to lowest total jobs)
    4. Individual Schools (with helpful notes)
    """
    import pandas as pd
    from chart_utils import create_bar_chart, create_pie_charts_for_data
    from data_processing import get_totals_from_data, calculate_fill_rates
    from templates import get_comparison_card_html, get_navigation_html
    
    # Create subfolder for borough
    borough_clean = borough.replace(' ', '_').replace('/', '_')
    borough_dir = os.path.join(output_dir, f"Borough_{borough_clean}")
    os.makedirs(borough_dir, exist_ok=True)
    
    # Get borough data
    df_borough = df[df['Borough'] == borough]
    
    # === SECTION 1: OVERALL SUMMARY (Borough vs Citywide) ===
    # Get comparison data
    overall_totals = district_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    borough_totals = get_totals_from_data(borough_data)
    
    # Calculate fill rates
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    
    # Filter matching analysis data for this borough and calculate average match percentage
    citywide_avg_match = 0
    borough_avg_match = 0
    borough_matching = pd.DataFrame()
    
    if matching_stats is not None and not matching_stats.empty:
        # Get borough schools from the district-level matching data
        borough_schools = df[df['Borough'] == borough]['Location'].unique()
        borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools)].copy()
        
        # Calculate average match percentages
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Citywide average
            citywide_avg_match = matching_stats[match_col].mean()
            
            # Borough average
            if not borough_matching.empty:
                borough_avg_match = borough_matching[match_col].mean()
    
    # Create comparison cards with match percentage
    comparison_cards = []
    
    # Citywide card with match percentage
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%",
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_avg_match:.1f}%" if citywide_avg_match > 0 else "N/A",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card with match percentage  
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_avg_match:.1f}%" if borough_avg_match > 0 else "N/A",
        "Number of Schools": f"{len(df[df['Borough'] == borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"This Borough", borough_stats, "borough"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # === SECTION 2: MATCH PAYROLL ANALYSIS (for districts in this borough) ===
    payroll_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty and not borough_matching.empty:
        # Find the match percentage column
        match_col = None
        for col in borough_matching.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Add district information to borough matching data
            district_info = df[['Location', 'District']].drop_duplicates()
            borough_matching_with_district = borough_matching.merge(district_info, on='Location', how='left')
            
            # Aggregate by district to show district-level analysis
            district_analysis = borough_matching_with_district.groupby('District').agg({
                'SubCentral Job Days' if 'SubCentral Job Days' in borough_matching.columns else 'SubCentral_Count': 'sum',
                'Payroll Job Days' if 'Payroll Job Days' in borough_matching.columns else 'Payroll_Count': 'sum'
            }).reset_index()
            
            # Find matched column and add it
            matched_col = None
            for col in borough_matching.columns:
                if 'Matched' in col and 'Job' in col:
                    matched_col = col
                    break
            
            if matched_col:
                district_matched = borough_matching_with_district.groupby('District')[matched_col].sum().reset_index()
                district_analysis = district_analysis.merge(district_matched, on='District', how='left')
                
                # Calculate district-level match percentages
                subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in borough_matching.columns else 'SubCentral_Count'
                district_analysis['Match_Percentage'] = (
                    district_analysis[matched_col] / district_analysis[subcentral_col] * 100
                ).round(1)
                
                # Sort by Match Percentage (lowest to highest per feedback)
                district_analysis = district_analysis.sort_values('Match_Percentage', ascending=True)
                
                # Rename column for display (remove underscore)
                district_analysis_display = district_analysis.rename(columns={'Match_Percentage': 'Match Percentage'})
                
                # Calculate totals
                total_subcentral = district_analysis[subcentral_col].sum()
                total_payroll = district_analysis['Payroll Job Days' if 'Payroll Job Days' in borough_matching.columns else 'Payroll_Count'].sum()
                total_matched = district_analysis[matched_col].sum()
                
                # Create formatters for district analysis table
                district_formatters = {
                    'District': lambda x: f"District {int(x)}",
                    subcentral_col: format_int,
                    'Payroll Job Days' if 'Payroll Job Days' in borough_matching.columns else 'Payroll_Count': format_int,
                    matched_col: format_int,
                    'Match Percentage': format_pct
                }
                
                payroll_analysis_html = f"""
                <div class="section">
                    <h3>SubCentral vs Payroll Analysis (District Level)</h3>
                    <p><em>This analysis shows district-level matching within {borough} borough.</em></p>
                    
                    <div class="summary-box">
                        <h4>Borough Matching Summary</h4>
                        <ul>
                            <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                            <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                            <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                            <li><strong>Average Match Rate:</strong> {borough_avg_match:.1f}%</li>
                        </ul>
                    </div>
                    
                    <div class="table-responsive">
                        <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify districts needing attention.</em></p>
                        {create_conditional_formatted_table(district_analysis_display, district_formatters, 'Match Percentage')}
                    </div>
                </div>
                """
    
    # === SECTION 3: CLASSIFICATION INFORMATION ===
    # Sort by total jobs (highest to lowest per feedback)
    borough_data_sorted = borough_data.sort_values('Total', ascending=False)
    
    # Use all the columns needed for tabbed tables
    required_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                     'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_cols = [col for col in required_cols if col in borough_data_sorted.columns]
    
    # Create formatters for all the columns
    formatters = {}
    for col in existing_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str  # For Classification
    
    classification_table_html = create_classification_tabbed_tables(borough_data_sorted[existing_cols], formatters)
    
    # Create bar chart
    bar_chart_file = os.path.join(borough_dir, f'{borough_clean}_bar_chart.html')
    create_bar_chart(
        borough_data_sorted,
        f'Jobs by Classification and Type - {borough}',
        bar_chart_file,
        f"borough_{borough_clean}_bar_chart"
    )
    
    # Create pie charts
    pie_charts_html = create_pie_charts_for_data(borough_data_sorted, borough_clean, borough_dir)
    
    # === SECTION 4: DISTRICT LEVEL FILL RATES ===
    # Create summary by district within this borough
    district_summary = create_summary_stats(df_borough, ['District'])
    district_summary = district_summary.groupby('District', as_index=False).agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    
    # Calculate percentages
    district_summary['Vacancy_Fill_Pct'] = (district_summary['Vacancy_Filled'] / district_summary['Total_Vacancy'] * 100).fillna(0).round(1)
    district_summary['Absence_Fill_Pct'] = (district_summary['Absence_Filled'] / district_summary['Total_Absence'] * 100).fillna(0).round(1)
    district_summary['Total_Filled'] = district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']
    district_summary['Total_Unfilled'] = district_summary['Vacancy_Unfilled'] + district_summary['Absence_Unfilled']
    district_summary['Overall_Fill_Pct'] = ((district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']) / district_summary['Total'] * 100).fillna(0).round(1)
    
    # Create formatters for district summary
    district_formatters = {
        'District': lambda x: f"District {int(x)}" if pd.notna(x) else x,
        'Vacancy Filled': format_int, 'Vacancy Unfilled': format_int, 'Total Vacancy': format_int,
        'Vacancy Fill %': format_pct, 'Absence Filled': format_int, 'Absence Unfilled': format_int,
        'Total Absence': format_int, 'Absence Fill %': format_pct, 'Total Filled': format_int, 
        'Total Unfilled': format_int, 'Total': format_int, 'Overall Fill %': format_pct
    }
    district_summary_html = create_district_tabbed_tables(
        district_summary.rename(columns={
            'District': 'District',
            'Vacancy_Filled': 'Vacancy_Filled', 'Vacancy_Unfilled': 'Vacancy_Unfilled', 'Total_Vacancy': 'Total_Vacancy',
            'Vacancy_Fill_Pct': 'Vacancy_Fill_Pct', 'Absence_Filled': 'Absence_Filled', 'Absence_Unfilled': 'Absence_Unfilled',
            'Total_Absence': 'Total_Absence', 'Absence_Fill_Pct': 'Absence_Fill_Pct', 'Total_Filled': 'Total_Filled', 
            'Total_Unfilled': 'Total_Unfilled', 'Total': 'Total', 'Overall_Fill_Pct': 'Overall_Fill_Pct'
        }), 
        district_formatters
    )
    
    # Get districts in this borough and create links
    borough_districts = sorted(df[df['Borough'] == borough]['District'].unique())
    district_links = ""
    for district in borough_districts:
        total_jobs = district_summary[district_summary['District'] == district]['Total'].iloc[0]
        district_links += f'<li><a href="../District_{int(district)}/{int(district)}_report.html">District {int(district)} Report</a> - {int(total_jobs):,} total jobs</li>\n'
    
    # Build content with new structure
    content = f"""
        {get_header_html("../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"Borough: {borough}", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([("../index.html", "← Back to Overall Summary")])}
            
            <!-- SECTION 1: Overall Summary (Borough vs Citywide) -->
            <div class="section">
                <h3>1. Overall Summary - {borough} vs. Citywide</h3>
                <p><em>Comparison frames everything else you will see on this page</em></p>
                {comparison_html}
            </div>

            <!-- SECTION 2: Match Payroll Analysis -->
            {payroll_analysis_html}

            <!-- SECTION 3: Classification Information -->
            <div class="section">
                <h3>3. Classification Information (Borough Level)</h3>
                <h4>Summary Statistics</h4>
                <p><em>Data sorted from highest to lowest total jobs</em></p>
                {classification_table_html}
            </div>

            <div class="section">
                <h4>Jobs by Classification Type</h4>
                <div class="chart-container">
                    <iframe src="{borough_clean}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h4>Breakdown by Classification</h4>
                <div class="pie-container">{pie_charts_html}</div>
            </div>

            <!-- SECTION 4: District Level Fill Rates -->
            <div class="section">
                <h3>4. District Level Fill Rates</h3>
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest overall fill rate to identify districts needing attention. This data is based on SubCentral data only. Use the tabs below to switch between different views. Click on district links for detailed reports.</em></p>
                {district_summary_html}
                
                <h4>Individual District Reports</h4>
                <p><em><strong>Note:</strong> Click on district links below for detailed district-level reports. Links are ordered by district number.</em></p>
                <div class="district-links"><ul>{district_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - {borough}", "../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(borough_dir, f'{borough_clean}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file

def create_overall_summary(df, citywide_stats, borough_stats, output_dir, date_range_info, matching_stats=None, district_stats=None):
    """
    Create an overall summary report across all districts with restructured sections:
    1. Overall Summary with Average Match Percentage
    2. Match Payroll Analysis (citywide)
    3. Classification Information (sorted highest to lowest total jobs)
    4. Borough Breakdowns
    """
    import pandas as pd
    import numpy as np
    
    # === SECTION 1: OVERALL SUMMARY WITH MATCH PERCENTAGE ===
    # Use pre-calculated matching stats instead of recalculating
    citywide_avg_match = 0
    if matching_stats is not None and not matching_stats.empty:
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                citywide_avg_match = matching_stats[match_col].mean()
                break
    
    # Use citywide_stats for overall statistics - already sorted by total jobs (highest to lowest)
    overall_stats = citywide_stats.copy()
    if overall_stats.empty:
        # Fallback: create from district stats if citywide is empty
        overall_stats = district_stats.groupby('Classification', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
            'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
        overall_stats['Vacancy_Fill_Pct'] = np.where(
            overall_stats['Total_Vacancy'] > 0,
            (overall_stats['Vacancy_Filled'] / overall_stats['Total_Vacancy'] * 100).round(1), 0
        )
        overall_stats['Absence_Fill_Pct'] = np.where(
            overall_stats['Total_Absence'] > 0,
            (overall_stats['Absence_Filled'] / overall_stats['Total_Absence'] * 100).round(1), 0
        )
        overall_stats['Total_Filled'] = overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']
        overall_stats['Total_Unfilled'] = overall_stats['Vacancy_Unfilled'] + overall_stats['Absence_Unfilled']
        overall_stats['Overall_Fill_Pct'] = np.where(
            overall_stats['Total'] > 0,
            ((overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']) / overall_stats['Total'] * 100).round(1), 0
        )
    
    # Sort by total jobs (highest to lowest per feedback)
    overall_stats = overall_stats.sort_values('Total', ascending=False)

    # === SECTION 2: MATCH PAYROLL ANALYSIS (Borough Level) ===
    payroll_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty:
        # Find the match percentage column
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Add borough information to matching data
            borough_info = df[['Location', 'Borough']].drop_duplicates()
            matching_with_borough = matching_stats.merge(borough_info, on='Location', how='left')
            
            # Aggregate by borough to show borough-level analysis (ensuring unique boroughs)
            borough_analysis = matching_with_borough.groupby('Borough', as_index=False).agg({
                'SubCentral Job Days' if 'SubCentral Job Days' in matching_stats.columns else 'SubCentral_Count': 'sum',
                'Payroll Job Days' if 'Payroll Job Days' in matching_stats.columns else 'Payroll_Count': 'sum'
            })
            
            # Find matched column and add it
            matched_col = None
            for col in matching_stats.columns:
                if 'Matched' in col and 'Job' in col:
                    matched_col = col
                    break
            
            if matched_col:
                borough_matched = matching_with_borough.groupby('Borough', as_index=False)[matched_col].sum()
                borough_analysis = borough_analysis.merge(borough_matched, on='Borough', how='left')
                
                # Calculate borough-level match percentages
                subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in matching_stats.columns else 'SubCentral_Count'
                borough_analysis['Match_Percentage'] = (
                    borough_analysis[matched_col] / borough_analysis[subcentral_col] * 100
                ).round(1)
                
                # Sort by Match Percentage (lowest to highest per feedback)
                borough_analysis = borough_analysis.sort_values('Match_Percentage', ascending=True)
                
                # Rename column for display (remove underscore)
                borough_analysis_display = borough_analysis.rename(columns={'Match_Percentage': 'Match Percentage'})
                
                # Calculate totals
                total_subcentral = borough_analysis[subcentral_col].sum()
                total_payroll = borough_analysis['Payroll Job Days' if 'Payroll Job Days' in matching_stats.columns else 'Payroll_Count'].sum()
                total_matched = borough_analysis[matched_col].sum()
                
                # Create formatters for borough analysis table
                borough_formatters = {
                    'Borough': str,
                    subcentral_col: format_int,
                    'Payroll Job Days' if 'Payroll Job Days' in matching_stats.columns else 'Payroll_Count': format_int,
                    matched_col: format_int,
                    'Match Percentage': format_pct
                }
                
                payroll_analysis_html = f"""
                <div class="section">
                    <h3>2. SubCentral vs Payroll Analysis (Borough Level)</h3>
                    <p><em>This analysis shows borough-level matching across all five boroughs.</em></p>
                    
                    <div class="summary-box">
                        <h4>Citywide Matching Summary</h4>
                        <ul>
                            <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                            <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                            <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                            <li><strong>Average Match Rate:</strong> {citywide_avg_match:.1f}%</li>
                        </ul>
                    </div>
                    
                    <div class="table-responsive">
                        <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify boroughs needing attention.</em></p>
                        {create_conditional_formatted_table(borough_analysis_display, borough_formatters, 'Match Percentage')}
                    </div>
                </div>
                """

    overall_chart_file = os.path.join(output_dir, 'overall_bar_chart.html')
    create_overall_bar_chart(overall_stats, overall_chart_file)

    district_summary = district_stats.groupby('District', as_index=False).agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    }) if district_stats is not None else pd.DataFrame()
    district_summary['Vacancy_Fill_Pct'] = np.where(
        district_summary['Total_Vacancy'] > 0,
        (district_summary['Vacancy_Filled'] / district_summary['Total_Vacancy'] * 100).round(1), 0
    )
    district_summary['Absence_Fill_Pct'] = np.where(
        district_summary['Total_Absence'] > 0,
        (district_summary['Absence_Filled'] / district_summary['Total_Absence'] * 100).round(1), 0
    )
    district_summary['Total_Filled'] = district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']
    district_summary['Total_Unfilled'] = district_summary['Vacancy_Unfilled'] + district_summary['Absence_Unfilled']
    district_summary['Overall_Fill_Pct'] = np.where(
        district_summary['Total'] > 0,
        ((district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']) / district_summary['Total'] * 100).round(1), 0
    )
    district_summary = district_summary.sort_values('Total', ascending=False)

    # Vectorized navigation link generation
    district_links = ''.join([
        f'<li><a href="District_{int(row.District)}/{int(row.District)}_report.html">District {int(row.District)} Report</a> - {int(row.Total):,} total jobs</li>\n'
        for _, row in district_summary.sort_values('District').iterrows()
    ])

    borough_totals = borough_stats.groupby('Borough')['Total'].sum()
    borough_links = ''.join([
        f'<li><a href="Borough_{borough.replace(" ", "_").replace("/", "_")}/{borough.replace(" ", "_").replace("/", "_")}_report.html">{borough} Report</a> - {int(total):,} total jobs</li>\n'
        for borough, total in borough_totals.items() if borough != 'Unknown'
    ])

    # Vectorized statistics
    fill_status_counts = df['Fill_Status'].value_counts()
    type_counts = df['Type'].value_counts()
    total_jobs = len(df)
    total_filled = fill_status_counts.get('Filled', 0)
    total_vacancies = type_counts.get('Vacancy', 0)
    total_absences = type_counts.get('Absence', 0)
    unique_districts = df['District'].nunique()
    unique_schools = df['Location'].nunique()
    unique_classifications = df['Classification'].nunique()

    summary_box = f"""
    <div class="section">
        <div class="summary-box">
            <h3>Key Statistics</h3>
            <ul>
                <li><strong>Total Jobs</strong>{total_jobs:,}</li>
                <li><strong>Total Vacancies</strong>{total_vacancies:,} ({(total_vacancies/total_jobs*100):.1f}%)</li>
                <li><strong>Total Absences</strong>{total_absences:,} ({(total_absences/total_jobs*100):.1f}%)</li>
                <li><strong>Total Filled</strong>{total_filled:,} ({(total_filled/total_jobs*100):.1f}%)</li>
                <li><strong>Total Districts</strong>{unique_districts}</li>
                <li><strong>Total Schools</strong>{unique_schools}</li>
                <li><strong>Total Classifications</strong>{unique_classifications}</li>
            </ul>
        </div>
    </div>
    """
    
    # Create tabbed summary tables - sorted by total jobs (highest to lowest)
    # Use all the columns needed for tabbed tables
    required_overall_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                            'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                            'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_overall_cols = [col for col in required_overall_cols if col in overall_stats.columns]
    
    overall_formatters = {}
    for col in existing_overall_cols:
        if 'Pct' in col:
            overall_formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            overall_formatters[col] = format_int
        else:
            overall_formatters[col] = str  # For Classification
    
    overall_table_html = create_classification_tabbed_tables(overall_stats[existing_overall_cols], overall_formatters)
    
    # Create borough summary table with proper column formatting
    required_borough_cols = ['Borough', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                            'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                            'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_borough_cols = [col for col in required_borough_cols if col in borough_stats.columns]
    
    if existing_borough_cols and not borough_stats.empty:
        # Aggregate borough data by Borough (sum numeric columns, recalculate percentages)
        borough_agg = borough_stats.groupby('Borough', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
        
        # Recalculate percentages for aggregated data
        borough_agg['Vacancy_Fill_Pct'] = (
            borough_agg['Vacancy_Filled'] / borough_agg['Total_Vacancy'] * 100
        ).fillna(0).round(1)
        borough_agg['Absence_Fill_Pct'] = (
            borough_agg['Absence_Filled'] / borough_agg['Total_Absence'] * 100
        ).fillna(0).round(1)
        borough_agg['Total_Filled'] = borough_agg['Vacancy_Filled'] + borough_agg['Absence_Filled']
        borough_agg['Total_Unfilled'] = borough_agg['Vacancy_Unfilled'] + borough_agg['Absence_Unfilled']
        borough_agg['Overall_Fill_Pct'] = (
            (borough_agg['Vacancy_Filled'] + borough_agg['Absence_Filled']) / borough_agg['Total'] * 100
        ).fillna(0).round(1)
        
        borough_for_table = borough_agg[existing_borough_cols].sort_values('Overall_Fill_Pct', ascending=True)
        
        borough_formatters = {}
        for col in existing_borough_cols:
            if col == 'Borough':
                borough_formatters[col] = str
            elif 'Pct' in col:
                borough_formatters[col] = format_pct
            elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                         'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
                borough_formatters[col] = format_int
            else:
                borough_formatters[col] = str
        
        borough_table_html = create_borough_tabbed_tables(
            borough_for_table, 
            borough_formatters
        )
    else:
        borough_table_html = "<p><em>No borough data available</em></p>"
    
    # Create district summary table with proper column formatting
    required_district_cols = ['District', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                             'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                             'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_district_cols = [col for col in required_district_cols if col in district_summary.columns]
    district_for_table = district_summary[existing_district_cols].sort_values('Overall_Fill_Pct', ascending=True)
    
    district_formatters = {}
    for col in existing_district_cols:
        if col == 'District':
            district_formatters[col] = lambda x: f"District {int(x)}" if pd.notna(x) else x
        elif 'Pct' in col:
            district_formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            district_formatters[col] = format_int
        else:
            district_formatters[col] = str
    
    district_table_html = create_district_tabbed_tables(
        district_for_table, 
        district_formatters
    )
    
    # Create district choropleth map
    district_map_html = ""
    try:
        from district_mapping import create_district_choropleth, get_district_map_section_html
        map_file = os.path.join(output_dir, 'district_fillrate_map.html')
        map_content = create_district_choropleth(district_summary, map_file)
        if map_content:
            district_map_html = get_district_map_section_html(district_summary, 'district_fillrate_map.html')
        else:
            print("⚠ Could not create district choropleth map")
    except Exception as e:
        print(f"⚠ Could not create district map - {e}")
        # Continue without the map
    
    # Build content with new structure per feedback
    content = f"""
        {get_header_html("Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Dashboard", 
                        "Citywide Summary Report", 
                        date_range_info)}
        
        <div class="content">
            <!-- SECTION 1: Overall Summary with Match Percentage -->
            <div class="section">
                <h3>1. Overall Summary</h3>
                <div class="summary-box">
                    <h4>Key Statistics</h4>
                    <ul>
                        <li><strong>Total Jobs:</strong> {total_jobs:,}</li>
                        <li><strong>Total Vacancies:</strong> {total_vacancies:,} ({(total_vacancies/total_jobs*100):.1f}%)</li>
                        <li><strong>Total Absences:</strong> {total_absences:,} ({(total_absences/total_jobs*100):.1f}%)</li>
                        <li><strong>Total Filled:</strong> {total_filled:,} ({(total_filled/total_jobs*100):.1f}%)</li>
                        <li><strong>Average Match %:</strong> {citywide_avg_match:.1f}% (key metric for SubCentral usage)</li>
                        <li><strong>Total Districts:</strong> {unique_districts}</li>
                        <li><strong>Total Schools:</strong> {unique_schools}</li>
                        <li><strong>Total Classifications:</strong> {unique_classifications}</li>
                    </ul>
                </div>
            </div>

            <!-- SECTION 2: Match Payroll Analysis -->
            {payroll_analysis_html}
            
            <!-- SECTION 3: Classification Information -->
            <div class="section">
                <h3>3. Classification Information (Citywide)</h3>
                <h4>Summary Statistics</h4>
                <p><em>Data sorted from highest to lowest total jobs</em></p>
                {overall_table_html}
            </div>
            
            <div class="section">
                <h4>Jobs by Classification Type</h4>
                <div class="chart-container">
                    <iframe src="overall_bar_chart.html" width="1450" height="600" frameborder="0"></iframe>
                </div>
            </div>
            
            <!-- SECTION 4: Borough Level Summary -->
            <div class="section">
                <h3>4. Borough Level Fill Rates</h3>
                <h4>Summary by Borough</h4>
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest overall fill rate to identify boroughs needing attention. Use the tabs below to switch between different views. Click on borough links for detailed reports.</em></p>
                {borough_table_html}
            </div>
            
            <!-- SECTION 5: District Level Summary -->
            <div class="section">
                <h3>5. District Level Fill Rates</h3>
                <h4>Summary by District</h4>
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest overall fill rate to identify districts needing attention. Use the tabs below to switch between different views. Click on district links for detailed reports.</em></p>
                {district_table_html}
                {district_map_html}
            </div>
            
            <div class="section">
                <h4>Individual District Reports</h4>
                <p><em><strong>Note:</strong> Click on district links below for detailed district-level reports. Links are ordered by district number.</em></p>
                <div class="district-links"><ul>{district_links}</ul></div>
            </div>
            
            <div class="section">
                <h4>Individual Borough Reports</h4>
                <p><em><strong>Note:</strong> Borough reports provide classification breakdowns and district summaries. Links are ordered alphabetically by borough.</em></p>
                <div class="borough-links"><ul>{borough_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template("Jobs Dashboard - Overall Summary", "Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    index_file = os.path.join(output_dir, 'index.html')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return index_file

def main():
    """
    Main function to generate static reports
    """
    # Configuration - Updated to use multiple CSV files
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
    output_directory = 'nycdoe_reports'
    
    start_time = time.time()
    print("🚀 NYC DOE Paraprofessional Fill Rate Analysis")
    print("=" * 50)
    
    try:
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Copy logo for deployment
        copy_logo_to_output(output_directory)
        
        # Load and process data from multiple files
        print("Loading data sources...")
        df, srepp_df = load_and_process_data(csv_files)
        
        # Handle SREPP data if present
        if not srepp_df.empty:
            print(f"✓ SREPP payroll data: {len(srepp_df)} records")
        else:
            print("⚠ No SREPP payroll data found")
            
        # Show main data info
        if not df.empty:
            print(f"✓ SubCentral data: {len(df)} records")
        else:
            print("✗ No SubCentral data found")
            
        # Create matching analysis between SubCentral and SREPP data
        print("Creating payroll matching analysis...")
        matching_stats = create_matching_analysis(df, srepp_df)
        if not matching_stats.empty:
            print(f"✓ Analysis completed for {len(matching_stats)} locations")
        else:
            print("⚠ No matching analysis available")
        
        # Continue with main data processing
        if df.empty:
            print("✗ Error: No main data loaded. Check your CSV files.")
            return
        
        # Get date range information
        date_range_info = get_data_date_range(df)
        print(f"✓ Report period: {date_range_info}")
        
        # OPTIMIZATION: Calculate ALL statistics levels once (like matching analysis)
        print("Creating comprehensive statistics...")
        
        # Create all levels of statistics
        citywide_stats = create_summary_stats(df, [])  # No grouping = citywide
        borough_stats = create_summary_stats(df, ['Borough'])
        district_stats = create_summary_stats(df, ['District'])  
        school_stats = create_summary_stats(df, ['District', 'Location'])
        
        # Validate statistics were created successfully
        stats_info = [
            ('citywide', citywide_stats),
            ('borough', borough_stats), 
            ('district', district_stats),
            ('school', school_stats)
        ]
        
        for name, stats in stats_info:
            if stats.empty:
                print(f"⚠ Warning: {name} statistics are empty")
            else:
                print(f"✓ {name.capitalize()} stats: {len(stats)} records, columns: {list(stats.columns)}")
        
        # Clean up any Type_Fill_Status columns
        for stats in [citywide_stats, borough_stats, district_stats, school_stats]:
            if 'Type_Fill_Status' in stats.columns:
                stats.drop(columns=['Type_Fill_Status'], inplace=True)

        # Convert to int to avoid float display issues
        int_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled', 
                   'Total_Vacancy', 'Total_Absence', 'Total']
        for stats in [citywide_stats, borough_stats, district_stats, school_stats]:
            for col in int_cols:
                if col in stats.columns:
                    stats[col] = stats[col].astype(int)
        
        print(f"✓ Statistics created: citywide, {len(borough_stats)} boroughs, {len(district_stats)} districts, {len(school_stats)} schools")
        
        # For backward compatibility, keep summary_stats as district level
        summary_stats = district_stats
        
        # Create reports for each District
        districts = sorted(df['District'].unique())
        summary_districts = sorted(summary_stats['District'].unique())
        print(f"Generating district reports ({len(districts)} districts)...")
        report_files = []
        all_school_reports = []
        
        for district in districts:
            district_data = summary_stats[summary_stats['District'] == district].copy()
            if len(district_data) > 0:
                # Check if district exists in main dataframe
                district_schools = df[df['District'] == district]
                if district_schools.empty:
                    print(f"⚠ District {int(district)}: no schools found, skipping...")
                    continue
                
                print(f"✓ Generating report for District {int(district)}...")
                result = create_district_report(
                    district, district_data, df, output_directory, district_stats, date_range_info, matching_stats, school_stats
                )
                if result is not None:
                    report_file, school_reports = result
                    report_files.append(report_file)
                    all_school_reports.extend(school_reports)
        
        # Create reports for each borough
        boroughs = sorted(df['Borough'].unique())
        print(f"Generating borough reports ({len(boroughs)} boroughs)...")
        borough_report_files = []

        for borough in boroughs:
            if borough != 'Unknown':  # Skip if no valid borough found
                borough_data = borough_stats[borough_stats['Borough'] == borough].copy()
                if len(borough_data) > 0:
                    print(f"✓ Generating report for Borough {borough}...")
                    report_file = create_borough_report(
                        borough, borough_data, df, output_directory, district_stats, date_range_info, matching_stats
                    )
                    borough_report_files.append(report_file)
        
        # Create overall summary
        index_file = create_overall_summary(df, citywide_stats, borough_stats, output_directory, date_range_info, matching_stats, district_stats)
        
        print("✓ Reports generated successfully!")
        print(f"  • Main report: {index_file}")
        print(f"  • District reports: {len(report_files)} files")
        print(f"  • Borough reports: {len(borough_report_files)} files")
        print(f"  • School reports: {len(all_school_reports)} files")
        print(f"  • Open '{index_file}' to view the dashboard")
        
        elapsed = time.time() - start_time
        print(f"⏱ Completed in {elapsed:.1f} seconds")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find one or more CSV files: {csv_files}")
        print("Please make sure all files exist in the specified paths.")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
