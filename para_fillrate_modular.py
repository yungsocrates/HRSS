"""
NYC DOE Paraprofessional Jobs Dashboard - Main Script (Modularized)

This is the main entry point for generating the NYC DOE reports dashboard.
The heavy lifting is now done by imported modules for better maintainability.
"""

import os
import time

# Import our custom modules
from data_processing import (
    load_and_process_data, get_data_date_range, create_summary_stats, 
    create_borough_summary_stats, copy_logo_to_output, df_with_pretty_columns,
    DISPLAY_COLS, format_pct, format_int
)
from report_generators import create_district_report
from chart_utils import create_overall_bar_chart
from templates import get_html_template, get_header_html, get_professional_footer

def create_borough_report(borough, borough_data, df, output_dir, summary_stats, date_range_info):
    """
    Create a comprehensive report for a single borough
    """
    import pandas as pd
    from chart_utils import create_bar_chart, create_pie_charts_for_data
    from data_processing import get_totals_from_data, calculate_fill_rates
    from templates import get_comparison_card_html, get_navigation_html
    
    # Create subfolder for borough
    borough_clean = borough.replace(' ', '_').replace('/', '_')
    borough_dir = os.path.join(output_dir, f"Borough_{borough_clean}")
    os.makedirs(borough_dir, exist_ok=True)
    
    # Create summary table
    table_html = df_with_pretty_columns(borough_data[DISPLAY_COLS]).to_html(
        index=False,
        table_id='summary-table',
        classes='table table-striped',
        formatters={
            df_with_pretty_columns(borough_data[DISPLAY_COLS]).columns[i]: format_pct if 'Pct' in col else format_int
            for i, col in enumerate(DISPLAY_COLS)
        }
    )
    
    # Create bar chart
    bar_chart_file = os.path.join(borough_dir, f'{borough_clean}_bar_chart.html')
    create_bar_chart(
        borough_data,
        f'Jobs by Classification and Type - {borough}',
        bar_chart_file,
        f"borough_{borough_clean}_bar_chart"
    )
    
    # Create pie charts
    pie_charts_html = create_pie_charts_for_data(borough_data, borough_clean, borough_dir)
    
    # Create summary by district table
    df_borough = df[df['Borough'] == borough]
    summary_by_district = create_summary_stats(df_borough, ['District'])
    summary_by_district = summary_by_district.groupby('District', as_index=False).agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    
    # Calculate percentages
    summary_by_district['Vacancy_Fill_Pct'] = (summary_by_district['Vacancy_Filled'] / summary_by_district['Total_Vacancy'] * 100).fillna(0).round(1)
    summary_by_district['Absence_Fill_Pct'] = (summary_by_district['Absence_Filled'] / summary_by_district['Total_Absence'] * 100).fillna(0).round(1)
    summary_by_district['Overall_Fill_Pct'] = ((summary_by_district['Vacancy_Filled'] + summary_by_district['Absence_Filled']) / summary_by_district['Total'] * 100).fillna(0).round(1)
    
    summary_by_district_html = df_with_pretty_columns(summary_by_district).to_html(
        index=False,
        classes='table',
        formatters={
            'District': lambda x: f"D{int(x)}" if pd.notna(x) else x,
            'Vacancy Filled': format_int, 'Vacancy Unfilled': format_int, 'Total Vacancy': format_int,
            'Vacancy Fill %': format_pct, 'Absence Filled': format_int, 'Absence Unfilled': format_int,
            'Total Absence': format_int, 'Absence Fill %': format_pct, 'Total': format_int, 'Overall Fill %': format_pct
        }
    )
    
    # Get districts in this borough and create links
    borough_districts = sorted(df[df['Borough'] == borough]['District'].unique())
    district_links = ""
    for district in borough_districts:
        total_jobs = summary_by_district[summary_by_district['District'] == district]['Total'].iloc[0]
        district_links += f'<li><a href="../District_{int(district)}/{int(district)}_report.html">District {int(district)} Report</a> - {int(total_jobs)} total jobs</li>\n'
    
    # Get comparison data
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    
    borough_totals = get_totals_from_data(borough_data)
    
    # Calculate fill rates
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    
    # Create comparison cards
    comparison_cards = []
    
    # Citywide card
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%",
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Number of Schools": f"{len(df[df['Borough'] == borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"This Borough", borough_stats, "borough"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # Build content
    content = f"""
        {get_header_html("../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"Borough: {borough}", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([("../index.html", "← Back to Overall Summary")])}
            
            <div class="section">
                <h3>Summary Statistics</h3>
                <div class="table-responsive">{table_html}</div>
            </div>

            <div class="section">
                <h3>Summary by District</h3>
                <div class="table-responsive">{summary_by_district_html}</div>
            </div>

            <div class="section">
                <h3>Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="{borough_clean}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h3>Breakdown by Classification</h3>
                <div class="pie-container">{pie_charts_html}</div>
            </div>

            <div class="section">
                <h3>Comparison: {borough} vs. Citywide</h3>
                {comparison_html}
            </div>
            
            <div class="section">
                <h3>Individual District Reports</h3>
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

def create_overall_summary(df, summary_stats, borough_stats, output_dir, date_range_info):
    """
    Create an overall summary report across all districts
    """
    import pandas as pd
    import numpy as np
    
    # Overall statistics by classification
    overall_stats = summary_stats.groupby('Classification').agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    }).reset_index()
    
    # Recalculate percentages
    overall_stats['Vacancy_Fill_Pct'] = np.where(
        overall_stats['Total_Vacancy'] > 0,
        (overall_stats['Vacancy_Filled'] / overall_stats['Total_Vacancy'] * 100).round(1), 0
    )
    overall_stats['Absence_Fill_Pct'] = np.where(
        overall_stats['Total_Absence'] > 0,
        (overall_stats['Absence_Filled'] / overall_stats['Total_Absence'] * 100).round(1), 0
    )
    overall_stats['Overall_Fill_Pct'] = np.where(
        overall_stats['Total'] > 0,
        ((overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']) / overall_stats['Total'] * 100).round(1), 0
    )
    
    # Create overall bar chart
    overall_chart_file = os.path.join(output_dir, 'overall_bar_chart.html')
    create_overall_bar_chart(overall_stats, overall_chart_file)
    
    # Create District summary table
    district_summary = summary_stats.groupby('District').agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    }).reset_index()
    
    # Recalculate percentages for district summary
    district_summary['Vacancy_Fill_Pct'] = np.where(
        district_summary['Total_Vacancy'] > 0,
        (district_summary['Vacancy_Filled'] / district_summary['Total_Vacancy'] * 100).round(1), 0
    )
    district_summary['Absence_Fill_Pct'] = np.where(
        district_summary['Total_Absence'] > 0,
        (district_summary['Absence_Filled'] / district_summary['Total_Absence'] * 100).round(1), 0
    )
    district_summary['Overall_Fill_Pct'] = np.where(
        district_summary['Total'] > 0,
        ((district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']) / district_summary['Total'] * 100).round(1), 0
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
    
    # Create summary box
    summary_box = f"""
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
    """
    
    # Build content
    content = f"""
        {get_header_html("Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Dashboard", 
                        "Citywide Summary Report", 
                        date_range_info)}
        
        <div class="content">
            {summary_box}
            
            <div class="section">
                <h3>Overall Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="overall_bar_chart.html" width="1420" height="520" frameborder="0"></iframe>
                </div>
            </div>
            
            <div class="section">
                <h3>Summary by Classification (All Districts)</h3>
                <div class="table-responsive">
                    {df_with_pretty_columns(overall_stats[DISPLAY_COLS]).to_html(
                        index=False, classes='table',
                        formatters={
                            df_with_pretty_columns(overall_stats[DISPLAY_COLS]).columns[i]: format_pct if 'Pct' in col else format_int
                            for i, col in enumerate(DISPLAY_COLS)
                        }
                    )}
                </div>
            </div>
            
            <div class="section">
                <h3>Summary by District</h3>
                <div class="table-responsive">
                    {district_summary[['District'] + DISPLAY_COLS[1:]].sort_values('District').rename(columns={'District': 'District', **{col: df_with_pretty_columns(pd.DataFrame(columns=DISPLAY_COLS)).columns[i] for i, col in enumerate(DISPLAY_COLS)}}).to_html(
                        index=False, classes='table',
                        formatters={
                            'District': lambda x: f"D{int(x)}" if pd.notna(x) else x,
                            **{
                                df_with_pretty_columns(pd.DataFrame(columns=DISPLAY_COLS)).columns[i]: format_pct if 'Pct' in col else format_int
                                for i, col in enumerate(DISPLAY_COLS)
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
                        <ul>{borough_links}</ul>
                    </div>
                    <div class="links-section">
                        <h4>District Reports</h4>
                        <ul>{district_links}</ul>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <p style="text-align: center; font-style: italic; color: #666; font-size: 1.1em;">
                    Generated from data containing {len(df):,} job records
                </p>
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
    # Configuration
    csv_file_path = 'Fill Rate Data/mayjobs.csv'
    output_directory = 'nycdoe_reports'
    
    start_time = time.time()
    print("Starting report generation...")
    
    try:
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Copy logo for deployment
        copy_logo_to_output(output_directory)
        
        # Load and process data
        print("Loading and processing data...")
        df = load_and_process_data(csv_file_path)
        
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
            summary_stats[col] = summary_stats[col].astype(int)

        # Create borough-level statistics
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
                report_file, school_reports = create_district_report(
                    district, district_data, df, output_directory, summary_stats, date_range_info
                )
                report_files.append(report_file)
                all_school_reports.extend(school_reports)
                print(f"District {int(district)} report finished.")
        
        # Create reports for each borough
        boroughs = sorted(df['Borough'].unique())
        print(f"Creating reports for {len(boroughs)} boroughs...")
        borough_report_files = []

        for borough in boroughs:
            if borough != 'Unknown':  # Skip if no valid borough found
                borough_data = borough_stats[borough_stats['Borough'] == borough].copy()
                if len(borough_data) > 0:
                    report_file = create_borough_report(
                        borough, borough_data, df, output_directory, summary_stats, date_range_info
                    )
                    borough_report_files.append(report_file)
                    print(f"Borough {borough} report finished.")
        
        # Create overall summary
        index_file = create_overall_summary(df, summary_stats, borough_stats, output_directory, date_range_info)
        
        print(f"Reports generated successfully!")
        print(f"Main report: {index_file}")
        print(f"Individual District reports: {len(report_files)} files created")
        print(f"Individual Borough reports: {len(borough_report_files)} files created")
        print(f"Individual School reports: {len(all_school_reports)} files created")
        print(f"Open '{index_file}' in your web browser to view the dashboard")
        
        elapsed = time.time() - start_time
        print(f"Total run time: {elapsed:.2f} seconds")
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_file_path}'")
        print("Please make sure the file exists and update the csv_file_path variable.")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
