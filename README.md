# NYCDOE Paraprofessional Jobs Fill Rate Analytics Dashboard

[![Deploy to Netlify](https://img.shields.io/badge/deploy-netlify-00c7b7?style=flat-square&logo=netlify)](https://app.netlify.com/start/deploy?repository=https://github.com/yourusername/ParaJobs)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive analytics dashboard for tracking and visualizing NYC Department of Education (NYCDOE) substitute paraprofessional job fill rates across all districts, boroughs, and schools.

## 🎯 Overview

This project analyzes substitute paraprofessional job postings and fill rates across the NYCDOE system, providing detailed insights into:

- **Fill Rate Analysis**: Comprehensive tracking of filled vs. unfilled positions
- **Geographic Breakdown**: Analysis by borough, district, and individual schools
- **Multi-language Support**: Specialized tracking for bilingual paraprofessional positions
- **Interactive Dashboards**: Modern, responsive HTML reports with interactive charts
- **Time-series Analysis**: Historical trends and patterns in job filling
- **Data Period Tracking**: Clear display of date ranges for all analyzed data

## 🚀 Features

### 📊 Interactive Reports
- **Citywide Overview**: High-level summary with key performance indicators and data period display
- **Borough Reports**: Detailed analysis for each NYC borough with modern, elegant styling
- **District Reports**: Individual district performance with enhanced data presentation and responsive design
- **School Reports**: Granular analysis for every school with professional layout and improved tables

### 📈 Visualizations
- **Pie Charts**: Distribution of filled/unfilled positions by classification
- **Bar Charts**: Comparative analysis across different job types
- **Enhanced Summary Tables**: Professional tables with solid-color headers and responsive overflow handling
- **Trend Analysis**: Fill rate patterns and performance metrics with modern, card-based interface
- **Date Range Display**: Clear indication of data period on all reports

### 🎨 Modern Design Features
- **Elegant UI**: Professional gradient headers and card-based layouts
- **Responsive Design**: Optimized for desktop, tablet, and mobile viewing
- **Enhanced Tables**: Improved readability with solid-color headers and responsive containers
- **Hover Effects**: Interactive elements with smooth transitions
- **Professional Styling**: Consistent color scheme and typography throughout

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

```
ParaJobs/
├── 📁 Fill Rate Data/           # Raw CSV data files
├── 📁 nycdoe_reports/          # Generated HTML reports
│   ├── index.html              # Main dashboard
│   ├── overall_summary_chart.html
│   ├── Borough_*/              # Borough-specific reports
│   └── District_*/             # District and school reports
├── para_fillrate_by_location.py # Main analytics engine
├── para_fillrate_oo.py         # Object-oriented implementation
└── README.md                   # This file
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

# Run the analysis
python para_fillrate_by_location.py
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

## 🎨 Modern UI Features (Version 3.0)

### Design Elements
- **Responsive Layout**: Mobile-friendly design that works perfectly on all devices
- **Professional Styling**: Clean, modern interface with consistent color scheme (#2C5282 primary)
- **Enhanced Typography**: Optimized font choices with proper visual hierarchy
- **Interactive Elements**: Smooth hover effects and intuitive user interactions
- **Solid Color Headers**: Improved table readability with solid primary color headers
- **Optimized Tables**: Enhanced overflow handling and responsive table design

### Navigation & UX
- **Breadcrumb Navigation**: Intuitive hierarchical navigation system
- **Quick Access Links**: Direct navigation to related reports and sections
- **Table Enhancements**: Sticky headers, improved sorting, and better data presentation
- **Performance Optimized**: Faster loading with embedded CSS and optimized layouts

### Technical Improvements
- **Container Width**: Increased from 1400px to 1600px for better data display
- **Responsive Tables**: Horizontal scrolling on smaller screens with preserved functionality
- **Modern CSS**: CSS Grid and Flexbox layouts for optimal rendering
- **Embedded Styling**: Reduced HTTP requests for improved performance

## 📱 Deployment

### Netlify Deployment
This project is optimized for Netlify deployment:

1. Connect your GitHub repository to Netlify
2. Set build command: `python para_fillrate_by_location.py`
3. Set publish directory: `nycdoe_reports`
4. Deploy!

### Manual Deployment
```bash
# Generate reports
python para_fillrate_by_location.py

# Upload nycdoe_reports/ directory to your web server
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

## 📄 License

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
