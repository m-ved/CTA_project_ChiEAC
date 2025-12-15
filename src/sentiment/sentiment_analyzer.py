"""
Sentiment Analysis Module
Uses VADER and TextBlob to analyze tweet sentiment
"""

import pandas as pd
import numpy as np
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from typing import Dict, Tuple
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analyzer using VADER and TextBlob"""
    
    def __init__(self, primary_method: str = 'vader'):
        """
        Initialize sentiment analyzer
        
        Args:
            primary_method: 'vader' or 'textblob' - which method to use as primary
        """
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.primary_method = primary_method.lower()
        
        if self.primary_method not in ['vader', 'textblob']:
            logger.warning(f"Unknown method {primary_method}, defaulting to VADER")
            self.primary_method = 'vader'
    
    def analyze_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if pd.isna(text) or text == '':
            return {
                'vader_compound': 0.0,
                'vader_pos': 0.0,
                'vader_neu': 0.0,
                'vader_neg': 0.0
            }
        
        scores = self.vader_analyzer.polarity_scores(str(text))
        return {
            'vader_compound': scores['compound'],
            'vader_pos': scores['pos'],
            'vader_neu': scores['neu'],
            'vader_neg': scores['neg']
        }
    
    def analyze_textblob(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if pd.isna(text) or text == '':
            return {
                'textblob_polarity': 0.0,
                'textblob_subjectivity': 0.0
            }
        
        try:
            blob = TextBlob(str(text))
            return {
                'textblob_polarity': blob.sentiment.polarity,
                'textblob_subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.warning(f"TextBlob analysis error: {e}")
            return {
                'textblob_polarity': 0.0,
                'textblob_subjectivity': 0.0
            }
    
    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using both methods
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with all sentiment scores
        """
        vader_scores = self.analyze_vader(text)
        textblob_scores = self.analyze_textblob(text)
        
        # Combine scores
        combined = {**vader_scores, **textblob_scores}
        
        # Determine primary polarity and subjectivity
        if self.primary_method == 'vader':
            combined['polarity'] = combined['vader_compound']
            combined['subjectivity'] = combined['vader_pos'] + combined['vader_neu']
        else:  # textblob
            combined['polarity'] = combined['textblob_polarity']
            combined['subjectivity'] = combined['textblob_subjectivity']
        
        return combined
    
    def categorize_sentiment(self, polarity: float, thresholds: Dict[str, float] = None) -> str:
        """
        Categorize sentiment into positive, neutral, or negative
        
        Args:
            polarity: Sentiment polarity score
            thresholds: Dictionary with 'positive' and 'negative' threshold values
        
        Returns:
            'positive', 'neutral', or 'negative'
        """
        if thresholds is None:
            thresholds = {'positive': 0.05, 'negative': -0.05}
        
        if polarity >= thresholds['positive']:
            return 'positive'
        elif polarity <= thresholds['negative']:
            return 'negative'
        else:
            return 'neutral'


def analyze_tweets(df: pd.DataFrame, content_column: str = 'content') -> pd.DataFrame:
    """
    Analyze sentiment for all tweets in DataFrame
    
    Args:
        df: DataFrame with tweet data
        content_column: Name of column containing tweet text
    
    Returns:
        DataFrame with sentiment scores added
    """
    logger.info("Starting sentiment analysis")
    
    if df.empty:
        logger.warning("Empty DataFrame provided")
        return df
    
    if content_column not in df.columns:
        logger.error(f"Content column '{content_column}' not found in DataFrame")
        return df
    
    analyzer = SentimentAnalyzer(primary_method='vader')
    
    # Initialize sentiment columns
    sentiment_cols = [
        'vader_compound', 'vader_pos', 'vader_neu', 'vader_neg',
        'textblob_polarity', 'textblob_subjectivity',
        'polarity', 'subjectivity', 'sentiment_category'
    ]
    
    for col in sentiment_cols:
        if col not in df.columns:
            df[col] = np.nan
    
    # Analyze each tweet
    logger.info(f"Analyzing {len(df)} tweets...")
    
    for idx, row in df.iterrows():
        text = row[content_column]
        
        # Get sentiment scores
        scores = analyzer.analyze(text)
        
        # Update DataFrame
        for key, value in scores.items():
            if key in df.columns:
                df.at[idx, key] = value
        
        # Categorize sentiment
        polarity = scores.get('polarity', 0.0)
        category = analyzer.categorize_sentiment(polarity)
        df.at[idx, 'sentiment_category'] = category
        
        # Progress logging
        if (idx + 1) % 100 == 0:
            logger.info(f"Processed {idx + 1}/{len(df)} tweets")
    
    logger.info("Sentiment analysis complete")
    
    # Print summary
    if 'sentiment_category' in df.columns:
        logger.info("\n=== Sentiment Distribution ===")
        logger.info(df['sentiment_category'].value_counts())
        logger.info(f"\nAverage Polarity: {df['polarity'].mean():.3f}")
        logger.info(f"Average Subjectivity: {df['subjectivity'].mean():.3f}")
    
    return df


def main():
    """Main function to analyze tweet sentiment"""
    import sys
    import os
    
    # Load tweet data
    input_path = PROJECT_ROOT / "data" / "cleaned" / "tweets.csv"
    output_path = PROJECT_ROOT / "data" / "cleaned" / "tweets_with_sentiment.csv"
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return
    
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} tweets from {input_path}")
    
    # Analyze sentiment
    df_analyzed = analyze_tweets(df)
    
    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_analyzed.to_csv(output_path, index=False)
    logger.info(f"Saved analyzed tweets to {output_path}")


if __name__ == "__main__":
    main()

