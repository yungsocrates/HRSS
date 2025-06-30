"""
Object-Oriented Paraprofessional Fill Rate Report Generator
Refactored version with classes for better organization and maintainability
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# === DATA CLASSES ===
@dataclass
class JobMetrics:
    """Data class to hold job statistics"""
    vacancy_filled: int = 0
    vacancy_unfilled: int = 0
    absence_filled: int = 0
    absence_unfilled: int = 0
    
    @property
    def total_vacancy(self) -> int:
        return self.vacancy_filled + self.vacancy_unfilled
    
    @property
    def total_absence(self) -> int:
        return self.absence_filled + self.absence_unfilled
    
    @property
    def total_jobs(self) -> int:
        return self.total_vacancy + self.total_absence
    
    @property
    def vacancy_fill_pct(self) -> float:
        return (self.vacancy_filled / self.total_vacancy * 100) if self.total_vacancy > 0 else 0.0
    
    @property
    def absence_fill_pct(self) -> float:
        return (self.absence_filled / self.total_absence * 100) if self.total_absence > 0 else 0.0
    
    @property
    def overall_fill_pct(self) -> float:
        total_filled = self.vacancy_filled + self.absence_filled
        return (total_filled / self.total_jobs * 100) if self.total_jobs > 0 else 0.0
    
    def __add__(self, other: 'JobMetrics') -> 'JobMetrics':
        """Add two JobMetrics together"""
        return JobMetrics(
            vacancy_filled=self.vacancy_filled + other.vacancy_filled,
            vacancy_unfilled=self.vacancy_unfilled + other.vacancy_unfilled,
            absence_filled=self.absence_filled + other.absence_filled,
            absence_unfilled=self.absence_unfilled + other.absence_unfilled
        )


# === UTILITY FUNCTIONS ===
def inspect_csv_structure(csv_file_path: str):
    """Inspect the CSV file structure to understand the data format"""
    try:
        df = pd.read_csv(csv_file_path)
        print(f"CSV File: {csv_file_path}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nColumn data types:")
        print(df.dtypes)
        print("\nSample values for each column:")
        for col in df.columns:
            print(f"{col}: {df[col].dropna().unique()[:5]}")
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None


# === UTILITY CLASSES ===
class DataProcessor:
    """Handles data loading and processing"""
    
    FILLED_STATUSES = [
        'Finished/Admin Assigned',
        'Finished/IVR Assigned',
        'Finished/Pre Arranged',
        'Finished/Web Sub Search'
    ]
    
    BOROUGH_MAP = {
        'M': 'Manhattan',
        'K': 'Brooklyn', 
        'Q': 'Queens',
        'X': 'Bronx',
        'R': 'Staten Island'
    }
    
    @classmethod
    def load_and_process_data(cls, csv_file_path: str) -> pd.DataFrame:
        """Load CSV data and process it for dashboard display"""
        df = pd.read_csv(csv_file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Debug: Print available columns
        print("Available columns in CSV:", df.columns.tolist())
        
        # Your CSV has: Job #, Status, Specified Sub, Classification, Location, District, Type
        # Map to our expected column names
        if 'Job #' in df.columns:
            df['Job_Number'] = df['Job #']
        
        # Status column should already exist
        if 'Status' not in df.columns:
            raise ValueError("Required 'Status' column not found in CSV")
        
        # Classification column should already exist  
        if 'Classification' not in df.columns:
            raise ValueError("Required 'Classification' column not found in CSV")
            
        # Location column should already exist
        if 'Location' not in df.columns:
            raise ValueError("Required 'Location' column not found in CSV")
            
        # District column should already exist
        if 'District' not in df.columns:
            raise ValueError("Required 'District' column not found in CSV")
        else:
            # Clean and convert District to integer, dropping rows with NaN districts
            print(f"Original data size: {len(df)} rows")
            df = df.dropna(subset=['District'])  # Remove rows with NaN districts
            print(f"After removing NaN districts: {len(df)} rows")
            df['District'] = df['District'].astype(int)
            
        # Type column should already exist
        if 'Type' not in df.columns:
            raise ValueError("Required 'Type' column not found in CSV")
        else:
            df['Type'] = df['Type'].str.strip().str.title()
        
        # Add borough column based on location
        df['Borough'] = df['Location'].apply(cls._get_borough_from_location)
        
        # Clean location names for folder creation
        df['Location_Clean'] = df['Location'].str.replace(r'[<>:"/\\|?*]', '_', regex=True)
        
        # Create fill status based on Status column
        df['Fill_Status'] = df['Status'].apply(
            lambda x: 'Filled' if x in cls.FILLED_STATUSES else 'Unfilled'
        )
        
        # Create combined category for Type + Fill Status
        df['Type_Fill_Status'] = df['Type'] + '_' + df['Fill_Status']
        
        # Debug: Print sample of processed data
        print(f"Processed {len(df)} records")
        print("Sample of processed data:")
        print(df[['Location', 'District', 'Borough', 'Classification', 'Type', 'Status', 'Type_Fill_Status']].head())
        print(f"Unique districts: {sorted(df['District'].unique())}")
        print(f"Unique boroughs: {df['Borough'].unique()}")
        print(f"Unique types: {df['Type'].unique()}")
        print(f"Unique statuses: {df['Status'].unique()}")
        print(f"Unique classifications: {df['Classification'].unique()}")
        
        # Debug: Check district-borough mapping
        district_borough_map = df.groupby('District')['Borough'].unique()
        multi_borough_districts = []
        for district, boroughs in district_borough_map.items():
            if len(boroughs) > 1:
                multi_borough_districts.append((district, boroughs))
        
        if multi_borough_districts:
            print(f"\nWARNING: Districts appearing in multiple boroughs:")
            for district, boroughs in multi_borough_districts:
                print(f"  District {district}: {list(boroughs)}")
                # Show sample locations for this district
                sample_locations = df[df['District'] == district][['Location', 'Borough']].drop_duplicates()
                print(f"    Sample locations: {sample_locations.to_dict('records')[:3]}")
        
        return df
    
    @classmethod
    def _get_borough_from_location(cls, location: str) -> str:
        """Extract borough from location based on first letter"""
        if pd.isna(location) or not location:
            return 'Unknown'
        
        first_char = location.strip()[0].upper()
        return cls.BOROUGH_MAP.get(first_char, 'Unknown')


class HTMLFormatter:
    """Handles HTML formatting utilities"""
    
    @staticmethod
    def format_pct(x) -> str:
        return f"{x:.1f}%" if isinstance(x, (int, float)) else str(x)
    
    @staticmethod
    def format_int(x) -> str:
        return f"{int(x):,}" if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else str(x)
    
    @staticmethod
    def clean_classification_for_display(classification: str) -> str:
        return classification.replace(' SPEAKING PARA', '')
    
    @staticmethod
    def get_professional_footer() -> str:
        """Return the professional footer HTML"""
        return f"""
        <div class="footer">
            <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">Created by HR School Support</div>
            <div style="margin-bottom:6px;">For internal use only.</div>
            <div style="margin-bottom:6px;">For inquiries, please contact <a href="mailto:SubCentral@schools.nyc.gov">SubCentral@schools.nyc.gov</a>.</div>
            <div style="font-size:13px; color:#e0e0e0;">&copy; {pd.Timestamp.now().year} Property of the NYCDOE</div>
        </div>
        """
    
    @staticmethod
    def get_base_css() -> str:
        """Return the base CSS styles"""
        return """
        <style>
            body { font-family: Verdana, sans-serif; margin: 20px; }
            h1 { color: #2E86AB; text-align: center; }
            h2 { color: #A61E1E; border-bottom: 2px solid #ccc; }
            .table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            .table th { background-color: #f2f2f2; font-weight: bold; }
            .pie-container { display: flex; flex-wrap: wrap; justify-content: space-around; }
            .navigation { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .summary-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .footer { background-color: #2E86AB; color: white; text-align: center; padding: 20px; margin-top: 40px; border-radius: 5px; font-size: 14px; }
            .footer a { color: #FFD700; text-decoration: none; }
            .footer a:hover { text-decoration: underline; }
        </style>
        """


# === BASE CLASSES ===
class BaseEntity(ABC):
    """Base class for all geographic entities (School, District, Borough)"""
    
    def __init__(self, name: str, df: pd.DataFrame):
        self.name = name
        self.df = df
        self._metrics_by_classification: Dict[str, JobMetrics] = {}
        self._total_metrics: Optional[JobMetrics] = None
        self._process_data()
    
    @abstractmethod
    def _process_data(self):
        """Process the data to calculate metrics"""
        pass
    
    @property
    def total_metrics(self) -> JobMetrics:
        """Get total metrics across all classifications"""
        if self._total_metrics is None:
            total = JobMetrics()
            for metrics in self._metrics_by_classification.values():
                total += metrics
            self._total_metrics = total
        return self._total_metrics
    
    @property
    def classifications(self) -> List[str]:
        """Get list of classifications"""
        return list(self._metrics_by_classification.keys())
    
    def get_metrics_for_classification(self, classification: str) -> JobMetrics:
        """Get metrics for a specific classification"""
        return self._metrics_by_classification.get(classification, JobMetrics())


class BaseReport(ABC):
    """Base class for all report generators"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.formatter = HTMLFormatter()
    
    @abstractmethod
    def generate(self) -> str:
        """Generate the report and return the file path"""
        pass
    
    def _create_bar_chart(self, entity_name: str, metrics_by_classification: Dict[str, JobMetrics], 
                         output_file: str, width: int = 1200) -> str:
        """Create a grouped bar chart"""
        fig = go.Figure()
        
        classifications = list(metrics_by_classification.keys())
        clean_names = [self.formatter.clean_classification_for_display(c) for c in classifications]
        
        # Add traces
        fig.add_trace(go.Bar(
            name='Vacancy Filled',
            x=clean_names,
            y=[metrics_by_classification[c].vacancy_filled for c in classifications],
            marker_color='darkgreen',
            text=[metrics_by_classification[c].vacancy_filled for c in classifications],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Vacancy Unfilled',
            x=clean_names,
            y=[metrics_by_classification[c].vacancy_unfilled for c in classifications],
            marker_color='lightcoral',
            text=[metrics_by_classification[c].vacancy_unfilled for c in classifications],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Absence Filled',
            x=clean_names,
            y=[metrics_by_classification[c].absence_filled for c in classifications],
            marker_color='forestgreen',
            text=[metrics_by_classification[c].absence_filled for c in classifications],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Absence Unfilled',
            x=clean_names,
            y=[metrics_by_classification[c].absence_unfilled for c in classifications],
            marker_color='red',
            text=[metrics_by_classification[c].absence_unfilled for c in classifications],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f'Jobs by Classification and Type - {entity_name}',
            xaxis_title='Classification',
            yaxis_title='Number of Jobs',
            barmode='group',
            height=500,
            width=width
        )
        
        pyo.plot(fig, filename=output_file, auto_open=False)
        return output_file
    
    def _create_pie_charts(self, entity_name: str, metrics_by_classification: Dict[str, JobMetrics],
                          output_dir: str, file_prefix: str) -> str:
        """Create pie charts for each classification"""
        pie_charts_html = ""
        
        for classification, metrics in metrics_by_classification.items():
            if metrics.total_jobs > 0:
                safe_classification = re.sub(r'[<>:"/\\|?*]', '_', classification)
                
                pie_fig = go.Figure(data=[go.Pie(
                    labels=['Vacancy Filled', 'Vacancy Unfilled', 'Absence Filled', 'Absence Unfilled'],
                    values=[metrics.vacancy_filled, metrics.vacancy_unfilled, 
                           metrics.absence_filled, metrics.absence_unfilled],
                    hole=0.3,
                    marker_colors=['darkgreen', 'lightcoral', 'forestgreen', 'red'],
                    textinfo='value+percent',
                    textposition='inside',
                    textfont=dict(size=14)
                )])
                
                pie_fig.update_layout(
                    title=dict(
                        text=f"{classification}<br>({metrics.total_jobs:,} total jobs)",
                        y=0.95,
                        x=0.5,
                        xanchor='center',
                        yanchor='top',
                        font=dict(size=16)
                    ),
                    height=450,
                    width=400,
                    showlegend=True,
                    margin=dict(t=60, b=40, l=40, r=40)
                )
                
                pie_file = os.path.join(output_dir, f'{file_prefix}_{safe_classification}_pie.html')
                pyo.plot(pie_fig, filename=pie_file, auto_open=False)
                
                pie_charts_html += f'<iframe src="{os.path.basename(pie_file)}" width="420" height="470" frameborder="0"></iframe>\n'
        
        return pie_charts_html


# === ENTITY CLASSES ===
class School(BaseEntity):
    """Represents a single school"""
    
    def __init__(self, location: str, district_num: int, df: pd.DataFrame):
        self.location = location
        self.district_num = district_num
        self.location_clean = re.sub(r'[<>:"/\\|?*]', '_', location)
        super().__init__(location, df)
    
    def _process_data(self):
        """Process school data to calculate metrics by classification"""
        school_df = self.df[(self.df['Location'] == self.name) & (self.df['District'] == self.district_num)]
        
        for classification in school_df['Classification'].unique():
            class_df = school_df[school_df['Classification'] == classification]
            
            metrics = JobMetrics()
            for _, row in class_df.iterrows():
                if row['Type_Fill_Status'] == 'Vacancy_Filled':
                    metrics.vacancy_filled += 1
                elif row['Type_Fill_Status'] == 'Vacancy_Unfilled':
                    metrics.vacancy_unfilled += 1
                elif row['Type_Fill_Status'] == 'Absence_Filled':
                    metrics.absence_filled += 1
                elif row['Type_Fill_Status'] == 'Absence_Unfilled':
                    metrics.absence_unfilled += 1
            
            if metrics.total_jobs > 0:
                self._metrics_by_classification[classification] = metrics


class District(BaseEntity):
    """Represents a school district"""
    
    def __init__(self, district_num: int, df: pd.DataFrame):
        self.district_num = district_num
        self.schools: Dict[str, School] = {}
        super().__init__(f"District {district_num}", df)
    
    def _process_data(self):
        """Process district data to calculate metrics and create schools"""
        district_df = self.df[self.df['District'] == self.district_num]
        
        # Create schools
        for location in district_df['Location'].unique():
            self.schools[location] = School(location, self.district_num, self.df)
        
        # Calculate district-level metrics by classification
        for classification in district_df['Classification'].unique():
            class_df = district_df[district_df['Classification'] == classification]
            
            metrics = JobMetrics()
            for _, row in class_df.iterrows():
                if row['Type_Fill_Status'] == 'Vacancy_Filled':
                    metrics.vacancy_filled += 1
                elif row['Type_Fill_Status'] == 'Vacancy_Unfilled':
                    metrics.vacancy_unfilled += 1
                elif row['Type_Fill_Status'] == 'Absence_Filled':
                    metrics.absence_filled += 1
                elif row['Type_Fill_Status'] == 'Absence_Unfilled':
                    metrics.absence_unfilled += 1
            
            if metrics.total_jobs > 0:
                self._metrics_by_classification[classification] = metrics
    
    @property
    def borough(self) -> str:
        """Get the borough this district belongs to"""
        district_df = self.df[self.df['District'] == self.district_num]
        if not district_df.empty:
            return district_df['Borough'].iloc[0]
        return 'Unknown'
    
    def get_school_summary_data(self) -> List[Dict]:
        """Get summary data for all schools in this district"""
        summary_data = []
        for school_name, school in self.schools.items():
            metrics = school.total_metrics
            summary_data.append({
                'School': school_name,
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            })
        # Sort by school name alphabetically
        summary_data.sort(key=lambda x: x['School'])
        return summary_data


class Borough(BaseEntity):
    """Represents a borough"""
    
    def __init__(self, borough_name: str, df: pd.DataFrame):
        self.borough_name = borough_name
        self.districts: Dict[int, District] = {}
        super().__init__(borough_name, df)
    
    def _process_data(self):
        """Process borough data to calculate metrics (districts are assigned externally)"""
        borough_df = self.df[self.df['Borough'] == self.name]
        
        # Note: Districts are now created and assigned at the citywide level
        # This method only calculates borough-level metrics by classification
        for classification in borough_df['Classification'].unique():
            class_df = borough_df[borough_df['Classification'] == classification]
            
            metrics = JobMetrics()
            for _, row in class_df.iterrows():
                if row['Type_Fill_Status'] == 'Vacancy_Filled':
                    metrics.vacancy_filled += 1
                elif row['Type_Fill_Status'] == 'Vacancy_Unfilled':
                    metrics.vacancy_unfilled += 1
                elif row['Type_Fill_Status'] == 'Absence_Filled':
                    metrics.absence_filled += 1
                elif row['Type_Fill_Status'] == 'Absence_Unfilled':
                    metrics.absence_unfilled += 1
            
            if metrics.total_jobs > 0:
                self._metrics_by_classification[classification] = metrics
    
    def get_district_summary_data(self) -> List[Dict]:
        """Get summary data for all districts in this borough"""
        summary_data = []
        for district_num, district in self.districts.items():
            # Skip if district_num is NaN or invalid
            if pd.isna(district_num):
                continue
            metrics = district.total_metrics
            summary_data.append({
                'District': f"D{int(district_num)}",  # Ensure integer conversion
                'District_Sort': int(district_num),  # Add numeric sort field
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            })
        # Sort by district number numerically
        summary_data.sort(key=lambda x: x['District_Sort'])
        # Remove the sort field before returning
        for item in summary_data:
            del item['District_Sort']
        return summary_data


class CityWide:
    """Represents citywide data and statistics"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.boroughs: Dict[str, Borough] = {}
        self._process_data()
    
    def _process_data(self):
        """Process citywide data and create boroughs"""
        # First, create all districts globally to avoid duplicates
        all_districts = {}
        for district_num in self.df['District'].unique():
            if not pd.isna(district_num):
                all_districts[district_num] = District(district_num, self.df)
        
        # Then assign districts to boroughs based on their primary borough
        for borough_name in self.df['Borough'].unique():
            if borough_name != 'Unknown':
                borough = Borough(borough_name, self.df)
                # Only assign districts that primarily belong to this borough
                borough_districts = self.df[self.df['Borough'] == borough_name]['District'].unique()
                for district_num in borough_districts:
                    if not pd.isna(district_num) and district_num in all_districts:
                        borough.districts[district_num] = all_districts[district_num]
                self.boroughs[borough_name] = borough
        
        # Store reference to all districts for citywide summary
        self.all_districts = all_districts
    
    @property
    def total_metrics(self) -> JobMetrics:
        """Get total citywide metrics"""
        total = JobMetrics()
        for borough in self.boroughs.values():
            total += borough.total_metrics
        return total
    
    def get_district_summary_data(self) -> List[Dict]:
        """Get summary data for all districts citywide"""
        district_data = {}  # Use dict to prevent duplicates
        
        # Define citywide districts that don't belong to a specific borough
        citywide_districts = {62, 97}
        
        # Use all_districts to ensure we include all districts, including citywide ones
        for district_num, district in self.all_districts.items():
            # Skip if district_num is NaN or invalid
            if pd.isna(district_num):
                continue
            
            metrics = district.total_metrics
            borough_name = "Citywide" if district_num in citywide_districts else district.borough
            district_data[district_num] = {
                'District': f"D{int(district_num)}",
                'District_Sort': int(district_num),
                'Borough': borough_name,
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            }
        
        # Convert to list and sort numerically
        summary_data = list(district_data.values())
        summary_data.sort(key=lambda x: x['District_Sort'])
        
        # Remove the sort field before returning
        for item in summary_data:
            del item['District_Sort']
            
        return summary_data
    
    def get_overall_classification_metrics(self) -> Dict[str, JobMetrics]:
        """Get overall metrics by classification across all boroughs"""
        classification_metrics = {}
        
        for borough in self.boroughs.values():
            for classification in borough.classifications:
                if classification not in classification_metrics:
                    classification_metrics[classification] = JobMetrics()
                classification_metrics[classification] += borough.get_metrics_for_classification(classification)
        
        return classification_metrics


# === REPORT CLASSES ===
class SchoolReport(BaseReport):
    """Generates school-level reports"""
    
    def __init__(self, school: School, output_dir: str):
        super().__init__(output_dir)
        self.school = school
    
    def generate(self) -> str:
        """Generate school report"""
        # Create school directory
        school_dir = os.path.join(
            self.output_dir, 
            f"District_{int(self.school.district_num)}", 
            "Schools", 
            f"School_{self.school.location_clean}"
        )
        os.makedirs(school_dir, exist_ok=True)
        
        # Create summary table
        table_data = []
        for classification in self.school.classifications:
            metrics = self.school.get_metrics_for_classification(classification)
            table_data.append({
                'Classification': classification,
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            })
        
        table_df = pd.DataFrame(table_data)
        table_html = table_df.to_html(index=False, classes='table table-striped')
        
        # Create bar chart
        bar_chart_file = os.path.join(school_dir, f'{self.school.location_clean}_bar_chart.html')
        self._create_bar_chart(self.school.location, self.school._metrics_by_classification, bar_chart_file)
        
        # Create pie charts
        pie_charts_html = self._create_pie_charts(
            self.school.location, 
            self.school._metrics_by_classification,
            school_dir, 
            self.school.location_clean
        )
        
        # Generate key insights
        total_metrics = self.school.total_metrics
        key_insights_html = f"""
        <div class="summary-box">
            <h3>Key Insights</h3>
            <ul>
                <li><strong>Total Jobs:</strong> {total_metrics.total_jobs:,}</li>
                <li><strong>Total Vacancies:</strong> {total_metrics.total_vacancy:,} ({total_metrics.total_vacancy/total_metrics.total_jobs*100 if total_metrics.total_jobs > 0 else 0:.1f}%)</li>
                <li><strong>Total Absences:</strong> {total_metrics.total_absence:,} ({total_metrics.total_absence/total_metrics.total_jobs*100 if total_metrics.total_jobs > 0 else 0:.1f}%)</li>
                <li><strong>Overall Fill Rate:</strong> {total_metrics.overall_fill_pct:.1f}%</li>
                <li><strong>Vacancy Fill Rate:</strong> {total_metrics.vacancy_fill_pct:.1f}%</li>
                <li><strong>Absence Fill Rate:</strong> {total_metrics.absence_fill_pct:.1f}%</li>
            </ul>
        </div>
        """
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYCDOE Jobs Report - {self.school.location}</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
            {self.formatter.get_base_css()}
            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('.table').DataTable({{paging: false, searching: false, info: false, order: []}});
                }});
            </script>
        </head>
        <body>
            <div class="navigation">
                <a href="../../../index.html">← Back to Overall Summary</a> | 
                <a href="../../{int(self.school.district_num)}_report.html">← Back to District {int(self.school.district_num)}</a>
            </div>
            
            <h1>NYCDOE Substitute Paraprofessional Jobs Report</h1>
            <h2>School: {self.school.location} (District {int(self.school.district_num)})</h2>
            {key_insights_html}
            
            <h3>Summary Statistics</h3>
            {table_html}
            
            <h3>Jobs by Classification and Type (Bar Chart)</h3>
            <iframe src="{self.school.location_clean}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
            
            <h3>Breakdown by Classification</h3>
            <div class="pie-container">
                {pie_charts_html}
            </div>
            
            {self.formatter.get_professional_footer()}
        </body>
        </html>
        """
        
        # Save report
        report_file = os.path.join(school_dir, f'{self.school.location_clean}_report.html')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"School report finished: {self.school.location} (District {int(self.school.district_num)})")
        return report_file


class DistrictReport(BaseReport):
    """Generates district-level reports"""
    
    def __init__(self, district: District, citywide: CityWide, output_dir: str):
        super().__init__(output_dir)
        self.district = district
        self.citywide = citywide
    
    def generate(self) -> str:
        """Generate district report"""
        # Create district directory
        district_dir = os.path.join(self.output_dir, f"District_{int(self.district.district_num)}")
        os.makedirs(district_dir, exist_ok=True)
        
        # Generate school reports first
        school_reports = []
        school_links = ""
        # Sort schools alphabetically for consistent ordering
        sorted_schools = sorted(self.district.schools.items(), key=lambda x: x[0])
        for school_name, school in sorted_schools:
            if school.total_metrics.total_jobs > 0:
                school_report = SchoolReport(school, self.output_dir)
                report_file = school_report.generate()
                school_reports.append(report_file)
                school_links += f'<li><a href="Schools/School_{school.location_clean}/{school.location_clean}_report.html">{school_name}</a> - {school.total_metrics.total_jobs} total jobs</li>\n'
        
        # Create district summary table
        table_data = []
        for classification in self.district.classifications:
            metrics = self.district.get_metrics_for_classification(classification)
            table_data.append({
                'Classification': classification,
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            })
        
        table_df = pd.DataFrame(table_data)
        table_html = table_df.to_html(index=False, classes='table table-striped')
        
        # Create school summary table
        school_summary_data = self.district.get_school_summary_data()
        school_summary_df = pd.DataFrame(school_summary_data)
        school_summary_html = school_summary_df.to_html(index=False, classes='table')
        
        # Create bar chart
        bar_chart_file = os.path.join(district_dir, f'{int(self.district.district_num)}_bar_chart.html')
        self._create_bar_chart(f"District {int(self.district.district_num)}", self.district._metrics_by_classification, bar_chart_file)
        
        # Create pie charts
        pie_charts_html = self._create_pie_charts(
            f"District {int(self.district.district_num)}",
            self.district._metrics_by_classification,
            district_dir,
            str(int(self.district.district_num))
        )
        
        # Get comparison data
        borough = self.citywide.boroughs[self.district.borough]
        citywide_metrics = self.citywide.total_metrics
        borough_metrics = borough.total_metrics
        district_metrics = self.district.total_metrics
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYCDOE Jobs Report - District {int(self.district.district_num)}</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
            {self.formatter.get_base_css()}
            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('.table').DataTable({{paging: false, searching: false, info: false, order: []}});
                }});
            </script>
        </head>
        <body>
            <div class="navigation">
                <a href="../index.html">← Back to Overall Summary</a> | 
                <a href="../Borough_{self.district.borough.replace(' ', '_')}/{self.district.borough.replace(' ', '_')}_report.html">← Back to {self.district.borough}</a>
            </div>
            
            <h1>NYCDOE Substitute Paraprofessional Jobs Report</h1>
            <h2>District: {int(self.district.district_num)}</h2>
            
            <h3>Summary Statistics</h3>
            {table_html}
            
            <h3>Summary by School</h3>
            {school_summary_html}
            
            <h3>Jobs by Classification and Type (Bar Chart)</h3>
            <iframe src="{int(self.district.district_num)}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
            
            <h3>Breakdown by Classification</h3>
            <div class="pie-container">
                {pie_charts_html}
            </div>
            
            <h3>Comparison: Citywide vs Borough vs District</h3>
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                <div style="width: 31%; background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>Citywide Statistics</h4>
                    <ul>
                        <li>Total Jobs: {citywide_metrics.total_jobs:,}</li>
                        <li>Total Vacancies: {citywide_metrics.total_vacancy:,} ({citywide_metrics.total_vacancy/citywide_metrics.total_jobs*100 if citywide_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Total Absences: {citywide_metrics.total_absence:,} ({citywide_metrics.total_absence/citywide_metrics.total_jobs*100 if citywide_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Overall Fill Rate: {citywide_metrics.overall_fill_pct:.1f}%</li>
                        <li>Vacancy Fill Rate: {citywide_metrics.vacancy_fill_pct:.1f}%</li>
                        <li>Absence Fill Rate: {citywide_metrics.absence_fill_pct:.1f}%</li>
                    </ul>
                </div>
                <div style="width: 31%; background-color: #f4e8f8; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>{self.district.borough} Statistics</h4>
                    <ul>
                        <li>Total Jobs: {borough_metrics.total_jobs:,}</li>
                        <li>Total Vacancies: {borough_metrics.total_vacancy:,} ({borough_metrics.total_vacancy/borough_metrics.total_jobs*100 if borough_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Total Absences: {borough_metrics.total_absence:,} ({borough_metrics.total_absence/borough_metrics.total_jobs*100 if borough_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Overall Fill Rate: {borough_metrics.overall_fill_pct:.1f}%</li>
                        <li>Vacancy Fill Rate: {borough_metrics.vacancy_fill_pct:.1f}%</li>
                        <li>Absence Fill Rate: {borough_metrics.absence_fill_pct:.1f}%</li>
                    </ul>
                </div>
                <div style="width: 31%; background-color: #f0f8e8; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>District {int(self.district.district_num)} Statistics</h4>
                    <ul>
                        <li>Total Jobs: {district_metrics.total_jobs:,}</li>
                        <li>Total Vacancies: {district_metrics.total_vacancy:,} ({district_metrics.total_vacancy/district_metrics.total_jobs*100 if district_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Total Absences: {district_metrics.total_absence:,} ({district_metrics.total_absence/district_metrics.total_jobs*100 if district_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Overall Fill Rate: {district_metrics.overall_fill_pct:.1f}%</li>
                        <li>Vacancy Fill Rate: {district_metrics.vacancy_fill_pct:.1f}%</li>
                        <li>Absence Fill Rate: {district_metrics.absence_fill_pct:.1f}%</li>
                    </ul>
                </div>
            </div>
            
            <h3>Individual School Reports</h3>
            <ul>
                {school_links}
            </ul>
            
            {self.formatter.get_professional_footer()}
        </body>
        </html>
        """
        
        # Save report
        report_file = os.path.join(district_dir, f'{int(self.district.district_num)}_report.html')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"District report finished: District {int(self.district.district_num)}")
        return report_file


class BoroughReport(BaseReport):
    """Generates borough-level reports"""
    
    def __init__(self, borough: Borough, citywide: CityWide, output_dir: str):
        super().__init__(output_dir)
        self.borough = borough
        self.citywide = citywide
    
    def generate(self) -> str:
        """Generate borough report"""
        # Create borough directory
        borough_clean = self.borough.name.replace(' ', '_').replace('/', '_')
        borough_dir = os.path.join(self.output_dir, f"Borough_{borough_clean}")
        os.makedirs(borough_dir, exist_ok=True)
        
        # Generate district reports first
        district_links = ""
        # Sort districts numerically for consistent ordering
        sorted_districts = sorted(self.borough.districts.items(), key=lambda x: x[0])
        for district_num, district in sorted_districts:
            if district.total_metrics.total_jobs > 0:
                district_report = DistrictReport(district, self.citywide, self.output_dir)
                district_report.generate()
                district_links += f'<li><a href="../District_{int(district_num)}/{int(district_num)}_report.html">District {int(district_num)} Report</a> - {district.total_metrics.total_jobs} total jobs</li>\n'
        
        # Create borough summary table
        table_data = []
        for classification in self.borough.classifications:
            metrics = self.borough.get_metrics_for_classification(classification)
            table_data.append({
                'Classification': classification,
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            })
        
        table_df = pd.DataFrame(table_data)
        table_html = table_df.to_html(index=False, classes='table table-striped')
        
        # Create district summary table
        district_summary_data = self.borough.get_district_summary_data()
        district_summary_df = pd.DataFrame(district_summary_data)
        district_summary_html = district_summary_df.to_html(index=False, classes='table')
        
        # Create bar chart
        bar_chart_file = os.path.join(borough_dir, f'{borough_clean}_bar_chart.html')
        self._create_bar_chart(self.borough.name, self.borough._metrics_by_classification, bar_chart_file)
        
        # Create pie charts
        pie_charts_html = self._create_pie_charts(
            self.borough.name,
            self.borough._metrics_by_classification,
            borough_dir,
            borough_clean
        )
        
        # Get comparison data
        citywide_metrics = self.citywide.total_metrics
        borough_metrics = self.borough.total_metrics
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYCDOE Jobs Report - {self.borough.name}</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
            {self.formatter.get_base_css()}
            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('.table').DataTable({{paging: false, searching: false, info: false, order: []}});
                }});
            </script>
        </head>
        <body>
            <div class="navigation">
                <a href="../index.html">← Back to Overall Summary</a>
            </div>
            
            <h1>NYCDOE Substitute Paraprofessional Jobs Report</h1>
            <h2>Borough: {self.borough.name}</h2>
            
            <h3>Summary Statistics</h3>
            {table_html}
            
            <h3>Summary by District</h3>
            {district_summary_html}
            
            <h3>Jobs by Classification and Type (Bar Chart)</h3>
            <iframe src="{borough_clean}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
            
            <h3>Breakdown by Classification</h3>
            <div class="pie-container">
                {pie_charts_html}
            </div>
            
            <h3>Comparison: {self.borough.name} vs. Citywide</h3>
            <div style="display: flex; justify-content: space-between;">
                <div style="width: 48%; background-color: #e8f4f8; padding: 15px; border-radius: 5px;">
                    <h4>Citywide Statistics</h4>
                    <ul>
                        <li>Total Jobs: {citywide_metrics.total_jobs:,}</li>
                        <li>Total Vacancies: {citywide_metrics.total_vacancy:,} ({citywide_metrics.total_vacancy/citywide_metrics.total_jobs*100 if citywide_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Total Absences: {citywide_metrics.total_absence:,} ({citywide_metrics.total_absence/citywide_metrics.total_jobs*100 if citywide_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Overall Fill Rate: {citywide_metrics.overall_fill_pct:.1f}%</li>
                        <li>Vacancy Fill Rate: {citywide_metrics.vacancy_fill_pct:.1f}%</li>
                        <li>Absence Fill Rate: {citywide_metrics.absence_fill_pct:.1f}%</li>
                    </ul>
                </div>
                <div style="width: 48%; background-color: #f0f8e8; padding: 15px; border-radius: 5px;">
                    <h4>This Borough</h4>
                    <ul>
                        <li>Total Jobs: {borough_metrics.total_jobs:,}</li>
                        <li>Total Vacancies: {borough_metrics.total_vacancy:,} ({borough_metrics.total_vacancy/borough_metrics.total_jobs*100 if borough_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Total Absences: {borough_metrics.total_absence:,} ({borough_metrics.total_absence/borough_metrics.total_jobs*100 if borough_metrics.total_jobs > 0 else 0:.1f}%)</li>
                        <li>Overall Fill Rate: {borough_metrics.overall_fill_pct:.1f}%</li>
                        <li>Vacancy Fill Rate: {borough_metrics.vacancy_fill_pct:.1f}%</li>
                        <li>Absence Fill Rate: {borough_metrics.absence_fill_pct:.1f}%</li>
                    </ul>
                </div>
            </div>
            
            <h3>Individual District Reports</h3>
            <ul>
                {district_links}
            </ul>
            
            {self.formatter.get_professional_footer()}
        </body>
        </html>
        """
        
        # Save report
        report_file = os.path.join(borough_dir, f'{borough_clean}_report.html')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Borough report finished: {self.borough.name}")
        return report_file


class CityWideReport(BaseReport):
    """Generates citywide summary report"""
    
    def __init__(self, citywide: CityWide, output_dir: str):
        super().__init__(output_dir)
        self.citywide = citywide
    
    def generate(self) -> str:
        """Generate citywide report"""
        # Generate borough reports first
        borough_links = ""
        # Sort boroughs alphabetically for consistent ordering
        sorted_boroughs = sorted(self.citywide.boroughs.items(), key=lambda x: x[0])
        for borough_name, borough in sorted_boroughs:
            if borough.total_metrics.total_jobs > 0:
                borough_report = BoroughReport(borough, self.citywide, self.output_dir)
                borough_report.generate()
                borough_clean = borough_name.replace(' ', '_').replace('/', '_')
                borough_links += f'<li><a href="Borough_{borough_clean}/{borough_clean}_report.html">{borough_name} Report</a> - {borough.total_metrics.total_jobs} total jobs</li>\n'
        
        # Get overall classification metrics
        classification_metrics = self.citywide.get_overall_classification_metrics()
        
        # Create overall bar chart
        overall_chart_file = os.path.join(self.output_dir, 'overall_summary_chart.html')
        # Filter out PARAPROFESSIONAL for the chart
        filtered_metrics = {k: v for k, v in classification_metrics.items() if k != 'PARAPROFESSIONAL'}
        self._create_bar_chart("All Districts", filtered_metrics, overall_chart_file, width=1400)
        
        # Create classification summary table
        table_data = []
        for classification, metrics in classification_metrics.items():
            table_data.append({
                'Classification': classification,
                'Vacancy Filled': f"{metrics.vacancy_filled:,}",
                'Vacancy Unfilled': f"{metrics.vacancy_unfilled:,}",
                'Total Vacancy': f"{metrics.total_vacancy:,}",
                'Vacancy Fill %': f"{metrics.vacancy_fill_pct:.1f}%",
                'Absence Filled': f"{metrics.absence_filled:,}",
                'Absence Unfilled': f"{metrics.absence_unfilled:,}",
                'Total Absence': f"{metrics.total_absence:,}",
                'Absence Fill %': f"{metrics.absence_fill_pct:.1f}%",
                'Total': f"{metrics.total_jobs:,}",
                'Overall Fill %': f"{metrics.overall_fill_pct:.1f}%"
            })
        
        classification_df = pd.DataFrame(table_data)
        classification_html = classification_df.to_html(index=False, classes='table')
        
        # Create district summary table
        district_summary_data = self.citywide.get_district_summary_data()
        district_summary_df = pd.DataFrame(district_summary_data)
        district_summary_html = district_summary_df.to_html(index=False, classes='table')
        
        # Get total metrics
        total_metrics = self.citywide.total_metrics
        total_schools = sum(len(borough.districts[dist_num].schools) 
                           for borough in self.citywide.boroughs.values() 
                           for dist_num in borough.districts.keys())
        total_districts = sum(len(borough.districts) for borough in self.citywide.boroughs.values())
        total_classifications = len(classification_metrics)
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYCDOE Jobs Dashboard - Overall Summary</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
            {self.formatter.get_base_css()}
            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('.table').DataTable({{paging: false, searching: false, info: false, order: []}});
                }});
            </script>
        </head>
        <body>
            <h1>NYCDOE Substitute Paraprofessional Jobs Dashboard</h1>
            <h2>Citywide Summary Report</h2>
            
            <div class="summary-box">
                <h3>Key Statistics</h3>
                <ul>
                    <li><strong>Total Jobs:</strong> {total_metrics.total_jobs:,}</li>
                    <li><strong>Total Vacancies:</strong> {total_metrics.total_vacancy:,} ({total_metrics.total_vacancy/total_metrics.total_jobs*100 if total_metrics.total_jobs > 0 else 0:.1f}%)</li>
                    <li><strong>Total Absences:</strong> {total_metrics.total_absence:,} ({total_metrics.total_absence/total_metrics.total_jobs*100 if total_metrics.total_jobs > 0 else 0:.1f}%)</li>
                    <li><strong>Total Filled:</strong> {total_metrics.vacancy_filled + total_metrics.absence_filled:,} ({total_metrics.overall_fill_pct:.1f}%)</li>
                    <li><strong>Total Districts:</strong> {total_districts}</li>
                    <li><strong>Total Schools:</strong> {total_schools}</li>
                    <li><strong>Total Classifications:</strong> {total_classifications}</li>
                </ul>
            </div>
            
            <h3>Overall Jobs by Classification and Type</h3>
            <iframe src="overall_summary_chart.html" width="1420" height="520" frameborder="0"></iframe>
            
            <h3>Summary by Classification (All Districts)</h3>
            {classification_html}
            
            <h3>Summary by District</h3>
            {district_summary_html}
            
            <h3>Individual Borough Reports</h3>
            <ul>
                {borough_links}
            </ul>
            
            <p><em>Generated from data containing {len(self.citywide.df)} job records</em></p>
            {self.formatter.get_professional_footer()}
        </body>
        </html>
        """
        
        # Save report
        index_file = os.path.join(self.output_dir, 'index.html')
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Citywide summary report finished: index.html")
        return index_file


# === MAIN REPORT GENERATOR ===
class ReportGenerator:
    """Main class that orchestrates the entire report generation process"""
    
    def __init__(self, csv_file_path: str, output_dir: str):
        self.csv_file_path = csv_file_path
        self.output_dir = output_dir
        self.citywide: Optional[CityWide] = None
    
    def generate_all_reports(self) -> str:
        """Generate all reports and return the index file path"""
        print("Loading and processing data...")
        df = DataProcessor.load_and_process_data(self.csv_file_path)
        
        print("Creating citywide data structure...")
        self.citywide = CityWide(df)
        
        print("Generating citywide summary report...")
        citywide_report = CityWideReport(self.citywide, self.output_dir)
        index_file = citywide_report.generate()
        
        print(f"Reports generated successfully! Index file: {index_file}")
        return index_file


# === MAIN EXECUTION ===
def main():
    """Main function to generate static reports"""
    # Start timing
    start_time = time.time()
    print("Starting report generation...")
    
    # Configuration - Updated for your specific file
    csv_file_path = r'Fill Rate Data\mayjobs.csv'  # Your specific CSV file
    output_dir = 'nycdoe_reports'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate reports
    generator = ReportGenerator(csv_file_path, output_dir)
    index_file = generator.generate_all_reports()
    
    # Calculate and display runtime
    end_time = time.time()
    runtime = end_time - start_time
    minutes = int(runtime // 60)
    seconds = runtime % 60
    
    print(f"\nAll reports generated! Open {index_file} to view the dashboard.")
    print(f"Total runtime: {minutes:02d}:{seconds:05.2f} ({runtime:.2f} seconds)")


if __name__ == "__main__":
    main()
