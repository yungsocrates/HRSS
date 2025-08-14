"""
Report generation functions for NYC DOE Reports
"""

import os
import re
import numpy as np
from templates import (
    get_html_template, get_header_html, get_professional_footer,
    get_navigation_html, get_comparison_card_html, create_classification_tabbed_tables, create_school_tabbed_tables,
    create_district_tabbed_tables, create_borough_tabbed_tables,
    create_simple_table_with_tabbed_styling, create_conditional_formatted_table
)
from chart_utils import (
    create_bar_chart, create_pie_charts_for_data, create_overall_bar_chart
)
from data_processing import (
    df_with_pretty_columns, format_pct, format_int, DISPLAY_COLS,
    create_summary_stats, calculate_fill_rates, get_totals_from_data
)

def create_school_report(district, location, location_clean, school_data, df, summary_stats, output_dir, date_range_info, matching_stats=None):
    """
    Create a comprehensive report for a single school
    """
    # Create subfolder for school if it doesn't exist
    school_dir = os.path.join(output_dir, f"District_{int(district)}", "Schools", f"School_{location_clean}")
    os.makedirs(school_dir, exist_ok=True)
    
    # Sanitize location name for files - more robust for Windows
    safe_location_name = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location_clean)).strip()
    safe_location_name = re.sub(r'_+', '_', safe_location_name).strip('_')
    safe_location_name = safe_location_name.replace('.', '_')
    if len(safe_location_name) > 200:
        safe_location_name = safe_location_name[:200].rstrip('._')
    
    # Create tabbed summary tables - use all required columns for school classification data
    # For school reports, the data should be aggregated by classification
    school_classification_data = school_data.groupby('Classification').agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    }).reset_index()
    
    # Calculate percentages for the aggregated data
    school_classification_data['Vacancy_Fill_Pct'] = np.where(
        school_classification_data['Total_Vacancy'] > 0,
        (school_classification_data['Vacancy_Filled'] / school_classification_data['Total_Vacancy'] * 100).round(1), 0
    )
    school_classification_data['Absence_Fill_Pct'] = np.where(
        school_classification_data['Total_Absence'] > 0,
        (school_classification_data['Absence_Filled'] / school_classification_data['Total_Absence'] * 100).round(1), 0
    )
    school_classification_data['Total_Filled'] = school_classification_data['Vacancy_Filled'] + school_classification_data['Absence_Filled']
    school_classification_data['Total_Unfilled'] = school_classification_data['Vacancy_Unfilled'] + school_classification_data['Absence_Unfilled']
    school_classification_data['Overall_Fill_Pct'] = np.where(
        school_classification_data['Total'] > 0,
        ((school_classification_data['Vacancy_Filled'] + school_classification_data['Absence_Filled']) / school_classification_data['Total'] * 100).round(1), 0
    )
    
    # Use all the columns needed for tabbed tables
    required_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                     'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_cols = [col for col in required_cols if col in school_classification_data.columns]
    
    # Create formatters for all the columns
    formatters = {}
    for col in existing_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str
    
    table_html = create_classification_tabbed_tables(school_classification_data[existing_cols], formatters)
    
    # Create bar chart
    bar_chart_file = os.path.join(school_dir, f'{safe_location_name}_bar_chart.html')
    create_bar_chart(
        school_data,
        f'Jobs by Classification and Type - {location}',
        bar_chart_file,
        f"{safe_location_name}_bar_chart"
    )
    
    # Create pie charts
    pie_charts_html = create_pie_charts_for_data(school_data, location_clean, school_dir)
    
    # Get comparison data
    school_borough = df[df['Location'] == location]['Borough'].iloc[0]
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    
    borough_data = create_summary_stats(df[df['Borough'] == school_borough], ['Borough'])
    district_data = create_summary_stats(df[df['District'] == district], ['District'])
    
    borough_totals = get_totals_from_data(borough_data)
    district_totals = get_totals_from_data(district_data)
    school_totals = get_totals_from_data(school_data)
    
    # Calculate fill rates
    school_rates = calculate_fill_rates(school_totals)
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    district_rates = calculate_fill_rates(district_totals)
    
    # Calculate average match percentages from pre-calculated matching stats
    citywide_match_pct = 0
    borough_match_pct = 0
    district_match_pct = 0
    
    if matching_stats is not None and not matching_stats.empty:
        # Find match percentage column
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Calculate averages by filtering the pre-calculated data
            citywide_match_pct = matching_stats[match_col].mean()
            
            # Borough average
            borough_schools = df[df['Borough'] == school_borough]['Location'].unique()
            borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools)]
            if not borough_matching.empty:
                borough_match_pct = borough_matching[match_col].mean()
            
            # District average
            district_schools = df[df['District'] == district]['Location'].unique()
            district_matching = matching_stats[matching_stats['Location'].isin(district_schools)]
            if not district_matching.empty:
                district_match_pct = district_matching[match_col].mean()
    
    # Create comparison cards
    comparison_cards = []
    
    # Citywide card
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Total Vacancies": f"{overall_stats['Total_Vacancy']:,} ({(overall_stats['Total_Vacancy'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{overall_stats['Total_Absence']:,} ({(overall_stats['Total_Absence'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%",
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_match_pct:.1f}%" if citywide_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Total Vacancies": f"{borough_totals['Total_Vacancy']:,} ({(borough_totals['Total_Vacancy'] / borough_totals['Total'] * 100) if borough_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{borough_totals['Total_Absence']:,} ({(borough_totals['Total_Absence'] / borough_totals['Total'] * 100) if borough_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_match_pct:.1f}%" if borough_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df[df['Borough'] == school_borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"{school_borough} Statistics", borough_stats, "borough"))
    
    # District card
    district_stats = {
        "Total Jobs": f"{district_totals['Total']:,}",
        "Total Vacancies": f"{district_totals['Total_Vacancy']:,} ({(district_totals['Total_Vacancy'] / district_totals['Total'] * 100) if district_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{district_totals['Total_Absence']:,} ({(district_totals['Total_Absence'] / district_totals['Total'] * 100) if district_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{district_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{district_rates[1]:.1f}%",
        "Absence Fill Rate": f"{district_rates[2]:.1f}%",
        "Average Match %": f"{district_match_pct:.1f}%" if district_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df[df['District'] == district]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"District {int(district)} Statistics", district_stats, "district"))
    
    # School card
    school_stats = {
        "Total Jobs": f"{school_totals['Total']:,}",
        "Total Vacancies": f"{school_totals['Total_Vacancy']:,} ({(school_totals['Total_Vacancy'] / school_totals['Total'] * 100) if school_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{school_totals['Total_Absence']:,} ({(school_totals['Total_Absence'] / school_totals['Total'] * 100) if school_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{school_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{school_rates[1]:.1f}%",
        "Absence Fill Rate": f"{school_rates[2]:.1f}%",
        "Classifications": ", ".join(school_data['Classification'].unique())
    }
    comparison_cards.append(get_comparison_card_html(f"This School ({location})", school_stats, "school"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # Build content with new structure
    content = f"""
        {get_header_html("../../../../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"School: {location} (District {int(district)})", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([
                ("../../../index.html", "← Back to Overall Summary"),
                (f"../../{int(district)}_report.html", f"← Back to District {int(district)}")
            ])}
            
            <div class="section">
                <h3>School Overview: Comparison</h3>
                <p><em>This comparison shows how this school performs relative to district, borough, and citywide averages.</em></p>
                {comparison_html}
            </div>
            
            <div class="section">
                <h3>Classification Information</h3>
                <p><em><strong>Note:</strong> This data is based on SubCentral data only. Use the tabs below to switch between different views of the classification data. Data is sorted alphabetically by classification type.</em></p>
                {table_html}
            </div>

            <div class="section">
                <h3>Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="{safe_location_name}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h3>Breakdown by Classification</h3>
                <div class="pie-container">{pie_charts_html}</div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - {location}", "../../../../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(school_dir, f'{safe_location_name}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file

def create_district_report(district, district_data, df, output_dir, summary_stats, date_range_info, matching_stats=None, school_stats=None):
    """
    Create a comprehensive report for a single District following the new structure:
    1. Comparison cards (Citywide vs Borough vs District)
    2. SubCentral vs Payroll Analysis
    3. Classification Information
    4. School Level Fill Rates
    """
    # Create subfolder for District
    district_dir = os.path.join(output_dir, f"District_{int(district)}")
    os.makedirs(district_dir, exist_ok=True)
    
    # Get the borough for this district with error handling
    district_schools = df[df['District'] == district]
    if district_schools.empty:
        print(f"Warning: No schools found for district {district}")
        return None, []
    
    district_borough = district_schools['Borough'].iloc[0]
    borough_name_clean = district_borough.replace(' ', '_').replace('/', '_')
    borough_data = create_summary_stats(df[df['Borough'] == district_borough], ['Borough'])
    
    # Get comparison data for Section 1
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    
    borough_totals = get_totals_from_data(borough_data)
    district_totals = get_totals_from_data(district_data)
    
    # Calculate fill rates
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    district_rates = calculate_fill_rates(district_totals)
    
    # Calculate average match percentage for each level
    citywide_match_pct = 0
    borough_match_pct = 0
    district_match_pct = 0
    
    if matching_stats is not None and not matching_stats.empty:
        # Calculate citywide average
        match_col = 'Match_Percentage'
        if match_col not in matching_stats.columns:
            for col in matching_stats.columns:
                if 'Match' in col and ('Percentage' in col or '%' in col):
                    match_col = col
                    break
        
        if match_col in matching_stats.columns:
            citywide_match_pct = matching_stats[match_col].mean()
            
            # Borough average
            borough_schools = df[df['Borough'] == district_borough]['Location'].unique()
            borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools)]
            if not borough_matching.empty:
                borough_match_pct = borough_matching[match_col].mean()
            
            # District average
            district_school_list = df[df['District'] == district]['Location'].unique()
            district_matching = matching_stats[matching_stats['Location'].isin(district_school_list)]
            if not district_matching.empty:
                district_match_pct = district_matching[match_col].mean()
    
    # Section 1: Comparison Cards
    comparison_cards = []
    
    # Citywide card with match percentage
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%", 
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_match_pct:.1f}%" if matching_stats is not None and not matching_stats.empty else "N/A",
        "Number of Districts": f"{len(df['District'].unique())}",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card with match percentage
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_match_pct:.1f}%" if matching_stats is not None and not matching_stats.empty else "N/A",
        "Number of Schools": f"{len(df[df['Borough'] == district_borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"{district_borough} Statistics", borough_stats, "borough"))
    
    # District card with match percentage
    district_stats = {
        "Total Jobs": f"{district_totals['Total']:,}",
        "Overall Fill Rate": f"{district_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{district_rates[1]:.1f}%",
        "Absence Fill Rate": f"{district_rates[2]:.1f}%",
        "Average Match %": f"{district_match_pct:.1f}%" if matching_stats is not None and not matching_stats.empty else "N/A",
        "Number of Schools": f"{len(df[df['District'] == district]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"This District ({int(district)})", district_stats, "district"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # Section 2: SubCentral vs Payroll Analysis (simple table, no tabs)
    payroll_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty and not district_matching.empty:
        # Sort by Match Percentage (lowest to highest)
        district_matching_sorted = district_matching.sort_values(match_col, ascending=True)
        
        # Rename Match_Percentage column for display (remove underscore)
        district_matching_display = district_matching_sorted.rename(columns={'Match_Percentage': 'Match Percentage'})
        
        # Create summary stats
        subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in district_matching.columns else 'SubCentral_Count'
        payroll_col = 'Payroll Job Days' if 'Payroll Job Days' in district_matching.columns else 'Payroll_Count'
        matched_col = None
        for col in district_matching.columns:
            if 'Matched' in col and 'Job' in col:
                matched_col = col
                break
        
        total_subcentral = district_matching[subcentral_col].sum() if subcentral_col in district_matching.columns else 0
        total_payroll = district_matching[payroll_col].sum() if payroll_col in district_matching.columns else 0
        total_matched = district_matching[matched_col].sum() if matched_col and matched_col in district_matching.columns else 0
        
        # Create formatters for matching table
        match_formatters = {
            col: format_pct if 'Match' in col and ('Percentage' in col or '%' in col) else format_int
            for col in district_matching_display.columns
        }
        
        payroll_analysis_html = f"""
        <div class="section">
            <h3>SubCentral vs Payroll Analysis</h3>
            <p><em>This analysis matches individual jobs using Location + EIS ID + Date between SubCentral and SREPP payroll systems.</em></p>
            
            <div class="summary-box">
                <h4>District Matching Summary</h4>
                <ul>
                    <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                    <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                    <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                    <li><strong>Average Match Rate:</strong> {district_match_pct:.1f}%</li>
                </ul>
            </div>
            
            <div class="table-responsive">
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify schools needing attention.</em></p>
                {create_conditional_formatted_table(district_matching_display, match_formatters, 'Match Percentage')}
            </div>
        </div>
        """
    
    # Section 3: Classification Information (sorted by total jobs - highest to lowest)
    district_data_sorted = district_data.sort_values('Total', ascending=False)
    
    # Use all the columns needed for tabbed tables
    required_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                     'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    available_display_cols = [col for col in required_cols if col in district_data_sorted.columns]
    
    # Create formatters for all the columns
    formatters = {}
    for col in available_display_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str
    
    table_html = create_classification_tabbed_tables(district_data_sorted[available_display_cols], formatters, debug_district=True)
    
    # Create bar chart (use full data for chart)
    bar_chart_file = os.path.join(district_dir, f'{int(district)}_bar_chart.html')
    create_bar_chart(
        district_data_sorted,
        f'Jobs by Classification and Type - District {int(district)}',
        bar_chart_file,
        f"district_{int(district)}_bar_chart"
    )
    
    # Create pie charts (use full data for chart)
    pie_charts_html = create_pie_charts_for_data(district_data_sorted, f"District_{int(district)}", district_dir)
    
    # Generate school reports and create summary table
    df_district = df[df['District'] == district]
    
    # Use pre-calculated school stats if available, otherwise calculate
    if school_stats is not None:
        # Filter school stats for this district and aggregate by location
        district_schools_data = school_stats[school_stats['District'] == district]
        summary_by_school = district_schools_data.groupby('Location', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
    else:
        # Fallback: calculate school stats
        summary_by_school = create_summary_stats(df_district, ['Location'])
        summary_by_school = summary_by_school.groupby('Location', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
    
    # Calculate percentages for schools
    summary_by_school['Vacancy_Fill_Pct'] = (summary_by_school['Vacancy_Filled'] / summary_by_school['Total_Vacancy'] * 100).fillna(0).round(1)
    summary_by_school['Absence_Fill_Pct'] = (summary_by_school['Absence_Filled'] / summary_by_school['Total_Absence'] * 100).fillna(0).round(1)
    
    # Calculate combined totals for schools
    summary_by_school['Total_Filled'] = summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']
    summary_by_school['Total_Unfilled'] = summary_by_school['Vacancy_Unfilled'] + summary_by_school['Absence_Unfilled']
    
    summary_by_school['Overall_Fill_Pct'] = ((summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']) / summary_by_school['Total'] * 100).fillna(0).round(1)
    
    # Generate school reports and links
    district_schools = df[df['District'] == district]['Location'].unique()
    school_links = ""
    school_reports = []
    
    for location in sorted(district_schools):
        # More robust sanitization for Windows filenames
        location_clean = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location)).strip()
        location_clean = re.sub(r'_+', '_', location_clean).strip('_')
        location_clean = location_clean.replace('.', '_')
        if len(location_clean) > 200:
            location_clean = location_clean[:200].rstrip('._')
        
        school_df = df[(df['District'] == district) & (df['Location'] == location)]
        school_summary = create_summary_stats(school_df, ['District', 'Location'])
        
        if len(school_summary) > 0:
            school_report = create_school_report(
                district, location, location_clean, school_summary, 
                df, summary_stats, output_dir, date_range_info, matching_stats
            )
            school_reports.append(school_report)
            
            total_jobs = int(school_summary['Total'].sum())
            school_links += f'<li><a href="Schools/School_{location_clean}/{location_clean}_report.html">{location}</a> - {total_jobs:,} total jobs</li>\n'
    
    # Create school summary table HTML using tabbed interface
    school_formatters = {
        'School': str,
        'Vacancy Filled': format_int, 'Vacancy Unfilled': format_int, 'Total Vacancy': format_int,
        'Vacancy Fill %': format_pct, 'Absence Filled': format_int, 'Absence Unfilled': format_int,
        'Total Absence': format_int, 'Absence Fill %': format_pct, 'Total Filled': format_int, 
        'Total Unfilled': format_int, 'Total': format_int, 'Overall Fill %': format_pct
    }
    summary_by_school_html = create_school_tabbed_tables(
        summary_by_school.rename(columns={'Location': 'School'}), 
        school_formatters
    )
    
    # Build content with new structure
    content = f"""
        {get_header_html("../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"District: {int(district)}", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([
                ("../index.html", "← Back to Overall Summary"),
                (f"../Borough_{borough_name_clean}/{borough_name_clean}_report.html", f"← Back to {district_borough} Report")
            ])}
            
            <div class="section">
                <h3>District Overview: Comparison</h3>
                {comparison_html}
            </div>

            {payroll_analysis_html}

            <div class="section">
                <h3>Classification Information</h3>
                <p><em><strong>Note:</strong> Use the tabs below to switch between different views of the data. Data sorted by highest to lowest total jobs.</em></p>
                {table_html}
            </div>

            <div class="section">
                <h3>Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="{int(district)}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h3>Breakdown by Classification</h3>
                <div class="pie-container">{pie_charts_html}</div>
            </div>
            
            <div class="section">
                <h3>School Level Fill Rates</h3>
                <p><em><strong>Note:</strong> This data is based on SubCentral data only. Data is sorted from lowest to highest overall fill rate to identify schools needing attention. Use the tabs below to switch between different views. Click on school codes for detailed reports.</em></p>
                {summary_by_school_html}
                
                <h4>Individual School Reports</h4>
                <div class="district-links"><ul>{school_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - District {int(district)}", "../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(district_dir, f'{int(district)}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file, school_reports
