"""
Temporal Pattern Analysis Module
Analyzes day-of-week, time-of-day, and seasonal patterns in urban data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def analyze_day_of_week_patterns(df: pd.DataFrame, date_col: str = 'date', 
                                 metric_cols: list = None) -> pd.DataFrame:
    """
    Analyze patterns by day of week
    
    Args:
        df: DataFrame with date and metric columns
        date_col: Name of date column
        metric_cols: List of metric columns to analyze (default: auto-detect)
    
    Returns:
        DataFrame with day-of-week aggregations
    """
    if df.empty or date_col not in df.columns:
        logger.warning("Empty dataframe or missing date column")
        return pd.DataFrame()
    
    df_work = df.copy()
    df_work[date_col] = pd.to_datetime(df_work[date_col], errors='coerce')
    
    # Extract day of week (0=Monday, 6=Sunday)
    df_work['day_of_week'] = df_work[date_col].dt.dayofweek
    df_work['day_name'] = df_work[date_col].dt.day_name()
    
    # Auto-detect metric columns if not provided
    if metric_cols is None:
        metric_cols = [col for col in df_work.columns 
                      if col not in [date_col, 'day_of_week', 'day_name'] 
                      and df_work[col].dtype in [np.int64, np.float64]]
    
    if not metric_cols:
        logger.warning("No numeric metric columns found")
        return pd.DataFrame()
    
    # Aggregate by day of week
    agg_dict = {col: 'mean' for col in metric_cols}
    agg_dict['day_name'] = 'first'  # Keep day name
    
    day_patterns = df_work.groupby('day_of_week').agg(agg_dict).reset_index()
    day_patterns = day_patterns.sort_values('day_of_week')
    
    # Add day names in order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_patterns['day_name'] = [day_order[int(dow)] for dow in day_patterns['day_of_week']]
    
    return day_patterns


def analyze_time_patterns(df: pd.DataFrame, date_col: str = 'date',
                          metric_cols: list = None) -> pd.DataFrame:
    """
    Analyze patterns by time of day (if hour data available) or weekday vs weekend
    
    Args:
        df: DataFrame with date and metric columns
        date_col: Name of date column
        metric_cols: List of metric columns to analyze
    
    Returns:
        DataFrame with time period aggregations
    """
    if df.empty or date_col not in df.columns:
        logger.warning("Empty dataframe or missing date column")
        return pd.DataFrame()
    
    df_work = df.copy()
    df_work[date_col] = pd.to_datetime(df_work[date_col], errors='coerce')
    
    # Check if hour data is available
    if 'hour' in df_work.columns or any('hour' in str(col).lower() for col in df_work.columns):
        # Analyze by hour
        hour_col = [col for col in df_work.columns if 'hour' in str(col).lower()][0]
        df_work['time_period'] = df_work[hour_col]
        period_type = 'hour'
    else:
        # Analyze by weekday vs weekend
        df_work['is_weekend'] = df_work[date_col].dt.dayofweek >= 5
        df_work['time_period'] = df_work['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
        period_type = 'weekday_weekend'
    
    # Auto-detect metric columns if not provided
    if metric_cols is None:
        metric_cols = [col for col in df_work.columns 
                      if col not in [date_col, 'time_period', 'is_weekend', 'hour'] 
                      and df_work[col].dtype in [np.int64, np.float64]]
    
    if not metric_cols:
        logger.warning("No numeric metric columns found")
        return pd.DataFrame()
    
    # Aggregate by time period
    agg_dict = {col: 'mean' for col in metric_cols}
    time_patterns = df_work.groupby('time_period').agg(agg_dict).reset_index()
    
    return time_patterns


def get_peak_days(df: pd.DataFrame, metric_col: str, 
                  day_col: str = 'day_name') -> dict:
    """
    Identify peak and low days for a metric
    
    Args:
        df: DataFrame with day patterns
        metric_col: Name of metric column
        day_col: Name of day name column
    
    Returns:
        Dictionary with peak_day, peak_value, low_day, low_value, avg_value
    """
    if df.empty or metric_col not in df.columns:
        return {}
    
    if day_col not in df.columns:
        day_col = df.columns[0]  # Fallback to first column
    
    peak_idx = df[metric_col].idxmax()
    low_idx = df[metric_col].idxmin()
    
    avg_value = df[metric_col].mean()
    
    return {
        'peak_day': df.loc[peak_idx, day_col],
        'peak_value': df.loc[peak_idx, metric_col],
        'low_day': df.loc[low_idx, day_col],
        'low_value': df.loc[low_idx, metric_col],
        'avg_value': avg_value,
        'peak_pct_above_avg': ((df.loc[peak_idx, metric_col] / avg_value - 1) * 100) if avg_value > 0 else 0,
        'low_pct_below_avg': ((1 - df.loc[low_idx, metric_col] / avg_value) * 100) if avg_value > 0 else 0
    }


def format_temporal_insight(day: str, value: float, metric_name: str, 
                           avg_value: float, is_peak: bool = True) -> str:
    """
    Create plain-language insight about temporal patterns
    
    Args:
        day: Day name or time period
        value: Value for that day/period
        metric_name: Name of the metric
        avg_value: Average value across all periods
        is_peak: Whether this is a peak (True) or low (False)
    
    Returns:
        Plain-language insight string
    """
    if avg_value == 0:
        return f"{day} has {value:,.0f} {metric_name}"
    
    pct_diff = ((value / avg_value - 1) * 100) if is_peak else ((1 - value / avg_value) * 100)
    
    if is_peak:
        return f"{day} has {pct_diff:.0f}% more {metric_name} than average ({value:,.0f} vs {avg_value:,.0f})"
    else:
        return f"{day} has {pct_diff:.0f}% fewer {metric_name} than average ({value:,.0f} vs {avg_value:,.0f})"


def get_seasonal_patterns(df: pd.DataFrame, date_col: str = 'date',
                          metric_cols: list = None) -> pd.DataFrame:
    """
    Analyze seasonal patterns by month
    
    Args:
        df: DataFrame with date and metric columns
        date_col: Name of date column
        metric_cols: List of metric columns to analyze
    
    Returns:
        DataFrame with monthly aggregations
    """
    if df.empty or date_col not in df.columns:
        logger.warning("Empty dataframe or missing date column")
        return pd.DataFrame()
    
    df_work = df.copy()
    df_work[date_col] = pd.to_datetime(df_work[date_col], errors='coerce')
    df_work['month'] = df_work[date_col].dt.month
    df_work['month_name'] = df_work[date_col].dt.strftime('%B')
    
    # Auto-detect metric columns if not provided
    if metric_cols is None:
        metric_cols = [col for col in df_work.columns 
                      if col not in [date_col, 'month', 'month_name'] 
                      and df_work[col].dtype in [np.int64, np.float64]]
    
    if not metric_cols:
        logger.warning("No numeric metric columns found")
        return pd.DataFrame()
    
    # Aggregate by month
    agg_dict = {col: 'mean' for col in metric_cols}
    agg_dict['month_name'] = 'first'
    
    seasonal_patterns = df_work.groupby('month').agg(agg_dict).reset_index()
    seasonal_patterns = seasonal_patterns.sort_values('month')
    
    return seasonal_patterns

