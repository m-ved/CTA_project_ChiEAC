"""
Traffic Volume Data Collection
Downloads traffic volume and speed data from data.cityofchicago.org
"""

import requests
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Traffic Volume API endpoint - Using Traffic Tracker Historical Congestion Estimates
TRAFFIC_VOLUME_URL = "https://data.cityofchicago.org/resource/4g9f-3jbs.json"


def collect_traffic_data(limit: int = 50000, year: Optional[int] = None, max_total: int = 1000000) -> pd.DataFrame:
    """
    Collects traffic volume data from the Chicago Data Portal API.
    
    Args:
        limit: The maximum number of records to fetch per request.
        year: The specific year to fetch data for. If None, fetches for the last 90 days.
        max_total: Maximum total records to collect (default: 1,000,000). Data is ordered by time DESC, so latest data is collected first.
    
    Returns:
        A pandas DataFrame containing the raw traffic data.
    """
    logger.info(f"Starting Traffic data collection with limit: {limit}, max_total: {max_total:,}, for year: {year if year else 'last 90 days'}.")
    
    date_filter = ""
    if year:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        date_filter = f"time between '{start_date.strftime('%Y-%m-%dT00:00:00.000')}' and '{end_date.strftime('%Y-%m-%dT23:59:59.999')}'"
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        date_filter = f"time between '{start_date.strftime('%Y-%m-%dT00:00:00.000')}' and '{end_date.strftime('%Y-%m-%dT23:59:59.999')}'"
    
    params = {
        "$limit": limit,
        "$order": "time DESC",
        "$where": date_filter
    }
    
    all_data = []
    offset = 0
    
    while len(all_data) < max_total:
        current_params = params.copy()
        current_params["$offset"] = offset
        # Adjust limit for the last batch to not exceed max_total
        remaining = max_total - len(all_data)
        current_params["$limit"] = min(limit, remaining)
        
        try:
            response = requests.get(TRAFFIC_VOLUME_URL, params=current_params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.info("No more traffic data received from the API.")
                break
            
            all_data.extend(data)
            logger.info(f"Collected {len(data)} traffic records (total: {len(all_data):,}).")
            
            if len(data) < limit or len(all_data) >= max_total:
                break
            
            offset += limit
            time.sleep(0.5)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error collecting Traffic data: {e}")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred during Traffic data collection: {e}")
            break
    
    if not all_data:
        logger.warning("No Traffic data collected.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    logger.info(f"Successfully collected a total of {len(df)} Traffic records for {year if year else 'last 90 days'}.")
    return df


def main():
    """Main function to collect and save Traffic data."""
    df_traffic = collect_traffic_data(year=2025, limit=100000, max_total=1000000)  # Fetch for 2025, capped at 1M records (latest first)
    
    if not df_traffic.empty:
        output_path = PROJECT_ROOT / "data" / "raw" / "traffic_raw.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_traffic.to_csv(output_path, index=False)
        logger.info(f"Traffic raw data saved to {output_path}")
    else:
        logger.warning("No Traffic data to save.")


if __name__ == "__main__":
    main()

