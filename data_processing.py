"""
Data processing utilities for NYC DOE Reports
"""

import pandas as pd
import numpy as np
import shutil
import os
import re

# === GLOBAL CONSTANTS ===
DISPLAY_COLS = [
    'Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
    'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct'
]

DISPLAY_COLS_RENAME = {
    'Classification': 'Classification',
    'Vacancy_Filled': 'Vacancy Filled',
    'Vacancy_Unfilled': 'Vacancy Unfilled',
    'Total_Vacancy': 'Total Vacancy',
    'Vacancy_Fill_Pct': 'Vacancy Fill %',
    'Absence_Filled': 'Absence Filled',
    'Absence_Unfilled': 'Absence Unfilled',
    'Total_Absence': 'Total Absence',
    'Absence_Fill_Pct': 'Absence Fill %',
    'Total': 'Total',
    'Overall_Fill_Pct': 'Overall Fill %'
}

def format_pct(x):
    """Format percentage values"""
    return f"{x:.1f}%" if isinstance(x, (int, float)) else str(x)

def format_int(x):
    """Format integer values with commas"""
    return f"{int(x):,}" if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else str(x)

def copy_logo_to_output(output_directory):
    """
    Copy the logo file to the output directory for the citywide report
    """
    logo_source = "Horizontal_logo_White_PublicSchools.png"
    logo_dest = os.path.join(output_directory, "Horizontal_logo_White_PublicSchools.png")
    
    if os.path.exists(logo_source):
        try:
            shutil.copy2(logo_source, logo_dest)
            print(f"Logo copied to {logo_dest} for citywide report")
        except Exception as e:
            print(f"Warning: Could not copy logo file: {e}")
    else:
        print(f"Warning: Logo file {logo_source} not found")

def load_and_process_data(csv_file_paths):
    """
    Load CSV data from multiple files and process it for dashboard display
    
    Args:
        csv_file_paths: Single CSV file path (string) or list of CSV file paths
    """
    # Handle both single file and multiple files
    if isinstance(csv_file_paths, str):
        csv_file_paths = [csv_file_paths]
    
    # Read and combine all CSV files
    dataframes = []
    for csv_file_path in csv_file_paths:
        print(f"Loading data from: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        # Add source file information for tracking
        df['Source_File'] = os.path.basename(csv_file_path)
        dataframes.append(df)
    
    # Combine all dataframes
    df = pd.concat(dataframes, ignore_index=True)
    print(f"Combined data: {len(df)} total records from {len(csv_file_paths)} files")
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # Parse Job Start dates (handle different formats)
    if 'Job Start' in df.columns:
        try:
            # First, try to convert numeric Excel serial dates
            numeric_mask = pd.to_numeric(df['Job Start'], errors='coerce').notna()
            if numeric_mask.any():
                # Convert Excel serial date to datetime for numeric values
                df.loc[numeric_mask, 'Job Start'] = pd.to_datetime(
                    pd.to_numeric(df.loc[numeric_mask, 'Job Start']) - 1, 
                    unit='D', 
                    origin='1900-01-01'
                )
            
            # Then try to parse any remaining string dates
            string_mask = ~numeric_mask
            if string_mask.any():
                df.loc[string_mask, 'Job Start'] = pd.to_datetime(
                    df.loc[string_mask, 'Job Start'], 
                    errors='coerce'
                )
        except Exception as e:
            print(f"Warning: Could not parse some Job Start dates - {e}")
            # Try a general datetime conversion as fallback
            df['Job Start'] = pd.to_datetime(df['Job Start'], errors='coerce')
    
    # Clean Classification names to remove newlines and extra spaces
    df['Classification'] = df['Classification'].str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
    df['Classification'] = df['Classification'].str.replace(r'\s+', ' ', regex=True)
    
    # Clean up gender-specific classifications
    df['Classification'] = df['Classification'].apply(clean_classification_gender)
    
    # Create District code (ensure it's an integer and remove rows with NaN districts)
    df = df.dropna(subset=['District'])  # Remove rows where District is NaN
    df['District'] = df['District'].astype(int)

    # Add column for boroughs
    df['Borough'] = df['Location'].apply(get_borough_from_location)
    
    # Clean Location names for folder creation
    df['Location_Clean'] = df['Location'].str.replace(r'[<>:"/\\|?*]', '_', regex=True)
    df['Type'] = df['Type'].str.strip().str.title()
    
    # Define filled vs unfilled status
    filled_statuses = [
        'Finished/Admin Assigned',
        'Finished/IVR Assigned', 
        'Finished/Pre Arranged',
        'Finished/Web Sub Search'
    ]
    
    # Create fill status column
    df['Fill_Status'] = df['Status'].apply(
        lambda x: 'Filled' if x in filled_statuses else 'Unfilled'
    )
    
    # Create combined category for Type + Fill Status
    df['Type_Fill_Status'] = df['Type'] + '_' + df['Fill_Status']
    
    return df

def clean_classification_gender(classification):
    """
    Clean up classification names by removing gender identifiers and standardizing terms
    
    Args:
        classification (str): Original classification name
        
    Returns:
        str: Cleaned classification name
    """
    if pd.isna(classification):
        return classification
    
    # Convert to string and strip whitespace
    clean_name = str(classification).strip()
    
    # Handle specific cases first
    if clean_name.upper() in ['FEMALE PARA', 'MALE PARA']:
        return 'PARAPROFESSIONAL'
    
    # Remove FEMALE or MALE from the classification
    # Use word boundaries to avoid partial matches
    clean_name = re.sub(r'\b(FEMALE|MALE)\s*', '', clean_name, flags=re.IGNORECASE)
    
    # Clean up any extra whitespace that might result from removal
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    
    return clean_name

def get_borough_from_location(location):
    """
    Extract borough from location based on first letter
    """
    if pd.isna(location) or not location:
        return 'Unknown'
    
    first_char = location.strip()[0].upper()
    borough_map = {
        'M': 'Manhattan', 
        'K': 'Brooklyn',
        'Q': 'Queens',
        'X': 'Bronx',
        'R': 'Staten Island'
    }

    return borough_map.get(first_char, 'Unknown')

def get_data_date_range(df):
    """
    Get the date range from Job Start column
    """
    if 'Job Start' not in df.columns:
        return "Date range not available"
    
    try:
        # Get min and max dates, excluding NaT (Not a Time) values
        valid_dates = df['Job Start'].dropna()
        if len(valid_dates) == 0:
            return "Date range not available"
        
        min_date = valid_dates.min()
        max_date = valid_dates.max()
        
        # Format dates as readable strings
        min_date_str = min_date.strftime('%B %d, %Y')
        max_date_str = max_date.strftime('%B %d, %Y')
        
        if min_date.date() == max_date.date():
            return f"Job dates: {min_date_str}"
        else:
            return f"Job dates: {min_date_str} to {max_date_str}"
    except Exception as e:
        print(f"Warning: Could not parse date range - {e}")
        return "Date range not available"

def create_borough_summary_stats(df):
    """
    Create summary statistics by borough
    """
    return create_summary_stats(df, ['Borough'])

def create_summary_stats(df, group_cols):
    """
    Create summary statistics by specified grouping columns
    """
    # Group by specified columns and Type_Fill_Status
    summary = df.groupby(group_cols + ['Classification', 'Type_Fill_Status']).size().reset_index(name='Count')
    
    # Pivot to get all combinations
    summary_pivot = summary.pivot_table(
        index=group_cols + ['Classification'],
        columns='Type_Fill_Status',
        values='Count',
        fill_value=0
    )
    # Flatten columns if pivot_table creates a MultiIndex
    if isinstance(summary_pivot.columns, pd.MultiIndex):
        summary_pivot.columns = summary_pivot.columns.get_level_values(-1)
    summary_pivot = summary_pivot.reset_index()
    summary_pivot.columns.name = None
    
    # Ensure all possible columns exist
    expected_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled']
    for col in expected_cols:
        if col not in summary_pivot.columns:
            summary_pivot[col] = 0
    
    # Calculate totals and percentages
    summary_pivot['Total_Vacancy'] = summary_pivot['Vacancy_Filled'] + summary_pivot['Vacancy_Unfilled']
    summary_pivot['Total_Absence'] = summary_pivot['Absence_Filled'] + summary_pivot['Absence_Unfilled']
    summary_pivot['Total'] = summary_pivot['Total_Vacancy'] + summary_pivot['Total_Absence']
    
    # Ensure count columns are integers
    count_columns = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total']
    for col in count_columns:
        summary_pivot[col] = summary_pivot[col].astype(int)
    
    # Calculate percentages
    summary_pivot['Vacancy_Fill_Pct'] = np.where(
        summary_pivot['Total_Vacancy'] > 0,
        (summary_pivot['Vacancy_Filled'] / summary_pivot['Total_Vacancy'] * 100).round(1),
        0
    )
    summary_pivot['Absence_Fill_Pct'] = np.where(
        summary_pivot['Total_Absence'] > 0,
        (summary_pivot['Absence_Filled'] / summary_pivot['Total_Absence'] * 100).round(1),
        0
    )
    summary_pivot['Overall_Fill_Pct'] = np.where(
        summary_pivot['Total'] > 0,
        ((summary_pivot['Vacancy_Filled'] + summary_pivot['Absence_Filled']) / summary_pivot['Total'] * 100).round(1),
        0
    )

    # Remove 'Type_Fill_Status' if present
    if 'Type_Fill_Status' in summary_pivot.columns:
        summary_pivot = summary_pivot.drop(columns=['Type_Fill_Status'])

    # Only keep the columns needed for display
    display_cols = group_cols + [
        'Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total', 'Overall_Fill_Pct'
    ]
    summary_pivot = summary_pivot[[col for col in display_cols if col in summary_pivot.columns]]
    return summary_pivot

def df_with_pretty_columns(df):
    """
    Return a copy of df with columns renamed for display.
    """
    return df.rename(columns=DISPLAY_COLS_RENAME)

def calculate_fill_rates(data):
    """
    Calculate fill rates for a given data dictionary
    
    Args:
        data: Dictionary with keys Total, Total_Vacancy, Total_Absence, Vacancy_Filled, Absence_Filled
    
    Returns:
        Tuple of (overall_fill_rate, vacancy_fill_rate, absence_fill_rate)
    """
    total = data['Total']
    total_vacancy = data['Total_Vacancy']
    total_absence = data['Total_Absence']
    vacancy_filled = data['Vacancy_Filled']
    absence_filled = data['Absence_Filled']
    
    overall_fill_rate = ((vacancy_filled + absence_filled) / total * 100) if total > 0 else 0
    vacancy_fill_rate = (vacancy_filled / total_vacancy * 100) if total_vacancy > 0 else 0
    absence_fill_rate = (absence_filled / total_absence * 100) if total_absence > 0 else 0
    
    return overall_fill_rate, vacancy_fill_rate, absence_fill_rate

def get_totals_from_data(data):
    """
    Extract totals from summary data
    
    Args:
        data: DataFrame with summary statistics
    
    Returns:
        Dictionary with total statistics
    """
    return {
        'Total': int(data['Total'].sum()),
        'Total_Vacancy': int(data['Total_Vacancy'].sum()),
        'Total_Absence': int(data['Total_Absence'].sum()),
        'Vacancy_Filled': int(data['Vacancy_Filled'].sum()),
        'Absence_Filled': int(data['Absence_Filled'].sum())
    }
