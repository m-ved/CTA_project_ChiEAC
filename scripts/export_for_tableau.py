#!/usr/bin/env python3
"""
Export combined dataset for Tableau/Power BI dashboard creation
Formats data optimally for these visualization tools
"""

import sys
import os
import pandas as pd
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


def prepare_tableau_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data specifically for Tableau/Power BI
    - Ensures proper date formatting
    - Adds calculated fields that are useful for visualization
    - Renames columns for clarity
    """
    df_export = df.copy()
    
    # Ensure date is datetime
    df_export['date'] = pd.to_datetime(df_export['date'])
    
    # Add calculated fields useful for visualization
    df_export['year'] = df_export['date'].dt.year
    df_export['month'] = df_export['date'].dt.month
    df_export['day_of_week'] = df_export['date'].dt.day_name()
    df_export['day_of_week_num'] = df_export['date'].dt.dayofweek
    df_export['is_weekend'] = df_export['day_of_week_num'].isin([5, 6])
    df_export['week'] = df_export['date'].dt.isocalendar().week
    
    # Calculate sentiment ratio
    df_export['positive_ratio'] = df_export['positive'] / df_export['total_tweets'].replace(0, 1)
    df_export['negative_ratio'] = df_export['negative'] / df_export['total_tweets'].replace(0, 1)
    df_export['neutral_ratio'] = df_export['neutral'] / df_export['total_tweets'].replace(0, 1)
    
    # Calculate complaint rate per 1000 rides
    df_export['complaints_per_1000_rides'] = (df_export['total_311_complaints'] / 
                                             df_export['total_cta_rides'].replace(0, 1) * 1000)
    
    # Calculate sentiment score category
    df_export['sentiment_category'] = pd.cut(
        df_export['avg_polarity'],
        bins=[-1, -0.05, 0.05, 1],
        labels=['Negative', 'Neutral', 'Positive']
    )
    
    # Reorder columns for better organization
    column_order = [
        'date', 'year', 'month', 'week', 'day_of_week', 'day_of_week_num', 'is_weekend',
        'avg_polarity', 'std_polarity', 'avg_subjectivity', 'sentiment_category',
        'total_tweets', 'tweet_count', 'positive', 'neutral', 'negative',
        'positive_ratio', 'negative_ratio', 'neutral_ratio',
        'total_cta_rides', 'bus_rides', 'train_rides',
        'total_311_complaints', 'transit_related_complaints', 'complaints_per_1000_rides'
    ]
    
    # Only include columns that exist
    column_order = [col for col in column_order if col in df_export.columns]
    df_export = df_export[column_order]
    
    return df_export


def export_to_excel(df: pd.DataFrame, output_path: Path):
    """Export to Excel with multiple sheets for different views"""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Main combined dataset
        df.to_excel(writer, sheet_name='Combined Data', index=False)
        
        # Summary statistics
        summary = pd.DataFrame({
            'Metric': [
                'Total Days', 'Date Range Start', 'Date Range End',
                'Total Tweets', 'Total CTA Rides', 'Total 311 Complaints',
                'Avg Daily Sentiment', 'Avg Daily Rides', 'Avg Daily Complaints'
            ],
            'Value': [
                len(df),
                df['date'].min(),
                df['date'].max(),
                df['total_tweets'].sum(),
                df['total_cta_rides'].sum(),
                df['total_311_complaints'].sum(),
                df['avg_polarity'].mean(),
                df['total_cta_rides'].mean(),
                df['total_311_complaints'].mean()
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Daily sentiment trends
        sentiment_trends = df[['date', 'avg_polarity', 'total_tweets', 'positive', 'neutral', 'negative']].copy()
        sentiment_trends.to_excel(writer, sheet_name='Sentiment Trends', index=False)
        
        # Ridership trends
        ridership_trends = df[['date', 'total_cta_rides', 'bus_rides', 'train_rides']].copy()
        ridership_trends.to_excel(writer, sheet_name='Ridership Trends', index=False)
        
        # Complaint trends
        complaint_trends = df[['date', 'total_311_complaints', 'transit_related_complaints']].copy()
        complaint_trends.to_excel(writer, sheet_name='Complaint Trends', index=False)


def main():
    """Main export function"""
    logger.info("="*60)
    logger.info("Tableau/Power BI Data Export")
    logger.info("="*60)
    
    # Load combined data
    combined_path = PROJECT_ROOT / "data" / "combined" / "combined_data.csv"
    if not combined_path.exists():
        logger.error(f"Combined data not found: {combined_path}")
        logger.error("Please run the data integration step first:")
        logger.error("  python src/sentiment/integrate_data.py")
        return
    
    logger.info(f"Loading combined data from: {combined_path}")
    df = pd.read_csv(combined_path)
    logger.info(f"Loaded {len(df)} rows")
    
    # Prepare data for Tableau/Power BI
    logger.info("\nPreparing data for Tableau/Power BI...")
    df_export = prepare_tableau_data(df)
    logger.info(f"Prepared {len(df_export)} rows with {len(df_export.columns)} columns")
    
    # Create exports directory
    exports_dir = PROJECT_ROOT / "data" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Export to CSV (primary format)
    csv_path = exports_dir / "combined_data_for_tableau.csv"
    df_export.to_csv(csv_path, index=False)
    logger.info(f"\n✓ Exported CSV to: {csv_path}")
    
    # Export to Excel (if openpyxl is available)
    try:
        excel_path = exports_dir / "combined_data_for_tableau.xlsx"
        export_to_excel(df_export, excel_path)
        logger.info(f"✓ Exported Excel to: {excel_path}")
    except ImportError:
        logger.warning("openpyxl not installed - skipping Excel export")
        logger.warning("Install with: pip install openpyxl")
    except Exception as e:
        logger.warning(f"Could not export to Excel: {e}")
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("Export Summary")
    logger.info("="*60)
    logger.info(f"Date Range: {df_export['date'].min()} to {df_export['date'].max()}")
    logger.info(f"Total Days: {len(df_export)}")
    logger.info(f"Columns: {len(df_export.columns)}")
    logger.info(f"\nColumn List:")
    for i, col in enumerate(df_export.columns, 1):
        logger.info(f"  {i:2d}. {col}")
    
    logger.info("\n" + "="*60)
    logger.info("Export Complete!")
    logger.info("="*60)
    logger.info(f"\nFiles saved to: {exports_dir}")
    logger.info("\nNext steps:")
    logger.info("1. Open Tableau or Power BI")
    logger.info("2. Import the CSV or Excel file")
    logger.info("3. Follow the dashboard guide: docs/tableau_dashboard_guide.md")


if __name__ == "__main__":
    main()

