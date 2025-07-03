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

This is the main entry point for the application. It orchestrates the entire report generation process by:
- Loading and processing data
- Creating summary statistics
- Generating district, borough, and school reports
- Creating the overall dashboard

Key functions:
- `create_borough_report()`: Generates comprehensive reports for each borough
- `create_overall_summary()`: Creates the main dashboard with citywide statistics
- `main()`: Entry point for the application

### `data_processing.py`

Handles all data loading, cleaning, and statistical analysis:
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

Key functions:
- `create_bar_chart()`: Generates bar charts for district and borough reports
- `create_overall_bar_chart()`: Creates specialized bar charts for the main dashboard
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

## Best Practices for Future Development

1. **Add New Features**: Extend existing modules or create new ones as needed
2. **Update Documentation**: Keep this documentation in sync with code changes
3. **Maintain Consistency**: Follow the established patterns for new functionality
4. **Testing**: Add unit tests for critical functionality
5. **Error Handling**: Continue robust error handling with meaningful messages
