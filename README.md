# NYC Public Schools Paraprofessional Jobs Fill Rate Analytics Dashboard

[![Deploy to Netlify](https://img.shields.io/badge/deploy-netlify-00c7b7?style=flat-square&logo=netlify)](https://app.netlify.com/start/deploy?repository=https://github.com/yourusername/ParaJobs)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive analytics dashboard for tracking and visualizing NYC Department of Education substitute paraprofessional job fill rates across all districts, boroughs, and schools. Features a modern, modular architecture with standardized branding and enhanced visual design.

## 🎯 Overview

This project analyzes substitute paraprofessional job postings and fill rates across the NYC Public Schools system, providing detailed insights into:

- **Fill Rate Analysis**: Comprehensive tracking of filled vs. unfilled positions
- **Geographic Breakdown**: Analysis by borough, district, and individual schools
- **Multi-language Support**: Specialized tracking for bilingual paraprofessional positions
- **Interactive Dashboards**: Modern, responsive HTML reports with interactive charts and bold typography
- **Time-series Analysis**: Historical trends and patterns in job filling
- **Data Period Tracking**: Clear display of date ranges for all analyzed data
- **Standardized Branding**: Professional NYC Public Schools logo integration across all reports

## 🚀 Features

### 📊 Interactive Reports
- **Citywide Overview**: High-level summary with key performance indicators and data period display
- **Borough Reports**: Detailed analysis for each NYC borough with modern, elegant styling
- **District Reports**: Individual district performance with enhanced data presentation and responsive design
- **School Reports**: Granular analysis for every school with professional layout, improved tables, and comprehensive comparison features
- **Bold Typography**: Enhanced visual hierarchy with bold report titles throughout the dashboard
- **Consistent Branding**: NYC Public Schools logo displayed prominently on all reports with correct sizing and positioning

### 📈 Visualizations
- **Pie Charts**: Distribution of filled/unfilled positions by classification
- **Bar Charts**: Comparative analysis across different job types with integer value displays
- **Enhanced Summary Tables**: Professional tables with solid-color headers and responsive overflow handling
- **Trend Analysis**: Fill rate patterns and performance metrics with modern, card-based interface
- **Comparison Cards**: Four-way comparison system (Citywide vs Borough vs District vs School) with color-coded cards
- **Date Range Display**: Clear indication of data period on all reports

### 🎨 Modern Design Features
- **Full-Width Layout**: Professional edge-to-edge header and footer design that spans the entire screen width
- **Enhanced Container Width**: Optimized 1500px content width for better data display and readability
- **Clean Header/Footer**: Left-aligned text with proportional 80px logo placement and bold typography
- **Responsive Design**: Optimized for desktop, tablet, and mobile viewing
- **Enhanced Tables**: Improved readability with solid-color headers and responsive containers
- **Hover Effects**: Interactive elements with smooth transitions
- **Professional Styling**: Consistent color scheme and typography throughout with NYC Public Schools branding
- **Comparison System**: Visual comparison cards with distinct color coding for different administrative levels
- **Modern CSS**: Clean, professional header/footer design with improved spacing and typography hierarchy

### 🌐 Multi-language Support
Specialized tracking for paraprofessional positions requiring:
- Spanish
- Arabic
- Bengali
- Mandarin
- Russian
- Korean
- French
- And many other languages

## 🏗️ Architecture

The project follows a modern modular architecture for maintainability and scalability:

```
ParaJobs/
├── 📁 Core Modules (Modular Architecture)
│   ├── para_fillrate_modular.py   # Main entry point - orchestrates the entire pipeline
│   ├── data_processing.py         # Data loading, cleaning, and summary statistics
│   ├── chart_utils.py             # Chart generation with Plotly
│   ├── templates.py               # HTML/CSS/JS templates and styling components
│   ├── report_generators.py       # Report generation for districts and schools
│   └── Horizontal_logo_White_PublicSchools.png  # Official NYC Public Schools logo
│
├── 📁 Fill Rate Data/           # Raw CSV data files
│   ├── mayjobs.csv              # Primary job data
│   └── nycdoe_job_summary.csv   # Summary statistics
│
├── 📁 nycdoe_reports/          # Generated HTML reports (created at runtime)
│   ├── index.html              # Main dashboard
│   ├── overall_bar_chart.html  # Overall visualization
│   ├── Horizontal_logo_White_PublicSchools.png  # Logo copy for deployment
│   ├── Borough_*/              # Borough-specific reports
│   └── District_*/             # District and school reports
│
├── 📄 Documentation & Configuration
│   ├── README.md               # This comprehensive guide
│   ├── CHANGELOG.md            # Version history and updates
│   ├── script_documentation.md # Technical documentation
│   ├── requirements.txt        # Python dependencies
│   ├── netlify.toml           # Netlify deployment configuration
│   └── .gitignore             # Version control exclusions
│
└── 📄 Legacy Files (Ignored in .gitignore)
    ├── para_fillrate_by_location.py # Original monolithic script
    ├── para_fillrate_oo.py         # Object-oriented implementation
    └── debug_test.py               # Development testing script
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Required Python packages (see requirements.txt)

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/ParaJobs.git
cd ParaJobs

# Install dependencies
pip install -r requirements.txt

# Run the analysis (using the new modular script)
python para_fillrate_modular.py
```

### Dependencies
```python
pandas>=1.3.0
plotly>=5.0.0
numpy>=1.21.0
```

## 📊 Data Sources

The system processes CSV files containing:
- Job postings data
- Fill status information
- Geographic location codes
- Classification details
- Timestamp information

### Data Fields
- **Classification**: Type of paraprofessional position
- **Type**: Job type (Vacancy or Absence)
- **Status**: Current fill status
- **Location**: School identifier
- **District**: School district number
- **Date/Time Information**: When jobs were posted and filled

## 🎨 Modern UI Features (Version 4.3)

### Visual Design & Branding
- **NYC Public Schools Logo**: Official white PNG logo (80px height) optimally sized and positioned on all reports
- **Full-Width Layout**: Professional edge-to-edge header and footer design spanning entire screen width
- **Bold Typography**: Enhanced visual hierarchy with bold report titles (font-weight: 700 for h1, 600 for h2)
- **Professional Header Layout**: Left-aligned text with right-aligned logo and optimal spacing
- **Consistent Footer**: Clean, professional "Property of the New York City Department of Education" footer
- **Relative Path Handling**: Smart logo path resolution for all report types and directory structures

### Responsive Layout & Design
- **Enhanced Container Width**: Optimized 1500px content width for superior data display and readability
- **Mobile-Friendly Design**: Works perfectly on all devices with responsive breakpoints
- **Professional Styling**: Clean, modern interface with consistent color scheme (#2C5282 primary)
- **Enhanced Typography**: Optimized font choices with proper visual hierarchy
- **Interactive Elements**: Smooth hover effects and intuitive user interactions
- **Solid Color Headers**: Improved table readability with solid primary color headers
- **Optimized Tables**: Enhanced overflow handling and responsive table design
- **Comparison Cards**: Color-coded cards for multi-level statistical comparisons

### Navigation & UX
- **Breadcrumb Navigation**: Intuitive hierarchical navigation system
- **Quick Access Links**: Direct navigation to related reports and sections
- **Table Enhancements**: Sticky headers, improved sorting, and better data presentation
- **Performance Optimized**: Faster loading with embedded CSS and optimized layouts
- **Multi-Level Comparison**: School reports now include citywide, borough, district, and school-level performance comparisons

### Chart Improvements
- **Integer Display**: Bar chart values now display as clean integers instead of decimals
- **Enhanced Readability**: Improved text positioning and formatting in all charts
- **Consistent Styling**: Unified chart appearance across all report levels

### Technical Improvements
- **Full-Width Architecture**: Header and footer span entire viewport width for professional appearance
- **Optimized Container Width**: 1500px content width for enhanced data presentation
- **Responsive Tables**: Horizontal scrolling on smaller screens with preserved functionality
- **Modern CSS**: CSS Grid and Flexbox layouts for optimal rendering
- **Embedded Styling**: Reduced HTTP requests for improved performance

## 📱 Deployment

### Netlify Deployment
This project is optimized for Netlify deployment with automatic logo handling:

1. Connect your GitHub repository to Netlify
2. Set build command: `python para_fillrate_modular.py`
3. Set publish directory: `nycdoe_reports`
4. Deploy! (Logo files are automatically copied for correct display)

The modular architecture ensures all assets, including the NYC Public Schools logo, are properly deployed and display correctly in both local and production environments.

### Manual Deployment
```bash
# Generate reports using the modular architecture
python para_fillrate_modular.py

# Upload nycdoe_reports/ directory to your web server
# Logo and all assets are automatically included
```

## 📈 Key Metrics & KPIs

### Fill Rate Metrics
- **Overall Fill Rate**: Percentage of all positions successfully filled
- **Vacancy Fill Rate**: Specifically for permanent position vacancies
- **Absence Fill Rate**: For temporary absence coverage
- **Response Time**: Average time to fill positions

### Geographic Performance
- **Borough Comparison**: Relative performance across NYC boroughs
- **District Rankings**: Best and worst performing districts
- **School-level Analysis**: Individual school performance metrics

### Classification Analysis
- **Position Type Demand**: Most in-demand paraprofessional classifications
- **Language Specialist Needs**: Bilingual position requirements
- **Seasonal Patterns**: Time-based filling trends

## 🔄 Data Pipeline

1. **Data Ingestion**: CSV files are processed and cleaned
2. **Geographic Mapping**: Schools mapped to districts and boroughs
3. **Classification Processing**: Job types categorized and standardized
4. **Statistical Analysis**: Fill rates and performance metrics calculated
5. **Visualization Generation**: Interactive charts and tables created
6. **Report Assembly**: HTML pages generated with responsive design

## 🎯 Strategic Insights

### Hiring Recommendations
- **High-Need Areas**: Geographic regions requiring attention
- **Staffing Gaps**: Unfilled position patterns
- **Resource Allocation**: Data-driven staffing decisions
- **Performance Benchmarks**: Best practices from high-performing areas

### Operational Improvements
- **Process Optimization**: Identifying bottlenecks in hiring
- **Predictive Analytics**: Forecasting staffing needs
- **Quality Metrics**: Tracking improvement over time

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## � Troubleshooting

### File Path Issues (Fixed in v3.2.0)

If you encounter errors like `[Errno 22] Invalid argument` when generating reports, this has been resolved with enhanced file path sanitization:

**Error Example:**
```
Error: [Errno 22] Invalid argument: 'nycdoe_reports\\District_27\\Schools\\School_Q351\\Q351_bar_chart.html'
```

**Solution Implemented:**
- Enhanced filename sanitization using regex pattern `r'[<>:"/\\|?*\n\r\t]'`
- Added automatic `.strip()` to remove problematic whitespace
- Implemented filename length limits (200 characters max)
- Added explicit directory creation before file operations
- Applied consistent sanitization across all report types

### District Sorting

Districts are now properly sorted numerically (D2, D3, ..., D11, D12) rather than alphabetically. This ensures logical ordering in all reports and navigation links.

### Performance Tips

- **Large Datasets**: For datasets over 100k records, consider increasing system memory
- **Network Drives**: Run from local drives for better I/O performance
- **Browser Compatibility**: Modern browsers (Chrome 80+, Firefox 75+, Safari 13+) recommended for optimal chart rendering

### Common Issues

1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **Data Format**: Ensure CSV headers match expected column names
3. **Date Parsing**: Excel serial dates are automatically converted
4. **Memory Usage**: Close unused applications for large dataset processing

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support

For questions, issues, or contributions:
- **GitHub Issues**: Report bugs or request features
- **Documentation**: Comprehensive guides and API documentation
- **Community**: Join our discussions and share insights

## 🏆 Acknowledgments

- NYC Department of Education for data access
- Education workforce analytics community
- Open source visualization libraries (Plotly, Pandas)

---

**Built with ❤️ for educational equity and workforce analytics**

> This tool helps ensure that every student in NYC has access to the paraprofessional support they need by providing actionable insights into staffing patterns and hiring effectiveness.
