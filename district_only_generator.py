"""
NYC DOE Paraprofessional Jobs - District-Only Report Generator

This module generates individual district and school reports as HTML files
using the EXACT same functions as para_fillrate_modular.py but only for districts and schools.
"""

import os
import time

# Import existing modules - use everything that already works
from data_processing import (
    load_and_process_data, get_data_date_range, create_summary_stats, 
    copy_logo_to_output, create_matching_analysis, df_with_pretty_columns,
    DISPLAY_COLS, format_pct, format_int, get_totals_from_data, calculate_fill_rates
)
from chart_utils import create_bar_chart, create_pie_charts_for_data, sanitize_filename
from templates import (
    get_html_template, get_header_html, get_professional_footer, 
    create_tabbed_summary_tables, get_comparison_card_html
)
from report_generators import create_school_report

def create_district_report_no_nav(district, district_data, df, output_dir, summary_stats, date_range_info, matching_stats=None):
    """
    EXACT copy of create_district_report from report_generators.py but WITHOUT navigation links
    """
    # Create subfolder for District
    district_dir = os.path.join(output_dir, f"District_{int(district)}")
    os.makedirs(district_dir, exist_ok=True)
    
    # Copy logo to district folder
    copy_logo_to_output(district_dir)
    
    # Get the borough for this district with error handling
    district_schools = df[df['District'] == district]
    if district_schools.empty:
        print(f"Warning: No schools found for district {district}")
        return None, []
    
    district_borough = district_schools['Borough'].iloc[0]
    borough_name_clean = district_borough.replace(' ', '_').replace('/', '_')
    borough_data = create_summary_stats(df[df['Borough'] == district_borough], ['Borough'])
    
    # Create tabbed summary tables
    formatters = {
        df_with_pretty_columns(district_data[DISPLAY_COLS]).columns[i]: format_pct if 'Pct' in col else format_int
        for i, col in enumerate(DISPLAY_COLS)
    }
    table_html = create_tabbed_summary_tables(district_data[DISPLAY_COLS], formatters)
    
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
    
    # Calculate combined totals for schools
    summary_by_school['Total_Filled'] = summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']
    summary_by_school['Total_Unfilled'] = summary_by_school['Vacancy_Unfilled'] + summary_by_school['Absence_Unfilled']
    
    summary_by_school['Overall_Fill_Pct'] = ((summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']) / summary_by_school['Total'] * 100).fillna(0).round(1)
    
    # Generate school reports and links
    district_schools_list = df[df['District'] == district]['Location'].unique()
    school_links = ""
    school_reports = []
    
    for location in sorted(district_schools_list):
        # More robust sanitization for Windows filenames
        location_clean = sanitize_filename(location)
        
        school_df = df[(df['District'] == district) & (df['Location'] == location)]
        school_summary = create_summary_stats(school_df, ['District', 'Location'])
        
        if len(school_summary) > 0:
            school_report = create_school_report(
                district, location, location_clean, school_summary, 
                df, summary_stats, output_dir, date_range_info
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
    summary_by_school_html = create_tabbed_summary_tables(
        summary_by_school.rename(columns={'Location': 'School'}), 
        school_formatters
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
    
    # Create comparison cards - EXACT same as original
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
    
    # Build content - EXACT same structure as original but WITHOUT navigation links
    content = f"""
        {get_header_html("Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"District: {int(district)}", 
                        date_range_info)}
        
        <div class="content">
            <div class="section">
                <h3>Summary Statistics</h3>
                {table_html}
            </div>

            <div class="section">
                <h3>Summary by School</h3>
                {summary_by_school_html}
            </div>"""
    
    # Add matching statistics section if available - EXACT same as original
    if matching_stats is not None and not matching_stats.empty:
        # Filter matching stats for this district
        district_matching = matching_stats[matching_stats['Location'].isin(
            df[df['District'] == district]['Location'].unique()
        )]
        
        if len(district_matching) > 0:
            # Create matching stats table with enhanced styling to match tabbed tables
            matching_table_html = df_with_pretty_columns(district_matching).to_html(
                index=False,
                classes='table table-striped',
                formatters={
                    'SubCentral Job Days': format_int,
                    'Payroll Job Days': format_int,
                    'Matched Jobs': format_int,
                    'Match Percentage': format_pct
                }
            )
            
            content += f"""
            <div class="section">
                <h3>SubCentral vs Payroll Analysis</h3>
                <div class="tabbed-container">
                    <div class="tab-content active" data-tab="matching" data-tab-title="SubCentral vs Payroll Analysis">
                        <div class="table-responsive">{matching_table_html}</div>
                    </div>
                </div>
                <p style="font-style: italic; color: #666; margin-top: 10px;">
                    This analysis matches individual jobs using <strong>Location + EIS ID + Date</strong> between SubCentral and payroll systems. 
                    Match Percentage shows what percentage of payroll records have corresponding SubCentral records.
                </p>
            </div>"""
    
    # Continue with charts and sections - EXACT same as original
    content += f"""
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
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML - EXACT same as original (but without "../" path prefix)
    html_content = get_html_template(f"Jobs Report - District {int(district)}", "Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(district_dir, f'{int(district)}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file, school_reports

def main_district_only():
    """
    Main function to generate individual district and school reports only
    Uses the EXACT same functions as para_fillrate_modular.py
    """
    # Configuration - same as main script
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
    
    # Separate output directory (untracked by git)
    output_directory = 'district_individual_reports'
    
    start_time = time.time()
    print("Starting individual district/school report generation...")
    print(f"Output directory: {output_directory}")
    print("Note: This directory will not be tracked by git")
    
    try:
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Create .gitignore file to ensure this directory is not tracked
        gitignore_path = os.path.join(output_directory, '.gitignore')
        with open(gitignore_path, 'w') as f:
            f.write("# This directory contains individual reports for dissemination\n")
            f.write("# Not tracked in git\n")
            f.write("*\n")
            f.write("!.gitignore\n")
        
        # Also add to main .gitignore if it exists
        main_gitignore = '.gitignore'
        if os.path.exists(main_gitignore):
            with open(main_gitignore, 'r') as f:
                content = f.read()
            if 'district_individual_reports/' not in content:
                with open(main_gitignore, 'a') as f:
                    f.write(f"\n# Individual district reports directory\n")
                    f.write(f"district_individual_reports/\n")
        else:
            with open(main_gitignore, 'w') as f:
                f.write(f"# Individual district reports directory\n")
                f.write(f"district_individual_reports/\n")
        
        # Copy logo for deployment
        copy_logo_to_output(output_directory)
        
        # Load and process data - EXACT same as main script
        print("Loading and processing data from multiple sources...")
        df, srepp_df = load_and_process_data(csv_files)
        
        # Handle SREPP data if present
        if not srepp_df.empty:
            print(f"SREPP payroll data loaded: {len(srepp_df)} records")
        else:
            print("No SREPP payroll data found")
            
        # Show main data info
        if not df.empty:
            print(f"Main SubCentral data loaded: {len(df)} records")
        else:
            print("No main SubCentral data found")
            
        # Create matching analysis between SubCentral and SREPP data
        print("Creating matching analysis between SubCentral and payroll data...")
        matching_stats = create_matching_analysis(df, srepp_df)
        if not matching_stats.empty:
            print(f"Matching analysis completed for {len(matching_stats)} locations")
        else:
            print("No matching analysis data available")
        
        # Continue with main data processing
        if df.empty:
            print("Warning: No main data loaded. Check your CSV files.")
            return
        
        # Get date range information - EXACT same as main script
        date_range_info = get_data_date_range(df)
        print(f"Data range: {date_range_info}")
        
        # Create summary statistics - EXACT same as main script
        summary_stats = create_summary_stats(df, ['District'])
        if 'Type_Fill_Status' in summary_stats.columns:
            summary_stats = summary_stats.drop(columns=['Type_Fill_Status'])

        # Convert to int to avoid float display issues - EXACT same as main script
        int_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled', 
                   'Total_Vacancy', 'Total_Absence', 'Total']
        for col in int_cols:
            summary_stats[col] = summary_stats[col].astype(int)

        # Create reports for each District - EXACT same as main script
        districts = sorted(df['District'].unique())
        summary_districts = sorted(summary_stats['District'].unique())
        print(f"Districts in main data: {districts}")
        print(f"Districts in summary_stats: {summary_districts}")
        print(f"Creating reports for {len(districts)} districts...")
        report_files = []
        all_school_reports = []
        
        for district in districts:
            district_data = summary_stats[summary_stats['District'] == district].copy()
            if len(district_data) > 0:
                # Check if district exists in main dataframe
                district_schools = df[df['District'] == district]
                if district_schools.empty:
                    print(f"Warning: District {int(district)} has no schools in main data, skipping...")
                    continue
                    
                # Use the custom function without navigation links
                result = create_district_report_no_nav(
                    district, district_data, df, output_directory, summary_stats, date_range_info, matching_stats
                )
                if result is not None:
                    report_file, school_reports = result
                    report_files.append(report_file)
                    all_school_reports.extend(school_reports)
                    print(f"District {int(district)} report finished.")
                else:
                    print(f"District {int(district)} report skipped due to missing data.")
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"INDIVIDUAL DISTRICT/SCHOOL REPORT GENERATION COMPLETED")
        print(f"{'='*70}")
        print(f"Output Directory: {output_directory}")
        print(f"Individual District reports: {len(report_files)} files created")
        print(f"Individual School reports: {len(all_school_reports)} files created")
        print(f"Total Time: {elapsed:.2f} seconds")
        print(f"\nDirectory Structure:")
        print(f"  {output_directory}/")
        print(f"  ├── District_1/")
        print(f"  │   ├── 1_report.html (EXACT same as main reports)")
        print(f"  │   ├── 1_bar_chart.html")
        print(f"  │   ├── [pie charts...]")
        print(f"  │   └── Schools/")
        print(f"  │       ├── School_[Name1]/")
        print(f"  │       │   └── [Name1]_report.html")
        print(f"  │       └── School_[Name2]/")
        print(f"  │           └── [Name2]_report.html")
        print(f"  ├── District_2/")
        print(f"  │   └── [similar structure...]")
        print(f"  └── [etc...]")
        print(f"\nNote: These reports are IDENTICAL to the main reports, just organized for individual dissemination.")
        print(f"Note: This directory is excluded from git tracking.")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find one or more CSV files: {csv_files}")
        print("Please make sure all files exist in the specified paths.")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_district_only()
