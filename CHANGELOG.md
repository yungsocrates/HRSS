# Changelog

All notable changes to the NYC Public Schools Paraprofessional Jobs Fill Rate Analytics project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.6.0] - 2025-07-08

### Fixed
- 🖼️ **Scrollbar Elimination**: Resolved horizontal scrollbars on overall summary bar chart
  - Increased chart width from 1400px to 1450px for optimal display
  - Increased iframe dimensions to 1450px x 600px to match chart size perfectly
  - Enhanced container max-width to 1700px to accommodate larger charts
  - Optimized chart-container CSS with proper padding and overflow handling
  - Achieved seamless visual experience without horizontal scrolling

### Enhanced
- 📊 **Chart Display**: Improved visual presentation of overall summary bar chart
- 🎨 **Layout Optimization**: Fine-tuned container dimensions for perfect chart fit
- 📱 **Responsive Design**: Maintained responsive behavior while eliminating scrollbars

## [4.5.0] - 2025-07-08

### Added
- 📊 **Multi-Source Data Integration**: Combined data processing from multiple CSV files (mayjobs.csv and junejobs.csv)
- 🔄 **Enhanced Navigation**: Added back-to-borough navigation links in district reports for improved user experience
- 👤 **Gender-Neutral Classifications**: Standardized job classifications by removing gender identifiers
- 📅 **Robust Date Parsing**: Improved date handling for various formats including Excel serial dates and standard strings
- 📋 **Source Tracking**: Each data record now maintains information about its source CSV file

### Enhanced
- 🎯 **Data Processing**: 
  - Automatic combination of multiple CSV files with intelligent merging
  - Standardization of "FEMALE PARA" and "MALE PARA" to "PARAPROFESSIONAL"
  - Removal of "FEMALE" and "MALE" prefixes from all job classifications
  - Enhanced error handling for malformed dates and missing fields
- 🧭 **Navigation System**: 
  - District reports now include navigation back to their parent borough
  - Complete navigation hierarchy: Overview → Borough → District → School
  - Consistent navigation links across all report levels
- 📈 **Visualization Improvements**: 
  - Fixed bar chart displays showing integer values instead of floats
  - Cleaned up data source information display in headers
  - Enhanced chart formatting with proper number formatting
- 🗂️ **Data Management**: 
  - Combined dataset tracking with source file identification
  - Date range calculation across multiple data sources
  - Improved data validation and processing pipeline

### Technical
- 🔧 **Function Updates**: 
  - Modified `load_and_process_data()` to accept multiple CSV file paths
  - Added `clean_classification_gender()` function for standardizing job titles
  - Enhanced `get_data_date_range()` to handle multi-source data
  - Updated chart creation functions to ensure integer value display
- 📊 **Data Pipeline**: 
  - Robust CSV combination with error handling
  - Enhanced date parsing with fallback mechanisms
  - Standardized data type conversions throughout processing
  - Source file tracking integration
- 🎨 **UI/UX**: 
  - Simplified header information display (removed redundant data source listings)
  - Enhanced navigation breadcrumb system
  - Improved chart value formatting consistency

### Fixed
- 🔢 **Chart Display**: Bar charts now show clean integer values instead of floating-point numbers
- 📅 **Date Processing**: Resolved date parsing errors for string-format dates mixed with numeric formats
- 🧭 **Navigation**: Added missing back-to-borough links in district reports
- 📊 **Data Types**: Ensured consistent integer conversion for all count-based metrics

## [4.4.0] - 2025-07-03

### Added
- 🖥️ **Full-Width Layout**: Header and footer now extend the complete width of the screen for maximum visual impact
- 📐 **Optimized Content Width**: Increased content area to 1600px for better data presentation and readability
- 🎨 **Unified Design Language**: Complete alignment with Renewal project's professional layout and styling
- 🔄 **Layout Consistency**: Removed container-based layout in favor of full-width design for modern appearance

### Enhanced
- 🌐 **Screen Utilization**: Full-width header and footer maximize screen real estate usage
- 📊 **Content Display**: Wider content area (1600px) provides better accommodation for large data tables and charts
- 🎭 **Visual Impact**: Enhanced professional appearance with edge-to-edge header and footer design
- 🏗️ **Template Architecture**: Simplified HTML structure removing unnecessary container wrappers
- 📱 **Responsive Behavior**: Maintained responsive design while achieving full-width layout
- 🔧 **CSS Optimization**: Streamlined styling removing container-specific CSS for cleaner codebase

### Technical
- ♻️ **HTML Structure**: Updated template generation to remove container div wrapper
- 🎨 **CSS Updates**: Modified header, footer, and content CSS for full-width layout
- 📏 **Width Management**: Optimized max-width settings for header content and main content areas
- 🚀 **Performance**: Simplified DOM structure for better rendering performance

## [4.3.0] - 2025-07-03

### Added
- 🎨 **Enhanced Header/Footer Design**: Replicated improved CSS styling from Renewal project for consistent, professional appearance
- 📐 **Proportional Logo Sizing**: Updated logo to optimal 80px height for better proportion and visual balance
- 🔄 **Unified Branding**: Standardized header/footer layout across both ParaJobs and Renewal projects
- 📧 **Consistent Contact Information**: Maintained appropriate contact emails for each project (SubCentral@schools.nyc.gov for ParaJobs)

### Enhanced
- 🎭 **Modern Header Layout**: 
  - Left-aligned header text with improved spacing and typography hierarchy
  - Right-aligned logo with proper flex layout and sizing
  - Enhanced text shadow and font weights for professional appearance
  - Improved date information display with better opacity and formatting
- 🦶 **Professional Footer Styling**: 
  - Clean, centered layout with appropriate padding and margins
  - Consistent color scheme using primary brand colors
  - Improved link styling with hover effects
  - Unified footer structure across all report types
- 🏗️ **CSS Architecture**: 
  - Removed unnecessary decorative elements for cleaner appearance
  - Improved flex layout for better responsive behavior
  - Enhanced color consistency and professional styling
  - Better typography hierarchy with appropriate font weights

### Technical
- 🔧 **Template Improvements**: Updated `templates.py` with new header/footer CSS from Renewal project
- 📱 **Responsive Design**: Improved mobile and tablet viewing experience
- 🎯 **Cross-Project Consistency**: Aligned visual design language between ParaJobs and Renewal projects

## [4.2.0] - 2025-01-02

### Added
- 📋 **Updated Documentation**: Comprehensive README.md updates reflecting modular architecture
- 🏗️ **Architecture Documentation**: Detailed explanation of modular file structure and responsibilities
- 🚀 **Deployment Guidance**: Updated deployment instructions for both Netlify and manual deployments
- 📚 **Enhanced Project Overview**: Improved project description highlighting standardized branding and bold typography

### Enhanced
- 🎯 **Branding Consistency**: Removed "NYCDOE" references throughout documentation in favor of "NYC Public Schools"
- 📖 **Technical Documentation**: Updated all technical references to point to the new modular entry point
- 🔧 **Configuration Updates**: Netlify build command updated to use `para_fillrate_modular.py`

### Documentation
- Updated architecture section to reflect current modular structure
- Enhanced feature descriptions to include bold typography and logo standardization
- Improved troubleshooting section with current file references
- Added comprehensive module descriptions and responsibilities

## [4.1.0] - 2025-01-02

### Added
- 🎨 **Bold Header Titles**: Enhanced visual hierarchy with bold main titles (font-weight: 700) and semi-bold subtitles (font-weight: 600)
- 🔗 **Universal Logo Compatibility**: Implemented relative path system that works both locally and on Netlify deployment
- 📂 **Smart Logo Management**: Logo copying functionality for deployment while using efficient relative paths
- 🌐 **Production-Ready Logo Display**: Logo now displays correctly in both local development and deployed environments

### Fixed
- 🌐 **Cross-Platform Logo Display**: Fixed logo path issues that prevented display on Netlify while maintaining local functionality
- 🔄 **Relative Path Implementation**: Switched from absolute paths to relative paths for broader compatibility:
  - Main dashboard: `Horizontal_logo_White_PublicSchools.png` (same directory)
  - Borough reports: `../Horizontal_logo_White_PublicSchools.png` (one level up)
  - District/School reports: Various levels of `../` based on directory depth
- ✅ **Logo Asset Management**: Ensured logo files are properly copied to output directory for deployment

### Enhanced
- 💪 **Typography Improvements**: Strengthened visual hierarchy with bold titles for better readability
- 🎯 **Deployment Optimization**: Streamlined logo handling for both local development and production deployment
- 🔧 **Asset Pipeline**: Improved asset management for web deployment compatibility

## [4.0.0] - 2025-07-02

### Added
- 🏗️ **Complete Codebase Modularization**: Refactored the monolithic script into specialized modules
  - `para_fillrate_modular.py`: New main entry point for the application
  - `data_processing.py`: Data loading, cleaning, and summary statistics functions
  - `chart_utils.py`: Chart generation utilities for all visualization types
  - `templates.py`: HTML/CSS/JS templates and helper functions
  - `report_generators.py`: District, school, and specialized report generation
- 🔄 **Improved Code Organization**: Clear separation of concerns for better maintainability
- 🔧 **Standardized Module Imports**: Structured imports with explicit function naming
- 📦 **Encapsulated Functionality**: Self-contained modules that can be reused and tested independently
- 🧪 **Improved Testability**: Better structure allows for easier unit testing

### Enhanced
- 🎨 **Consistent Logo Usage**: Standardized white PNG logo across all reports
- 📋 **Removed "NYCDOE" from Report Titles**: Cleaner, more professional titles
- 🔗 **Optimized Resource Paths**: Efficient logo file referencing from project root
- 🧩 **Improved Header Implementation**: Consistent header across all report types
- 📱 **Responsive Design Improvements**: Better handling on mobile devices

### Technical Improvements
- Legacy code preserved as reference but excluded from version control
- Improved error handling and logging throughout the application
- Centralized configuration in main script
- Enhanced documentation with detailed function descriptions
- Netlify deployment configuration updated to use new modular entry point

## [3.3.0] - 2025-07-02

### Added
- 🔄 **Four-Way Comparison in School Reports**: Replaced "Key Insights" section with comprehensive comparison system
  - Citywide vs Borough vs District vs School performance comparison
  - Color-coded comparison cards with distinct styling for each administrative level
  - Consistent layout matching borough and district reports
- 🎨 **Enhanced Visual Hierarchy**: Positioned comparison section after pie charts for better flow
- 📊 **Integer Bar Chart Values**: Fixed bar chart text labels to display clean integers instead of floats
  - Applied `int()` conversion to all bar chart value displays
  - Improved readability with comma-separated thousands formatting
- 🧩 **Alternative Table Layout**: Preserved original table-based comparison as commented code for future reference

### Enhanced
- 🎯 **Report Consistency**: Unified comparison section layout across all report types
- 🎨 **School Card Styling**: Added unique orange gradient for school comparison cards
- 📱 **Responsive Design**: Added mobile-friendly responsive grid for comparison cards
- 🔧 **Code Organization**: Maintained backward compatibility while implementing new features

### Technical Improvements
- Updated `create_school_report()` function with new comparison logic
- Added CSS styles for school comparison cards (`comparison-card.school`)
- Implemented responsive design for comparison grid on mobile devices
- Enhanced data calculation functions for multi-level statistics
- Preserved alternative implementation as documentation

## [3.2.0] - 2025-07-02

### Fixed
- 🔧 **Windows File Path Compatibility**: Resolved "Invalid argument" errors for file creation
  - Enhanced filename sanitization using comprehensive regex pattern `r'[<>:"/\\|?*\n\r\t]'`
  - Added `.strip()` to remove leading/trailing whitespace from filenames
  - Implemented filename length limits (200 characters) to prevent Windows path length issues
  - Added explicit directory existence checks with `os.makedirs(exist_ok=True)`
- 📊 **Consistent File Naming**: Applied uniform sanitization across all report types
  - Fixed school report file naming (bar charts, pie charts, HTML reports)
  - Fixed district and borough report file naming consistency
  - Ensured HTML iframe references match actual generated file names
- 🔢 **District Sorting**: Confirmed numeric sorting implementation
  - Districts now properly sorted as D2, D3, ..., D11, D12 (not D11, D12, D2, D3)
  - Applied `key=int` sorting in district lists and summary tables
  - Enhanced district summary table generation with proper numeric ordering

### Enhanced
- 🛠️ **Error Handling**: Improved robustness for file system operations
- 📁 **File Management**: Added comprehensive directory creation before file writes
- 🎯 **Code Quality**: Standardized file path handling across all functions
- 📊 **Report Generation**: More reliable chart and report file creation

### Technical Improvements
- Updated `create_school_report()` function with enhanced file path sanitization
- Updated `create_district_report()` function with consistent naming patterns
- Updated `create_borough_report()` function with improved file handling
- Added safety checks for Windows file system limitations
- Improved error messages and debugging information

## [3.1.0] - 2025-07-01

### Added
- 📅 **Data Period Display**: Added date range information to all reports showing earliest and latest job start dates
- 🕒 **Excel Date Parsing**: Automatic conversion of Excel serial date format to human-readable dates
- 📈 **Enhanced Data Transparency**: Clear indication of data coverage period on dashboard headers
- 🔄 **Automatic Date Detection**: Smart parsing of "Job Start" column with error handling

### Enhanced
- 🎨 **Report Headers**: Updated all report templates to display data period information
- 📊 **User Experience**: Improved data context with prominent date range display
- 🔧 **Error Handling**: Robust date parsing with fallback messages
- 📖 **Data Clarity**: Users can now clearly see the time period covered by the analysis

### Technical Improvements
- Added `get_data_date_range()` function for date range calculation
- Updated all report generation functions to include date range parameter
- Enhanced data loading with automatic date format conversion
- Improved error handling for date parsing edge cases

## [3.0.0] - 2024-12-31

### Added
- 🎨 **Modern CSS Framework**: Complete redesign with professional color scheme (#2C5282 primary)
- 📱 **Enhanced Responsive Design**: Improved mobile and tablet experience
- 🗂️ **Solid Table Headers**: Replaced gradients with solid colors for better readability
- 📊 **Table Overflow Handling**: Responsive table wrappers with horizontal scrolling
- 📏 **Expanded Container Width**: Increased from 1400px to 1600px for better data display
- 🧭 **Advanced Breadcrumb Navigation**: Improved hierarchical navigation system
- ⚡ **Performance Optimizations**: Embedded CSS and optimized layouts
- 🔧 **Bug Fixes**: Resolved DataFrame truth value ambiguity issues
- 📚 **Updated Documentation**: Enhanced LaTeX docs reflecting design changes
- 🚀 **Deployment Ready**: Prepared for GitHub commit and Netlify deployment

### Enhanced
- 🎯 **User Interface**: Professional, modern design with consistent styling
- 📊 **Data Presentation**: Improved table readability and chart integration
- 🌐 **Cross-Device Compatibility**: Seamless experience across all screen sizes
- 🔍 **Code Quality**: Fixed deprecation warnings and improved error handling
- 📖 **Documentation**: Updated README and technical documentation

### Technical Improvements
- Fixed ambiguous DataFrame boolean evaluation warnings
- Implemented modern CSS variables and responsive design patterns
- Enhanced table styling with sticky headers and overflow management
- Optimized HTML generation with embedded stylesheets
- Improved navigation structure and breadcrumb implementation

## [2.0.0] - 2025-01-07

### Added
- 🎨 **Complete UI Modernization**: Beautiful, responsive design with gradient backgrounds
- 📱 **Mobile-First Design**: Fully responsive layout that works on all devices
- 🌟 **Interactive Elements**: Hover effects, smooth transitions, and modern animations
- 🎯 **Enhanced Navigation**: Breadcrumb navigation and improved linking between reports
- 📊 **Advanced Visualizations**: Updated charts with better colors and interactivity
- 🔍 **DataTables Integration**: Sortable, searchable tables with pagination
- 🎨 **Professional Styling**: CSS3 features including gradients, shadows, and animations
- 📈 **Performance Metrics**: Detailed comparison cards for citywide vs borough vs district data
- 🌐 **Cross-Browser Compatibility**: Optimized for modern browsers
- 📄 **Comprehensive Documentation**: Detailed README and project documentation

### Enhanced
- 🏗️ **Code Architecture**: Improved organization and modularity
- 📊 **Data Processing**: More efficient data handling and processing
- 🎯 **User Experience**: Intuitive navigation and improved information hierarchy
- 🔧 **Error Handling**: Better error messages and graceful fallbacks
- 📱 **Accessibility**: Improved accessibility features and semantic HTML

### Fixed
- 🐛 **File Naming Issues**: Resolved special character handling in file names
- 📊 **Chart Rendering**: Fixed pie chart display issues
- 🔗 **Navigation Links**: Corrected relative path issues in reports
- 📱 **Mobile Layout**: Fixed responsive design issues on small screens

## [1.0.0] - 2024-12-15

### Added
- 📊 **Initial Analytics Engine**: Core data processing and analysis functionality
- 📈 **Basic Reporting**: HTML report generation for districts and schools
- 🗺️ **Geographic Analysis**: Borough and district-level breakdowns
- 📊 **Visualization Support**: Basic charts and tables
- 🔄 **Data Pipeline**: CSV processing and transformation
- 📁 **File Management**: Automated folder structure creation

### Features
- Fill rate analysis by location and job type
- Multi-language paraprofessional position tracking
- Borough and district-level reporting
- School-specific analytics
- Basic HTML dashboard generation

## [Unreleased]

### Planned
- 🔮 **Predictive Analytics**: Machine learning models for forecasting staffing needs
- 📊 **Advanced Dashboards**: Interactive dashboards with real-time updates
- 🔄 **API Integration**: Direct integration with NYCDOE systems
- 📱 **Mobile App**: Dedicated mobile application for on-the-go access
- 🔔 **Alerts System**: Automated notifications for critical staffing needs
- 🎯 **Recommendation Engine**: AI-powered hiring recommendations

### Technical Debt
- [ ] Migrate to modern Python packaging (pyproject.toml)
- [ ] Add comprehensive test suite
- [ ] Implement CI/CD pipeline
- [ ] Add type hints throughout codebase
- [ ] Optimize database queries for large datasets

---

## Version History

- **v2.0.0**: Modern UI and enhanced functionality
- **v1.0.0**: Initial release with basic analytics

## Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
