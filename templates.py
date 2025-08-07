"""
HTML Templates and CSS Styles for NYC            .he            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1800px;
                margin: 0 auto;
                padding: 0 20px;
            }tent {
                display: flex;
                .content {
                max-width: 1800px;
                margin: 0 auto;
                padding: 20px;
            }   .content {
                max-width: 1750px;
                margin: 0 auto;
                padding: 20px;
            }           justify-content: space-between;
                align-items: center;
                max-width: 1750px;
                margin: 0 auto;
                padding: 0 20px;
            }orts
"""

import time
import pandas as pd

def get_base_css():
    """Return the base CSS styles used across all reports"""
    return """
            :root {
                --primary-color: #2E86AB;
                --secondary-color: #A23B72;
                --success-color: #2ca02c;
                --warning-color: #ff7f0e;
                --danger-color: #d62728;
                --light-bg: #f5f5f5;
                --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
                --hover-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 0; 
                background-color: #f5f5f5;
            }

            .header { 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 20px; 
                margin: 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1600px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .header-text {
                flex: 1;
                text-align: left;
                margin-right: 30px;
            }

            .header-text h1 {
                margin: 0;
                font-size: 2.2em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                line-height: 1.2;
            }

            .header-text h2 {
                margin: 8px 0;
                font-size: 1.2em;
                font-weight: 600;
                opacity: 0.9;
                line-height: 1.3;
            }

            .header-text .date-info {
                margin: 8px 0 0 0;
                font-size: 1.0em;
                opacity: 0.8;
            }

            .header-text p {
                font-size: 1.0em;
                opacity: 0.8;
                margin: 8px 0 0 0;
            }

            .header-logo {
                flex-shrink: 0;
                display: flex;
                align-items: center;
            }

            .logo {
                height: 80px;
                width: auto;
                filter: brightness(1.1);
                margin-left: 20px;
            }

            .content {
                max-width: 1550px;
                margin: 0 auto;
                padding: 20px;
            }

            .section { 
                background: white;
                margin: 20px 0; 
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-width: 1520px;
                margin-left: auto;
                margin-right: auto;
            }

            .section h2, .section h3 { 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                margin-top: 0;
                font-weight: 700;
                font-size: 1.8em;
            }

            .section h3 {
                font-size: 1.5em;
                font-weight: 600;
            }

            .navigation { 
                background: #e3f2fd; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 5px solid var(--primary-color);
            }

            .navigation a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                display: inline-block;
                margin: 5px;
            }

            .navigation a:hover {
                background: var(--primary-color);
                color: white;
            }

            .summary-box { 
                background: #e3f2fd; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 5px solid #1976d2;
            }

            .summary-box h3 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.4em;
            }

            .summary-box ul {
                list-style: none;
                padding: 0;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }

            .summary-box li {
                padding: 15px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.7);
                font-size: 1.1em;
                text-align: center;
            }

            .summary-box li:hover {
                background: rgba(255, 255, 255, 0.9);
            }

            .summary-box strong {
                color: var(--primary-color);
                display: block;
                font-size: 0.9em;
                margin-bottom: 5px;
            }

            .table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 25px 0; 
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .table-responsive {
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }

            .table th, .table td { 
                padding: 15px 12px; 
                text-align: center; 
                border-bottom: 1px solid #e0e0e0;
            }

            .table th { 
                background: var(--primary-color);
                color: white;
                font-weight: 600;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .table tbody tr {
                transition: all 0.3s ease;
            }

            .table tbody tr:nth-child(even) {
                background-color: #f8f9fa;
            }

            .table tbody tr:hover {
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .pie-container { 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin: 25px 0;
            }

            .comparison-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }

            .comparison-card {
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }

            .comparison-card:hover {
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }

            .comparison-card.citywide {
                background: linear-gradient(135deg, #e8f4f8, #d6eaf8);
            }

            .comparison-card.borough {
                background: linear-gradient(135deg, #f0f8e8, #e8f8d6);
            }

            .comparison-card.district {
                background: linear-gradient(135deg, #f0f8e8, #e8f8d6);
            }

            .comparison-card.school {
                background: linear-gradient(135deg, #fff8e1, #ffe0b2);
            }

            .comparison-card h4 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }

            .comparison-card ul {
                list-style: none;
                padding: 0;
            }

            .comparison-card li {
                padding: 8px 0;
                border-bottom: 1px solid rgba(46, 134, 171, 0.1);
                font-size: 1.1em;
            }

            .comparison-card li:last-child {
                border-bottom: none;
            }

            .links-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }

            .links-section {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .links-section h4 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }

            .links-section ul {
                list-style: none;
                padding: 0;
            }

            .links-section li {
                padding: 8px 0;
                break-inside: avoid;
            }

            .links-section a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }

            .links-section a:hover {
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }

            .district-links {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .district-links ul {
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 30px;
            }

            .district-links li {
                padding: 8px 0;
                break-inside: avoid;
            }

            .district-links a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }

            .district-links a:hover {
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }

            .chart-container { 
                margin: 25px 0; 
                text-align: center;
                background: white;
                padding: 20px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                overflow: hidden;
                max-width: 100%;
            }

            .chart-container iframe {
                max-width: 100%;
                border: none;
                display: block;
                margin: 0 auto;
            }

            .footer {
                background-color: var(--primary-color);
                color: white;
                text-align: center;
                padding: 30px 20px;
                margin-top: 40px;
                font-size: 1.1em;
            }

            .footer p {
                margin: 8px 0;
            }

            .footer a {
                color: #e3f2fd;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }

            .footer a:hover {
                text-decoration: underline;
                color: #FFD700;
            }

            iframe {
                border: none;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
            }

            iframe:hover {
                box-shadow: var(--hover-shadow);
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                body {
                    padding: 10px;
                }

                .header {
                    padding: 20px;
                }

                .header h1 {
                    font-size: 1.8em;
                }

                .content {
                    padding: 15px;
                }

                .section {
                    padding: 20px;
                    margin: 15px 0;
                }

                .pie-container {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }

                .comparison-grid {
                    grid-template-columns: 1fr;
                }

                .summary-box ul {
                    grid-template-columns: 1fr;
                }

                .links-grid {
                    grid-template-columns: 1fr;
                }

                .district-links ul {
                    columns: 1;
                }

                iframe {
                    width: 100% !important;
                    height: 450px !important;
                    max-width: 100%;
                }
            }

            /* Print Styles */
            /* Tabbed Tables */
            .tabbed-container {
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
            }

            .tab-buttons {
                display: flex;
                background: var(--light-bg);
                border-bottom: 2px solid #ddd;
            }

            .tab-button {
                background: none;
                border: none;
                padding: 15px 25px;
                cursor: pointer;
                font-size: 1.1em;
                font-weight: 600;
                color: #666;
                transition: all 0.3s ease;
                border-bottom: 3px solid transparent;
                flex: 1;
                text-align: center;
            }

            .tab-button:hover {
                background: rgba(46, 134, 171, 0.1);
                color: var(--primary-color);
            }

            .tab-button.active {
                background: white;
                color: var(--primary-color);
                border-bottom-color: var(--primary-color);
            }

            .tab-content {
                display: none;
                padding: 0;
            }

            .tab-content.active {
                display: block;
            }

            .tab-content .table-responsive {
                margin: 0;
                border-radius: 0;
            }

            .tab-content table {
                margin: 0;
                border-radius: 0;
            }

            .tab-content table thead th {
                background: var(--light-bg);
                font-weight: 600;
                color: var(--primary-color);
            }

            /* Print styles for tabs */
            @media print {
                .tab-buttons {
                    display: none;
                }
                
                .tab-content {
                    display: block !important;
                    page-break-inside: avoid;
                    margin-bottom: 20px;
                }
                
                .tab-content:before {
                    content: attr(data-tab-title);
                    display: block;
                    font-weight: bold;
                    font-size: 1.2em;
                    color: var(--primary-color);
                    margin-bottom: 10px;
                    border-bottom: 2px solid var(--primary-color);
                    padding-bottom: 5px;
                }
            }

            @media print {
                body {
                    background: white;
                }

                .section {
                    break-inside: avoid;
                    page-break-inside: avoid;
                    box-shadow: none;
                    border: 1px solid #ddd;
                }

                .header {
                    background: white !important;
                    color: black !important;
                    border: 2px solid var(--primary-color);
                }

                iframe {
                    display: none;
                }
            }
            
            /* Map Styles */
            .map-summary {
                margin: 20px 0;
            }

            .summary-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .stat-card {
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
                border: 1px solid rgba(46, 134, 171, 0.2);
            }

            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: var(--hover-shadow);
            }

            .stat-card h4 {
                color: var(--primary-color);
                margin-bottom: 10px;
                font-size: 1.1em;
                font-weight: 600;
            }

            .stat-value {
                font-size: 1.8em;
                font-weight: 700;
                color: var(--secondary-color);
                margin-top: 5px;
            }

            .map-notes {
                background: var(--light-bg);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid var(--primary-color);
                margin-top: 15px;
            }

            @media (max-width: 768px) {
                .summary-stats-grid {
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                }

                .stat-card {
                    padding: 15px;
                }

                .stat-value {
                    font-size: 1.5em;
                }
            }
    """

def get_base_javascript():
    """Return the base JavaScript used across all reports"""
    return """
        $(document).ready(function() {
            $('.table').DataTable({
                paging: false, 
                searching: false, 
                info: false, 
                order: [],
                responsive: true
            });
            
            // Tab functionality
            $('.tab-button').click(function() {
                var targetTab = $(this).data('tab');
                var container = $(this).closest('.tabbed-container');
                
                // Remove active class from all buttons and content in this container
                container.find('.tab-button').removeClass('active');
                container.find('.tab-content').removeClass('active');
                
                // Add active class to clicked button and corresponding content
                $(this).addClass('active');
                container.find('.tab-content[data-tab="' + targetTab + '"]').addClass('active');
            });
            
            // Activate first tab by default
            $('.tabbed-container').each(function() {
                $(this).find('.tab-button:first').addClass('active');
                $(this).find('.tab-content:first').addClass('active');
            });
        });
    """

def get_html_template(title, logo_path, content, extra_css="", extra_js=""):
    """
    Generate a complete HTML template for reports
    
    Args:
        title: Page title
        logo_path: Relative path to logo file
        content: HTML content to insert in the body
        extra_css: Additional CSS styles
        extra_js: Additional JavaScript
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
        <style>
            {get_base_css()}
            {extra_css}
        </style>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            {get_base_javascript()}
            {extra_js}
        </script>
    </head>
    <body>
        {content}
    </body>
    </html>
    """

def get_header_html(logo_path, title, subtitle="", date_range_info=""):
    """Generate header HTML section"""
    return f"""
    <div class="header">
        <div class="header-content">
            <div class="header-text">
                <h1>{title}</h1>
                {f"<h2>{subtitle}</h2>" if subtitle else ""}
                {f'<div class="date-info">{date_range_info}</div>' if date_range_info else ""}
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            <div class="header-logo">
                <img src="{logo_path}" alt="NYC Public Schools" class="logo">
            </div>
        </div>
    </div>
    """

def get_professional_footer(contact_emails=None):
    """Return the professional footer HTML with NYC Public Schools branding"""
    contact_info = ""
    if contact_emails:
        contact_links = " | ".join([f'<a href="mailto:{email}" style="color: #e3f2fd;">{email}</a>' for email in contact_emails])
        contact_info = f"<p>Contact: {contact_links}</p>"
    else:
        contact_info = f"<p>Contact: <a href=\"mailto:SubCentral@schools.nyc.gov\" style=\"color: #e3f2fd;\">SubCentral@schools.nyc.gov</a></p>"
    
    return f"""
    <div class="footer">
        <p>Property of the New York City Department of Education</p>
        {contact_info}
        <p>HR School Support Analysis Team | {pd.Timestamp.now().year}</p>
    </div>
    """

def get_navigation_html(back_links):
    """
    Generate navigation HTML
    
    Args:
        back_links: List of tuples (url, text) for navigation links
    """
    links = " | ".join([f'<a href="{url}">{text}</a>' for url, text in back_links])
    return f"""
    <div class="navigation">
        {links}
    </div>
    """

def get_comparison_card_html(title, stats, card_class=""):
    """
    Generate a comparison card HTML
    
    Args:
        title: Card title
        stats: Dictionary of statistics to display
        card_class: CSS class for styling
    """
    stats_html = ""
    for label, value in stats.items():
        stats_html += f'<li><strong>{label}:</strong> {value}</li>'
    
    return f"""
    <div class="comparison-card {card_class}">
        <h4>{title}</h4>
        <ul>
            {stats_html}
        </ul>
    </div>
    """

def create_tabbed_summary_tables(data, formatters):
    """
    Create tabbed summary tables separating Vacancy, Absence, and Combined data
    
    Args:
        data: DataFrame with summary statistics
        formatters: Dictionary of column formatters
    
    Returns:
        str: HTML for tabbed table interface
    """
    from data_processing import df_with_pretty_columns, format_pct, format_int
    
    # Define columns for each tab
    if 'Classification' in data.columns:
        base_cols = ['Classification']
    elif 'School' in data.columns:
        base_cols = ['School']
    elif 'Borough' in data.columns:
        base_cols = ['Borough']
    elif 'District' in data.columns:
        base_cols = ['District']
    else:
        base_cols = []
    
    # Combine vacancy and absence columns into one detailed tab
    details_cols = base_cols + [
        'Vacancy Filled', 'Vacancy Unfilled', 'Total Vacancy', 'Vacancy Fill %',
        'Absence Filled', 'Absence Unfilled', 'Total Absence', 'Absence Fill %'
    ]
    combined_cols = base_cols + ['Total Filled', 'Total Unfilled', 'Total', 'Overall Fill %']
    
    # Create pretty column names
    pretty_data = df_with_pretty_columns(data)
    
    # Filter columns that exist in the data
    details_cols = [col for col in details_cols if col in pretty_data.columns]
    combined_cols = [col for col in combined_cols if col in pretty_data.columns]
    
    # Create tables for each tab
    details_table = pretty_data[details_cols].to_html(
        index=False,
        classes='table table-striped',
        formatters={col: formatters.get(col, str) for col in details_cols}
    ) if details_cols else "<p>No details data available</p>"
    
    combined_table = pretty_data[combined_cols].to_html(
        index=False,
        classes='table table-striped',
        formatters={col: formatters.get(col, str) for col in combined_cols}
    ) if combined_cols else "<p>No combined data available</p>"
    
    return f"""
    <div class="tabbed-container">
        <div class="tab-buttons">
            <button class="tab-button" data-tab="combined">Combined Totals</button>
            <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
        </div>
        
        <div class="tab-content" data-tab="combined" data-tab-title="Combined Totals">
            <div class="table-responsive">{combined_table}</div>
        </div>
        
        <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
            <div class="table-responsive">{details_table}</div>
        </div>
    </div>
    """
