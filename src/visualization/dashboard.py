"""
Interactive Dashboard Module
Creates an interactive Dash dashboard for CityPulse
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path
import base64
import io
import sys

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Add project root to path for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import new modules
from src.utils.export_utils import (
    export_chart_png, export_chart_pdf, export_data_csv, export_data_excel,
    generate_pdf_report, create_export_directory
)
from src.analytics.statistical_analysis import (
    calculate_confidence_interval, calculate_correlation_with_stats,
    calculate_effect_size, linear_regression, calculate_all_statistics
)
from src.analytics.neighborhood_analysis import (
    aggregate_by_neighborhood, aggregate_by_ward, detect_hotspots, compare_neighborhoods,
    rank_hotspots_by_metric, get_top_hotspots, format_hotspot_description, detect_hotspots_simple
)
from src.analytics.temporal_analysis import (
    analyze_day_of_week_patterns, analyze_time_patterns, get_peak_days,
    format_temporal_insight, get_seasonal_patterns
)
from src.analytics.simple_correlations import (
    calculate_simple_correlations, format_correlation_insight,
    get_top_correlations, get_correlation_summary
)
from src.analytics.health_scores import (
    calculate_urban_health_index, get_health_status,
    calculate_route_efficiency_score, calculate_safety_index, calculate_trend_indicator
)
from src.visualization.viz_helpers import (
    create_simple_bar_chart, create_insight_card, create_correlation_heatmap,
    create_health_gauge, format_number_for_display, create_multi_metric_bar_chart
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app with professional theme and Font Awesome icons
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
)
app.title = "CityPulse: Urban Mobility & Service Dashboard"

# Add custom CSS for enhanced styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Custom styles for polished dashboard */
            .card {
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .metric-card {
                border-radius: 8px;
            }
            /* Fix date picker calendar z-index and positioning to prevent overlap */
            /* Use very high z-index to ensure calendar appears above all other elements */
            .DateRangePicker {
                position: relative !important;
                z-index: 100000 !important;
            }
            .DateRangePickerInput {
                position: relative !important;
                z-index: 100000 !important;
            }
            .DateRangePicker_picker {
                z-index: 100000 !important;
                position: absolute !important;
                top: 100% !important;
                left: 0 !important;
                margin-top: 4px !important;
                background: white !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            .DayPicker {
                z-index: 100000 !important;
                position: relative !important;
            }
            .DayPicker__horizontal {
                z-index: 100000 !important;
            }
            .DayPicker__withBorder {
                z-index: 100000 !important;
            }
            .CalendarMonthGrid {
                z-index: 100000 !important;
                position: relative !important;
            }
            .CalendarMonth {
                z-index: 100000 !important;
                position: relative !important;
            }
            .CalendarMonth_caption {
                z-index: 100000 !important;
            }
            .DayPicker_transitionContainer {
                z-index: 100000 !important;
            }
            /* Ensure metric cards have lower z-index */
            .card {
                overflow: visible !important;
                position: relative !important;
                z-index: 1 !important;
            }
            .card-body {
                overflow: visible !important;
            }
            /* Ensure dropdowns also have proper z-index */
            .Select-menu-outer {
                z-index: 9999 !important;
            }
            .Select-control {
                position: relative;
            }
            /* Ensure container doesn't clip */
            .container-fluid {
                overflow: visible !important;
            }
            .row {
                overflow: visible !important;
            }
            .col, .col-md-4 {
                overflow: visible !important;
            }
            /* Add padding to filter card to give calendar space */
            #date-picker {
                position: relative !important;
            }
            /* Crime map date picker specific styling */
            #crime-map-date-picker {
                position: relative !important;
                z-index: 100001 !important;
            }
            #crime-map-date-picker .DateRangePicker {
                position: relative !important;
                z-index: 100001 !important;
            }
            #crime-map-date-picker .DateRangePickerInput {
                position: relative !important;
                z-index: 100001 !important;
            }
            #crime-map-date-picker .DateRangePicker_picker {
                z-index: 100001 !important;
                position: absolute !important;
                top: 100% !important;
                left: 0 !important;
                margin-top: 4px !important;
                background: white !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            /* Ensure DayPicker has relative positioning for navigation buttons */
            #crime-map-date-picker .DayPicker {
                position: relative !important;
            }
            /* Ensure month navigation arrows are visible and clickable - positioned at corners */
            #crime-map-date-picker .DayPickerNavigation {
                z-index: 100002 !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: 40px !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                padding: 0 10px !important;
                pointer-events: none !important;
            }
            #crime-map-date-picker .DayPickerNavigation_button {
                z-index: 100003 !important;
                position: absolute !important;
                cursor: pointer !important;
                background: white !important;
                border: 1px solid #dce0e0 !important;
                padding: 8px 12px !important;
                border-radius: 4px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                pointer-events: auto !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
            #crime-map-date-picker .DayPickerNavigation_leftButton__horizontalDefault {
                left: 10px !important;
                right: auto !important;
            }
            #crime-map-date-picker .DayPickerNavigation_rightButton__horizontalDefault {
                right: 10px !important;
                left: auto !important;
            }
            #crime-map-date-picker .DayPickerNavigation_button:hover {
                background: #f0f0f0 !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
            }
            #crime-map-date-picker .DayPickerNavigation_button__default {
                z-index: 100003 !important;
            }
            #crime-map-date-picker .CalendarMonth_caption {
                z-index: 100001 !important;
                position: relative !important;
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
                padding: 12px 0 !important;
                text-align: center !important;
                background: white !important;
                border-bottom: 2px solid #e0e0e0 !important;
                margin-bottom: 12px !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            #crime-map-date-picker .DayPicker_weekHeader {
                z-index: 100001 !important;
            }
            #crime-map-date-picker .CalendarDay {
                z-index: 100001 !important;
                cursor: pointer !important;
            }
            /* Ensure calendar month caption is visible and styled */
            #crime-map-date-picker .CalendarMonth_caption strong,
            #crime-map-date-picker .CalendarMonth_caption > div,
            #crime-map-date-picker .CalendarMonth_caption > span {
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            /* Style for the month/year text - catch all text content */
            #crime-map-date-picker .CalendarMonth_caption {
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
            }
            /* Ensure the CalendarMonth container shows the caption */
            #crime-map-date-picker .CalendarMonth {
                position: relative !important;
            }
            #crime-map-date-picker .CalendarMonth > div:first-child {
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
                padding: 12px 0 !important;
                text-align: center !important;
                border-bottom: 2px solid #e0e0e0 !important;
                margin-bottom: 12px !important;
            }
            /* Complaint map date picker specific styling - same as crime map */
            #complaint-map-date-picker {
                position: relative !important;
                z-index: 100001 !important;
            }
            #complaint-map-date-picker .DateRangePicker {
                position: relative !important;
                z-index: 100001 !important;
            }
            #complaint-map-date-picker .DateRangePickerInput {
                position: relative !important;
                z-index: 100001 !important;
            }
            #complaint-map-date-picker .DateRangePicker_picker {
                z-index: 100001 !important;
                position: absolute !important;
                top: 100% !important;
                left: 0 !important;
                margin-top: 4px !important;
                background: white !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            /* Ensure month navigation arrows are visible and clickable - positioned at corners */
            #complaint-map-date-picker .DayPickerNavigation {
                z-index: 100002 !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: 40px !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                padding: 0 10px !important;
                pointer-events: none !important;
            }
            #complaint-map-date-picker .DayPickerNavigation_button {
                z-index: 100003 !important;
                position: absolute !important;
                cursor: pointer !important;
                background: white !important;
                border: 1px solid #dce0e0 !important;
                padding: 8px 12px !important;
                border-radius: 4px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                pointer-events: auto !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
            #complaint-map-date-picker .DayPickerNavigation_leftButton__horizontalDefault {
                left: 10px !important;
                right: auto !important;
            }
            #complaint-map-date-picker .DayPickerNavigation_rightButton__horizontalDefault {
                right: 10px !important;
                left: auto !important;
            }
            #complaint-map-date-picker .DayPickerNavigation_button:hover {
                background: #f0f0f0 !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
            }
            #complaint-map-date-picker .DayPickerNavigation_button__default {
                z-index: 100003 !important;
            }
            #complaint-map-date-picker .CalendarMonth_caption {
                z-index: 100001 !important;
                position: relative !important;
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
                padding: 12px 0 !important;
                text-align: center !important;
                background: white !important;
                border-bottom: 2px solid #e0e0e0 !important;
                margin-bottom: 12px !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            #complaint-map-date-picker .DayPicker_weekHeader {
                z-index: 100001 !important;
            }
            #complaint-map-date-picker .CalendarDay {
                z-index: 100001 !important;
                cursor: pointer !important;
            }
            /* Ensure calendar month caption is visible and styled */
            #complaint-map-date-picker .CalendarMonth_caption strong,
            #complaint-map-date-picker .CalendarMonth_caption > div,
            #complaint-map-date-picker .CalendarMonth_caption > span {
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            /* Ensure the CalendarMonth container shows the caption */
            #complaint-map-date-picker .CalendarMonth {
                position: relative !important;
            }
            #complaint-map-date-picker .CalendarMonth > div:first-child {
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #1a1a1a !important;
                padding: 12px 0 !important;
                text-align: center !important;
                border-bottom: 2px solid #e0e0e0 !important;
                margin-bottom: 12px !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Professional color palette
COLORS = {
    'primary': '#1E88E5',      # Professional blue
    'secondary': '#43A047',   # Green for positive metrics
    'accent': '#E53935',       # Red for alerts
    'warning': '#FB8C00',      # Orange for warnings
    'info': '#00ACC1',         # Cyan for info
    'dark': '#263238',         # Dark gray
    'light': '#ECEFF1',        # Light gray
    'success': '#43A047',
    'danger': '#F44336',  # Red for danger/alerts
    'sentiment_positive': '#4CAF50',
    'sentiment_negative': '#F44336',
    'sentiment_neutral': '#FFC107',
    'chart_blue': '#2196F3',
    'chart_green': '#4CAF50',
    'chart_orange': '#FF9800',
    'chart_red': '#F44336',
    'chart_purple': '#9C27B0',
}


def get_complaint_symbol_mapping():
    """
    Map complaint types to symbols and colors for visualization
    Returns: dict mapping complaint_type -> (symbol, color)
    Note: Scattermapbox supports: circle, square, diamond, triangle, star, x, cross
    """
    # Define symbol mapping based on complaint categories
    # Using symbols supported by Scattermapbox
    symbol_map = {
        # Infrastructure - Triangles
        'Pothole in Street': ('triangle', COLORS['chart_orange']),
        'Street Resurfacing Request': ('triangle', COLORS['chart_orange']),
        'Sidewalk Repair': ('triangle', COLORS['chart_orange']),
        'Street Light Out': ('triangle', COLORS['chart_orange']),
        'Alley Light Out': ('triangle', COLORS['chart_orange']),
        'Traffic Signal Out': ('triangle', COLORS['chart_orange']),
        
        # Transit-related - Circles
        'Transit Delay': ('circle', COLORS['chart_blue']),
        'Bus Stop Request': ('circle', COLORS['chart_blue']),
        'CTA Complaint': ('circle', COLORS['chart_blue']),
        
        # Safety - Squares
        'Rodent Baiting / Rat Complaint': ('square', COLORS['chart_red']),
        'Graffiti Removal': ('square', COLORS['chart_red']),
        'Abandoned Vehicle': ('square', COLORS['chart_red']),
        'Vehicle on Sidewalk': ('square', COLORS['chart_red']),
        
        # Environmental - Diamonds
        'Tree Debris': ('diamond', COLORS['chart_green']),
        'Garbage Cart': ('diamond', COLORS['chart_green']),
        'Dead Animal': ('diamond', COLORS['chart_green']),
        'Sanitation Code Violation': ('diamond', COLORS['chart_green']),
        
        # Other - Stars and crosses
        'Aircraft Noise Complaint': ('star', COLORS['chart_purple']),
        'Noise Complaint': ('star', COLORS['chart_purple']),
        'Building Violation': ('x', COLORS['warning']),
    }
    
    return symbol_map

def get_complaint_symbol(complaint_type, symbol_map):
    """Get symbol and color for a complaint type, with fallback"""
    if complaint_type in symbol_map:
        return symbol_map[complaint_type]
    
    # Default based on keywords - using Scattermapbox-compatible symbols
    complaint_lower = str(complaint_type).lower()
    if any(word in complaint_lower for word in ['pothole', 'street', 'sidewalk', 'light', 'traffic']):
        return ('triangle', COLORS['chart_orange'])
    elif any(word in complaint_lower for word in ['transit', 'bus', 'cta', 'train']):
        return ('circle', COLORS['chart_blue'])
    elif any(word in complaint_lower for word in ['rodent', 'rat', 'graffiti', 'vehicle', 'abandoned']):
        return ('square', COLORS['chart_red'])
    elif any(word in complaint_lower for word in ['tree', 'garbage', 'sanitation', 'dead']):
        return ('diamond', COLORS['chart_green'])
    elif any(word in complaint_lower for word in ['noise', 'aircraft']):
        return ('star', COLORS['chart_purple'])
    else:
        return ('circle', COLORS['chart_blue'])  # Default

def get_crime_symbol_mapping():
    """
    Map crime types to symbols and colors for visualization
    Returns: dict mapping primary_type -> (symbol, color)
    Note: Scattermapbox supports: circle, square, diamond, triangle, star, x, cross
    """
    symbol_map = {
        # Violent crimes - Triangles (red/orange)
        'ASSAULT': ('triangle', COLORS['chart_red']),
        'BATTERY': ('triangle', COLORS['danger']),
        'ROBBERY': ('triangle', COLORS['chart_orange']),
        'HOMICIDE': ('triangle', '#8B0000'),  # Dark red
        'CRIM SEXUAL ASSAULT': ('triangle', '#DC143C'),  # Crimson
        
        # Property crimes - Circles (blue)
        'THEFT': ('circle', COLORS['chart_blue']),
        'BURGLARY': ('circle', '#4169E1'),  # Royal blue
        'MOTOR VEHICLE THEFT': ('circle', '#1E90FF'),  # Dodger blue
        
        # Damage/Vandalism - Squares (orange/yellow)
        'CRIMINAL DAMAGE': ('square', COLORS['chart_orange']),
        'ARSON': ('square', COLORS['warning']),
        
        # Drug-related - Diamonds (purple)
        'NARCOTICS': ('diamond', COLORS['chart_purple']),
        'OTHER NARCOTIC VIOLATION': ('diamond', '#9370DB'),  # Medium purple
        
        # Fraud/Deception - Stars (yellow)
        'DECEPTIVE PRACTICE': ('star', COLORS['warning']),
        'FORGERY': ('star', '#FFD700'),  # Gold
        
        # Other offenses - Cross/X (gray)
        'OTHER OFFENSE': ('cross', '#808080'),  # Gray
        'CRIMINAL TRESPASS': ('x', '#A9A9A9'),  # Dark gray
        'PUBLIC PEACE VIOLATION': ('x', '#696969'),  # Dim gray
        
        # Weapons - Star (dark red)
        'WEAPONS VIOLATION': ('star', '#8B0000'),  # Dark red
        
        # Interference - Diamond (dark purple)
        'INTERFERENCE WITH PUBLIC OFFICER': ('diamond', '#4B0082'),  # Indigo
    }
    
    return symbol_map

def get_crime_symbol(crime_type, symbol_map):
    """Get symbol and color for a crime type, with fallback"""
    if crime_type in symbol_map:
        return symbol_map[crime_type]
    
    # Default based on keywords - using Scattermapbox-compatible symbols
    crime_lower = str(crime_type).lower()
    if any(word in crime_lower for word in ['assault', 'battery', 'robbery', 'homicide', 'sexual']):
        return ('triangle', COLORS['chart_red'])
    elif any(word in crime_lower for word in ['theft', 'burglary', 'motor vehicle']):
        return ('circle', COLORS['chart_blue'])
    elif any(word in crime_lower for word in ['damage', 'arson', 'vandalism']):
        return ('square', COLORS['chart_orange'])
    elif any(word in crime_lower for word in ['narcotic', 'drug']):
        return ('diamond', COLORS['chart_purple'])
    elif any(word in crime_lower for word in ['deceptive', 'forgery', 'fraud']):
        return ('star', COLORS['warning'])
    elif any(word in crime_lower for word in ['weapon', 'gun']):
        return ('star', '#8B0000')
    else:
        return ('circle', COLORS['chart_blue'])  # Default

def get_status_color(status):
    """Get color based on complaint status"""
    status_lower = str(status).lower() if pd.notna(status) else ''
    if 'open' in status_lower:
        return COLORS['accent']  # Red
    elif 'closed' in status_lower:
        return COLORS['success']  # Green
    elif 'completed' in status_lower:
        return COLORS['chart_blue']  # Blue
    elif 'progress' in status_lower or 'pending' in status_lower:
        return COLORS['warning']  # Yellow/Orange
    else:
        return COLORS['dark']  # Gray

def load_data():
    """Load combined data"""
    data_path = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    if data_path.exists():
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        logger.warning(f"Data file not found: {data_path}")
        return pd.DataFrame()


def create_dashboard_layout(df: pd.DataFrame):
    """Create polished, professional dashboard layout"""
    
    if df.empty:
        return html.Div([
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "No data available. Please run data collection and processing scripts first."
                ],
                color="warning",
                className="m-4"
            )
        ])
    
    # Get date range
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Get date range from crime data for crime map date picker
    crime_min_date = min_date
    crime_max_date = max_date
    crime_path = PROJECT_ROOT / "data" / "cleaned" / "crime_data.csv"
    if crime_path.exists():
        try:
            df_crimes_temp = pd.read_csv(crime_path, low_memory=False)
            if 'date' in df_crimes_temp.columns:
                df_crimes_temp['date'] = pd.to_datetime(df_crimes_temp['date'], errors='coerce')
                crime_dates = df_crimes_temp['date'].dropna()
                if not crime_dates.empty:
                    crime_min_date = crime_dates.min()
                    crime_max_date = crime_dates.max()
        except Exception as e:
            logger.warning(f"Could not load crime dates: {e}")
    
    # Get date range from 311 data for complaint map date picker
    complaint_min_date = min_date
    complaint_max_date = max_date
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    if complaints_path.exists():
        try:
            df_complaints_temp = pd.read_csv(complaints_path, low_memory=False)
            if 'date' in df_complaints_temp.columns:
                df_complaints_temp['date'] = pd.to_datetime(df_complaints_temp['date'], errors='coerce')
                complaint_dates = df_complaints_temp['date'].dropna()
                if not complaint_dates.empty:
                    complaint_min_date = complaint_dates.min()
                    complaint_max_date = complaint_dates.max()
        except Exception as e:
            logger.warning(f"Could not load complaint dates: {e}")
    
    # Convert dates to strings for DatePickerRange component
    # Ensure we always have valid dates (use main date range as fallback)
    if pd.notna(crime_min_date):
        if isinstance(crime_min_date, pd.Timestamp):
            crime_min_date = crime_min_date.strftime('%Y-%m-%d')
        else:
            crime_min_date = str(crime_min_date)
    else:
        # Fallback to main date range
        if pd.notna(min_date):
            crime_min_date = min_date.strftime('%Y-%m-%d') if isinstance(min_date, pd.Timestamp) else str(min_date)
        else:
            crime_min_date = None
    
    if pd.notna(crime_max_date):
        if isinstance(crime_max_date, pd.Timestamp):
            crime_max_date = crime_max_date.strftime('%Y-%m-%d')
        else:
            crime_max_date = str(crime_max_date)
    else:
        # Fallback to main date range
        if pd.notna(max_date):
            crime_max_date = max_date.strftime('%Y-%m-%d') if isinstance(max_date, pd.Timestamp) else str(max_date)
        else:
            crime_max_date = None
    
    # Convert complaint dates to strings for DatePickerRange component
    if pd.notna(complaint_min_date):
        if isinstance(complaint_min_date, pd.Timestamp):
            complaint_min_date = complaint_min_date.strftime('%Y-%m-%d')
        else:
            complaint_min_date = str(complaint_min_date)
    else:
        # Fallback to main date range
        if pd.notna(min_date):
            complaint_min_date = min_date.strftime('%Y-%m-%d') if isinstance(min_date, pd.Timestamp) else str(min_date)
        else:
            complaint_min_date = None
    
    if pd.notna(complaint_max_date):
        if isinstance(complaint_max_date, pd.Timestamp):
            complaint_max_date = complaint_max_date.strftime('%Y-%m-%d')
        else:
            complaint_max_date = str(complaint_max_date)
    else:
        # Fallback to main date range
        if pd.notna(max_date):
            complaint_max_date = max_date.strftime('%Y-%m-%d') if isinstance(max_date, pd.Timestamp) else str(max_date)
        else:
            complaint_max_date = None
    
    # Get available complaint types from 311 data file
    complaint_types = ['All']
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    if complaints_path.exists():
        try:
            df_complaints = pd.read_csv(complaints_path, low_memory=False)
            # Check for sr_type or service_request_type column
            type_col = 'sr_type' if 'sr_type' in df_complaints.columns else ('service_request_type' if 'service_request_type' in df_complaints.columns else None)
            if type_col:
                unique_types = df_complaints[type_col].dropna().unique().tolist()
                complaint_types.extend(sorted(unique_types)[:20])  # Show up to 20 types
        except Exception as e:
            logger.warning(f"Could not load complaint types: {e}")
    
    return dbc.Container([
        # Professional Header with Branding
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-city fa-3x", style={'color': COLORS['primary'], 'marginRight': '20px'}),
                                html.Div([
                                    html.H1("CityPulse", className="mb-1", style={
                                        'color': COLORS['primary'],
                                        'fontWeight': '700',
                                        'fontSize': '2.5rem'
                                    }),
                                    html.H5("Urban Mobility & Service Dashboard", className="text-muted mb-2", style={
                                        'fontWeight': '400',
                                        'fontSize': '1.1rem'
                                    }),
                                    html.P(
                                        "Real-time analysis of Chicago's transit ridership, bike share, crime, and service request patterns",
                                        className="text-muted mb-0",
                                        style={'fontSize': '0.9rem'}
                                    )
                                ])
                            ], style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center'
                            })
                        ], className="text-center")
                    ])
                ], className="mb-4", style={
                    'background': f'linear-gradient(135deg, {COLORS["light"]} 0%, white 100%)',
                    'border': 'none',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
                })
            ])
        ]),
        
        # Enhanced Filters Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-filter me-2", style={'color': COLORS['primary']}),
                            html.Strong("Filters", style={'fontSize': '1.1rem', 'color': COLORS['dark']})
                        ], className="mb-3"),
                        dbc.Row([
                            # Hidden date picker to maintain callback functionality
                            html.Div([
                dcc.DatePickerRange(
                    id='date-picker',
                    start_date=min_date,
                    end_date=max_date,
                    display_format='YYYY-MM-DD',
                                    style={'display': 'none'}
                )
                            ]),
            dbc.Col([
                                html.Label([
                                    html.I(className="fas fa-list me-2"),
                                    "Complaint Type"
                                ], className="fw-bold mb-2", style={'color': COLORS['dark']}),
                                html.Div([
                dcc.Dropdown(
                    id='complaint-type-filter',
                    options=[{'label': ct, 'value': ct} for ct in complaint_types],
                    value='All',
                                        className="mb-3",
                                        style={'width': '100%'}
                                    )
                                ], style={'position': 'relative', 'zIndex': '1'})
                            ], md=6),
                            dbc.Col([
                                html.Label([
                                    html.I(className="fas fa-map-marker-alt me-2"),
                                    "Neighborhood/Ward"
                                ], className="fw-bold mb-2", style={'color': COLORS['dark']}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='neighborhood-filter',
                                        options=[{'label': 'All Areas', 'value': 'All'}],
                                        value='All',
                                        className="mb-3",
                                        style={'width': '100%'}
                                    )
                                ], style={'position': 'relative', 'zIndex': '1'})
            ], md=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label([
                                    html.I(className="fas fa-gavel me-2"),
                                    "Crime Type"
                                ], className="fw-bold mb-2", style={'color': COLORS['dark']}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='crime-type-filter',
                                        options=[{'label': 'All Crime Types', 'value': 'All'}],
                                        value='All',
                                        className="mb-3",
                                        style={'width': '100%'}
                                    )
                                ], style={'position': 'relative', 'zIndex': '1'})
                            ], md=4)
                        ])
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
                    'overflow': 'visible'  # Allow calendar to extend beyond card
                })
            ])
        ]),
        
        # Export and Help Buttons
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([
                        html.I(className="fas fa-download me-2"),
                        "Export Data"
                    ], id="export-data-btn", color="primary", outline=True, className="me-2"),
                    dbc.Button([
                        html.I(className="fas fa-file-pdf me-2"),
                        "Export Report"
                    ], id="export-report-btn", color="primary", outline=True, className="me-2"),
                    dbc.Button([
                        html.I(className="fas fa-question-circle me-2"),
                        "Help"
                    ], id="help-btn", color="info", outline=True, className="me-2"),
                    dbc.Button([
                        html.I(className="fas fa-info-circle me-2"),
                        "About"
                    ], id="about-btn", color="secondary", outline=True)
                ], className="mb-3")
            ])
        ]),
        
        # Enhanced Key Metrics Cards with Icons
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-car fa-2x", style={
                                'color': COLORS['primary'],
                                'marginBottom': '10px'
                            }),
                            html.Div([
                                html.H6("Traffic Volume", className="text-muted mb-2", style={
                                    'fontSize': '0.85rem',
                                    'textTransform': 'uppercase',
                                    'letterSpacing': '0.5px',
                                    'display': 'inline-block',
                                    'marginRight': '5px'
                                }),
                                html.I(
                                    className="fas fa-info-circle text-muted",
                                    id="traffic-volume-help",
                                    style={"cursor": "pointer", "fontSize": "0.7rem"}
                                )
                            ], style={'textAlign': 'center'}),
                            html.H2(id="total-traffic-volume", style={
                                'color': COLORS['primary'],
                                'fontWeight': '700',
                                'marginBottom': '0'
                            })
                        ], className="text-center")
                    ])
                ], className="mb-4 h-100", style={
                    'border': 'none',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'transition': 'transform 0.2s, box-shadow 0.2s',
                    'borderTop': f'4px solid {COLORS["primary"]}'
                })
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-bus fa-2x", style={
                                'color': COLORS['success'],
                                'marginBottom': '10px'
                            }),
                            html.Div([
                                html.H6("Total CTA Rides", className="text-muted mb-2", style={
                                    'fontSize': '0.85rem',
                                    'textTransform': 'uppercase',
                                    'letterSpacing': '0.5px',
                                    'display': 'inline-block',
                                    'marginRight': '5px'
                                }),
                                html.I(
                                    className="fas fa-info-circle text-muted",
                                    id="cta-rides-help",
                                    style={"cursor": "pointer", "fontSize": "0.7rem"}
                                )
                            ], style={'textAlign': 'center'}),
                            html.H2(id="total-rides", style={
                                'color': COLORS['success'],
                                'fontWeight': '700',
                                'marginBottom': '0'
                            })
                        ], className="text-center")
                    ])
                ], className="mb-4 h-100", style={
                    'border': 'none',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'transition': 'transform 0.2s, box-shadow 0.2s',
                    'borderTop': f'4px solid {COLORS["success"]}'
                })
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-exclamation-circle fa-2x", style={
                                'color': COLORS['warning'],
                                'marginBottom': '10px'
                            }),
                            html.Div([
                                html.H6("311 Complaints", className="text-muted mb-2", style={
                                    'fontSize': '0.85rem',
                                    'textTransform': 'uppercase',
                                    'letterSpacing': '0.5px',
                                    'display': 'inline-block',
                                    'marginRight': '5px'
                                }),
                                html.I(
                                    className="fas fa-info-circle text-muted",
                                    id="complaints-help",
                                    style={"cursor": "pointer", "fontSize": "0.7rem"}
                                )
                            ], style={'textAlign': 'center'}),
                            html.H2(id="total-complaints", style={
                                'color': COLORS['warning'],
                                'fontWeight': '700',
                                'marginBottom': '0'
                            })
                        ], className="text-center")
                    ])
                ], className="mb-4 h-100", style={
                    'border': 'none',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'transition': 'transform 0.2s, box-shadow 0.2s',
                    'borderTop': f'4px solid {COLORS["warning"]}'
                })
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-shield-alt fa-2x", style={
                                'color': COLORS['danger'],
                                'marginBottom': '10px'
                            }),
                            html.Div([
                                html.H6("Total Crimes", className="text-muted mb-2", style={
                                    'fontSize': '0.85rem',
                                    'textTransform': 'uppercase',
                                    'letterSpacing': '0.5px',
                                    'display': 'inline-block',
                                    'marginRight': '5px'
                                }),
                                html.I(
                                    className="fas fa-info-circle text-muted",
                                    id="crimes-help",
                                    style={"cursor": "pointer", "fontSize": "0.7rem"}
                                )
                            ], style={'textAlign': 'center'}),
                            html.H2(id="total-crimes", style={
                                'color': COLORS['danger'],
                                'fontWeight': '700',
                                'marginBottom': '0'
                            })
                        ], className="text-center")
                    ])
                ], className="mb-4 h-100", style={
                    'border': 'none',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'transition': 'transform 0.2s, box-shadow 0.2s',
                    'borderTop': f'4px solid {COLORS["danger"]}'
                })
            ], md=3)
        ], className="mb-4"),
        
        # Map Section (if geospatial data available)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-map-marked-alt me-2"),
                            "Complaint Density Map",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="complaint-map-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-calendar-alt me-2"),
                                "Select Date Range for Complaint Map"
                            ], className="fw-bold mb-2", style={'color': COLORS['dark'], 'fontSize': '0.9rem'}),
                            html.Div([
                                dcc.DatePickerRange(
                                    id='complaint-map-date-picker',
                                    start_date=complaint_min_date,
                                    end_date=complaint_max_date,
                                    min_date_allowed=complaint_min_date,
                                    max_date_allowed=complaint_max_date,
                                    display_format='YYYY-MM-DD',
                                    className="mb-3",
                                    style={'width': '100%', 'position': 'relative', 'zIndex': '100001'}
                                )
                            ], style={'position': 'relative', 'zIndex': '100001', 'overflow': 'visible'})
                        ], className="mb-3", style={'position': 'relative', 'zIndex': '100001', 'overflow': 'visible'}),
                        dcc.Graph(
                            id="complaint-map",
                            style={'height': '400px'},
                            config={
                                'scrollZoom': True,
                                'displayModeBar': True,
                                'modeBarButtonsToRemove': [],
                                'displaylogo': False
                            }
                        )
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Crime Map Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-map-marker-alt me-2"),
                            "Crime Location Map",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="crime-map-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-calendar-alt me-2"),
                                "Select Date Range for Crime Map"
                            ], className="fw-bold mb-2", style={'color': COLORS['dark'], 'fontSize': '0.9rem'}),
                            html.Div([
                                dcc.DatePickerRange(
                                    id='crime-map-date-picker',
                                    start_date=crime_min_date,
                                    end_date=crime_max_date,
                                    min_date_allowed=crime_min_date,
                                    max_date_allowed=crime_max_date,
                                    display_format='YYYY-MM-DD',
                                    className="mb-3",
                                    style={'width': '100%', 'position': 'relative', 'zIndex': '100001'}
                                )
                            ], style={'position': 'relative', 'zIndex': '100001', 'overflow': 'visible'})
                        ], className="mb-3", style={'position': 'relative', 'zIndex': '100001', 'overflow': 'visible'}),
                        dcc.Graph(
                            id="crime-map",
                            style={'height': '400px'},
                            config={
                                'scrollZoom': True,
                                'displayModeBar': True,
                                'modeBarButtonsToRemove': [],
                                'displaylogo': False
                            }
                        )
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Enhanced Hotspot Analysis Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-map-marked-alt me-2"),
                            "Problem Hotspots",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="hotspot-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="hotspot-map-enhanced")
                            ], md=8),
                            dbc.Col([
                                html.Div(id="hotspot-ranking-list")
                            ], md=4)
                        ])
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Statistical Analysis Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6([
                            html.I(className="fas fa-chart-line me-2"),
                            "Statistical Analysis",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="statistical-analysis-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        html.Div(id="statistical-analysis")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Temporal Patterns Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-calendar-week me-2"),
                            "Day of Week Patterns",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="day-of-week-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        html.Div(id="temporal-patterns-insights", className="mb-3"),
                        dcc.Graph(id="day-of-week-chart")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Simple Correlation Insights Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-project-diagram me-2"),
                            "How Things Are Connected",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="corr-simple-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        html.Div(id="correlation-insights-cards", className="mb-3"),
                        dcc.Graph(id="correlation-heatmap-simple")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Urban Health Score Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-heartbeat me-2"),
                            "Overall City Health",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="health-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="health-gauge-chart")
                            ], md=6),
                            dbc.Col([
                                html.Div(id="health-score-breakdown")
                            ], md=6)
                        ])
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # New Chart Types Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-chart-box me-2"),
                            "Crime Distribution Analysis",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="crime-distribution-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        dcc.Graph(id="box-violin-chart")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-tachometer-alt me-2"),
                            "Performance Indicators",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="performance-indicators-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        dcc.Graph(id="gauge-charts")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-sun me-2"),
                            "Complaint Type Hierarchy",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="complaint-hierarchy-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        html.P([
                            html.I(className="fas fa-info-circle me-2", style={'color': COLORS['primary']}),
                            "Click on segments to drill down. Use mouse wheel to zoom, drag to pan."
                        ], className="text-muted small mb-2", style={'fontSize': '12px'}),
                        dcc.Graph(
                            id="sunburst-chart",
                            config={
                                'scrollZoom': True,
                                'displayModeBar': True,
                                'displaylogo': False,
                                'modeBarButtonsToAdd': ['resetScale2d', 'pan2d', 'zoomIn2d', 'zoomOut2d'],
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'sunburst_chart',
                                    'height': 500,
                                    'width': 800,
                                    'scale': 1
                                }
                            }
                        )
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Neighborhood/Ward Analysis Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-map-marked-alt me-2"),
                            "Neighborhood & Ward Analysis",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="neighborhood-analysis-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        dcc.Graph(id="neighborhood-analysis")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Main Charts with Professional Styling
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-chart-line me-2"),
                            "CTA Ridership & Complaints Trends",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="cta-trend-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                dcc.Graph(id="sentiment-ridership-chart")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-chart-area me-2"),
                            "Time Series Overview",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="ts-overview-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                dcc.Graph(id="time-series-chart")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Complaint Type Distribution",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="complaint-distribution-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                dcc.Graph(id="sentiment-distribution-chart")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-project-diagram me-2"),
                            "Correlation Matrix",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="corr-matrix-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                dcc.Graph(id="correlation-heatmap")
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=6)
        ]),
        
        # Traffic & Crime Comparison Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-chart-pie me-2"),
                            "Traffic Volume vs Crime Comparison",
                            html.I(
                                className="fas fa-info-circle ms-2 text-muted",
                                id="traffic-crime-help",
                                style={"cursor": "pointer", "fontSize": "0.9rem"}
                            )
                        ], className="mb-3", style={'color': COLORS['dark'], 'fontWeight': '600'}),
                        dcc.Graph(
                            id="traffic-crime-chart",
                            style={'height': '400px'}
                        )
                    ])
                ], className="mb-4", style={
                    'border': f'1px solid {COLORS["light"]}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], md=12)
        ]),
        
        # Help Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Help & User Guide")),
            dbc.ModalBody([
                html.H5("Keyboard Shortcuts", className="mb-3"),
                html.Ul([
                    html.Li("Ctrl/Cmd + E: Export current data"),
                    html.Li("Ctrl/Cmd + R: Export report"),
                    html.Li("Ctrl/Cmd + H: Show this help"),
                    html.Li("Ctrl/Cmd + A: Show about"),
                    html.Li("Esc: Close modals")
        ], className="mb-4"),
                html.H5("Chart Explanations", className="mb-3"),
                html.P([
                    html.Strong("CTA Ridership vs. Complaints:"), " Shows correlation between transit usage and service complaints."
                ], className="mb-2"),
                html.P([
                    html.Strong("Time Series Overview:"), " Displays trends over time for ridership, complaints, traffic volume, and crime."
                ], className="mb-2"),
                html.P([
                    html.Strong("Box/Violin Plots:"), " Distribution analysis showing crime patterns by day of week."
                ], className="mb-2"),
                html.P([
                    html.Strong("Gauge Charts:"), " Performance indicators with thresholds for key metrics."
                ], className="mb-2"),
                html.P([
                    html.Strong("Sunburst Chart:"), " Hierarchical breakdown of complaint types."
                ], className="mb-2"),
                html.P([
                    html.Strong("Neighborhood Analysis:"), " Geographic analysis by community area and ward with hotspot detection."
                ], className="mb-4"),
                html.H5("Export Options", className="mb-3"),
                html.P("Use the export buttons to download charts as PNG/PDF, data as CSV/Excel, or generate comprehensive PDF reports."),
                html.H5("Methodology", className="mb-3"),
                html.P([
                    "Statistical analysis includes confidence intervals (95%), ",
                    "p-values, effect sizes (Cohen's d), and regression coefficients. Hotspot detection uses DBSCAN clustering."
                ])
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-help", className="ms-auto", n_clicks=0)
            )
        ], id="help-modal", is_open=False),
        
        # About Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("About CityPulse")),
            dbc.ModalBody([
                html.H5("Project Overview", className="mb-3"),
                html.P([
                    "CityPulse is an integrated dashboard that visualizes mobility and service patterns in Chicago, ",
                    "combining transportation data, bike share usage, crime statistics, and 311 service data to reveal urban trends and patterns."
        ], className="mb-4"),
                html.H5("Data Sources", className="mb-3"),
                html.Ul([
                    html.Li("Chicago 311 Service Requests API"),
                    html.Li("Chicago Transit Authority (CTA) Ridership Data"),
                    html.Li("Traffic Volume Data"),
                    html.Li("Chicago Crime Data")
                ], className="mb-4"),
                html.H5("Technology Stack", className="mb-3"),
                html.P([
                    "Built with Python, Dash, Plotly, pandas, and scikit-learn. ",
                    "Statistical analysis powered by scipy and scikit-learn. ",
                    "Statistical analysis using scipy."
                ], className="mb-4"),
                html.H5("Key Features", className="mb-3"),
                html.Ul([
                    html.Li("Real-time data integration"),
                    html.Li("Advanced statistical analysis with confidence intervals and p-values"),
                    html.Li("Geographic hotspot detection"),
                    html.Li("Neighborhood and ward-level analysis"),
                    html.Li("Export capabilities (PNG, PDF, CSV, Excel)"),
                    html.Li("Interactive visualizations")
                ]),
                html.Hr(),
                html.P([
                    html.I(className="fas fa-link me-2"),
                    html.A("Data Dictionary", href="#", id="data-dict-link", className="text-decoration-none")
                ], className="mb-2"),
                html.P([
                    html.I(className="fas fa-book me-2"),
                    "For detailed methodology, see the project documentation."
                ], className="text-muted", style={'fontSize': '0.9rem'})
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-about", className="ms-auto", n_clicks=0)
            )
        ], id="about-modal", is_open=False),
        
        # Download components
        dcc.Download(id="download-data"),
        dcc.Download(id="download-report"),
        
        # Professional Footer
        dbc.Row([
            dbc.Col([
                html.Hr(style={'borderTop': f'2px solid {COLORS["light"]}', 'marginTop': '3rem', 'marginBottom': '2rem'}),
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.H6("CityPulse Dashboard", className="mb-2", style={
                                    'color': COLORS['primary'],
                                    'fontWeight': '600'
                                }),
                                html.P("Urban Mobility & Service Analysis", className="text-muted mb-2", style={'fontSize': '0.9rem'}),
                                html.P([
                                    html.I(className="fas fa-map-marker-alt me-2"),
                                    "Chicago, IL"
                                ], className="text-muted mb-1", style={'fontSize': '0.85rem'}),
                                html.P([
                                    html.I(className="fas fa-database me-2"),
                                    "Data Sources: Chicago 311 API, CTA Ridership Data, Traffic Volume Data, Crime Data"
                                ], className="text-muted mb-1", style={'fontSize': '0.85rem'}),
                                html.P([
                                    html.I(className="fas fa-clock me-2"),
                                    f"Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
                                ], className="text-muted mb-0", style={'fontSize': '0.85rem'})
                            ], className="text-center")
                        ])
                    ])
                ], style={
                    'background': f'linear-gradient(135deg, {COLORS["light"]} 0%, white 100%)',
                    'border': 'none',
                    'boxShadow': 'none'
                })
            ])
        ], className="mt-5"),
        
        # Tooltips for chart explanations
        dbc.Tooltip(
            [
                html.P("Shows total citywide traffic volume over the selected period.", className="mb-1"),
                html.Ul([
                    html.Li("Higher values mean more vehicles or bus/message counts on the network."),
                    html.Li("Compare this with crime and complaints to see if busy days are also 'problem' days."),
                    html.Li("Use date filters to focus on specific months or weeks."),
                ], className="mb-0")
            ],
            target="traffic-volume-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows how many trips people took on CTA during the selected period.", className="mb-1"),
                html.Ul([
                    html.Li("Higher ridership can mean more people depending on transit that day."),
                    html.Li("Check if high-ridership days correspond to more or fewer complaints."),
                    html.Li("Look for ridership dips that might signal service disruptions or holidays."),
                ], className="mb-0")
            ],
            target="cta-rides-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows how many 311 service requests were filed.", className="mb-1"),
                html.Ul([
                    html.Li("Spikes can indicate service or infrastructure stress (e.g., potholes, lights, noise)."),
                    html.Li("Compare with traffic and crimes to find days when the city 'felt worse' to residents."),
                    html.Li("Use complaint-type filters to narrow to specific issues."),
                ], className="mb-0")
            ],
            target="complaints-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows reported crime incidents during the selected period.", className="mb-1"),
                html.Ul([
                    html.Li("Use it as a high-level safety indicator over time."),
                    html.Li("Compare with traffic and 311 to see if busy or noisy days have more crime."),
                    html.Li("Filter by crime type on the map to see specific patterns."),
                ], className="mb-0")
            ],
            target="crimes-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows where 311 complaints are concentrated across the city.", className="mb-1"),
                html.Ul([
                    html.Li("Use the date and complaint type filters to focus on particular issues."),
                    html.Li("Denser clusters can indicate chronic infrastructure or noise problems."),
                    html.Li("Compare with hotspots and neighborhood analysis to see systemic issues."),
                ], className="mb-0")
            ],
            target="complaint-map-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows where reported crimes occur.", className="mb-1"),
                html.Ul([
                    html.Li("Filter by date range and crime type to see specific patterns."),
                    html.Li("Clusters near major transit or traffic corridors may need safety interventions."),
                    html.Li("Helps align police, lighting, and design changes with actual risk."),
                ], className="mb-0")
            ],
            target="crime-map-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Highlights locations where many complaints cluster in a small area.", className="mb-1"),
                html.Ul([
                    html.Li("Large or dark markers show areas with the most complaints."),
                    html.Li("The ranking list on the right explains the top hotspots in plain language."),
                    html.Li("Use this to prioritize field inspections, repairs, or targeted programs."),
                ], className="mb-0")
            ],
            target="hotspot-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows how key metrics behave differently across days of the week.", className="mb-1"),
                html.Ul([
                    html.Li("Look for patterns: e.g., are Mondays busier for traffic and complaints?"),
                    html.Li("Weekend vs weekday differences can reveal commuter vs leisure patterns."),
                    html.Li("Use this to plan staffing or maintenance schedules."),
                ], className="mb-0")
            ],
            target="day-of-week-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Translates key correlations into plain-language insights.", className="mb-1"),
                html.Ul([
                    html.Li("Each card explains one important relationship (e.g., traffic vs crime)."),
                    html.Li("Green or strong values suggest metrics that consistently move together."),
                    html.Li("Use these statements as talking points in board discussions."),
                ], className="mb-0")
            ],
            target="corr-simple-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Summarizes transit, complaints, crime (and optionally traffic speed) into one health score.", className="mb-1"),
                html.Ul([
                    html.Li("Higher scores mean better mobility, fewer complaints, and safer conditions overall."),
                    html.Li("The breakdown shows which component (ridership, complaints, crime, speed) is dragging the score down."),
                    html.Li("Use this to track whether the city is improving over time, not just on single metrics."),
                ], className="mb-0")
            ],
            target="health-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Compares CTA ridership with 311 complaints over time.", className="mb-1"),
                html.Ul([
                    html.Li("See if complaints rise when ridership is high (possible strain) or low (service issues)."),
                    html.Li("Look for periods where complaints spike without a ridership change."),
                    html.Li("Use this to argue for targeted improvements on specific dates or seasons."),
                ], className="mb-0")
            ],
            target="cta-trend-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows how key metrics move together over the year.", className="mb-1"),
                html.Ul([
                    html.Li("Look for parallel lines: metrics that rise and fall together may be related."),
                    html.Li("Check for repeated weekly or seasonal peaks."),
                    html.Li("Use date filters to zoom into a specific incident or month."),
                ], className="mb-0")
            ],
            target="ts-overview-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows how strongly each metric moves with the others.", className="mb-1"),
                html.Ul([
                    html.Li("Dark/bright cells indicate stronger relationships (positive or negative)."),
                    html.Li("Focus on pairs like traffic vs crime, ridership vs complaints."),
                    html.Li("Correlations do not prove causation, but highlight where to investigate."),
                ], className="mb-0")
            ],
            target="corr-matrix-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Compares traffic volume against crime levels.", className="mb-1"),
                html.Ul([
                    html.Li("Look for whether high traffic days tend to have more or fewer crimes."),
                    html.Li("Helps distinguish 'busy but safe' from 'busy and risky' periods."),
                    html.Li("Use this to argue for targeted enforcement or safety investments on key corridors/days."),
                ], className="mb-0")
            ],
            target="traffic-crime-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows statistical relationships between metrics with confidence intervals and significance tests.", className="mb-1"),
                html.Ul([
                    html.Li("P-values < 0.05 indicate statistically significant relationships."),
                    html.Li("Effect sizes show how strong the relationship is (small, medium, or large)."),
                    html.Li("Use this to make data-driven decisions with statistical backing."),
                ], className="mb-0")
            ],
            target="statistical-analysis-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows how crime counts vary by day of week using box and violin plots.", className="mb-1"),
                html.Ul([
                    html.Li("Box plots show median, quartiles, and outliers for each day."),
                    html.Li("Violin plots show the full distribution shape (where crimes cluster)."),
                    html.Li("Use this to identify which days of the week have consistently higher crime."),
                ], className="mb-0")
            ],
            target="crime-distribution-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Gauge charts showing normalized performance metrics for key indicators.", className="mb-1"),
                html.Ul([
                    html.Li("Each gauge shows how a metric compares to its typical range (0-100%)."),
                    html.Li("Green zones indicate good performance, red zones need attention."),
                    html.Li("Use this for quick visual assessment of system health at a glance."),
                ], className="mb-0")
            ],
            target="performance-indicators-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Interactive hierarchical view of complaint types organized by category.", className="mb-1"),
                html.Ul([
                    html.Li("Click on segments to drill down into subcategories."),
                    html.Li("Larger segments represent more complaints in that category."),
                    html.Li("Use this to understand which types of issues dominate resident concerns."),
                ], className="mb-0")
            ],
            target="complaint-hierarchy-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Geographic breakdown of metrics by neighborhood or ward boundaries.", className="mb-1"),
                html.Ul([
                    html.Li("Compare different areas to see where problems are concentrated."),
                    html.Li("Use filters to focus on specific neighborhoods or metrics."),
                    html.Li("Helps identify areas that need targeted interventions or resources."),
                ], className="mb-0")
            ],
            target="neighborhood-analysis-help",
            placement="top",
            style={"maxWidth": "320px"}
        ),
        dbc.Tooltip(
            [
                html.P("Shows the breakdown of complaint types as a bar chart.", className="mb-1"),
                html.Ul([
                    html.Li("Taller bars indicate more complaints of that type."),
                    html.Li("Use this to see which issues residents report most frequently."),
                    html.Li("Compare with other metrics to see if certain complaint types correlate with traffic or crime."),
                ], className="mb-0")
            ],
            target="complaint-distribution-help",
            placement="top",
            style={"maxWidth": "320px"}
        )
    ], fluid=True, style={'padding': '20px', 'backgroundColor': '#FAFAFA'})


# Neighborhood filter callback
@app.callback(
    Output("neighborhood-filter", "options"),
    [Input("neighborhood-filter", "id")]
)
def update_neighborhood_filter(_):
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    options = [{'label': 'All Areas', 'value': 'All'}]
    
    if complaints_path.exists():
        try:
            df_complaints = pd.read_csv(complaints_path, low_memory=False)
            
            # Add neighborhoods
            if 'community_area' in df_complaints.columns:
                neighborhoods = df_complaints['community_area'].dropna().unique()
                for area in sorted(neighborhoods)[:30]:  # Limit to 30
                    options.append({'label': f"Area {area}", 'value': str(area)})
            
            # Add wards
            if 'ward' in df_complaints.columns:
                wards = df_complaints['ward'].dropna().unique()
                for ward in sorted(wards):
                    options.append({'label': f"Ward {int(ward)}", 'value': f"Ward_{int(ward)}"})
        except Exception as e:
            logger.warning(f"Error loading neighborhoods: {e}")
    
    return options

# Crime type filter callback
@app.callback(
    Output("crime-type-filter", "options"),
    [Input("crime-type-filter", "id")]
)
def update_crime_type_filter(_):
    crime_path = PROJECT_ROOT / "data" / "cleaned" / "crime_data.csv"
    options = [{'label': 'All Crime Types', 'value': 'All'}]
    
    if crime_path.exists():
        try:
            df_crimes = pd.read_csv(crime_path, low_memory=False)
            
            # Add crime types
            if 'primary_type' in df_crimes.columns:
                crime_types = df_crimes['primary_type'].dropna().unique()
                for crime_type in sorted(crime_types):
                    options.append({'label': str(crime_type), 'value': str(crime_type)})
        except Exception as e:
            logger.warning(f"Error loading crime types: {e}")
    
    return options

# Modal callbacks
@app.callback(
    Output("help-modal", "is_open"),
    [Input("help-btn", "n_clicks"), Input("close-help", "n_clicks")],
    [State("help-modal", "is_open")]
)
def toggle_help_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("about-modal", "is_open"),
    [Input("about-btn", "n_clicks"), Input("close-about", "n_clicks")],
    [State("about-modal", "is_open")]
)
def toggle_about_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Export callbacks
@app.callback(
    Output("download-data", "data"),
    [Input("export-data-btn", "n_clicks")],
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date'),
     State('complaint-type-filter', 'value')],
    prevent_initial_call=True
)
def export_data(n_clicks, start_date, end_date, complaint_type):
    if n_clicks:
        df = load_data()
        if not df.empty:
            # Filter data
            if start_date and end_date:
                mask = (df['date'] >= start_date) & (df['date'] <= end_date)
                df_filtered = df[mask].copy()
            else:
                df_filtered = df.copy()
            
            # Convert to CSV string
            csv_string = df_filtered.to_csv(index=False)
            filename = f"citypulse_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return dict(content=csv_string, filename=filename)
    return None

@app.callback(
    Output("download-report", "data"),
    [Input("export-report-btn", "n_clicks")],
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date')],
    prevent_initial_call=True
)
def export_report(n_clicks, start_date, end_date):
    if n_clicks:
        # For now, export data as Excel as a simple report
        # Full PDF report generation would require chart figures from callbacks
        df = load_data()
        if not df.empty:
            if start_date and end_date:
                mask = (df['date'] >= start_date) & (df['date'] <= end_date)
                df_filtered = df[mask].copy()
            else:
                df_filtered = df.copy()
            
            # Export as Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filtered.to_excel(writer, sheet_name='Data', index=False)
            
            buffer.seek(0)
            filename = f"citypulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            return dict(content=base64.b64encode(buffer.read()).decode(), filename=filename, type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return None

# Temporal Patterns Callback
@app.callback(
    [Output("day-of-week-chart", "figure"),
     Output("temporal-patterns-insights", "children")],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_temporal_patterns(start_date, end_date):
    df = load_data()
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("No data available", className="text-muted")
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Analyze day of week patterns
    metric_cols = ['total_cta_rides', 'total_311_complaints', 'total_crimes']
    metric_cols = [col for col in metric_cols if col in df_filtered.columns]
    
    if not metric_cols:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No metric data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("No metric data available", className="text-muted")
    
    day_patterns = analyze_day_of_week_patterns(df_filtered, date_col='date', metric_cols=metric_cols)
    
    if day_patterns.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No day patterns available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("No day patterns available", className="text-muted")
    
    # Create multi-metric bar chart
    fig = create_multi_metric_bar_chart(
        day_patterns, 
        x_col='day_name',
        y_cols=metric_cols,
        title="Average by Day of Week"
    )
    
    # Generate insights
    insights = []
    for metric_col in metric_cols:
        peak_info = get_peak_days(day_patterns, metric_col, day_col='day_name')
        if peak_info:
            metric_name = metric_col.replace('_', ' ').title()
            insights.append(
                dbc.Alert([
                    html.Strong(f"{metric_name}: "),
                    f"Peak: {peak_info['peak_day']}, Low: {peak_info['low_day']}"
                ], color="info", className="mb-2")
            )
    
    insights_div = html.Div(insights) if insights else html.P("No insights available", className="text-muted")
    
    return fig, insights_div

# Correlation Insights Callback
@app.callback(
    [Output("correlation-heatmap-simple", "figure"),
     Output("correlation-insights-cards", "children")],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_correlation_insights(start_date, end_date):
    df = load_data()
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=500)
        return empty_fig, html.P("No data available", className="text-muted")
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Calculate correlations
    metric_cols = ['total_cta_rides', 'total_311_complaints', 'total_crimes']
    metric_cols = [col for col in metric_cols if col in df_filtered.columns]
    
    if len(metric_cols) < 2:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Need at least 2 metrics for correlation", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=500)
        return empty_fig, html.P("Need at least 2 metrics for correlation", className="text-muted")
    
    corr_results = calculate_simple_correlations(df_filtered, metric_cols)
    
    if not corr_results or 'correlation_matrix' not in corr_results:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No correlation data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=500)
        return empty_fig, html.P("No correlation data available", className="text-muted")
    
    # Create heatmap
    labels = {
        'total_cta_rides': 'CTA Ridership',
        'total_311_complaints': '311 Complaints',
        'total_crimes': 'Crimes'
    }
    fig = create_correlation_heatmap(corr_results['correlation_matrix'], labels)
    
    # Create insight cards for top correlations
    top_corrs = get_top_correlations(df_filtered, n=3, metric_cols=metric_cols)
    cards = []
    
    for corr_data in top_corrs:
        insight = corr_data.get('insight', {})
        if isinstance(insight, dict):
            text = insight.get('text', '')
            emoji = insight.get('strength_emoji', '🔵')
        else:
            text = str(insight)
            emoji = '🔵'
        
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6([emoji, " ", text[:100]], className="mb-0", style={'fontSize': '0.9rem'})
                ])
            ], className="mb-2", style={'borderLeft': f'4px solid {COLORS["primary"]}'})
        )
    
    cards_div = html.Div(cards) if cards else html.P("No correlation insights available", className="text-muted")
    
    return fig, cards_div

# Health Score Callback
@app.callback(
    [Output("health-gauge-chart", "figure"),
     Output("health-score-breakdown", "children")],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_health_scores(start_date, end_date):
    df = load_data()
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("No data available", className="text-muted")
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Calculate health index
    health_data = calculate_urban_health_index(df_filtered)
    
    if not health_data:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No health data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("No health data available", className="text-muted")
    
    # Create gauge chart
    fig = create_health_gauge(health_data['overall_score'], "Overall City Health")
    
    # Create breakdown cards
    cards = []
    
    cards.append(
        dbc.Card([
            dbc.CardBody([
                html.H6("Mobility Score", className="mb-2"),
                html.H3(f"{health_data['mobility_score']}/10", style={'color': COLORS['primary']}),
                html.Small(f"Based on CTA Ridership", className="text-muted")
            ])
        ], className="mb-3", style={'borderTop': f'4px solid {COLORS["primary"]}'})
    )
    
    cards.append(
        dbc.Card([
            dbc.CardBody([
                html.H6("Service Quality Score", className="mb-2"),
                html.H3(f"{health_data['service_quality_score']}/10", style={'color': COLORS['warning']}),
                html.Small(f"Based on 311 Complaints", className="text-muted")
            ])
        ], className="mb-3", style={'borderTop': f'4px solid {COLORS["warning"]}'})
    )
    
    cards.append(
        dbc.Card([
            dbc.CardBody([
                html.H6("Safety Score", className="mb-2"),
                html.H3(f"{health_data['safety_score']}/10", style={'color': COLORS['danger']}),
                html.Small(f"Based on Crime Data", className="text-muted")
            ])
        ], className="mb-3", style={'borderTop': f'4px solid {COLORS["danger"]}'})
    )
    
    status_card = dbc.Alert([
        html.H5([health_data['status_emoji'], " ", health_data['status']], className="mb-0"),
        html.P(f"Overall Score: {health_data['overall_score']}/10", className="mb-0 mt-2")
    ], color="success" if health_data['overall_score'] >= 8 else 
       "warning" if health_data['overall_score'] >= 6 else 
       "danger", className="mt-3")
    
    cards.append(status_card)
    
    return fig, html.Div(cards)

# Enhanced Hotspot Analysis Callback
@app.callback(
    [Output("hotspot-map-enhanced", "figure"),
     Output("hotspot-ranking-list", "children")],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_hotspot_analysis(start_date, end_date):
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    
    if not complaints_path.exists():
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No complaint data available", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("No complaint data available", className="text-muted")
    
    try:
        df_complaints = pd.read_csv(str(complaints_path), low_memory=False)
        
        # Filter by date if available
        if 'created_date' in df_complaints.columns and start_date and end_date:
            df_complaints['created_date'] = pd.to_datetime(df_complaints['created_date'], errors='coerce')
            date_mask = (df_complaints['created_date'] >= start_date) & (df_complaints['created_date'] <= end_date)
            df_complaints = df_complaints[date_mask]
        
        # Filter valid coordinates
        df_map = df_complaints[
            (df_complaints['latitude'].notna()) &
            (df_complaints['longitude'].notna()) &
            (df_complaints['latitude'] >= 41.64) &
            (df_complaints['latitude'] <= 42.02) &
            (df_complaints['longitude'] >= -87.94) &
            (df_complaints['longitude'] <= -87.60)
        ].copy()
        
        if len(df_map) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="No geospatial data available", xref="paper", yref="paper", x=0.5, y=0.5)
            empty_fig.update_layout(height=400)
            return empty_fig, html.P("No geospatial data available", className="text-muted")
        
        # Detect hotspots
        try:
            df_labeled, hotspot_stats = detect_hotspots(df_map.head(5000))  # Limit for performance
        except:
            from src.analytics.neighborhood_analysis import detect_hotspots_simple
            df_labeled, hotspot_stats = detect_hotspots_simple(df_map.head(5000))
        
        # Create map
        fig = go.Figure()
        
        # Add all points
        fig.add_trace(go.Scattermapbox(
            lat=df_map['latitude'],
            lon=df_map['longitude'],
            mode='markers',
            marker=dict(size=5, color=COLORS['primary'], opacity=0.3),
            name='All Complaints',
            hovertemplate='<b>Complaint Location</b><br>Lat: %{lat:.4f}<br>Lon: %{lon:.4f}<extra></extra>'
        ))
        
        # Add hotspot centers if available
        if not hotspot_stats.empty:
            top_hotspots = get_top_hotspots(hotspot_stats, n=10)
            for idx, row in top_hotspots.iterrows():
                fig.add_trace(go.Scattermapbox(
                    lat=[row['center_latitude']],
                    lon=[row['center_longitude']],
                    mode='markers+text',
                    marker=dict(size=min(row['point_count']*2, 50), color=COLORS['danger'], opacity=0.7),
                    text=[f"#{int(row.get('rank', idx+1))}"],
                    textposition="middle center",
                    name=f"Hotspot {int(row.get('rank', idx+1))}",
                    hovertemplate=f'<b>Hotspot #{int(row.get("rank", idx+1))}</b><br>Count: {int(row["point_count"])}<extra></extra>'
                ))
        
        fig.update_layout(
            title="Complaint Hotspots",
            mapbox=dict(
                center=dict(lat=41.8781, lon=-87.6298),
                zoom=10,
                style="open-street-map"
            ),
            height=500,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Create ranking list
        if not hotspot_stats.empty:
            top_hotspots = get_top_hotspots(hotspot_stats, n=10)
            ranking_items = []
            for idx, row in top_hotspots.iterrows():
                desc = format_hotspot_description(row)
                ranking_items.append(
                    html.Div([
                        html.Strong(f"#{int(row.get('rank', idx+1))} "),
                        desc
                    ], className="mb-2 p-2", style={
                        'backgroundColor': COLORS['light'],
                        'borderRadius': '4px',
                        'fontSize': '0.9rem'
                    })
                )
            
            ranking_div = html.Div([
                html.H6("Top 10 Hotspots", className="mb-3"),
                html.Div(ranking_items)
            ])
        else:
            ranking_div = html.P("No hotspots detected", className="text-muted")
        
        return fig, ranking_div
        
    except Exception as e:
        logger.error(f"Error in hotspot analysis: {e}")
        import traceback
        logger.error(traceback.format_exc())
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Error loading hotspot data", xref="paper", yref="paper", x=0.5, y=0.5)
        empty_fig.update_layout(height=400)
        return empty_fig, html.P("Error loading hotspot data", className="text-muted")

# Statistical Analysis callback
@app.callback(
    Output("statistical-analysis", "children"),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_statistical_analysis(start_date, end_date):
    df = load_data()
    if df.empty:
        return html.P("No data available for statistical analysis", className="text-muted")
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    stats_cards = []
    
    # Calculate correlations with statistics
    if 'total_cta_rides' in df_filtered.columns and 'total_311_complaints' in df_filtered.columns:
        corr_stats = calculate_correlation_with_stats(
            df_filtered['total_cta_rides'], 
            df_filtered['total_311_complaints']
        )
        effect = calculate_effect_size(
            df_filtered['total_cta_rides'], 
            df_filtered['total_311_complaints']
        )
        
        stats_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6("CTA Ridership vs. Complaints", className="mb-2"),
                    html.P([
                        html.Strong("Correlation: "), f"{corr_stats['correlation']:.3f}",
                        html.Br(),
                        html.Strong("P-value: "), f"{corr_stats['p_value']:.4f}",
                        html.Br(),
                        html.Strong("95% CI: "), f"[{corr_stats['ci_lower']:.3f}, {corr_stats['ci_upper']:.3f}]",
                        html.Br(),
                        html.Strong("R²: "), f"{effect['r_squared']:.3f}",
                        html.Br(),
                        html.Strong("Effect Size: "), f"{effect['interpretation']} (d={effect['cohens_d']:.3f})",
                        html.Br(),
                        html.Span(
                            "✓ Significant" if corr_stats['significant'] else "✗ Not Significant",
                            style={'color': COLORS['success'] if corr_stats['significant'] else COLORS['accent']}
                        )
                    ], style={'fontSize': '0.9rem'})
                ])
            ], className="mb-2")
        )
    
    if 'total_traffic_volume' in df_filtered.columns and 'total_crimes' in df_filtered.columns:
        corr_stats = calculate_correlation_with_stats(
            df_filtered['total_traffic_volume'], 
            df_filtered['total_crimes']
        )
        
        stats_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6("Traffic Volume vs. Crime", className="mb-2"),
                    html.P([
                        html.Strong("Correlation: "), f"{corr_stats['correlation']:.3f}",
                        html.Br(),
                        html.Strong("P-value: "), f"{corr_stats['p_value']:.4f}",
                        html.Br(),
                        html.Strong("95% CI: "), f"[{corr_stats['ci_lower']:.3f}, {corr_stats['ci_upper']:.3f}]",
                        html.Br(),
                        html.Span(
                            "✓ Significant" if corr_stats['significant'] else "✗ Not Significant",
                            style={'color': COLORS['success'] if corr_stats['significant'] else COLORS['accent']}
                        )
                    ], style={'fontSize': '0.9rem'})
                ])
            ], className="mb-2")
        )
    
    if not stats_cards:
        return html.P("Insufficient data for statistical analysis", className="text-muted")
    
    return dbc.Row([dbc.Col(card, md=6) for card in stats_cards])

# New chart type callbacks
@app.callback(
    Output("box-violin-chart", "figure"),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_box_violin_chart(start_date, end_date):
    df = load_data()
    if df.empty or 'total_crimes' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Add day of week
    df_filtered['day_of_week'] = pd.to_datetime(df_filtered['date']).dt.day_name()
    
    # Create subplots with box and violin plots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Box Plot", "Violin Plot"),
        horizontal_spacing=0.15
    )
    
    # Box plot
    for day in df_filtered['day_of_week'].unique():
        day_data = df_filtered[df_filtered['day_of_week'] == day]['total_crimes']
        fig.add_trace(
            go.Box(
                y=day_data,
                name=day,
                boxpoints='outliers',
                marker_color=COLORS['chart_red']
            ),
            row=1, col=1
        )
    
    # Violin plot
    for day in df_filtered['day_of_week'].unique():
        day_data = df_filtered[df_filtered['day_of_week'] == day]['total_crimes']
        fig.add_trace(
            go.Violin(
                y=day_data,
                name=day,
                box_visible=True,
                meanline_visible=True,
                marker_color=COLORS['chart_purple']
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="Crime Distribution by Day of Week",
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

@app.callback(
    Output("gauge-charts", "figure"),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_gauge_charts(start_date, end_date):
    df = load_data()
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Create subplots for multiple gauges
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=("Traffic Volume Index", "Complaint Rate", "Ridership Index")
    )
    
    # Traffic volume gauge (normalized)
    if 'total_traffic_volume' in df_filtered.columns:
        traffic_volume = df_filtered['total_traffic_volume'].sum()
        traffic_max = df_filtered['total_traffic_volume'].max() if df_filtered['total_traffic_volume'].max() > 0 else 1
        traffic_norm = min(traffic_volume / (traffic_max * len(df_filtered)) * 100, 100) if traffic_max > 0 else 0
    else:
        traffic_norm = 0
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=traffic_norm,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Traffic Index"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['chart_blue']},
                'steps': [
                    {'range': [0, 33], 'color': COLORS['light']},
                    {'range': [33, 66], 'color': COLORS['chart_green']},
                    {'range': [66, 100], 'color': COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ),
        row=1, col=1
    )
    
    # Complaint rate gauge (normalized)
    if 'total_311_complaints' in df_filtered.columns:
        complaints = df_filtered['total_311_complaints'].sum()
        max_complaints = df['total_311_complaints'].max() if 'total_311_complaints' in df.columns else 100
        complaint_rate = min(complaints / max_complaints if max_complaints > 0 else 0, 1.0) * 100
    else:
        complaint_rate = 0
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=complaint_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Complaint Rate"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['chart_orange']},
                'steps': [
                    {'range': [0, 33], 'color': COLORS['sentiment_positive']},
                    {'range': [33, 66], 'color': COLORS['sentiment_neutral']},
                    {'range': [66, 100], 'color': COLORS['sentiment_negative']}
                ]
            }
        ),
        row=1, col=2
    )
    
    # Ridership index gauge
    if 'total_cta_rides' in df_filtered.columns:
        rides = df_filtered['total_cta_rides'].sum()
        max_rides = df['total_cta_rides'].max() if 'total_cta_rides' in df.columns else 1000000
        ridership_index = min(rides / max_rides if max_rides > 0 else 0, 1.0) * 100
    else:
        ridership_index = 0
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ridership_index,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Ridership Index"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['chart_green']},
                'steps': [
                    {'range': [0, 50], 'color': COLORS['sentiment_negative']},
                    {'range': [50, 75], 'color': COLORS['sentiment_neutral']},
                    {'range': [75, 100], 'color': COLORS['sentiment_positive']}
                ]
            }
        ),
        row=1, col=3
    )
    
    fig.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white')
    return fig

@app.callback(
    Output("sunburst-chart", "figure"),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('complaint-type-filter', 'value')]
)
def update_sunburst_chart(start_date, end_date, complaint_type):
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    if not complaints_path.exists():
        fig = go.Figure()
        fig.add_annotation(text="No complaint data available", xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    try:
        df_complaints = pd.read_csv(complaints_path)
        
        # Filter by date if available
        if 'created_date' in df_complaints.columns:
            df_complaints['created_date'] = pd.to_datetime(df_complaints['created_date'], errors='coerce')
            if start_date and end_date:
                mask = (df_complaints['created_date'] >= start_date) & (df_complaints['created_date'] <= end_date)
                df_complaints = df_complaints[mask]
        
        # Filter by complaint type - check for sr_type or service_request_type
        type_col = 'sr_type' if 'sr_type' in df_complaints.columns else ('service_request_type' if 'service_request_type' in df_complaints.columns else None)
        if complaint_type and complaint_type != 'All' and type_col:
            df_complaints = df_complaints[df_complaints[type_col] == complaint_type]
        
        # Create hierarchy: Status -> Type
        if 'status' in df_complaints.columns and type_col:
            hierarchy = df_complaints.groupby(['status', type_col]).size().reset_index(name='count')
            
            # Create sunburst chart
            fig = px.sunburst(
                hierarchy,
                path=['status', type_col],
                values='count',
                color='count',
                color_continuous_scale='Blues',
                branchvalues='total'
            )
            fig.update_layout(
                title=dict(
                    text="Complaint Type Hierarchy",
                    font=dict(size=16, color=COLORS['dark'], family="Arial, sans-serif"),
                    x=0.5,
                    xanchor='center'
                ),
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=60, b=20),
                # Enable interactions
                clickmode='event+select',
                hovermode='closest'
            )
            # Add custom hover template
            fig.update_traces(
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percentParent:.1%}<extra></extra>',
                textinfo='label+percent parent'
            )
        else:
            # Fallback: just complaint types
            type_col = 'sr_type' if 'sr_type' in df_complaints.columns else ('service_request_type' if 'service_request_type' in df_complaints.columns else None)
            if type_col:
                type_counts = df_complaints[type_col].value_counts().reset_index()
                type_counts.columns = ['type', 'count']
                fig = px.sunburst(
                    type_counts,
                    path=['type'],
                    values='count',
                    color='count',
                    color_continuous_scale='Blues',
                    branchvalues='total'
                )
                fig.update_layout(
                    title=dict(
                        text="Complaint Type Distribution",
                        font=dict(size=16, color=COLORS['dark'], family="Arial, sans-serif"),
                        x=0.5,
                        xanchor='center'
                    ),
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=60, b=20),
                    # Enable interactions
                    clickmode='event+select',
                    hovermode='closest'
                )
                # Add custom hover template
                fig.update_traces(
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percentRoot:.1%}<extra></extra>',
                    textinfo='label+percent root'
                )
            else:
                fig = go.Figure()
                fig.add_annotation(text="Insufficient data for sunburst chart", xref="paper", yref="paper", x=0.5, y=0.5)
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
    except Exception as e:
        logger.warning(f"Error creating sunburst chart: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Error loading data", xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
    
    return fig

@app.callback(
    Output("neighborhood-analysis", "figure"),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('neighborhood-filter', 'value')]
)
def update_neighborhood_analysis(start_date, end_date, neighborhood):
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    if not complaints_path.exists():
        fig = go.Figure()
        fig.add_annotation(text="No complaint data available", xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    try:
        df_complaints = pd.read_csv(complaints_path)
        
        # Filter by date if available
        if 'created_date' in df_complaints.columns:
            df_complaints['created_date'] = pd.to_datetime(df_complaints['created_date'], errors='coerce')
            if start_date and end_date:
                mask = (df_complaints['created_date'] >= start_date) & (df_complaints['created_date'] <= end_date)
                df_complaints = df_complaints[mask]
        
        # Aggregate by neighborhood
        if 'community_area' in df_complaints.columns:
            neighborhood_stats = aggregate_by_neighborhood(df_complaints)
            
            if not neighborhood_stats.empty and 'complaint_count' in neighborhood_stats.columns:
                # Create bar chart of top neighborhoods
                top_neighborhoods = neighborhood_stats.nlargest(15, 'complaint_count')
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=top_neighborhoods['complaint_count'],
                        y=top_neighborhoods['community_area'],
                        orientation='h',
                        marker=dict(
                            color=top_neighborhoods['complaint_count'],
                            colorscale='Reds',
                            showscale=True
                        ),
                        hovertemplate='<b>%{y}</b><br>Complaints: %{x}<extra></extra>'
                    )
                ])
                
                fig.update_layout(
                    title="Top Neighborhoods by Complaint Count",
                    xaxis_title="Number of Complaints",
                    yaxis_title="Community Area",
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    yaxis={'categoryorder': 'total ascending'}
                )
            else:
                fig = go.Figure()
                fig.add_annotation(text="No neighborhood data available", xref="paper", yref="paper", x=0.5, y=0.5)
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        else:
            # Try ward aggregation
            if 'ward' in df_complaints.columns:
                ward_stats = aggregate_by_ward(df_complaints)
                if not ward_stats.empty:
                    fig = go.Figure(data=[
                        go.Bar(
                            x=ward_stats['ward'],
                            y=ward_stats['complaint_count'],
                            marker_color=COLORS['chart_blue'],
                            hovertemplate='<b>Ward %{x}</b><br>Complaints: %{y}<extra></extra>'
                        )
                    ])
                    fig.update_layout(
                        title="Complaints by Ward",
                        xaxis_title="Ward",
                        yaxis_title="Number of Complaints",
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                else:
                    fig = go.Figure()
                    fig.add_annotation(text="No ward data available", xref="paper", yref="paper", x=0.5, y=0.5)
                    fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
            else:
                fig = go.Figure()
                fig.add_annotation(text="No geographic data available", xref="paper", yref="paper", x=0.5, y=0.5)
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
    except Exception as e:
        logger.warning(f"Error creating neighborhood analysis: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Error loading data", xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
    
    return fig

@app.callback(
    Output("crime-map", "figure"),
    [Input('crime-map-date-picker', 'start_date'),
     Input('crime-map-date-picker', 'end_date'),
     Input('crime-type-filter', 'value')]
)
def update_crime_map(start_date, end_date, crime_type):
    """Update crime map based on date and crime type filters"""
    crime_path = PROJECT_ROOT / "data" / "cleaned" / "crime_data.csv"
    if not crime_path.exists():
        fig = go.Figure()
        fig.add_annotation(
            text="No crime data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    try:
        df_crimes = pd.read_csv(str(crime_path), low_memory=False)
        if 'latitude' in df_crimes.columns and 'longitude' in df_crimes.columns:
            # Filter valid coordinates within Chicago city limits (excluding Lake Michigan)
            df_map = df_crimes[
                (df_crimes['latitude'].notna()) & 
                (df_crimes['longitude'].notna()) &
                (df_crimes['latitude'] != 0) &
                (df_crimes['longitude'] != 0) &
                (df_crimes['latitude'] >= 41.64) &
                (df_crimes['latitude'] <= 42.02) &
                (df_crimes['longitude'] >= -87.94) &
                (df_crimes['longitude'] <= -87.60)  # Lakefront Trail boundary
            ].copy()
            
            # Apply date filter if dates are available
            if 'date' in df_map.columns and start_date and end_date:
                df_map['date'] = pd.to_datetime(df_map['date'], errors='coerce')
                date_mask = (df_map['date'] >= start_date) & (df_map['date'] <= end_date)
                df_map = df_map[date_mask]
            
            # Apply crime type filter
            if crime_type and crime_type != 'All' and 'primary_type' in df_map.columns:
                df_map = df_map[df_map['primary_type'] == crime_type]
            
            # Limit for performance
            df_map = df_map.head(2000)
            
            if len(df_map) > 0:
                # Get symbol mapping
                symbol_map = get_crime_symbol_mapping()
                
                # Create figure
                fig = go.Figure()
                
                # Group by crime type and create separate traces
                if 'primary_type' in df_map.columns:
                    crime_types = df_map['primary_type'].dropna().unique()
                    
                    for crim_type in crime_types:
                        df_type = df_map[df_map['primary_type'] == crim_type]
                        
                        if len(df_type) == 0:
                            continue
                        
                        # Get symbol and color for this type
                        symbol, color = get_crime_symbol(crim_type, symbol_map)
                        
                        # Filter to only rows with valid coordinates
                        df_type_valid = df_type[df_type['latitude'].notna() & df_type['longitude'].notna()].copy()
                        if len(df_type_valid) == 0:
                            continue
                        
                        # Prepare hover data
                        hover_data = []
                        for idx, row in df_type_valid.iterrows():
                            arrest = str(row.get('arrest', 'False')).lower() == 'true'
                            arrest_emoji = '✅' if arrest else '❌'
                            arrest_text = 'Yes' if arrest else 'No'
                            
                            # Build hover text
                            hover_parts = [
                                f"<b>Crime Details</b>",
                                f"<br><b>Type:</b> {str(row.get('primary_type', 'N/A'))}",
                                f"<br><b>Case #:</b> {str(row.get('case_number', 'N/A'))}",
                                f"<br><b>Arrest:</b> {arrest_emoji} {arrest_text}"
                            ]
                            
                            if pd.notna(row.get('description')):
                                desc = str(row.get('description', ''))[:100]
                                if len(str(row.get('description', ''))) > 100:
                                    desc += "..."
                                hover_parts.append(f"<br><b>Description:</b> {desc}")
                            
                            if pd.notna(row.get('block')):
                                hover_parts.append(f"<br><b>Location:</b> {str(row.get('block', 'N/A'))}")
                            
                            if pd.notna(row.get('location_description')):
                                hover_parts.append(f"<br><b>Location Type:</b> {str(row.get('location_description', 'N/A'))}")
                            
                            if pd.notna(row.get('ward')) or pd.notna(row.get('community_area')):
                                ward = str(row.get('ward', 'N/A'))
                                area = str(row.get('community_area', 'N/A'))
                                hover_parts.append(f"<br><b>Ward:</b> {ward} | <b>Area:</b> {area}")
                            
                            if pd.notna(row.get('date')):
                                try:
                                    crime_date = pd.to_datetime(row.get('date'), errors='coerce')
                                    if pd.notna(crime_date):
                                        hover_parts.append(f"<br><b>Date:</b> {crime_date.strftime('%Y-%m-%d %H:%M')}")
                                except:
                                    pass
                            
                            hover_data.append("<br>".join(hover_parts))
                        
                        # Map symbols to valid Scattermapbox symbols
                        symbol_map_valid = {
                            'triangle-up': 'triangle',
                            'triangle': 'triangle',
                            'circle': 'circle',
                            'square': 'square',
                            'diamond': 'diamond',
                            'star': 'star',
                            'x': 'x',
                            'cross': 'cross'
                        }
                        valid_symbol = symbol_map_valid.get(symbol, 'circle')
                        
                        # Add trace for this crime type
                        try:
                            fig.add_trace(go.Scattermapbox(
                                lat=df_type_valid['latitude'].tolist(),
                                lon=df_type_valid['longitude'].tolist(),
                                mode='markers',
                                marker=dict(
                                    size=10,
                                    symbol=valid_symbol,
                                    color=color,
                                    opacity=0.7
                                ),
                                name=str(crim_type)[:30] + ('...' if len(str(crim_type)) > 30 else ''),
                                text=hover_data,
                                hovertemplate='%{text}<extra></extra>',
                                showlegend=True
                            ))
                        except Exception as trace_error:
                            logger.warning(f"Error adding trace for {crim_type}: {trace_error}")
                            # Fallback: add without custom hover
                            try:
                                fig.add_trace(go.Scattermapbox(
                                    lat=df_type_valid['latitude'].tolist(),
                                    lon=df_type_valid['longitude'].tolist(),
                                    mode='markers',
                                    marker=dict(
                                        size=10,
                                        color=color,
                                        opacity=0.7
                                    ),
                                    name=str(crim_type)[:30] + ('...' if len(str(crim_type)) > 30 else ''),
                                    hovertemplate=f'<b>{crim_type}</b><br>Lat: %{{lat:.4f}}<br>Lon: %{{lon:.4f}}<extra></extra>',
                                    showlegend=True
                                ))
                            except Exception as e2:
                                logger.error(f"Failed to add trace even with fallback: {e2}")
                                continue
                else:
                    # Fallback if no primary_type column
                    fig.add_trace(go.Scattermapbox(
                        lat=df_map['latitude'],
                        lon=df_map['longitude'],
                        mode='markers',
                        marker=dict(
                            size=8,
                            symbol='circle',
                            color=COLORS['chart_blue'],
                            opacity=0.7
                        ),
                        name='Crimes',
                        hovertemplate='<b>Crime Location</b><br>Lat: %{lat:.4f}<br>Lon: %{lon:.4f}<extra></extra>'
                    ))
                
                # Update layout
                fig.update_layout(
                    title=dict(
                        text="Crime Locations",
                        font=dict(size=16, color=COLORS['dark'], family="Arial, sans-serif"),
                        x=0.5,
                        xanchor='center'
                    ),
                    autosize=False,
                    margin=dict(l=0, r=0, t=60, b=0),
                    height=400,
                    mapbox=dict(
                        center=dict(lat=41.8781, lon=-87.6298),
                        zoom=10,
                        style="open-street-map",
                        bearing=0,
                        pitch=0
                    ),
                    hovermode='closest',
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=11,
                        font_family="Arial, sans-serif",
                        bordercolor=COLORS['primary'],
                        align="left"
                    ),
                    legend=dict(
                        title=dict(text="Crime Types", font=dict(size=10)),
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=0.99,
                        font=dict(size=8),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor=COLORS['light'],
                        borderwidth=1,
                        itemsizing="constant"
                    )
                )
            else:
                fig = go.Figure()
                fig.add_annotation(
                    text="No geospatial data available for selected filters",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    font=dict(size=14, color=COLORS['dark'])
                )
                fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="No geospatial data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14, color=COLORS['dark'])
            )
            fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
    except Exception as e:
        logger.warning(f"Error creating crime map: {e}")
        import traceback
        logger.error(traceback.format_exc())
        fig = go.Figure()
        fig.add_annotation(
            text="Error loading map data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
    
    return fig

@app.callback(
    [Output('sentiment-ridership-chart', 'figure'),
     Output('time-series-chart', 'figure'),
     Output('sentiment-distribution-chart', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('traffic-crime-chart', 'figure'),
     Output('total-traffic-volume', 'children'),
     Output('total-rides', 'children'),
     Output('total-complaints', 'children'),
     Output('total-crimes', 'children')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('complaint-type-filter', 'value')]
)
def update_dashboard(start_date, end_date, complaint_type):
    """Update dashboard based on filters"""
    
    df = load_data()
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        empty_fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400)
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A", "N/A"
    
    # Filter by date
    if start_date and end_date:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # Filter by complaint type (if applicable)
    # This would require additional data processing
    
    # 1. Enhanced Ridership vs Complaints Chart
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'total_cta_rides' in df_filtered.columns:
        fig1.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_cta_rides'],
                name='CTA Ridership',
                line=dict(color=COLORS['chart_green'], width=3),
                mode='lines+markers',
                marker=dict(size=6, color=COLORS['chart_green']),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Rides: %{y:,.0f}<extra></extra>'
            ),
            secondary_y=False
        )
    
    if 'total_311_complaints' in df_filtered.columns:
            fig1.add_trace(
                go.Scatter(
                    x=df_filtered['date'],
                y=df_filtered['total_311_complaints'],
                name='311 Complaints',
                line=dict(color=COLORS['chart_orange'], width=3),
                mode='lines+markers',
                marker=dict(size=6, color=COLORS['chart_orange']),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Complaints: %{y:,.0f}<extra></extra>'
                ),
                secondary_y=True
            )
    
    fig1.update_xaxes(
        title_text="Date",
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['light'],
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig1.update_yaxes(
        title_text="CTA Ridership",
        secondary_y=False,
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['light'],
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig1.update_yaxes(
        title_text="311 Complaints",
        secondary_y=True,
        showgrid=False,
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig1.update_layout(
        title=dict(
            text="CTA Ridership vs. Daily Complaints",
            font=dict(size=18, color=COLORS['dark'], family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        hovermode='x unified',
        height=450,
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Arial, sans-serif",
            bordercolor=COLORS['primary']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLORS['dark'])
        )
    )
    
    # 2. Enhanced Time Series Chart
    fig2 = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=("CTA Ridership", "311 Complaints", "Traffic Volume", "Crime Count")
    )
    
    if 'total_cta_rides' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_cta_rides'],
                name='Ridership',
                mode='lines',
                line=dict(color=COLORS['chart_green'], width=2.5),
                fill='tozeroy',
                fillcolor=f"rgba(76, 175, 80, 0.1)",
                hovertemplate='<b>Ridership</b><br>Date: %{x}<br>Rides: %{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    if 'total_311_complaints' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_311_complaints'],
                name='Complaints',
                mode='lines',
                line=dict(color=COLORS['chart_orange'], width=2.5),
                fill='tozeroy',
                fillcolor=f"rgba(255, 152, 0, 0.1)",
                hovertemplate='<b>Complaints</b><br>Date: %{x}<br>Count: %{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    if 'total_traffic_volume' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_traffic_volume'],
                name='Traffic Volume',
                mode='lines',
                line=dict(color=COLORS['chart_blue'], width=2.5),
                fill='tozeroy',
                fillcolor=f"rgba(33, 150, 243, 0.1)",
                hovertemplate='<b>Traffic Volume</b><br>Date: %{x}<br>Volume: %{y:,.0f}<extra></extra>'
            ),
            row=3, col=1
        )
    
    if 'total_crimes' in df_filtered.columns:
        fig2.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_crimes'],
                name='Crimes',
                mode='lines',
                line=dict(color=COLORS['chart_red'], width=2.5),
                fill='tozeroy',
                fillcolor=f"rgba(244, 67, 54, 0.1)",
                hovertemplate='<b>Crimes</b><br>Date: %{x}<br>Count: %{y:,.0f}<extra></extra>'
            ),
            row=4, col=1
        )
    
    fig2.update_xaxes(
        title_text="Date",
        row=4, col=1,
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['light'],
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig2.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['light'],
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig2.update_layout(
        height=800,
        showlegend=False,
        title=dict(
            text="Time Series Overview",
            font=dict(size=18, color=COLORS['dark'], family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=40, t=80, b=60),
        font=dict(family="Arial, sans-serif")
    )
    # Update subplot titles
    for i, title in enumerate(["CTA Ridership", "311 Complaints", "Traffic Volume", "Crime Count"], 1):
        if i <= len(fig2.layout.annotations):
            fig2.layout.annotations[i-1].update(
                font=dict(size=13, color=COLORS['dark'], family="Arial, sans-serif")
            )
    
    # 3. Complaint Distribution Chart
    if 'total_311_complaints' in df_filtered.columns:
        fig3 = go.Figure(data=[go.Histogram(
            x=df_filtered['total_311_complaints'],
            nbinsx=30,
            marker=dict(
                color=COLORS['chart_orange'],
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>Complaint Distribution</b><br>Range: %{x}<br>Frequency: %{y}<extra></extra>'
        )])
        fig3.update_layout(
            title=dict(
                text="Daily Complaint Count Distribution",
                font=dict(size=16, color=COLORS['dark'], family="Arial, sans-serif"),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Complaint Count",
                title_font=dict(size=12, color=COLORS['dark']),
                tickfont=dict(size=10, color=COLORS['dark']),
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['light']
            ),
            yaxis=dict(
                title="Frequency",
                title_font=dict(size=12, color=COLORS['dark']),
                tickfont=dict(size=10, color=COLORS['dark']),
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['light']
            ),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=40, t=60, b=50),
            hoverlabel=dict(
                bgcolor="white",
                font_size=11,
                font_family="Arial, sans-serif",
                bordercolor=COLORS['primary']
            )
        )
    else:
        fig3 = go.Figure()
        fig3.add_annotation(
            text="No complaint data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        fig3.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white')
    
    # 4. Enhanced Correlation Heatmap
    numeric_cols = df_filtered.select_dtypes(include=['number']).columns
    key_cols = ['total_cta_rides', 'total_311_complaints', 'total_traffic_volume', 
                'total_crimes', 'transit_related_complaints']
    corr_cols = [col for col in key_cols if col in numeric_cols]
    
    if len(corr_cols) >= 2:
        corr_matrix = df_filtered[corr_cols].corr()
        # Shorten column names for display
        display_cols = [col.replace('_', ' ').title()[:15] for col in corr_matrix.columns]
        fig4 = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=display_cols,
            y=display_cols,
            colorscale=[[0, '#E53935'], [0.5, 'white'], [1, '#1E88E5']],
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont=dict(size=10, color='black'),
            hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>',
            colorbar=dict(
                title=dict(text="Correlation", font=dict(size=11, color=COLORS['dark'])),
                tickfont=dict(size=10, color=COLORS['dark'])
            )
        ))
        fig4.update_layout(
            title=dict(
                text="Correlation Matrix",
                font=dict(size=16, color=COLORS['dark'], family="Arial, sans-serif"),
                x=0.5,
                xanchor='center'
            ),
            height=350,
            xaxis=dict(
                tickfont=dict(size=9, color=COLORS['dark']),
                title_font=dict(size=11, color=COLORS['dark'])
            ),
            yaxis=dict(
                tickfont=dict(size=9, color=COLORS['dark']),
                title_font=dict(size=11, color=COLORS['dark'])
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=40, t=60, b=50),
            hoverlabel=dict(
                bgcolor="white",
                font_size=11,
                font_family="Arial, sans-serif",
                bordercolor=COLORS['primary']
            )
        )
    else:
        fig4 = go.Figure()
        fig4.add_annotation(
            text="Insufficient data for correlation",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        fig4.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white')
    
    # 5. Traffic vs Crime Comparison Chart
    fig5 = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'total_traffic_volume' in df_filtered.columns:
        fig5.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_traffic_volume'],
                name='Traffic Volume',
                line=dict(color=COLORS['chart_blue'], width=3),
                mode='lines+markers',
                marker=dict(size=6, color=COLORS['chart_blue']),
                hovertemplate='<b>Traffic Volume</b><br>Date: %{x}<br>Volume: %{y:,.0f}<extra></extra>'
            ),
            secondary_y=False
        )
    
    if 'total_crimes' in df_filtered.columns:
        fig5.add_trace(
            go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['total_crimes'],
                name='Crime Count',
                line=dict(color=COLORS['chart_red'], width=3),
                mode='lines+markers',
                marker=dict(size=6, color=COLORS['chart_red']),
                hovertemplate='<b>Crime Count</b><br>Date: %{x}<br>Crimes: %{y:,.0f}<extra></extra>'
            ),
            secondary_y=True
        )
    
    fig5.update_xaxes(
        title_text="Date",
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['light'],
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig5.update_yaxes(
        title_text="Traffic Volume",
        secondary_y=False,
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['light'],
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    fig5.update_yaxes(
        title_text="Crime Count",
        secondary_y=True,
        showgrid=False,
        title_font=dict(size=12, color=COLORS['dark']),
        tickfont=dict(size=10, color=COLORS['dark'])
    )
    
    fig5.update_layout(
        title=dict(
            text="Traffic Volume vs. Crime Count",
            font=dict(size=18, color=COLORS['dark'], family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        hovermode='x unified',
        height=400,
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Arial, sans-serif",
            bordercolor=COLORS['primary']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLORS['dark'])
        )
    )
    
    # Note: Complaint map is now handled by a separate callback (update_complaint_map)
    
    # Calculate metrics
    total_traffic_volume = f"{df_filtered['total_traffic_volume'].sum():,.0f}" if 'total_traffic_volume' in df_filtered.columns else "N/A"
    total_rides = f"{df_filtered['total_cta_rides'].sum():,.0f}" if 'total_cta_rides' in df_filtered.columns else "N/A"
    total_complaints = f"{df_filtered['total_311_complaints'].sum():,.0f}" if 'total_311_complaints' in df_filtered.columns else "N/A"
    total_crimes = f"{df_filtered['total_crimes'].sum():,.0f}" if 'total_crimes' in df_filtered.columns else "N/A"
    
    return fig1, fig2, fig3, fig4, fig5, total_traffic_volume, total_rides, total_complaints, total_crimes

@app.callback(
    Output("complaint-map", "figure"),
    [Input('complaint-map-date-picker', 'start_date'),
     Input('complaint-map-date-picker', 'end_date'),
     Input('complaint-type-filter', 'value')]
)
def update_complaint_map(start_date, end_date, complaint_type):
    """Update complaint map based on date and complaint type filters"""
    complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    if not complaints_path.exists():
        fig = go.Figure()
        fig.add_annotation(
            text="No complaint data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    try:
        df_complaints = pd.read_csv(str(complaints_path), low_memory=False)
        if 'latitude' in df_complaints.columns and 'longitude' in df_complaints.columns:
            # Filter valid coordinates within Chicago city limits (excluding Lake Michigan)
            df_map = df_complaints[
                (df_complaints['latitude'].notna()) & 
                (df_complaints['longitude'].notna()) &
                (df_complaints['latitude'] != 0) &
                (df_complaints['longitude'] != 0) &
                (df_complaints['latitude'] >= 41.64) &
                (df_complaints['latitude'] <= 42.02) &
                (df_complaints['longitude'] >= -87.94) &
                (df_complaints['longitude'] <= -87.60)  # Lakefront Trail boundary (includes downtown Chicago)
            ].copy()
            
            # Apply date filter if dates are available
            if 'created_date' in df_map.columns and start_date and end_date:
                df_map['created_date'] = pd.to_datetime(df_map['created_date'], errors='coerce')
                date_mask = (df_map['created_date'] >= start_date) & (df_map['created_date'] <= end_date)
                df_map = df_map[date_mask]
            
            # Apply complaint type filter - check for sr_type or service_request_type
            type_col = 'sr_type' if 'sr_type' in df_map.columns else ('service_request_type' if 'service_request_type' in df_map.columns else None)
            if complaint_type and complaint_type != 'All' and type_col:
                df_map = df_map[df_map[type_col] == complaint_type]
            
            # Limit for performance
            df_map = df_map.head(2000)
                
            if len(df_map) > 0:
                # Get symbol mapping
                symbol_map = get_complaint_symbol_mapping()
                
                # Create figure
                fig = go.Figure()
                
                # Group by complaint type and create separate traces
                if type_col:
                    complaint_types = df_map[type_col].dropna().unique()
                    
                    for comp_type in complaint_types:
                        df_type = df_map[df_map[type_col] == comp_type]
                        
                        if len(df_type) == 0:
                            continue
                        
                        # Get symbol and color for this type
                        symbol, color = get_complaint_symbol(comp_type, symbol_map)
                        
                        # Filter to only rows with valid coordinates first
                        df_type_valid = df_type[df_type['latitude'].notna() & df_type['longitude'].notna()].copy()
                        if len(df_type_valid) == 0:
                            continue
                        
                        # Prepare hover data - aligned with valid coordinates
                        hover_data = []
                        for idx, row in df_type_valid.iterrows():
                            status = str(row.get('status', 'N/A'))
                            status_emoji = '🔴' if 'open' in status.lower() else '🟢' if 'closed' in status.lower() else '🔵' if 'completed' in status.lower() else '🟡'
                            
                            # Build hover text safely - use correct column names
                            type_val = row.get('sr_type', row.get('service_request_type', 'N/A'))
                            req_num = row.get('sr_number', row.get('service_request_number', 'N/A'))
                            hover_parts = [
                                f"<b>Complaint Details</b>",
                                f"<br><b>Type:</b> {str(type_val)}",
                                f"<br><b>Status:</b> {status_emoji} {status}",
                                f"<br><b>Request #:</b> {str(req_num)}"
                            ]
                            
                            if pd.notna(row.get('description')):
                                desc = str(row.get('description', ''))[:100]
                                if len(str(row.get('description', ''))) > 100:
                                    desc += "..."
                                hover_parts.append(f"<br><b>Description:</b> {desc}")
                            
                            if pd.notna(row.get('street_address')):
                                hover_parts.append(f"<br><b>Address:</b> {str(row.get('street_address', 'N/A'))}")
                            
                            if pd.notna(row.get('ward')) or pd.notna(row.get('community_area')):
                                ward = str(row.get('ward', 'N/A'))
                                area = str(row.get('community_area', 'N/A'))
                                hover_parts.append(f"<br><b>Ward:</b> {ward} | <b>Area:</b> {area}")
                            
                            if pd.notna(row.get('created_date')):
                                try:
                                    created = pd.to_datetime(row.get('created_date'), errors='coerce')
                                    if pd.notna(created):
                                        hover_parts.append(f"<br><b>Created:</b> {created.strftime('%Y-%m-%d %H:%M')}")
                                except:
                                    pass
                            
                            if pd.notna(row.get('updated_date')):
                                try:
                                    updated = pd.to_datetime(row.get('updated_date'), errors='coerce')
                                    if pd.notna(updated):
                                        hover_parts.append(f"<br><b>Updated:</b> {updated.strftime('%Y-%m-%d %H:%M')}")
                                except:
                                    pass
                            
                            if pd.notna(row.get('closed_date')):
                                try:
                                    closed = pd.to_datetime(row.get('closed_date'), errors='coerce')
                                    if pd.notna(closed):
                                        hover_parts.append(f"<br><b>Closed:</b> {closed.strftime('%Y-%m-%d %H:%M')}")
                                except:
                                    pass
                            
                            hover_data.append("<br>".join(hover_parts))
                        
                        # Map symbols to valid Scattermapbox symbols
                        symbol_map_valid = {
                            'triangle-up': 'triangle',
                            'triangle': 'triangle',
                            'circle': 'circle',
                            'square': 'square',
                            'diamond': 'diamond',
                            'star': 'star',
                            'x': 'x',
                            'cross': 'cross'
                        }
                        valid_symbol = symbol_map_valid.get(symbol, 'circle')
                        
                        # Add trace for this complaint type
                        try:
                            fig.add_trace(go.Scattermapbox(
                                lat=df_type_valid['latitude'].tolist(),
                                lon=df_type_valid['longitude'].tolist(),
                                mode='markers',
                                marker=dict(
                                    size=10,
                                    symbol=valid_symbol,
                                    color=color,
                                    opacity=0.7
                                ),
                                name=str(comp_type)[:30] + ('...' if len(str(comp_type)) > 30 else ''),
                                text=hover_data,
                                hovertemplate='%{text}<extra></extra>',
                                showlegend=True
                            ))
                        except Exception as trace_error:
                            logger.warning(f"Error adding trace for {comp_type}: {trace_error}")
                            # Fallback: add without custom hover
                            try:
                                fig.add_trace(go.Scattermapbox(
                                    lat=df_type_valid['latitude'].tolist(),
                                    lon=df_type_valid['longitude'].tolist(),
                                    mode='markers',
                                    marker=dict(
                                        size=10,
                                        color=color,
                                        opacity=0.7
                                    ),
                                    name=str(comp_type)[:30] + ('...' if len(str(comp_type)) > 30 else ''),
                                    hovertemplate=f'<b>{comp_type}</b><br>Lat: %{{lat:.4f}}<br>Lon: %{{lon:.4f}}<extra></extra>',
                                    showlegend=True
                                ))
                            except Exception as e2:
                                logger.error(f"Failed to add trace even with fallback: {e2}")
                                continue
                else:
                    # Fallback if no service_request_type column
                    fig.add_trace(go.Scattermapbox(
                        lat=df_map['latitude'],
                        lon=df_map['longitude'],
                        mode='markers',
                        marker=dict(
                            size=8,
                            symbol='circle',
                            color=COLORS['chart_blue'],
                            opacity=0.7
                        ),
                        name='Complaints',
                        hovertemplate='<b>Complaint Location</b><br>Lat: %{lat:.4f}<br>Lon: %{lon:.4f}<extra></extra>'
                    ))
                
                # Update layout
                fig.update_layout(
                    title=dict(
                        text="311 Complaint Locations",
                        font=dict(size=16, color=COLORS['dark'], family="Arial, sans-serif"),
                        x=0.5,
                        xanchor='center'
                    ),
                    autosize=False,
                    margin=dict(l=0, r=0, t=60, b=0),
                        height=400,
                    mapbox=dict(
                        center=dict(lat=41.8781, lon=-87.6298),
                        zoom=10,
                        style="open-street-map",
                        bearing=0,
                        pitch=0
                    ),
                    hovermode='closest',
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=11,
                        font_family="Arial, sans-serif",
                        bordercolor=COLORS['primary'],
                        align="left"
                    ),
                    legend=dict(
                        title=dict(text="Complaint Types", font=dict(size=10)),
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=0.99,
                        font=dict(size=8),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor=COLORS['light'],
                        borderwidth=1,
                        itemsizing="constant"
                    )
                )
            else:
                fig = go.Figure()
                fig.add_annotation(
                    text="No geospatial data available for selected filters",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    font=dict(size=14, color=COLORS['dark'])
                )
                fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
                return fig
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="No geospatial data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14, color=COLORS['dark'])
            )
            fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
            return fig
    except Exception as e:
        logger.warning(f"Error creating complaint map: {e}")
        import traceback
        logger.error(traceback.format_exc())
        fig = go.Figure()
        fig.add_annotation(
            text="Error loading map data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14, color=COLORS['dark'])
        )
        fig.update_layout(height=400, autosize=False, plot_bgcolor='white', paper_bgcolor='white')
    
    return fig


def run_dashboard(host='127.0.0.1', port=8050, debug=True):
    """Run the dashboard server"""
    df = load_data()
    app.layout = create_dashboard_layout(df)
    
    logger.info(f"Starting dashboard server on http://{host}:{port}")
    logger.info(f"Access the dashboard at http://localhost:{port} or http://127.0.0.1:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_dashboard()

