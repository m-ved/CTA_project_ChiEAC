"""
CTA Ridership Data Collection
Downloads CTA bus and train ridership data from data.cityofchicago.org
"""

import requests
import pandas as pd
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# Get project root directory (parent of src directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CTA Data Portal endpoints
CTA_BUS_RIDERSHIP_URL = "https://data.cityofchicago.org/resource/jyb9-n7fm.json"
# CTA Train (L) Station Entries - correct endpoint
CTA_TRAIN_RIDERSHIP_URL = "https://data.cityofchicago.org/resource/5neh-572f.json"
# Alternative endpoints to try if primary fails
CTA_TRAIN_ALTERNATIVE_URLS = [
    "https://data.cityofchicago.org/resource/fhrw-4uyv.json",  # Old endpoint (may not exist)
    "https://data.cityofchicago.org/resource/8pix-ypme.json",  # Station metadata (not ridership)
]


def fetch_cta_bus_ridership(days_back: int = 90, limit: int = 50000) -> pd.DataFrame:
    """
    Fetch CTA bus ridership data
    
    Args:
        days_back: Number of days to look back from today
        limit: Maximum number of records to fetch
    
    Returns:
        DataFrame with bus ridership data
    """
    logger.info("Fetching CTA bus ridership data")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format dates for API query
    start_date_str = start_date.strftime('%Y-%m-%dT00:00:00.000')
    end_date_str = end_date.strftime('%Y-%m-%dT23:59:59.999')
    
    all_records = []
    offset = 0
    batch_size = 5000
    
    while offset < limit:
        try:
            params = {
                '$limit': min(batch_size, limit - offset),
                '$offset': offset,
                '$where': f"date >= '{start_date_str}' AND date <= '{end_date_str}'",
                '$order': 'date DESC'
            }
            
            logger.info(f"Fetching bus data: offset={offset}, limit={params['$limit']}")
            
            response = requests.get(CTA_BUS_RIDERSHIP_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                break
            
            all_records.extend(data)
            logger.info(f"Fetched {len(data)} bus records (total: {len(all_records)})")
            
            if len(data) < batch_size:
                break
            
            offset += len(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching bus data: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    if not all_records:
        logger.warning("No bus ridership data fetched")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    df['mode'] = 'bus'  # Add mode identifier
    logger.info(f"Total bus records: {len(df)}")
    
    return df


def fetch_cta_train_ridership(days_back: int = 90, limit: int = 50000) -> pd.DataFrame:
    """
    Fetch CTA train (L) ridership data
    
    Args:
        days_back: Number of days to look back from today
        limit: Maximum number of records to fetch
    
    Returns:
        DataFrame with train ridership data
    """
    logger.info("Fetching CTA train ridership data")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format dates for API query
    start_date_str = start_date.strftime('%Y-%m-%dT00:00:00.000')
    end_date_str = end_date.strftime('%Y-%m-%dT23:59:59.999')
    
    all_records = []
    offset = 0
    batch_size = 5000
    
    # Try primary endpoint first
    endpoints_to_try = [CTA_TRAIN_RIDERSHIP_URL] + CTA_TRAIN_ALTERNATIVE_URLS
    
    for endpoint_url in endpoints_to_try:
        logger.info(f"Trying train endpoint: {endpoint_url}")
        all_records = []
        offset = 0
        
        while offset < limit:
            try:
                params = {
                    '$limit': min(batch_size, limit - offset),
                    '$offset': offset,
                    '$where': f"date >= '{start_date_str}' AND date <= '{end_date_str}'",
                    '$order': 'date DESC'
                }
                
                logger.info(f"Fetching train data: offset={offset}, limit={params['$limit']}")
                
                response = requests.get(endpoint_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    break
                
                all_records.extend(data)
                logger.info(f"Fetched {len(data)} train records (total: {len(all_records)})")
                
                if len(data) < batch_size:
                    break
                
                offset += len(data)
                
                # Rate limiting
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching train data from {endpoint_url}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error with {endpoint_url}: {e}")
                break
        
        # If we got data from this endpoint, use it
        if all_records:
            logger.info(f"Successfully fetched train data from {endpoint_url}")
            break
    
    if not all_records:
        logger.warning("No train ridership data fetched from any endpoint")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    
    # Standardize column names to match bus data structure
    # Train data has: station_id, stationname, date, daytype, rides
    # Bus data has: route, date, daytype, rides
    # We'll keep both structures but add a 'route' column for train (using stationname)
    if 'stationname' in df.columns and 'route' not in df.columns:
        df['route'] = df['stationname']  # Use station name as route identifier for trains
    
    df['mode'] = 'train'  # Add mode identifier
    logger.info(f"Total train records: {len(df)}")
    
    return df


def combine_ridership_data(bus_df: pd.DataFrame, train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine bus and train ridership data
    
    Args:
        bus_df: Bus ridership DataFrame
        train_df: Train ridership DataFrame
    
    Returns:
        Combined DataFrame
    """
    if bus_df.empty and train_df.empty:
        return pd.DataFrame()
    
    if bus_df.empty:
        return train_df
    
    if train_df.empty:
        return bus_df
    
    # Standardize column names for combination
    # Common columns might be: date, rides, station_id, route, etc.
    combined = pd.concat([bus_df, train_df], ignore_index=True)
    
    logger.info(f"Combined ridership data: {len(combined)} total records")
    
    return combined


def main():
    """Main function to collect and save CTA ridership data"""
    logger.info("Starting CTA ridership data collection")
    
    # Fetch bus and train data
    bus_df = fetch_cta_bus_ridership(days_back=90, limit=50000)
    train_df = fetch_cta_train_ridership(days_back=90, limit=50000)
    
    # Combine datasets
    combined_df = combine_ridership_data(bus_df, train_df)
    
    if combined_df.empty:
        logger.warning("No CTA ridership data collected. Exiting.")
        return
    
    # Save raw data
    output_path = PROJECT_ROOT / "data" / "raw" / "cta_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory if needed
    combined_df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(combined_df)} records to {output_path}")
    
    # Print summary
    logger.info("\n=== Data Summary ===")
    logger.info(f"Total records: {len(combined_df)}")
    if 'mode' in combined_df.columns:
        logger.info("\nBy mode:")
        logger.info(combined_df['mode'].value_counts())
    if 'date' in combined_df.columns:
        logger.info(f"\nDate range: {combined_df['date'].min()} to {combined_df['date'].max()}")


if __name__ == "__main__":
    main()

