# NYCDOE Paraprofessional Jobs Dashboard - Code Documentation

This document provides detailed information about the modular structure of the NYCDOE Paraprofessional Jobs Fill Rate Analytics Dashboard.

## Overview

The project has been refactored from a monolithic script into a modular architecture with specialized components:

```
ParaJobs/
├── Core Files (Version Controlled)
│   ├── para_fillrate_modular.py   # Main entry point
│   ├── data_processing.py         # Data loading and processing
│   ├── chart_utils.py             # Chart generation utilities
│   ├── templates.py               # HTML/CSS/JS templates
│   ├── report_generators.py       # Report generation functions
│   ├── requirements.txt           # Python dependencies
│   ├── Horizontal_logo_White_PublicSchools.png  # Logo file
│   └── README.md, CHANGELOG.md    # Documentation
│
├── Generated Output
│   └── nycdoe_reports/           # Generated HTML reports (not version controlled)
│
├── Raw Data
│   └── Fill Rate Data/           # CSV data files
│
└── Legacy Files (Not Version Controlled)
    ├── para_fillrate_by_location.py  # Original monolithic script
    ├── para_fillrate_oo.py           # Object-oriented implementation
    └── para_report_generation.log    # Old log files
```

## Module Descriptions

### `para_fillrate_modular.py`

This is the main entry point for the application with enhanced multi-source data processing. It orchestrates the entire report generation process by:
- **Multi-Source Data Loading**: Processes multiple CSV files (mayjobs.csv, junejobs.csv) automatically
- **Enhanced Navigation**: Creates comprehensive navigation links including back-to-borough functionality
- **Standardized Processing**: Applies gender-neutral classification standards across all data
- Creating summary statistics with integer formatting
- Generating district, borough, and school reports with improved navigation
- Creating the overall dashboard with combined data sources

Key functions:
- `create_borough_report()`: Generates comprehensive reports for each borough with enhanced styling
- `create_overall_summary()`: Creates the main dashboard with citywide statistics from combined sources
- `main()`: 
  - **Enhanced**: Now processes multiple CSV files automatically
  - Improved error handling for missing files
  - Better progress reporting and timing information
  - Handles combined data sources with source tracking

### `data_processing.py`

Handles all data loading, cleaning, and statistical analysis with enhanced multi-source capabilities:

**Key Functions:**
- `load_and_process_data(csv_file_paths)`: 
  - **Enhanced**: Now accepts single file or list of CSV files
  - Combines multiple data sources automatically
  - Tracks source file for each record
  - Applies gender-neutral classification cleaning
  - Handles various date formats robustly
- `clean_classification_gender(classification)`:
  - **New**: Removes gender identifiers from job classifications
  - Converts "FEMALE PARA" and "MALE PARA" to "PARAPROFESSIONAL"
  - Strips "FEMALE" and "MALE" prefixes from all classifications
- `get_data_date_range(df)`: 
  - **Enhanced**: Shows source files and date ranges
  - Handles multi-source date range calculation
- `create_summary_stats()`: Generates statistical summaries by grouping criteria
- `create_borough_summary_stats()`: Creates borough-level statistics
- `get_borough_from_location()`: Maps school codes to borough names
- `df_with_pretty_columns()`: Formats DataFrames for display

**Data Processing Features:**
- **Multi-Source Integration**: Seamlessly combines data from multiple CSV files
- **Gender Standardization**: Automatic removal of gender identifiers from job titles
- **Robust Date Parsing**: Handles Excel serial dates, standard formats, and error recovery
- **Source Tracking**: Maintains lineage of data records to source files
- **Integer Conversion**: Ensures clean integer display in charts and tables
- CSV file loading with proper error handling
- Data cleaning and standardization
- Summary statistics generation
- Date range extraction
- Helper functions for formatting

Key functions:
- `load_and_process_data()`: Loads and cleans the CSV data
- `create_summary_stats()`: Generates summary statistics by specified grouping
- `create_borough_summary_stats()`: Creates borough-level statistical summaries
- `get_data_date_range()`: Extracts date range information from data
- `format_pct()` and `format_int()`: Formatting helpers for tables

### `chart_utils.py`

Contains all chart generation logic:
- Bar chart creation for different report levels
- Pie chart generation for classifications
- Chart styling and customization
- **Optimized chart dimensions**: Charts sized to 1450px x 550px for perfect container fit

Key functions:
- `create_bar_chart()`: Generates bar charts for district and borough reports (1200px width)
- `create_overall_bar_chart()`: Creates specialized bar charts for the main dashboard (1450px width)
  - **Enhanced**: Optimized dimensions to eliminate horizontal scrollbars
  - Perfect fit within container with 1700px max-width layout
- `create_pie_charts_for_data()`: Generates pie charts for data breakdowns

### `templates.py`

Provides HTML, CSS, and JavaScript templates for the reports:
- Page templates with consistent styling
- Header and footer components
- Navigation elements
- CSS styling for responsive design

Key functions:
- `get_html_template()`: Returns the base HTML template for all reports
- `get_header_html()`: Generates the standardized header with logo
- `get_professional_footer()`: Creates the consistent footer for all reports
- `get_comparison_card_html()`: Generates comparison cards for statistics
- `get_navigation_html()`: Creates navigation links

### `report_generators.py`

Contains specialized functions for generating different report types:
- District reports with school breakdowns
- School-level detailed reports
- Specialized comparison reports

Key functions:
- `create_district_report()`: Generates reports for individual districts
- `create_school_report()`: Creates detailed school-level reports

## Key Improvements

### Standardized Logo Implementation
- Consistent white PNG logo (`Horizontal_logo_White_PublicSchools.png`)
- Logo positioned on the right side of the header with text center-aligned on the left
- **Bold header titles** for improved visual hierarchy (font-weight: 700 for main, 600 for subtitles)
- **Relative path handling** for universal compatibility (local and web deployment)
- Smart logo copying for deployment while maintaining efficient path references
- **Path structure**:
  - Main dashboard: `Horizontal_logo_White_PublicSchools.png` (same directory)
  - Borough reports: `../Horizontal_logo_White_PublicSchools.png` (one level up)
  - District/School reports: Appropriate `../` levels based on directory depth
- Responsive design that maintains logo visibility at different screen sizes

### Report Title Standardization
- Removed "NYCDOE" from all report titles
- Consistent naming convention across all report types
- Professional header styling with gradient background

### Enhanced Code Organization
- Clear separation of concerns
- Improved readability and maintainability
- Encapsulated functionality for easier testing
- Consistent error handling throughout

### Legacy Code Handling
- Original monolithic script (`para_fillrate_by_location.py`) preserved as reference but excluded from version control
- Object-oriented implementation (`para_fillrate_oo.py`) maintained as an alternate reference architecture
- Both legacy scripts are listed in `.gitignore` to keep the repository clean
- New modular architecture (`para_fillrate_modular.py`) is the recommended entry point for all operations
- Documentation and CHANGELOG provide clear tracking of architecture evolution
- Backward compatibility maintained for existing workflows and data formats

## Recent Enhancements (Version 4.5.0)

### Multi-Source Data Integration
- **CSV Combination**: Automatic processing of multiple CSV files with data merging
- **Source Tracking**: Each record maintains reference to its originating CSV file
- **Enhanced Configuration**: Updated main() function to handle list of CSV files
- **Error Handling**: Robust error handling for missing or malformed CSV files

### Gender-Neutral Processing
- **Classification Standardization**: Automatic removal of gender identifiers from job classifications
- **Specific Conversions**: "FEMALE PARA" and "MALE PARA" → "PARAPROFESSIONAL"
- **Pattern Matching**: Intelligent removal of "FEMALE" and "MALE" prefixes using regex
- **Data Consistency**: Ensures uniform job classification across all data sources

### Enhanced Navigation System
- **Back-to-Borough Links**: District reports now include navigation back to parent borough
- **Complete Hierarchy**: Overview → Borough → District → School navigation flow
- **Dynamic Link Generation**: Automatic creation of appropriate navigation based on report context
- **User Experience**: Improved navigation reduces clicks and enhances report accessibility

### Technical Improvements
- **Integer Display**: Fixed bar charts to show clean integer values instead of floats
- **Date Processing**: Enhanced date parsing for multiple formats including Excel serial dates
- **Error Recovery**: Improved error handling for various date format inconsistencies
- **Performance**: Optimized data processing pipeline for larger combined datasets

### Code Architecture
- **Modular Functions**: Separated gender cleaning logic into dedicated function
- **Flexible Parameters**: Updated functions to handle both single and multiple file inputs
- **Type Safety**: Enhanced type checking and validation throughout processing pipeline
- **Documentation**: Comprehensive inline documentation for new functionality

## Best Practices for Future Development

1. **Add New Features**: Extend existing modules or create new ones as needed
2. **Update Documentation**: Keep this documentation in sync with code changes
3. **Maintain Consistency**: Follow the established patterns for new functionality
4. **Testing**: Add unit tests for critical functionality
5. **Error Handling**: Continue robust error handling with meaningful messages
