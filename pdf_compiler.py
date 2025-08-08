"""
NYC DOE Paraprofessional Jobs - PDF Compiler

This module converts the individual district HTML reports to PDF format
for easier distribution and printing.
"""

import os
import asyncio
from pathlib import Path
import time

def check_playwright_installation():
    """Check if Playwright is installed and browsers are available"""
    try:
        from playwright.async_api import async_playwright
        return True
    except ImportError:
        return False

def install_playwright():
    """Install Playwright and browser dependencies"""
    import subprocess
    import sys
    
    print("Installing Playwright...")
    try:
        # Install playwright package
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        
        # Install browser binaries
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        
        print("✅ Playwright installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright: {e}")
        return False

async def convert_html_to_pdf(html_file_path, pdf_file_path, page_options=None):
    """
    Convert a single HTML file to PDF using Playwright
    
    Args:
        html_file_path: Path to HTML file
        pdf_file_path: Output PDF file path
        page_options: Dictionary of PDF generation options
    """
    from playwright.async_api import async_playwright
    
    if page_options is None:
        page_options = {
            'format': 'A4',
            'margin': {
                'top': '0.5in',
                'right': '0.5in', 
                'bottom': '0.5in',
                'left': '0.5in'
            },
            'print_background': True,  # Include background colors/images
            'prefer_css_page_size': True
        }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load the HTML file
        html_file_url = f"file:///{html_file_path.replace(chr(92), '/')}"  # Convert Windows paths
        await page.goto(html_file_url, wait_until='networkidle')
        
        # Wait a bit more for charts to fully render
        await page.wait_for_timeout(2000)
        
        # Generate PDF
        await page.pdf(path=pdf_file_path, **page_options)
        
        await browser.close()

async def compile_district_reports_to_pdf(reports_directory, output_directory=None, districts=None):
    """
    Compile district reports from HTML to PDF
    
    Args:
        reports_directory: Directory containing district HTML reports
        output_directory: Where to save PDFs (default: reports_directory/PDFs)
        districts: List of specific districts to convert (default: all)
    """
    if output_directory is None:
        output_directory = os.path.join(reports_directory, "PDFs")
    
    os.makedirs(output_directory, exist_ok=True)
    
    print(f"Compiling district reports to PDF...")
    print(f"Source: {reports_directory}")
    print(f"Output: {output_directory}")
    
    # Find all district directories
    district_dirs = []
    if os.path.exists(reports_directory):
        for item in os.listdir(reports_directory):
            item_path = os.path.join(reports_directory, item)
            if os.path.isdir(item_path) and item.startswith("District_"):
                try:
                    district_num = int(item.split("_")[1])
                    if districts is None or district_num in districts:
                        district_dirs.append((district_num, item_path))
                except (IndexError, ValueError):
                    continue
    
    if not district_dirs:
        print("❌ No district directories found!")
        return []
    
    district_dirs.sort()  # Sort by district number
    print(f"Found {len(district_dirs)} district directories")
    
    # PDF generation options optimized for reports
    pdf_options = {
        'format': 'A4',
        'margin': {
            'top': '0.75in',
            'right': '0.5in',
            'bottom': '0.75in', 
            'left': '0.5in'
        },
        'print_background': True,
        'prefer_css_page_size': True,
        'display_header_footer': True,
        'header_template': '<div style="font-size:9px; margin-left:0.5in;">NYC DOE Substitute Paraprofessional Jobs Report</div>',
        'footer_template': '<div style="font-size:9px; margin:0 auto;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
    }
    
    converted_files = []
    failed_conversions = []
    
    for district_num, district_path in district_dirs:
        district_report_file = os.path.join(district_path, f"{district_num}_report.html")
        
        if os.path.exists(district_report_file):
            pdf_filename = f"District_{district_num}_report.pdf"
            pdf_file_path = os.path.join(output_directory, pdf_filename)
            
            try:
                print(f"Converting District {district_num}...")
                await convert_html_to_pdf(district_report_file, pdf_file_path, pdf_options)
                converted_files.append(pdf_file_path)
                print(f"✅ District {district_num} → {pdf_filename}")
                
            except Exception as e:
                failed_conversions.append((district_num, str(e)))
                print(f"❌ Failed to convert District {district_num}: {e}")
        else:
            failed_conversions.append((district_num, "HTML report file not found"))
            print(f"❌ District {district_num}: HTML report not found")
    
    return converted_files, failed_conversions

async def compile_school_reports_to_pdf(reports_directory, output_directory=None, districts=None):
    """
    Compile individual school reports from HTML to PDF
    
    Args:
        reports_directory: Directory containing district HTML reports
        output_directory: Where to save PDFs (default: reports_directory/School_PDFs)
        districts: List of specific districts to process (default: all)
    """
    if output_directory is None:
        output_directory = os.path.join(reports_directory, "School_PDFs")
    
    os.makedirs(output_directory, exist_ok=True)
    
    print(f"Compiling school reports to PDF...")
    print(f"Source: {reports_directory}")
    print(f"Output: {output_directory}")
    
    # Find all district directories
    district_dirs = []
    if os.path.exists(reports_directory):
        for item in os.listdir(reports_directory):
            item_path = os.path.join(reports_directory, item)
            if os.path.isdir(item_path) and item.startswith("District_"):
                try:
                    district_num = int(item.split("_")[1])
                    if districts is None or district_num in districts:
                        district_dirs.append((district_num, item_path))
                except (IndexError, ValueError):
                    continue
    
    if not district_dirs:
        print("❌ No district directories found!")
        return []
    
    district_dirs.sort()
    
    # PDF options for school reports (slightly smaller margins)
    pdf_options = {
        'format': 'A4',
        'margin': {
            'top': '0.5in',
            'right': '0.4in',
            'bottom': '0.5in',
            'left': '0.4in'
        },
        'print_background': True,
        'prefer_css_page_size': True,
        'display_header_footer': True,
        'header_template': '<div style="font-size:8px; margin-left:0.4in;">NYC DOE School Report</div>',
        'footer_template': '<div style="font-size:8px; margin:0 auto;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
    }
    
    converted_files = []
    failed_conversions = []
    total_schools = 0
    
    for district_num, district_path in district_dirs:
        schools_dir = os.path.join(district_path, "Schools")
        
        if not os.path.exists(schools_dir):
            print(f"⚠️ District {district_num}: No Schools directory found")
            continue
        
        # Create district subfolder in output
        district_pdf_dir = os.path.join(output_directory, f"District_{district_num}")
        os.makedirs(district_pdf_dir, exist_ok=True)
        
        # Find all school directories
        school_count = 0
        for school_item in os.listdir(schools_dir):
            school_path = os.path.join(schools_dir, school_item)
            if os.path.isdir(school_path) and school_item.startswith("School_"):
                school_name = school_item.replace("School_", "")
                school_report_file = os.path.join(school_path, f"{school_name}_report.html")
                
                if os.path.exists(school_report_file):
                    pdf_filename = f"{school_name}_report.pdf"
                    pdf_file_path = os.path.join(district_pdf_dir, pdf_filename)
                    
                    try:
                        await convert_html_to_pdf(school_report_file, pdf_file_path, pdf_options)
                        converted_files.append(pdf_file_path)
                        school_count += 1
                        
                    except Exception as e:
                        failed_conversions.append((f"District {district_num} - {school_name}", str(e)))
                        print(f"❌ Failed to convert {school_name}: {e}")
        
        if school_count > 0:
            print(f"✅ District {district_num}: {school_count} school reports converted")
            total_schools += school_count
    
    print(f"📊 Total school reports converted: {total_schools}")
    return converted_files, failed_conversions

def main_pdf_compiler():
    """
    Main function to compile HTML reports to PDF
    """
    # Configuration
    reports_directory = 'district_individual_reports'
    
    if not os.path.exists(reports_directory):
        print(f"❌ Reports directory not found: {reports_directory}")
        print("Please run district_only_generator.py first to create the HTML reports.")
        return
    
    # Check if Playwright is installed
    if not check_playwright_installation():
        print("Playwright not found. Installing...")
        if not install_playwright():
            print("❌ Failed to install Playwright. Please install manually:")
            print("pip install playwright")
            print("playwright install chromium")
            return
    
    start_time = time.time()
    
    print("Starting PDF compilation...")
    print(f"Source directory: {reports_directory}")
    print("="*60)
    
    try:
        # Run the async compilation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Compile district reports
        print("🏫 Converting District Reports...")
        district_files, district_failures = loop.run_until_complete(
            compile_district_reports_to_pdf(reports_directory)
        )
        
        print("\n" + "="*40)
        
        # Compile school reports
        print("🎓 Converting School Reports...")
        school_files, school_failures = loop.run_until_complete(
            compile_school_reports_to_pdf(reports_directory)
        )
        
        loop.close()
        
        elapsed = time.time() - start_time
        
        # Summary
        print("\n" + "="*60)
        print("PDF COMPILATION COMPLETED")
        print("="*60)
        print(f"District PDFs: {len(district_files)} created")
        print(f"School PDFs: {len(school_files)} created")
        print(f"Total Time: {elapsed:.2f} seconds")
        
        if district_failures:
            print(f"\n⚠️ District conversion failures: {len(district_failures)}")
            for district, error in district_failures:
                print(f"  - District {district}: {error}")
        
        if school_failures:
            print(f"\n⚠️ School conversion failures: {len(school_failures)}")
            for school, error in school_failures[:5]:  # Show first 5
                print(f"  - {school}: {error}")
            if len(school_failures) > 5:
                print(f"  ... and {len(school_failures) - 5} more")
        
        print(f"\n📁 Output directories:")
        print(f"  District PDFs: {reports_directory}/PDFs/")
        print(f"  School PDFs: {reports_directory}/School_PDFs/")
        
    except Exception as e:
        print(f"❌ Error during PDF compilation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_pdf_compiler()
