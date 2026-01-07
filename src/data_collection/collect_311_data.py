"""
Chicago 311 Service Requests Data Collection
Collects transit-related complaints from Chicago 311 API
"""

import requests
import pandas as pd
import time
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path

# Get project root directory (parent of src directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chicago 311 API endpoint (Socrata Open Data API)
BASE_URL = "https://data.cityofchicago.org/resource/v6vf-nfxy.json"

# Transit-related service request types
TRANSIT_KEYWORDS = [
    'street light',
    'pothole',
    'transit',
    'traffic',
    'street',
    'sidewalk',
    'alley',
    'street lights',
    'streetlight'
]

# Service request types that are transit-related
TRANSIT_SERVICE_TYPES = [
    'Street Light Out',
    'Street Light - All/Out',
    'Pothole in Street',
    'Sidewalk Issue',
    'Alley Light Out',
    'Traffic Signal Out',
    'Traffic Signal - All/Out'
]


def fetch_311_data(
    limit: int = 50000,
    days_back: int = 90,
    service_types: List[str] = None,
    use_keyword_filter: bool = True
) -> pd.DataFrame:
    """
    Fetch 311 service requests from Chicago API
    
    Args:
        limit: Maximum number of records to fetch
        days_back: Number of days to look back from today
        service_types: List of service type names to filter (optional)
    
    Returns:
        DataFrame with 311 service request data
    """
    if service_types is None:
        service_types = TRANSIT_SERVICE_TYPES
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format dates for API query
    start_date_str = start_date.strftime('%Y-%m-%dT00:00:00.000')
    end_date_str = end_date.strftime('%Y-%m-%dT23:59:59.999')
    
    logger.info(f"Fetching 311 data from {start_date_str} to {end_date_str}")
    
    all_records = []
    offset = 0
    batch_size = 5000  # Socrata API limit per request
    
    while offset < limit:
        try:
            # Build query parameters - start simple
            params = {
                '$limit': min(batch_size, limit - offset),
                '$offset': offset,
                '$where': f"created_date >= '{start_date_str}' AND created_date <= '{end_date_str}'",
                '$order': 'created_date DESC'
            }
            
            # Add service type filter if provided
            # Use keyword-based filtering instead of exact service types
            if use_keyword_filter and service_types:
                # Filter by keywords in service_request_type
                keywords = ['street', 'light', 'pothole', 'traffic', 'sidewalk', 'alley']
                keyword_filter = " OR ".join([f"service_request_type like '%{kw}%'" for kw in keywords])
                params['$where'] += f" AND ({keyword_filter})"
            
            logger.info(f"Fetching batch: offset={offset}, limit={params['$limit']}")
            
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.info("No more records to fetch")
                break
            
            all_records.extend(data)
            logger.info(f"Fetched {len(data)} records (total: {len(all_records)})")
            
            # If we got fewer records than requested, we've reached the end
            if len(data) < batch_size:
                break
            
            offset += len(data)
            
            # Rate limiting - be respectful to the API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    if not all_records:
        logger.warning("No records fetched")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    logger.info(f"Total records fetched: {len(df)}")
    
    return df


def filter_transit_related(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter DataFrame to include only transit-related complaints
    
    Args:
        df: DataFrame with 311 service requests
    
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    # Create a copy to avoid SettingWithCopyWarning
    df_filtered = df.copy()
    
    # Filter by service request type
    if 'service_request_type' in df_filtered.columns:
        transit_mask = df_filtered['service_request_type'].str.contains(
            '|'.join(TRANSIT_KEYWORDS),
            case=False,
            na=False
        )
        df_filtered = df_filtered[transit_mask]
    
    # Also filter by description if available
    if 'description' in df_filtered.columns:
        desc_mask = df_filtered['description'].str.contains(
            '|'.join(TRANSIT_KEYWORDS),
            case=False,
            na=False
        )
        df_filtered = pd.concat([df_filtered, df[desc_mask]]).drop_duplicates()
    
    logger.info(f"Filtered to {len(df_filtered)} transit-related records")
    
    return df_filtered


def fetch_311_data_for_year(year: int = 2025, limit: int = 100000) -> pd.DataFrame:
    """
    Fetch 311 data for a specific year
    
    Args:
        year: Year to fetch data for (default: 2025)
        limit: Maximum number of records to fetch
    
    Returns:
        DataFrame with 311 service request data
    """
    logger.info(f"Fetching 311 data for year {year}")
    
    # Calculate date range for the entire year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
    # Format dates for API query
    start_date_str = start_date.strftime('%Y-%m-%dT00:00:00.000')
    end_date_str = end_date.strftime('%Y-%m-%dT23:59:59.999')
    
    logger.info(f"Fetching 311 data from {start_date_str} to {end_date_str}")
    
    all_records = []
    offset = 0
    batch_size = 5000
    
    while offset < limit:
        try:
            params = {
                '$limit': min(batch_size, limit - offset),
                '$offset': offset,
                '$where': f"created_date >= '{start_date_str}' AND created_date <= '{end_date_str}'",
                '$order': 'created_date DESC'
            }
            
            logger.info(f"Fetching batch: offset={offset}, limit={params['$limit']}")
            
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.info("No more records to fetch")
                break
            
            all_records.extend(data)
            logger.info(f"Fetched {len(data)} records (total: {len(all_records)})")
            
            if len(data) < batch_size:
                break
            
            offset += len(data)
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    if not all_records:
        logger.warning("No records fetched")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    logger.info(f"Total records fetched: {len(df)}")
    
    return df


def main():
    """Main function to collect and save 311 data"""
    logger.info("Starting 311 data collection")
    
    # Fetch data for 2025
    df = fetch_311_data_for_year(year=2025, limit=100000)
    
    if df.empty:
        logger.warning("No 2025 data found. Trying fallback method...")
        # Fallback: Try with keyword filter
        logger.info("Attempting to fetch 311 data with keyword filter...")
        df = fetch_311_data(limit=100000, days_back=365, use_keyword_filter=True)
        
        # If that fails, try without service type filter
        if df.empty:
            logger.info("No data with keyword filter. Trying without service type filter...")
            df = fetch_311_data(limit=100000, days_back=365, use_keyword_filter=False)
    
    if df.empty:
        logger.warning("No data collected. Exiting.")
        return
    
    # Filter for transit-related complaints
    df_transit = filter_transit_related(df)
    
    if df_transit.empty:
        logger.warning("No transit-related data found. Saving all data.")
        df_transit = df
    
    # Save raw data
    output_path = PROJECT_ROOT / "data" / "raw" / "311_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory if needed
    df_transit.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df_transit)} records to {output_path}")
    
    # Print summary
    logger.info("\n=== Data Summary ===")
    logger.info(f"Total records: {len(df_transit)}")
    if 'service_request_type' in df_transit.columns:
        logger.info("\nService Request Types:")
        logger.info(df_transit['service_request_type'].value_counts().head(10))
    if 'created_date' in df_transit.columns:
        logger.info(f"\nDate range: {df_transit['created_date'].min()} to {df_transit['created_date'].max()}")


if __name__ == "__main__":
    main()

