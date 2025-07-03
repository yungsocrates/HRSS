"""
HTML Templates and CSS Styles for NYC DOE Reports
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
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }

            .header { 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 40px 20px; 
                position: relative;
                overflow: hidden;
            }

            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="80" r="2.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                opacity: 0.3;
            }
            
            .header-content {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }
            
            .header-text {
                text-align: center;
                flex: 1;
                padding-right: 5%;
            }

            .header h1 {
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }

            .header h2 {
                font-size: 1.5em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
                margin-bottom: 10px;
            }

            .header p {
                font-size: 1.1em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
                margin: 5px 0;
            }

            .header-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
                position: relative;
                z-index: 1;
            }

            .header-logo {
                height: 120px;
                width: auto;
                filter: brightness(1.1);
                margin-right: 5%;
            }

            .header-text {
                text-align: left;
                flex: 1;
            }

            .header-text h1 {
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 10px;
                margin-top: 0;
                text-align: center;
            }

            .header-text h2 {
                font-size: 1.5em;
                font-weight: 600;
                opacity: 0.9;
                margin-bottom: 10px;
                margin-top: 0;
                text-align: center;
            }

            .header-text p {
                font-size: 1.1em;
                opacity: 0.9;
                margin: 5px 0;
                text-align: center;
            }

            .content {
                padding: 30px;
            }

            .section { 
                background: white;
                margin: 30px 0; 
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }

            .section:hover {
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }

            .section h2, .section h3 { 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.8em;
            }

            .section h3 {
                font-size: 1.5em;
            }

            .navigation { 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 20px; 
                border-radius: 15px; 
                margin: 20px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
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
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(46, 134, 171, 0.3);
            }

            .summary-box { 
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 25px; 
                border-radius: 15px; 
                margin: 25px 0;
                border-left: 5px solid var(--primary-color);
                box-shadow: var(--card-shadow);
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
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }

            .summary-box li:hover {
                transform: translateY(-2px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.15);
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
                padding: 30px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .footer { 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                text-align: center;
                padding: 30px;
                margin-top: 40px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }

            .footer a { 
                color: #FFD700; 
                text-decoration: none; 
                font-weight: 600;
                transition: all 0.3s ease;
            }

            .footer a:hover { 
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                transform: scale(1.05);
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
                    height: 400px !important;
                }
            }

            /* Print Styles */
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
        <div class="container">
            {content}
        </div>
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
                {f"<p>{date_range_info}</p>" if date_range_info else ""}
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            <img src="{logo_path}" alt="NYC Public Schools" class="header-logo">
        </div>
    </div>
    """

def get_professional_footer():
    """Return the professional footer HTML"""
    return f"""
    <div class="footer">
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">Created by HR School Support</div>
        <div style="margin-bottom:6px;">For internal use only.</div>
        <div style="margin-bottom:6px;">For inquiries, please contact <a href="mailto:SubCentral@schools.nyc.gov">SubCentral@schools.nyc.gov</a>.</div>
        <div style="font-size:13px; color:#e0e0e0;">&copy; {pd.Timestamp.now().year} Property of the New York City Department of Education</div>
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
