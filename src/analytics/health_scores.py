"""
Urban Health Score Calculation Module
Calculates composite health indices for urban mobility and service quality
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def normalize_metric(value: float, min_val: float, max_val: float, 
                     higher_is_better: bool = True) -> float:
    """
    Normalize a metric to 0-10 scale
    
    Args:
        value: Current value
        min_val: Minimum value in range
        max_val: Maximum value in range
        higher_is_better: True if higher values are better (e.g., ridership)
                         False if lower values are better (e.g., complaints, crime)
    
    Returns:
        Normalized score (0-10)
    """
    if max_val == min_val:
        return 5.0  # Neutral score if no variation
    
    if higher_is_better:
        # Higher is better: normalize 0-10 where max = 10, min = 0
        normalized = ((value - min_val) / (max_val - min_val)) * 10
    else:
        # Lower is better: invert so lower values get higher scores
        normalized = ((max_val - value) / (max_val - min_val)) * 10
    
    # Clamp to 0-10
    return max(0, min(10, normalized))


def calculate_urban_health_index(df: pd.DataFrame, 
                                 ridership_col: str = 'total_cta_rides',
                                 complaints_col: str = 'total_311_complaints',
                                 crime_col: str = 'total_crimes') -> dict:
    """
    Calculate overall urban health index combining multiple metrics
    
    Args:
        df: DataFrame with daily metrics
        ridership_col: Column name for ridership data
        complaints_col: Column name for complaints data
        crime_col: Column name for crime data
    
    Returns:
        Dictionary with health scores and breakdown
    """
    if df.empty:
        return {}
    
    # Get current period averages (or use all data if single period)
    if len(df) == 1:
        current_ridership = df[ridership_col].iloc[0] if ridership_col in df.columns else 0
        current_complaints = df[complaints_col].iloc[0] if complaints_col in df.columns else 0
        current_crime = df[crime_col].iloc[0] if crime_col in df.columns else 0
    else:
        current_ridership = df[ridership_col].mean() if ridership_col in df.columns else 0
        current_complaints = df[complaints_col].mean() if complaints_col in df.columns else 0
        current_crime = df[crime_col].mean() if crime_col in df.columns else 0
    
    # Calculate ranges for normalization (use historical data if available)
    ridership_min = df[ridership_col].min() if ridership_col in df.columns else 0
    ridership_max = df[ridership_col].max() if ridership_col in df.columns else 1
    
    complaints_min = df[complaints_col].min() if complaints_col in df.columns else 0
    complaints_max = df[complaints_col].max() if complaints_col in df.columns else 1
    
    crime_min = df[crime_col].min() if crime_col in df.columns else 0
    crime_max = df[crime_col].max() if crime_col in df.columns else 1
    
    # Normalize each metric to 0-10 scale
    # Higher ridership = better, Lower complaints/crime = better
    ridership_score = normalize_metric(current_ridership, ridership_min, ridership_max, 
                                      higher_is_better=True)
    complaints_score = normalize_metric(current_complaints, complaints_min, complaints_max, 
                                       higher_is_better=False)
    crime_score = normalize_metric(current_crime, crime_min, crime_max, 
                                  higher_is_better=False)
    
    # Weighted combination
    # Weights: Ridership (40%), Complaints (30%), Crime (30%)
    overall_score = (ridership_score * 0.4 + 
                     complaints_score * 0.3 + 
                     crime_score * 0.3)
    
    # Get status
    status = get_health_status(overall_score)
    
    return {
        'overall_score': round(overall_score, 1),
        'mobility_score': round(ridership_score, 1),
        'service_quality_score': round(complaints_score, 1),
        'safety_score': round(crime_score, 1),
        'status': status['label'],
        'status_color': status['color'],
        'status_emoji': status['emoji'],
        'breakdown': {
            'ridership': {
                'value': current_ridership,
                'score': round(ridership_score, 1),
                'min': ridership_min,
                'max': ridership_max
            },
            'complaints': {
                'value': current_complaints,
                'score': round(complaints_score, 1),
                'min': complaints_min,
                'max': complaints_max
            },
            'crime': {
                'value': current_crime,
                'score': round(crime_score, 1),
                'min': crime_min,
                'max': crime_max
            }
        }
    }


def get_health_status(score: float) -> dict:
    """
    Get health status label and color based on score
    
    Args:
        score: Health score (0-10)
    
    Returns:
        Dictionary with label, color, and emoji
    """
    if score >= 8:
        return {
            'label': 'Excellent',
            'color': '#28a745',  # Green
            'emoji': '🟢'
        }
    elif score >= 6:
        return {
            'label': 'Good',
            'color': '#ffc107',  # Yellow
            'emoji': '🟡'
        }
    elif score >= 4:
        return {
            'label': 'Fair',
            'color': '#fd7e14',  # Orange
            'emoji': '🟠'
        }
    else:
        return {
            'label': 'Needs Attention',
            'color': '#dc3545',  # Red
            'emoji': '🔴'
        }


def calculate_route_efficiency_score(ridership: float, complaints: float) -> dict:
    """
    Calculate efficiency score: rides per complaint
    
    Args:
        ridership: Total ridership
        complaints: Total complaints
    
    Returns:
        Dictionary with efficiency metrics
    """
    if complaints == 0:
        rides_per_complaint = ridership if ridership > 0 else 0
    else:
        rides_per_complaint = ridership / complaints
    
    # Normalize to 0-10 scale (higher is better)
    # Assume good efficiency is > 1000 rides per complaint
    max_efficiency = 10000  # Very high efficiency
    min_efficiency = 100    # Low efficiency
    
    efficiency_score = normalize_metric(rides_per_complaint, min_efficiency, max_efficiency, 
                                       higher_is_better=True)
    
    return {
        'rides_per_complaint': round(rides_per_complaint, 0),
        'efficiency_score': round(efficiency_score, 1),
        'status': 'Excellent' if efficiency_score >= 8 else 
               'Good' if efficiency_score >= 6 else 
               'Fair' if efficiency_score >= 4 else 'Needs Improvement'
    }


def calculate_safety_index(ridership: float, crime: float) -> dict:
    """
    Calculate safety index: crimes per 1000 rides
    
    Args:
        ridership: Total ridership
        crime: Total crimes
    
    Returns:
        Dictionary with safety metrics
    """
    if ridership == 0:
        crimes_per_1000 = 0
    else:
        crimes_per_1000 = (crime / ridership) * 1000
    
    # Normalize to 0-10 scale (lower crimes per 1000 rides is better)
    # Assume good safety is < 1 crime per 1000 rides
    max_crimes_per_1000 = 10  # High crime rate
    min_crimes_per_1000 = 0.1  # Low crime rate
    
    safety_score = normalize_metric(crimes_per_1000, min_crimes_per_1000, max_crimes_per_1000, 
                                   higher_is_better=False)
    
    return {
        'crimes_per_1000_rides': round(crimes_per_1000, 2),
        'safety_score': round(safety_score, 1),
        'status': 'Excellent' if safety_score >= 8 else 
                 'Good' if safety_score >= 6 else 
                 'Fair' if safety_score >= 4 else 'Needs Attention'
    }


def calculate_trend_indicator(current_value: float, previous_value: float, 
                              higher_is_better: bool = True) -> dict:
    """
    Calculate trend indicator (improving, declining, stable)
    
    Args:
        current_value: Current period value
        previous_value: Previous period value
        higher_is_better: True if higher values indicate improvement
    
    Returns:
        Dictionary with trend direction and percentage change
    """
    if previous_value == 0:
        pct_change = 0
    else:
        pct_change = ((current_value - previous_value) / previous_value) * 100
    
    if higher_is_better:
        is_improving = pct_change > 0
    else:
        is_improving = pct_change < 0
    
    if abs(pct_change) < 1:
        trend = 'Stable'
        emoji = '➡️'
    elif is_improving:
        trend = 'Improving'
        emoji = '↑'
    else:
        trend = 'Declining'
        emoji = '↓'
    
    return {
        'trend': trend,
        'emoji': emoji,
        'pct_change': round(pct_change, 1),
        'is_improving': is_improving
    }

