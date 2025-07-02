# Changelog

All notable changes to the NYCDOE Paraprofessional Jobs Fill Rate Analytics project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
