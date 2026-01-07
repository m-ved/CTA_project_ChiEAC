"""
Data Cleaning and Preprocessing Module
Handles missing values, duplicates, timestamp normalization, and location normalization
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_timestamps(df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
    """
    Normalize timestamp columns to datetime format
    
    Args:
        df: DataFrame to process
        date_columns: List of column names that contain dates
    
    Returns:
        DataFrame with normalized timestamps
    """
    df_clean = df.copy()
    
    for col in date_columns:
        if col in df_clean.columns:
            try:
                # Try to parse as datetime
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                logger.info(f"Normalized {col} to datetime format")
            except Exception as e:
                logger.warning(f"Could not normalize {col}: {e}")
    
    return df_clean


def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
    """
    Handle missing values in DataFrame
    
    Args:
        df: DataFrame to process
        strategy: 'drop' to drop rows with missing values, 'fill' to fill with defaults
    
    Returns:
        DataFrame with handled missing values
    """
    df_clean = df.copy()
    
    initial_count = len(df_clean)
    
    if strategy == 'drop':
        # Drop rows where all key columns are missing
        # Keep rows with partial data
        df_clean = df_clean.dropna(how='all')
        logger.info(f"Dropped {initial_count - len(df_clean)} rows with all missing values")
    elif strategy == 'fill':
        # Fill numeric columns with 0, string columns with empty string
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        string_cols = df_clean.select_dtypes(include=['object']).columns
        
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        df_clean[string_cols] = df_clean[string_cols].fillna('')
        
        logger.info("Filled missing values with defaults")
    
    return df_clean


def remove_duplicates(df: pd.DataFrame, subset: Optional[list] = None) -> pd.DataFrame:
    """
    Remove duplicate rows from DataFrame
    
    Args:
        df: DataFrame to process
        subset: List of columns to consider for duplicates (None = all columns)
    
    Returns:
        DataFrame with duplicates removed
    """
    df_clean = df.copy()
    
    initial_count = len(df_clean)
    
    if subset:
        df_clean = df_clean.drop_duplicates(subset=subset)
    else:
        df_clean = df_clean.drop_duplicates()
    
    removed = initial_count - len(df_clean)
    if removed > 0:
        logger.info(f"Removed {removed} duplicate rows")
    
    return df_clean


def normalize_locations(df: pd.DataFrame, location_column: str) -> pd.DataFrame:
    """
    Normalize location data to latitude/longitude (if possible)
    Note: This is a simplified version. Full geocoding requires API keys.
    
    Args:
        df: DataFrame to process
        location_column: Name of column containing location data
    
    Returns:
        DataFrame with normalized location data
    """
    df_clean = df.copy()
    
    if location_column not in df_clean.columns:
        logger.warning(f"Location column '{location_column}' not found")
        return df_clean
    
    # Add latitude and longitude columns if they don't exist
    if 'latitude' not in df_clean.columns:
        df_clean['latitude'] = np.nan
    if 'longitude' not in df_clean.columns:
        df_clean['longitude'] = np.nan
    
    # If location data is already in lat/lon format, extract it
    # This is a simplified approach - full geocoding would require external services
    logger.info("Location normalization: Basic structure added. Full geocoding requires external API.")
    
    return df_clean


def clean_311_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Chicago 311 service request data
    
    Args:
        df: Raw 311 DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning 311 data")
    df_clean = df.copy()
    
    # Normalize timestamps
    date_cols = ['created_date', 'updated_date', 'closed_date', 'sr_date']
    df_clean = normalize_timestamps(df_clean, date_cols)
    
    # Remove duplicates based on service request number
    if 'service_request_number' in df_clean.columns:
        df_clean = remove_duplicates(df_clean, subset=['service_request_number'])
    else:
        df_clean = remove_duplicates(df_clean)
    
    # Handle missing values
    df_clean = handle_missing_values(df_clean, strategy='drop')
    
    # Standardize column names (convert to lowercase, replace spaces with underscores)
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    
    # Normalize locations if coordinates exist
    if 'latitude' in df_clean.columns or 'longitude' in df_clean.columns:
        df_clean = normalize_locations(df_clean, 'location')
    
    logger.info(f"Cleaned 311 data: {len(df_clean)} records")
    
    return df_clean


def clean_cta_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean CTA ridership data
    
    Args:
        df: Raw CTA DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning CTA ridership data")
    df_clean = df.copy()
    
    # Normalize timestamps
    date_cols = ['date', 'service_date', 'daytype']
    df_clean = normalize_timestamps(df_clean, date_cols)
    
    # Remove duplicates
    if 'date' in df_clean.columns:
        # Remove duplicates based on date, station/route, and mode
        subset = ['date', 'mode']
        if 'station_id' in df_clean.columns:
            subset.append('station_id')
        if 'route' in df_clean.columns:
            subset.append('route')
        df_clean = remove_duplicates(df_clean, subset=subset)
    else:
        df_clean = remove_duplicates(df_clean)
    
    # Handle missing values
    df_clean = handle_missing_values(df_clean, strategy='fill')
    
    # Standardize column names
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    
    # Ensure numeric columns are numeric
    numeric_cols = ['rides', 'boardings', 'alightings']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
    
    logger.info(f"Cleaned CTA data: {len(df_clean)} records")
    
    return df_clean


def clean_traffic_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean traffic volume data
    
    Args:
        df: Raw traffic DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning traffic volume data")
    df_clean = df.copy()
    
    # Standardize column names first
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    
    # Normalize timestamps - use 'time' column from Traffic Tracker dataset
    date_cols = ['time', 'date', 'time_of_day']
    df_clean = normalize_timestamps(df_clean, date_cols)
    
    # Remove duplicates
    df_clean = remove_duplicates(df_clean)
    
    # Handle missing values
    df_clean = handle_missing_values(df_clean, strategy='fill')
    
    # Ensure numeric columns are numeric
    numeric_cols = ['speed', 'bus_count', 'message_count', 'volume', 'count']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
    
    # Extract date for aggregation - use 'time' column if available
    if 'time' in df_clean.columns:
        df_clean['date'] = pd.to_datetime(df_clean['time'], errors='coerce').dt.date
    elif 'date' in df_clean.columns:
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce').dt.date
    
    logger.info(f"Cleaned traffic data: {len(df_clean)} records")
    
    return df_clean


def clean_crime_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean crime data
    
    Args:
        df: Raw crime DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning crime data")
    df_clean = df.copy()
    
    # Normalize timestamps
    date_cols = ['date', 'updated_on']
    df_clean = normalize_timestamps(df_clean, date_cols)
    
    # Remove duplicates based on case_number
    if 'case_number' in df_clean.columns:
        df_clean = remove_duplicates(df_clean, subset=['case_number'])
    else:
        df_clean = remove_duplicates(df_clean)
    
    # Handle missing values
    df_clean = handle_missing_values(df_clean, strategy='drop')
    
    # Standardize column names
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    
    # Extract date for aggregation
    if 'date' in df_clean.columns:
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce').dt.date
    
    # Ensure arrest column is boolean/numeric
    if 'arrest' in df_clean.columns:
        df_clean['arrest'] = pd.to_numeric(df_clean['arrest'], errors='coerce').fillna(0)
    
    logger.info(f"Cleaned crime data: {len(df_clean)} records")
    
    return df_clean


def main():
    """Main function to clean all datasets"""
    logger.info("Starting data cleaning process")
    
    # Load raw data
    try:
        df_311 = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "311_raw.csv")
        logger.info(f"Loaded 311 data: {len(df_311)} records")
    except FileNotFoundError:
        logger.warning("311_raw.csv not found. Skipping 311 data cleaning.")
        df_311 = None
    
    try:
        df_cta = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "cta_raw.csv")
        logger.info(f"Loaded CTA data: {len(df_cta)} records")
    except FileNotFoundError:
        logger.warning("cta_raw.csv not found. Skipping CTA data cleaning.")
        df_cta = None
    
    try:
        df_traffic = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "traffic_raw.csv")
        logger.info(f"Loaded Traffic data: {len(df_traffic)} records")
    except FileNotFoundError:
        logger.warning("traffic_raw.csv not found. Skipping Traffic data cleaning.")
        df_traffic = None
    
    try:
        df_crime = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "crime_raw.csv")
        logger.info(f"Loaded crime data: {len(df_crime)} records")
    except FileNotFoundError:
        logger.warning("crime_raw.csv not found. Skipping crime data cleaning.")
        df_crime = None
    
    # Clean each dataset
    if df_311 is not None and not df_311.empty:
        df_311_clean = clean_311_data(df_311)
        output_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_311_clean.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned 311 data: {len(df_311_clean)} records")
    
    if df_cta is not None and not df_cta.empty:
        df_cta_clean = clean_cta_data(df_cta)
        output_path = PROJECT_ROOT / "data" / "cleaned" / "cta_ridership.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_cta_clean.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned CTA data: {len(df_cta_clean)} records")
    
    if df_traffic is not None and not df_traffic.empty:
        df_traffic_clean = clean_traffic_data(df_traffic)
        output_path = PROJECT_ROOT / "data" / "cleaned" / "traffic_data.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_traffic_clean.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned Traffic data: {len(df_traffic_clean)} records")
    
    if df_crime is not None and not df_crime.empty:
        df_crime_clean = clean_crime_data(df_crime)
        output_path = PROJECT_ROOT / "data" / "cleaned" / "crime_data.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_crime_clean.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned crime data: {len(df_crime_clean)} records")
    
    logger.info("Data cleaning complete")


if __name__ == "__main__":
    main()

