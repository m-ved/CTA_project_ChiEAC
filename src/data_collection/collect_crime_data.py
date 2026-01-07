"""
Chicago Crime Data Collection
Downloads crime data from data.cityofchicago.org
"""

import requests
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chicago Crime API endpoint
CRIME_URL = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"


def fetch_crime_data(days_back: int = 90, limit: int = 50000) -> pd.DataFrame:
    """
    Fetch Chicago crime data
    
    Args:
        days_back: Number of days to look back from today
        limit: Maximum number of records to fetch
    
    Returns:
        DataFrame with crime data
    """
    logger.info("Fetching Chicago crime data")
    
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
            
            logger.info(f"Fetching crime data: offset={offset}, limit={params['$limit']}")
            
            response = requests.get(CRIME_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                break
            
            all_records.extend(data)
            logger.info(f"Fetched {len(data)} crime records (total: {len(all_records)})")
            
            if len(data) < batch_size:
                break
            
            offset += len(data)
            time.sleep(0.5)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching crime data: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    if not all_records:
        logger.warning("No crime data fetched")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    logger.info(f"Successfully fetched {len(df)} crime records")
    
    return df


def fetch_crime_data_for_year(year: int = 2025, limit: int = 100000) -> pd.DataFrame:
    """
    Fetch crime data for a specific year
    
    Args:
        year: Year to fetch data for (default: 2025)
        limit: Maximum number of records to fetch
    
    Returns:
        DataFrame with crime data
    """
    logger.info(f"Fetching Chicago crime data for year {year}")
    
    # Calculate date range for the entire year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
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
            
            logger.info(f"Fetching crime data: offset={offset}, limit={params['$limit']}")
            
            response = requests.get(CRIME_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                break
            
            all_records.extend(data)
            logger.info(f"Fetched {len(data)} crime records (total: {len(all_records)})")
            
            if len(data) < batch_size:
                break
            
            offset += len(data)
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching crime data: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    if not all_records:
        logger.warning("No crime data fetched")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    logger.info(f"Successfully fetched {len(df)} crime records for {year}")
    
    return df


def main():
    """Main function to collect and save crime data"""
    logger.info("Starting Chicago crime data collection")
    
    # Fetch crime data for 2025
    df = fetch_crime_data_for_year(year=2025, limit=100000)
    
    if df.empty:
        logger.warning("No 2025 data found. Trying fallback method...")
        # Fallback: Fetch with days_back
        df = fetch_crime_data(days_back=365, limit=100000)
    
    if df.empty:
        logger.warning("No crime data collected. Exiting.")
        return
    
    # Save raw data
    output_path = PROJECT_ROOT / "data" / "raw" / "crime_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} records to {output_path}")
    
    # Print summary
    logger.info("\n=== Crime Data Summary ===")
    logger.info(f"Total records: {len(df)}")
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    if 'primary_type' in df.columns:
        logger.info("\nTop 10 crime types:")
        logger.info(df['primary_type'].value_counts().head(10))
    if 'arrest' in df.columns:
        arrest_rate = pd.to_numeric(df['arrest'], errors='coerce').mean()
        logger.info(f"\nArrest rate: {arrest_rate:.2%}")


if __name__ == "__main__":
    main()

