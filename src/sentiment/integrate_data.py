"""
Data Integration Module
Merges sentiment data with CTA ridership and 311 complaints by date
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def aggregate_cta_by_day(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Aggregate CTA ridership data by day
    
    Args:
        df: CTA ridership DataFrame
        date_column: Name of column containing date
    
    Returns:
        DataFrame with daily CTA metrics
    """
    logger.info("Aggregating CTA ridership by day")
    
    if df.empty:
        return pd.DataFrame()
    
    if date_column not in df.columns:
        logger.warning(f"Date column '{date_column}' not found")
        return pd.DataFrame()
    
    # Ensure date is datetime
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df['date_only'] = df[date_column].dt.date
    
    # Aggregate by date
    daily_cta = df.groupby('date_only').agg({
        'rides': 'sum' if 'rides' in df.columns else 'count',
    }).reset_index()
    
    # Separate by mode if available
    if 'mode' in df.columns:
        mode_agg = df.groupby(['date_only', 'mode']).agg({
            'rides': 'sum' if 'rides' in df.columns else 'count'
        }).reset_index()
        
        # Pivot to get bus and train columns
        mode_pivot = mode_agg.pivot(index='date_only', columns='mode', values='rides').reset_index()
        mode_pivot.columns.name = None
        
        # Merge with total
        daily_cta = daily_cta.merge(mode_pivot, on='date_only', how='left')
        daily_cta = daily_cta.rename(columns={'rides': 'total_cta_rides'})
        
        if 'bus' in daily_cta.columns:
            daily_cta['bus_rides'] = daily_cta['bus'].fillna(0)
        if 'train' in daily_cta.columns:
            daily_cta['train_rides'] = daily_cta['train'].fillna(0)
        
        # Clean up
        daily_cta = daily_cta.drop(columns=[col for col in daily_cta.columns if col in ['bus', 'train']], errors='ignore')
    else:
        daily_cta = daily_cta.rename(columns={'rides': 'total_cta_rides'})
        daily_cta['bus_rides'] = 0
        daily_cta['train_rides'] = 0
    
    # Convert date back to datetime
    daily_cta['date'] = pd.to_datetime(daily_cta['date_only'])
    daily_cta = daily_cta.drop('date_only', axis=1)
    
    logger.info(f"Aggregated {len(daily_cta)} days of CTA data")
    
    return daily_cta


def aggregate_311_by_day(df: pd.DataFrame, date_column: str = 'created_date') -> pd.DataFrame:
    """
    Aggregate 311 complaints by day
    
    Args:
        df: 311 DataFrame
        date_column: Name of column containing date
    
    Returns:
        DataFrame with daily 311 metrics
    """
    logger.info("Aggregating 311 complaints by day")
    
    if df.empty:
        return pd.DataFrame()
    
    if date_column not in df.columns:
        logger.warning(f"Date column '{date_column}' not found")
        return pd.DataFrame()
    
    # Ensure date is datetime
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df['date_only'] = df[date_column].dt.date
    
    # Aggregate by date
    daily_311 = df.groupby('date_only').agg({
        date_column: 'count'
    }).reset_index()
    daily_311 = daily_311.rename(columns={date_column: 'total_311_complaints'})
    
    # Count transit-related if we can identify them
    if 'service_request_type' in df.columns:
        transit_keywords = ['street', 'light', 'pothole', 'transit', 'traffic', 'sidewalk']
        transit_mask = df['service_request_type'].str.contains(
            '|'.join(transit_keywords), case=False, na=False
        )
        transit_df = df[transit_mask].groupby('date_only').size().reset_index(name='transit_related_complaints')
        daily_311 = daily_311.merge(transit_df, on='date_only', how='left')
        daily_311['transit_related_complaints'] = daily_311['transit_related_complaints'].fillna(0)
    else:
        daily_311['transit_related_complaints'] = daily_311['total_311_complaints']
    
    # Convert date back to datetime
    daily_311['date'] = pd.to_datetime(daily_311['date_only'])
    daily_311 = daily_311.drop('date_only', axis=1)
    
    logger.info(f"Aggregated {len(daily_311)} days of 311 data")
    
    return daily_311


def integrate_all_data(
    sentiment_path: str = None,
    cta_path: str = None,
    complaints_path: str = None
) -> pd.DataFrame:
    """
    Integrate all datasets by date
    
    Args:
        sentiment_path: Path to daily sentiment data (defaults to project path)
        cta_path: Path to CTA ridership data (defaults to project path)
        complaints_path: Path to 311 complaints data (defaults to project path)
    
    Returns:
        Combined DataFrame with all metrics
    """
    logger.info("Integrating all datasets")
    
    # Set default paths if not provided
    if sentiment_path is None:
        sentiment_path = PROJECT_ROOT / "data" / "combined" / "daily_sentiment.csv"
    else:
        sentiment_path = Path(sentiment_path)
    
    if cta_path is None:
        cta_path = PROJECT_ROOT / "data" / "cleaned" / "cta_ridership.csv"
    else:
        cta_path = Path(cta_path)
    
    if complaints_path is None:
        complaints_path = PROJECT_ROOT / "data" / "cleaned" / "311_data.csv"
    else:
        complaints_path = Path(complaints_path)
    
    # Load sentiment data
    if sentiment_path.exists():
        df_sentiment = pd.read_csv(sentiment_path)
        df_sentiment['date'] = pd.to_datetime(df_sentiment['date'])
        logger.info(f"Loaded sentiment data: {len(df_sentiment)} days")
    else:
        logger.warning(f"Sentiment data not found: {sentiment_path}")
        df_sentiment = pd.DataFrame()
    
    # Load and aggregate CTA data
    if cta_path.exists():
        df_cta_raw = pd.read_csv(cta_path)
        df_cta = aggregate_cta_by_day(df_cta_raw)
        logger.info(f"Loaded CTA data: {len(df_cta)} days")
    else:
        logger.warning(f"CTA data not found: {cta_path}")
        df_cta = pd.DataFrame()
    
    # Load and aggregate 311 data
    if complaints_path.exists():
        df_311_raw = pd.read_csv(complaints_path)
        df_311 = aggregate_311_by_day(df_311_raw)
        logger.info(f"Loaded 311 data: {len(df_311)} days")
    else:
        logger.warning(f"311 data not found: {complaints_path}")
        df_311 = pd.DataFrame()
    
    # Start with sentiment data as base
    if not df_sentiment.empty:
        combined = df_sentiment.copy()
    else:
        # Create empty DataFrame with date column
        combined = pd.DataFrame()
        if not df_cta.empty:
            combined = df_cta[['date']].copy()
        elif not df_311.empty:
            combined = df_311[['date']].copy()
        else:
            logger.error("No data available to combine")
            return pd.DataFrame()
    
    # Merge CTA data
    if not df_cta.empty:
        combined = combined.merge(df_cta, on='date', how='outer')
    
    # Merge 311 data
    if not df_311.empty:
        combined = combined.merge(df_311, on='date', how='outer')
    
    # Sort by date
    combined = combined.sort_values('date').reset_index(drop=True)
    
    # Fill missing values with 0 for numeric columns
    numeric_cols = combined.select_dtypes(include=[np.number]).columns
    combined[numeric_cols] = combined[numeric_cols].fillna(0)
    
    logger.info(f"Integrated data: {len(combined)} days")
    
    # Validate date alignment
    logger.info("\n=== Date Alignment Validation ===")
    logger.info(f"Date range: {combined['date'].min()} to {combined['date'].max()}")
    logger.info(f"Total days: {len(combined)}")
    
    # Check for data gaps
    if 'date' in combined.columns:
        date_range = pd.date_range(start=combined['date'].min(), end=combined['date'].max(), freq='D')
        missing_dates = set(date_range) - set(combined['date'])
        if missing_dates:
            logger.info(f"Missing dates: {len(missing_dates)} days")
        else:
            logger.info("No missing dates in range")
    
    return combined


def main():
    """Main function to integrate all data"""
    # Integrate all datasets
    combined_df = integrate_all_data()
    
    if combined_df.empty:
        logger.error("No data to save")
        return
    
    # Save combined data
    output_path = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    logger.info(f"Saved combined data to {output_path}")
    
    # Print summary
    logger.info("\n=== Combined Data Summary ===")
    logger.info(f"Shape: {combined_df.shape}")
    logger.info(f"Columns: {list(combined_df.columns)}")
    logger.info(f"\nFirst few rows:")
    print(combined_df.head())


if __name__ == "__main__":
    main()

