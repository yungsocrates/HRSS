"""
Report generation functions for NYC DOE Reports
"""

import os
import re
from templates import (
    get_html_template, get_header_html, get_professional_footer,
    get_navigation_html, get_comparison_card_html
)
from chart_utils import (
    create_bar_chart, create_pie_charts_for_data, create_overall_bar_chart
)
from data_processing import (
    df_with_pretty_columns, format_pct, format_int, DISPLAY_COLS,
    create_summary_stats, calculate_fill_rates, get_totals_from_data
)

def create_school_report(district, location, location_clean, school_data, df, summary_stats, output_dir, date_range_info):
    """
    Create a comprehensive report for a single school
    """
    # Create subfolder for school if it doesn't exist
    school_dir = os.path.join(output_dir, f"District_{int(district)}", "Schools", f"School_{location_clean}")
    os.makedirs(school_dir, exist_ok=True)
    
    # Sanitize location name for files
    safe_location_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(location_clean)).strip()
    safe_location_name = re.sub(r'_+', '_', safe_location_name)
    if len(safe_location_name) > 200:
        safe_location_name = safe_location_name[:200]
    
    # Create summary table
    table_html = df_with_pretty_columns(school_data[DISPLAY_COLS]).to_html(
        index=False,
        table_id='summary-table',
        classes='table table-striped',
        formatters={
            df_with_pretty_columns(school_data[DISPLAY_COLS]).columns[i]: format_pct if 'Pct' in col else format_int
            for i, col in enumerate(DISPLAY_COLS)
        }
    )
    
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
    
    # Build content
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
                <h3>Summary Statistics</h3>
                <div class="table-responsive">{table_html}</div>
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
            
            <div class="section">
                <h2>Comparison: Citywide vs Borough vs District vs School</h2>
                {comparison_html}
            </div>
        </div>
        
        {get_professional_footer()}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - {location}", "../../../../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(school_dir, f'{safe_location_name}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file

def create_district_report(district, district_data, df, output_dir, summary_stats, date_range_info):
    """
    Create a comprehensive report for a single District including school summaries
    """
    # Create subfolder for District
    district_dir = os.path.join(output_dir, f"District_{int(district)}")
    os.makedirs(district_dir, exist_ok=True)
    
    # Get the borough for this district
    district_borough = df[df['District'] == district]['Borough'].iloc[0]
    borough_name_clean = district_borough.replace(' ', '_').replace('/', '_')
    borough_data = create_summary_stats(df[df['Borough'] == district_borough], ['Borough'])
    
    # Create summary table
    table_html = df_with_pretty_columns(district_data[DISPLAY_COLS]).to_html(
        index=False,
        table_id='summary-table',
        classes='table table-striped',
        formatters={
            df_with_pretty_columns(district_data[DISPLAY_COLS]).columns[i]: format_pct if 'Pct' in col else format_int
            for i, col in enumerate(DISPLAY_COLS)
        }
    )
    
    # Create bar chart
    bar_chart_file = os.path.join(district_dir, f'{int(district)}_bar_chart.html')
    create_bar_chart(
        district_data,
        f'Jobs by Classification and Type - District {int(district)}',
        bar_chart_file,
        f"district_{int(district)}_bar_chart"
    )
    
    # Create pie charts
    pie_charts_html = create_pie_charts_for_data(district_data, f"District_{int(district)}", district_dir)
    
    # Generate school reports and create summary table
    df_district = df[df['District'] == district]
    summary_by_school = create_summary_stats(df_district, ['Location'])
    summary_by_school = summary_by_school.groupby('Location', as_index=False).agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    
    # Calculate percentages for schools
    summary_by_school['Vacancy_Fill_Pct'] = (summary_by_school['Vacancy_Filled'] / summary_by_school['Total_Vacancy'] * 100).fillna(0).round(1)
    summary_by_school['Absence_Fill_Pct'] = (summary_by_school['Absence_Filled'] / summary_by_school['Total_Absence'] * 100).fillna(0).round(1)
    summary_by_school['Overall_Fill_Pct'] = ((summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']) / summary_by_school['Total'] * 100).fillna(0).round(1)
    
    # Generate school reports and links
    district_schools = df[df['District'] == district]['Location'].unique()
    school_links = ""
    school_reports = []
    
    for location in sorted(district_schools):
        location_clean = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', str(location)).strip()
        if len(location_clean) > 200:
            location_clean = location_clean[:200]
        
        school_df = df[(df['District'] == district) & (df['Location'] == location)]
        school_summary = create_summary_stats(school_df, ['District', 'Location'])
        
        if len(school_summary) > 0:
            school_report = create_school_report(
                district, location, location_clean, school_summary, 
                df, summary_stats, output_dir, date_range_info
            )
            school_reports.append(school_report)
            
            total_jobs = int(school_summary['Total'].sum())
            school_links += f'<li><a href="Schools/School_{location_clean}/{location_clean}_report.html">{location}</a> - {total_jobs} total jobs</li>\n'
    
    # Create school summary table HTML
    summary_by_school_html = df_with_pretty_columns(summary_by_school.rename(columns={'Location': 'School'})).to_html(
        index=False,
        classes='table',
        formatters={
            'School': str,
            'Vacancy Filled': format_int, 'Vacancy Unfilled': format_int, 'Total Vacancy': format_int,
            'Vacancy Fill %': format_pct, 'Absence Filled': format_int, 'Absence Unfilled': format_int,
            'Total Absence': format_int, 'Absence Fill %': format_pct, 'Total': format_int, 'Overall Fill %': format_pct
        }
    )
    
    # Get comparison data
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
    
    # Create comparison cards
    comparison_cards = []
    
    # Citywide card
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%", 
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Number of Districts": f"{len(df['District'].unique())}",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Number of Schools": f"{len(df[df['Borough'] == district_borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"{district_borough} Statistics", borough_stats, "borough"))
    
    # District card
    district_stats = {
        "Total Jobs": f"{district_totals['Total']:,}",
        "Overall Fill Rate": f"{district_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{district_rates[1]:.1f}%",
        "Absence Fill Rate": f"{district_rates[2]:.1f}%",
        "Number of Schools": f"{len(df[df['District'] == district]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"This District ({int(district)})", district_stats, "district"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # Build content
    content = f"""
        {get_header_html("../../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"District: {int(district)}", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([("../index.html", "← Back to Overall Summary")])}
            
            <div class="section">
                <h3>Summary Statistics</h3>
                <div class="table-responsive">{table_html}</div>
            </div>

            <div class="section">
                <h3>Summary by School</h3>
                <div class="table-responsive">{summary_by_school_html}</div>
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
                <h3>Comparison: {district_borough} vs. Citywide</h3>
                {comparison_html}
            </div>
            
            <div class="section">
                <h3>Individual School Reports</h3>
                <div class="district-links"><ul>{school_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer()}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - District {int(district)}", "../../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(district_dir, f'{int(district)}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file, school_reports
