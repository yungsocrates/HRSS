"""
Data processing utilities for NYC DOE Reports
"""

import pandas as pd
import numpy as np
import shutil
import os
import re

def remove_unnamed_columns(df):
    """Remove columns with 'Unnamed' in their name from a DataFrame."""
    return df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

# === GLOBAL CONSTANTS ===
DISPLAY_COLS = [
    'Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
    'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
    'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct'
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
    'Total_Filled': 'Total Filled',
    'Total_Unfilled': 'Total Unfilled',
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
    
    # Separate SREPP files from main data files
    main_dataframes = []
    srepp_dataframes = []
    
    for csv_file_path in csv_file_paths:
        filename = os.path.basename(csv_file_path)
        
        if filename in ['SREPP1.csv', 'SREPP2.csv']:
            print(f"Loading payroll data from: {csv_file_path}")
            # First, read the file to check available columns
            try:
                # Try reading without specifying columns first
                temp_df = pd.read_csv(csv_file_path, nrows=1, encoding='UTF-8', sep=',')
                temp_df = remove_unnamed_columns(temp_df)
                available_cols = len(temp_df.columns)
                print(f"  Available columns in {filename}: {available_cols}")
                print(f"  Column names: {list(temp_df.columns)}")
                
                # Only read the columns that actually exist
                if available_cols >= 10:
                    # If we have enough columns, use the even-numbered ones
                    cols_to_use = [2*i for i in range(0, min(10, available_cols//2))]
                    df = pd.read_csv(csv_file_path, skiprows=[1], usecols=cols_to_use, encoding='UTF-8', sep=',')
                else:
                    # If we don't have enough columns, read all available columns
                    df = pd.read_csv(csv_file_path, encoding='UTF-8', sep=',')
                    
                print(f"  Loaded columns from {filename}: {list(df.columns)}")
                df = remove_unnamed_columns(df)
                df['Source_File'] = filename
                srepp_dataframes.append(df)
            except Exception as e:
                print(f"  Error loading {csv_file_path}: {str(e)}")
                print(f"  Skipping this file and continuing...")
                continue
        else:
            print(f"Loading data from: {csv_file_path}")
            df = pd.read_csv(csv_file_path)
            df = remove_unnamed_columns(df)
            # Add source file information for tracking
            df['Source_File'] = filename
            main_dataframes.append(df)

    # Combine main dataframes (excluding SREPP files)
    if main_dataframes:
        df = pd.concat(main_dataframes, ignore_index=True)
        df = remove_unnamed_columns(df)
    else:
        df = pd.DataFrame()  # Empty dataframe if no main files
    
    # Combine SREPP dataframes separately
    if srepp_dataframes:
        srepp_df = pd.concat(srepp_dataframes, ignore_index=True)
        srepp_df = remove_unnamed_columns(srepp_df)
        print(f"Combined SREPP payroll data: {len(srepp_df)} records from {len(srepp_dataframes)} files")
    else:
        srepp_df = pd.DataFrame()  # Empty dataframe if no SREPP files
    
    print(f"Combined main data: {len(df)} total records from {len(main_dataframes)} files")
    
    # Clean column names (remove extra spaces) for main dataframe
    if not df.empty:
        df.columns = df.columns.str.strip()
    
    # Clean column names for SREPP dataframe if it exists
    if not srepp_df.empty:
        srepp_df.columns = srepp_df.columns.str.strip()
    
    # Continue processing main dataframe only (SREPP data will be returned separately)
    df_to_process = df
    
    # Parse Job Start dates (handle different formats) - only for main data
    if 'Job Start' in df_to_process.columns and not df_to_process.empty:
        try:
            # First, try to convert numeric Excel serial dates
            numeric_mask = pd.to_numeric(df_to_process['Job Start'], errors='coerce').notna()
            if numeric_mask.any():
                # Convert Excel serial date to datetime for numeric values
                df_to_process.loc[numeric_mask, 'Job Start'] = pd.to_datetime(
                    pd.to_numeric(df_to_process.loc[numeric_mask, 'Job Start']) - 1, 
                    unit='D', 
                    origin='1900-01-01'
                )
            
            # Then try to parse any remaining string dates
            string_mask = ~numeric_mask
            if string_mask.any():
                df_to_process.loc[string_mask, 'Job Start'] = pd.to_datetime(
                    df_to_process.loc[string_mask, 'Job Start'], 
                    errors='coerce'
                )
        except Exception as e:
            print(f"Warning: Could not parse some Job Start dates - {e}")
            # Try a general datetime conversion as fallback
            df_to_process['Job Start'] = pd.to_datetime(df_to_process['Job Start'], errors='coerce')
    
    # Process main dataframe only (skip if empty)
    if not df_to_process.empty:
        # Clean Classification names to remove newlines and extra spaces
        df_to_process['Classification'] = df_to_process['Classification'].str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
        df_to_process['Classification'] = df_to_process['Classification'].str.replace(r'\s+', ' ', regex=True)
        
        # Clean up gender-specific classifications
        df_to_process['Classification'] = df_to_process['Classification'].apply(clean_classification_gender)
        
        # Create District code (ensure it's an integer and remove rows with NaN districts)
        df_to_process = df_to_process.dropna(subset=['District'])  # Remove rows where District is NaN
        df_to_process['District'] = df_to_process['District'].astype(int)

        # Add column for boroughs
        df_to_process['Borough'] = df_to_process['Location'].apply(get_borough_from_location)
        
        # Clean Location names for folder creation
        df_to_process['Location_Clean'] = df_to_process['Location'].str.replace(r'[<>:"/\\|?*]', '_', regex=True)
        df_to_process['Type'] = df_to_process['Type'].str.strip().str.title()
        
        # Define filled vs unfilled status
        filled_statuses = [
            'Finished/Admin Assigned',
            'Finished/IVR Assigned', 
            'Finished/IVR Sub Search',
            'Finished/Pre Arranged',
            'Finished/Web Sub Search'
        ]
        
        # Create fill status column
        df_to_process['Fill_Status'] = df_to_process['Status'].apply(
            lambda x: 'Filled' if x in filled_statuses else 'Unfilled'
        )
        
        # Create combined category for Type + Fill Status
        df_to_process['Type_Fill_Status'] = df_to_process['Type'] + '_' + df_to_process['Fill_Status']
    
    # Return both main processed data and SREPP data
    return df_to_process, srepp_df

def create_matching_analysis(main_df, srepp_df):
    """
    Create analysis comparing individual jobs between SubCentral and SREPP payroll data by location
    
    Args:
        main_df: SubCentral data with 'Location', 'Specified Sub', and 'Job Start' columns (filled jobs only)
        srepp_df: SREPP payroll data with 'SCHOOL', 'EISID', and 'DATE' columns  
    
    Returns:
        pandas.DataFrame: Job-level matching analysis by location with columns:
            - Location: School location
            - SubCentral Job Days: Total filled job days in SubCentral for this location
            - Payroll Job Days: Total payroll records for this location
            - Matched Jobs: Number of SubCentral jobs that have matching payroll records
            - Match Percentage: Percentage of payroll records that have corresponding SubCentral records
    """
    print(f"  Starting sophisticated job-level matching analysis...")
    print(f"  Main df shape: {main_df.shape}, SREPP df shape: {srepp_df.shape}")
    
    if main_df.empty and srepp_df.empty:
        print("  Both dataframes are empty, returning empty result")
        return pd.DataFrame()
    
    # Process SubCentral data to create unique job identifiers
    subcentral_jobs = {}
    subcentral_totals = {}
    if not main_df.empty:
        # Only work with filled jobs
        filled_jobs = main_df[main_df['Fill_Status'] == 'Filled'].copy()
        print(f"  Processing {len(filled_jobs)} filled jobs from {len(main_df)} total SubCentral records")
        
        if not filled_jobs.empty:
            # Check required columns
            required_cols = ['Location', 'Specified Sub', 'Job Start']
            missing_cols = [col for col in required_cols if col not in filled_jobs.columns]
            
            if missing_cols:
                print(f"  Warning: Missing required columns in SubCentral data: {missing_cols}")
                print(f"  Available columns: {list(filled_jobs.columns)}")
                print(f"  Cannot perform job-level matching")
            else:
                # Create unique job identifiers: LOCATION+SPECIFIED_SUB+DATE_INTEGER
                # First ensure Job Start is in datetime format
                filled_jobs['Job Start'] = pd.to_datetime(filled_jobs['Job Start'], errors='coerce')
                
                # Remove jobs with invalid dates
                filled_jobs = filled_jobs[filled_jobs['Job Start'].notna()].copy()
                print(f"  SubCentral jobs with valid dates: {len(filled_jobs)}")
                
                if len(filled_jobs) == 0:
                    print("  No SubCentral jobs with valid dates found")
                else:
                    # Remove jobs with NaN Specified Sub values and convert to int
                    filled_jobs = filled_jobs[filled_jobs['Specified Sub'].notna()].copy()
                    print(f"  SubCentral jobs after removing NaN Specified Sub: {len(filled_jobs)}")
                    
                    if len(filled_jobs) == 0:
                        print("  No SubCentral jobs with valid Specified Sub found")
                    else:
                        # Convert Job Start to date integer (YYYYMMDD format)
                        filled_jobs['Job_Date_Int'] = filled_jobs['Job Start'].dt.strftime('%Y%m%d').astype(str)
                        
                        # Clean and format Specified Sub (EISID) - convert to int first, then to 7-char string
                        filled_jobs['Specified_Sub_Int'] = pd.to_numeric(filled_jobs['Specified Sub'], errors='coerce').astype('Int64')
                        filled_jobs = filled_jobs[filled_jobs['Specified_Sub_Int'].notna()].copy()
                        print(f"  SubCentral jobs after converting Specified Sub to int: {len(filled_jobs)}")
                        
                        if len(filled_jobs) == 0:
                            print("  No SubCentral jobs with numeric Specified Sub found")
                        else:
                            # Format as 7-character zero-padded string
                            filled_jobs['EISID_Clean'] = filled_jobs['Specified_Sub_Int'].astype(str).str.zfill(7)
                            
                            # Clean Location
                            filled_jobs['Location_Clean'] = filled_jobs['Location'].astype(str).str.strip()
                
                            filled_jobs['Job_ID'] = (
                                filled_jobs['Location_Clean'] + '|' + 
                                filled_jobs['EISID_Clean'] + '|' + 
                                filled_jobs['Job_Date_Int']
                            )
                            
                            # Create location mapping for job IDs
                            for _, row in filled_jobs.iterrows():
                                location = row['Location_Clean']
                                job_id = row['Job_ID']
                                
                                if location not in subcentral_jobs:
                                    subcentral_jobs[location] = set()
                                subcentral_jobs[location].add(job_id)
                            
                            # Count total jobs by location
                            subcentral_totals = filled_jobs.groupby('Location_Clean').size().to_dict()
                            
                            total_subcentral_jobs = sum(subcentral_totals.values())
                            print(f"  SubCentral: {len(subcentral_totals)} locations, {total_subcentral_jobs} total job days")
                            print(f"  Created {sum(len(jobs) for jobs in subcentral_jobs.values())} unique job identifiers")
                            print(f"  Sample SubCentral job IDs: {list(list(subcentral_jobs.values())[0])[:3] if subcentral_jobs else []}")
                            print(f"  Top 5 SubCentral locations by job days: {dict(list(sorted(subcentral_totals.items(), key=lambda x: x[1], reverse=True)[:5]))}")
                            
                            # Debug output for M015 specifically
                            if 'M015' in subcentral_jobs:
                                print(f"  DEBUG M015 SubCentral - Total unique IDs: {len(subcentral_jobs['M015'])}")
                                print(f"  DEBUG M015 SubCentral - All unique IDs: {sorted(list(subcentral_jobs['M015']))}")
                            elif any('M015' in location for location in subcentral_jobs.keys()):
                                matching_locations = [loc for loc in subcentral_jobs.keys() if 'M015' in loc]
                                print(f"  DEBUG - Found locations containing M015: {matching_locations}")
                                for loc in matching_locations:
                                    print(f"  DEBUG {loc} SubCentral - Total unique IDs: {len(subcentral_jobs[loc])}")
                                    print(f"  DEBUG {loc} SubCentral - All unique IDs: {sorted(list(subcentral_jobs[loc]))}")
                            else:
                                print(f"  DEBUG - M015 not found in SubCentral locations. Available locations: {sorted(list(subcentral_jobs.keys())[:10])}")
        else:
            print("  No filled SubCentral jobs found")
    else:
        print("  No SubCentral data to process")
    
    # Process SREPP data to find matching jobs
    srepp_jobs = {}
    srepp_totals = {}
    if not srepp_df.empty:
        print(f"  Processing {len(srepp_df)} SREPP payroll records...")
        print(f"  SREPP columns available: {list(srepp_df.columns)}")
        
        # Check required columns
        required_cols = ['SCHOOL', 'EISID', 'DATE']
        missing_cols = [col for col in required_cols if col not in srepp_df.columns]
        
        if missing_cols:
            print(f"  Warning: Missing required columns in SREPP data: {missing_cols}")
            print(f"  Available columns: {list(srepp_df.columns)}")
            print(f"  Cannot perform job-level matching")
        else:
            print(f"  Using columns: SCHOOL, EISID, DATE for job matching")
            
            # Process SREPP records
            srepp_df_copy = srepp_df.copy()
            
            # Remove records with NaN EISID values
            srepp_df_copy = srepp_df_copy[srepp_df_copy['EISID'].notna()].copy()
            print(f"  SREPP records after removing NaN EISID: {len(srepp_df_copy)}")
            
            if len(srepp_df_copy) == 0:
                print("  No SREPP records with valid EISID found")
            else:
                # Clean SCHOOL column - remove first 2 characters and clean
                srepp_df_copy['School_Clean'] = srepp_df_copy['SCHOOL'].astype(str).str.strip().str[2:]
                
                # Clean and format EISID - convert to int first, then to 7-char string
                srepp_df_copy['EISID_Int'] = pd.to_numeric(srepp_df_copy['EISID'], errors='coerce').astype('Int64')
                srepp_df_copy = srepp_df_copy[srepp_df_copy['EISID_Int'].notna()].copy()
                print(f"  SREPP records after converting EISID to int: {len(srepp_df_copy)}")
                
                if len(srepp_df_copy) == 0:
                    print("  No SREPP records with numeric EISID found")
                else:
                    # Format as 7-character zero-padded string
                    srepp_df_copy['EISID_Clean'] = srepp_df_copy['EISID_Int'].astype(str).str.zfill(7)
                    
                    # Parse dates and convert to integer format (YYYYMMDD)
                    srepp_df_copy['DATE_Clean'] = pd.to_datetime(srepp_df_copy['DATE'], errors='coerce')
                    srepp_df_copy['Date_Int'] = srepp_df_copy['DATE_Clean'].dt.strftime('%Y%m%d').astype(str)
                    
                    # Remove records with invalid dates
                    valid_srepp = srepp_df_copy[srepp_df_copy['DATE_Clean'].notna()].copy()
                    print(f"  SREPP records with valid dates: {len(valid_srepp)}")
                    
                    if len(valid_srepp) > 0:
                        # Create job identifiers: SCHOOL_CLEAN+EISID_CLEAN+DATE_INTEGER
                        valid_srepp['Job_ID'] = (
                            valid_srepp['School_Clean'] + '|' + 
                            valid_srepp['EISID_Clean'] + '|' + 
                            valid_srepp['Date_Int']
                        )
                        
                        # Create location mapping from SubCentral locations to match with SREPP School_Clean
                        location_mapping = {}
                        if not main_df.empty:
                            main_locations = main_df['Location'].unique()
                            print(f"  Mapping to {len(main_locations)} unique SubCentral locations...")
                            
                            # Map location codes to full location names
                            for main_location in main_locations:
                                main_location_str = str(main_location).strip()
                                # Extract location code from main location (last 4 characters)
                                main_location_code = main_location_str[-4:]
                                location_mapping[main_location_code] = main_location_str
                            
                            print(f"  Created {len(location_mapping)} location mappings")
                        
                        # Map SREPP School_Clean to SubCentral location names
                        valid_srepp['Location'] = valid_srepp['School_Clean'].map(location_mapping)
                        
                        # Filter to only records that map to SubCentral locations
                        mapped_srepp = valid_srepp[valid_srepp['Location'].notna()].copy()
                        
                        print(f"  SREPP records: {len(mapped_srepp)} mapped to SubCentral locations, {len(valid_srepp) - len(mapped_srepp)} unmapped")
                        
                        if len(mapped_srepp) > 0:
                            # Create location mapping for SREPP job IDs (using the mapped SubCentral location names)
                            for _, row in mapped_srepp.iterrows():
                                location = row['Location']
                                job_id = row['Job_ID']
                                
                                if location not in srepp_jobs:
                                    srepp_jobs[location] = set()
                                srepp_jobs[location].add(job_id)
                            
                            # Count total SREPP records by location
                            srepp_totals = mapped_srepp.groupby('Location').size().to_dict()
                            
                            total_srepp_jobs = sum(srepp_totals.values())
                            print(f"  SREPP: {len(srepp_totals)} locations, {total_srepp_jobs} total job days")
                            print(f"  Created {sum(len(jobs) for jobs in srepp_jobs.values())} unique SREPP job identifiers")
                            print(f"  Sample SREPP job IDs: {list(list(srepp_jobs.values())[0])[:3] if srepp_jobs else []}")
                            print(f"  Top 5 SREPP locations by job days: {dict(list(sorted(srepp_totals.items(), key=lambda x: x[1], reverse=True)[:5]))}")
                            
                            # Debug output for M015 specifically in SREPP
                            if 'M015' in srepp_jobs:
                                print(f"  DEBUG M015 SREPP - Total unique IDs: {len(srepp_jobs['M015'])}")
                                print(f"  DEBUG M015 SREPP - All unique IDs: {sorted(list(srepp_jobs['M015']))}")
                            elif any('M015' in location for location in srepp_jobs.keys()):
                                matching_locations = [loc for loc in srepp_jobs.keys() if 'M015' in loc]
                                print(f"  DEBUG - Found SREPP locations containing M015: {matching_locations}")
                                for loc in matching_locations:
                                    print(f"  DEBUG {loc} SREPP - Total unique IDs: {len(srepp_jobs[loc])}")
                                    print(f"  DEBUG {loc} SREPP - All unique IDs: {sorted(list(srepp_jobs[loc]))}")
                            else:
                                print(f"  DEBUG - M015 not found in SREPP locations. Available locations: {sorted(list(srepp_jobs.keys())[:10])}")
                                # Also show the mapping process
                                print(f"  DEBUG - SREPP School_Clean values for first 10 records: {valid_srepp['School_Clean'].head(10).tolist()}")
                                print(f"  DEBUG - Location mapping sample: {dict(list(location_mapping.items())[:10])}")
                        else:
                            print("  No SREPP records could be mapped to SubCentral locations")
                    else:
                        print("  No valid SREPP records found")
    else:
        print("  No SREPP data to process")
    
    # Create comparison results
    all_locations = set(subcentral_totals.keys()) | set(srepp_totals.keys())
    print(f"  Total unique locations across both systems: {len(all_locations)}")
    
    if not all_locations:
        print("  No locations found in either system")
        return pd.DataFrame()
    
    # Calculate matches by location using simple unique ID matching
    matching_results = []
    total_matches = 0
    
    for location in all_locations:
        subcentral_days = subcentral_totals.get(location, 0)
        srepp_days = srepp_totals.get(location, 0)
        
        # Get unique job IDs for this location from both systems
        subcentral_job_set = subcentral_jobs.get(location, set())
        srepp_job_set = srepp_jobs.get(location, set())
        
        # Count how many SubCentral unique IDs also appear in payroll
        matched_jobs = 0
        for subcentral_id in subcentral_job_set:
            if subcentral_id in srepp_job_set:
                matched_jobs += 1
        
        total_matches += matched_jobs
        
        # Calculate match percentage (what percentage of payroll records have corresponding SubCentral records)
        if srepp_days > 0:
            coverage_rate = (matched_jobs / srepp_days * 100)
        else:
            coverage_rate = 0.0
        
        # Debug output for locations with potential matches
        if matched_jobs > 0 or (subcentral_days > 0 and srepp_days > 0):
            print(f"    {location}: SubC_IDs={len(subcentral_job_set)}, SREPP_IDs={len(srepp_job_set)}, Matches={matched_jobs}")
            if matched_jobs > 0:
                # Show a few example matching IDs
                sample_matches = [uid for uid in subcentral_job_set if uid in srepp_job_set][:3]
                print(f"      Sample matching IDs: {sample_matches}")
        
        matching_results.append({
            'Location': location,
            'SubCentral Job Days': subcentral_days,
            'Payroll Job Days': srepp_days,
            'Matched Jobs': matched_jobs,
            'Match Percentage': coverage_rate
        })
    
    # Convert to DataFrame and sort by location
    matching_df = pd.DataFrame(matching_results)
    matching_df = matching_df.sort_values('Location')
    
    # Calculate summary statistics
    total_subcentral = matching_df['SubCentral Job Days'].sum()
    total_srepp = matching_df['Payroll Job Days'].sum()
    overall_coverage = (total_matches / total_srepp * 100) if total_srepp > 0 else 0
    
    print(f"  Created matching analysis with {len(matching_df)} locations")
    print(f"  Total SubCentral job days: {total_subcentral}")
    print(f"  Total payroll job days: {total_srepp}")
    print(f"  Total matched jobs: {total_matches}")
    print(f"  Overall match percentage: {overall_coverage:.1f}%")
    
    return matching_df

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
    
    # Calculate combined totals
    summary_pivot['Total_Filled'] = summary_pivot['Vacancy_Filled'] + summary_pivot['Absence_Filled']
    summary_pivot['Total_Unfilled'] = summary_pivot['Vacancy_Unfilled'] + summary_pivot['Absence_Unfilled']
    
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
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
        'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct'
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
