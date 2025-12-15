"""
Sentiment Aggregation Module
Aggregates tweets by day and sentiment category
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


def aggregate_by_day(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Aggregate tweets by day and sentiment category
    
    Args:
        df: DataFrame with tweet data including sentiment scores
        date_column: Name of column containing date
    
    Returns:
        DataFrame with daily sentiment metrics
    """
    logger.info("Aggregating tweets by day")
    
    if df.empty:
        logger.warning("Empty DataFrame provided")
        return pd.DataFrame()
    
    if date_column not in df.columns:
        logger.error(f"Date column '{date_column}' not found")
        return pd.DataFrame()
    
    # Ensure date is datetime
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    
    # Extract date (remove time component)
    df['date_only'] = df[date_column].dt.date
    
    # Group by date
    daily_agg = df.groupby('date_only').agg({
        'polarity': ['mean', 'std', 'count'],
        'subjectivity': 'mean',
        'sentiment_category': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    # Flatten column names
    daily_agg.columns = ['date', 'avg_polarity', 'std_polarity', 'tweet_count', 
                        'avg_subjectivity', 'sentiment_distribution']
    
    # Expand sentiment distribution
    sentiment_counts = []
    for dist in daily_agg['sentiment_distribution']:
        if isinstance(dist, dict):
            sentiment_counts.append({
                'positive': dist.get('positive', 0),
                'neutral': dist.get('neutral', 0),
                'negative': dist.get('negative', 0)
            })
        else:
            sentiment_counts.append({'positive': 0, 'neutral': 0, 'negative': 0})
    
    sentiment_df = pd.DataFrame(sentiment_counts)
    daily_agg = pd.concat([daily_agg, sentiment_df], axis=1)
    daily_agg = daily_agg.drop('sentiment_distribution', axis=1)
    
    # Calculate total tweets
    daily_agg['total_tweets'] = daily_agg['positive'] + daily_agg['neutral'] + daily_agg['negative']
    
    # Convert date back to datetime
    daily_agg['date'] = pd.to_datetime(daily_agg['date'])
    
    # Sort by date
    daily_agg = daily_agg.sort_values('date').reset_index(drop=True)
    
    logger.info(f"Aggregated {len(daily_agg)} days of sentiment data")
    
    return daily_agg


def main():
    """Main function to aggregate sentiment data"""
    import os
    
    # Load tweet data with sentiment
    input_path = PROJECT_ROOT / "data" / "cleaned" / "tweets_with_sentiment.csv"
    
    if not input_path.exists():
        # Try loading from cleaned tweets and analyze
        logger.info("Sentiment data not found. Analyzing tweets first...")
        from sentiment.sentiment_analyzer import analyze_tweets
        
        tweets_path = PROJECT_ROOT / "data" / "cleaned" / "tweets.csv"
        if tweets_path.exists():
            df = pd.read_csv(tweets_path)
            df = analyze_tweets(df)
            input_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(input_path, index=False)
        else:
            logger.error(f"Tweet data not found: {tweets_path}")
            return
    
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} tweets with sentiment")
    
    # Aggregate by day
    daily_sentiment = aggregate_by_day(df)
    
    # Save aggregated data
    output_path = PROJECT_ROOT / "data" / "combined" / "daily_sentiment.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    daily_sentiment.to_csv(output_path, index=False)
    logger.info(f"Saved daily sentiment aggregation to {output_path}")
    
    # Print summary
    logger.info("\n=== Daily Sentiment Summary ===")
    logger.info(f"Date range: {daily_sentiment['date'].min()} to {daily_sentiment['date'].max()}")
    logger.info(f"Total days: {len(daily_sentiment)}")
    logger.info(f"Average tweets per day: {daily_sentiment['total_tweets'].mean():.1f}")
    logger.info(f"Average polarity: {daily_sentiment['avg_polarity'].mean():.3f}")


if __name__ == "__main__":
    main()

