"""
Neighborhood and Ward Analysis Module
Provides geographic aggregation, hotspot detection, and area comparisons
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed - hotspot detection will be limited")


def aggregate_by_neighborhood(df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude'):
    """
    Aggregate complaints by neighborhood/community area
    
    Args:
        df: DataFrame with complaint data
        lat_col: Name of latitude column
        lon_col: Name of longitude column
    
    Returns:
        DataFrame: Aggregated data by neighborhood
    """
    if 'community_area' not in df.columns:
        logger.warning("community_area column not found - cannot aggregate by neighborhood")
        return pd.DataFrame()
    
    # Group by community area - use sr_number or any available ID column
    count_col = 'sr_number' if 'sr_number' in df.columns else ('service_request_number' if 'service_request_number' in df.columns else df.columns[0])
    neighborhood_stats = df.groupby('community_area').agg({
        count_col: 'count',
        lat_col: 'mean',
        lon_col: 'mean'
    }).rename(columns={
        count_col: 'complaint_count',
        lat_col: 'avg_latitude',
        lon_col: 'avg_longitude'
    }).reset_index()
    
    # Add complaint type breakdown if available
    type_col = 'sr_type' if 'sr_type' in df.columns else ('service_request_type' if 'service_request_type' in df.columns else None)
    if type_col:
        type_counts = df.groupby(['community_area', type_col]).size().reset_index(name='count')
        type_pivot = type_counts.pivot(index='community_area', columns=type_col, values='count').fillna(0)
        neighborhood_stats = neighborhood_stats.merge(type_pivot, left_on='community_area', right_index=True, how='left')
    
    return neighborhood_stats


def aggregate_by_ward(df: pd.DataFrame):
    """
    Aggregate complaints by city ward
    
    Args:
        df: DataFrame with complaint data
    
    Returns:
        DataFrame: Aggregated data by ward
    """
    if 'ward' not in df.columns:
        logger.warning("ward column not found - cannot aggregate by ward")
        return pd.DataFrame()
    
    # Group by ward - use sr_number or any available ID column
    count_col = 'sr_number' if 'sr_number' in df.columns else ('service_request_number' if 'service_request_number' in df.columns else df.columns[0])
    ward_stats = df.groupby('ward').agg({
        count_col: 'count'
    }).rename(columns={
        count_col: 'complaint_count'
    }).reset_index()
    
    # Add complaint type breakdown if available
    type_col = 'sr_type' if 'sr_type' in df.columns else ('service_request_type' if 'service_request_type' in df.columns else None)
    if type_col:
        type_counts = df.groupby(['ward', type_col]).size().reset_index(name='count')
        type_pivot = type_counts.pivot(index='ward', columns=type_col, values='count').fillna(0)
        ward_stats = ward_stats.merge(type_pivot, left_on='ward', right_index=True, how='left')
    
    return ward_stats


def detect_hotspots(df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude', 
                    min_samples: int = 5, eps: float = 0.01):
    """
    Detect geographic hotspots using DBSCAN clustering
    
    Args:
        df: DataFrame with geographic data
        lat_col: Name of latitude column
        lon_col: Name of longitude column
        min_samples: Minimum samples for DBSCAN cluster
        eps: Maximum distance for DBSCAN
    
    Returns:
        DataFrame: Original data with hotspot labels
    """
    if not SKLEARN_AVAILABLE:
        logger.warning("scikit-learn not available - using simple density-based hotspot detection")
        return detect_hotspots_simple(df, lat_col, lon_col)
    
    # Filter valid coordinates
    valid_mask = df[lat_col].notna() & df[lon_col].notna()
    df_valid = df[valid_mask].copy()
    
    if len(df_valid) < min_samples:
        logger.warning("Insufficient data points for hotspot detection")
        df['hotspot_label'] = -1
        return df
    
    # Prepare coordinates
    coords = df_valid[[lat_col, lon_col]].values
    
    # Standardize coordinates (important for DBSCAN)
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)
    
    # Apply DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(coords_scaled)
    
    # Add labels to dataframe
    df['hotspot_label'] = -1
    df.loc[valid_mask, 'hotspot_label'] = labels
    
    # Calculate hotspot statistics - use sr_number or any available ID column
    count_col = 'sr_number' if 'sr_number' in df.columns else ('service_request_number' if 'service_request_number' in df.columns else df.columns[0])
    hotspot_stats = df[df['hotspot_label'] >= 0].groupby('hotspot_label').agg({
        lat_col: 'mean',
        lon_col: 'mean',
        count_col: 'count'
    }).rename(columns={
        count_col: 'point_count',
        lat_col: 'center_latitude',
        lon_col: 'center_longitude'
    }).reset_index()
    
    logger.info(f"Detected {len(hotspot_stats)} hotspots")
    
    return df, hotspot_stats


def detect_hotspots_simple(df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude'):
    """
    Simple density-based hotspot detection (fallback when sklearn not available)
    
    Args:
        df: DataFrame with geographic data
        lat_col: Name of latitude column
        lon_col: Name of longitude column
    
    Returns:
        tuple: (df with hotspot labels, hotspot statistics)
    """
    # Filter valid coordinates
    valid_mask = df[lat_col].notna() & df[lon_col].notna()
    df_valid = df[valid_mask].copy()
    
    if len(df_valid) == 0:
        df['hotspot_label'] = -1
        return df, pd.DataFrame()
    
    # Simple grid-based approach
    # Divide area into grid cells and count points in each
    lat_bins = 20
    lon_bins = 20
    
    df_valid['lat_bin'] = pd.cut(df_valid[lat_col], bins=lat_bins, labels=False)
    df_valid['lon_bin'] = pd.cut(df_valid[lon_col], bins=lon_bins, labels=False)
    
    # Count points per cell
    cell_counts = df_valid.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='count')
    
    # Identify hotspots (top 10% of cells by count)
    threshold = cell_counts['count'].quantile(0.9)
    hotspot_cells = cell_counts[cell_counts['count'] >= threshold]
    
    # Assign hotspot labels
    df['hotspot_label'] = -1
    for idx, row in hotspot_cells.iterrows():
        mask = (df_valid['lat_bin'] == row['lat_bin']) & (df_valid['lon_bin'] == row['lon_bin'])
        df.loc[df_valid[mask].index, 'hotspot_label'] = idx
    
    # Calculate hotspot centers - use sr_number or any available ID column
    count_col = 'sr_number' if 'sr_number' in df.columns else ('service_request_number' if 'service_request_number' in df.columns else df.columns[0])
    hotspot_stats = df[df['hotspot_label'] >= 0].groupby('hotspot_label').agg({
        lat_col: 'mean',
        lon_col: 'mean',
        count_col: 'count'
    }).rename(columns={
        count_col: 'point_count',
        lat_col: 'center_latitude',
        lon_col: 'center_longitude'
    }).reset_index()
    
    return df, hotspot_stats


def compare_neighborhoods(df: pd.DataFrame, metric_col: str = 'complaint_count'):
    """
    Compare neighborhoods by a metric
    
    Args:
        df: DataFrame with neighborhood data
        metric_col: Column to compare
    
    Returns:
        DataFrame: Sorted comparison
    """
    if metric_col not in df.columns:
        logger.warning(f"Column {metric_col} not found")
        return pd.DataFrame()
    
    comparison = df[[col for col in ['community_area', 'ward', metric_col] if col in df.columns]].copy()
    comparison = comparison.sort_values(metric_col, ascending=False)
    
    return comparison


def rank_hotspots_by_metric(hotspot_stats: pd.DataFrame, metric: str = 'point_count') -> pd.DataFrame:
    """
    Rank hotspots by a specific metric
    
    Args:
        hotspot_stats: DataFrame with hotspot statistics
        metric: Column name to rank by (default: point_count)
    
    Returns:
        DataFrame: Ranked hotspots
    """
    if hotspot_stats.empty:
        return pd.DataFrame()
    
    if metric not in hotspot_stats.columns:
        logger.warning(f"Metric {metric} not found in hotspot stats")
        return hotspot_stats.copy()
    
    ranked = hotspot_stats.copy()
    ranked = ranked.sort_values(metric, ascending=False)
    ranked['rank'] = range(1, len(ranked) + 1)
    
    return ranked


def get_top_hotspots(hotspot_stats: pd.DataFrame, n: int = 10, 
                     metric: str = 'point_count') -> pd.DataFrame:
    """
    Get top N hotspots by metric
    
    Args:
        hotspot_stats: DataFrame with hotspot statistics
        n: Number of top hotspots to return
        metric: Column name to rank by
    
    Returns:
        DataFrame: Top N hotspots with rankings
    """
    if hotspot_stats.empty:
        return pd.DataFrame()
    
    ranked = rank_hotspots_by_metric(hotspot_stats, metric)
    top_n = ranked.head(n).copy()
    
    return top_n


def format_hotspot_description(hotspot_row: pd.Series, 
                               include_coords: bool = False) -> str:
    """
    Create plain-language description of a hotspot
    
    Args:
        hotspot_row: Series with hotspot data (point_count, center_latitude, center_longitude)
        include_coords: Whether to include coordinates in description
    
    Returns:
        Plain-language description string
    """
    point_count = hotspot_row.get('point_count', 0)
    lat = hotspot_row.get('center_latitude', None)
    lon = hotspot_row.get('center_longitude', None)
    
    # Determine area name based on coordinates (simplified)
    area_name = "Area"
    if lat and lon:
        # Chicago approximate boundaries
        if 41.85 <= lat <= 41.95 and -87.75 <= lon <= -87.60:
            area_name = "Downtown Area"
        elif lat > 41.90:
            area_name = "North Side"
        elif lat < 41.80:
            area_name = "South Side"
        elif lon < -87.70:
            area_name = "West Side"
        else:
            area_name = "Central Area"
    
    description = f"{area_name} - {int(point_count)} incidents"
    
    if include_coords and lat and lon:
        description += f" (Lat: {lat:.4f}, Lon: {lon:.4f})"
    
    return description

