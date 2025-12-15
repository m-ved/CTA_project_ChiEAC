"""
Twitter/X Data Collection using Twitter API v2 (Tweepy)
Collects real tweets from Chicago-related hashtags using the official Twitter API
"""

import tweepy
import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Target hashtags - CTA and ChicagoTransit
HASHTAGS = [
    "CTA",           # #CTA
    "ChicagoTransit" # #ChicagoTransit
]

# Number of tweets to collect per hashtag - maximize collection
TWEETS_PER_HASHTAG = 500  # 2 hashtags × 500 = ~1000 tweets (as many as possible)


def get_twitter_client():
    """
    Initialize Twitter API v2 client using Tweepy
    
    Requires API keys in .env file or environment variables:
    - TWITTER_BEARER_TOKEN (for API v2)
    OR
    - TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
    
    Returns:
        tweepy.Client instance
    """
    # Try Bearer Token first (simplest for read-only access)
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    
    if bearer_token:
        logger.info("Using Bearer Token authentication")
        return tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    
    # Try OAuth 1.0a (if you have full API keys)
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    if api_key and api_secret and access_token and access_token_secret:
        logger.info("Using OAuth 1.0a authentication")
        return tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
    
    raise ValueError(
        "No Twitter API credentials found!\n"
        "Please set TWITTER_BEARER_TOKEN in .env file or provide OAuth credentials.\n"
        "See README_TWITTER_API.md for instructions."
    )


def search_tweets(client: tweepy.Client, query, max_results: int = 500) -> List[dict]:
    """
    Search for tweets using Twitter API v2 with pagination support
    
    Args:
        client: Tweepy client instance
        query: Can be a string (single hashtag) or tuple (hashtag1, hashtag2) for combined search
        max_results: Maximum number of tweets to retrieve (uses pagination if > 100)
    """
    # Handle both single hashtag and combined hashtag searches
    if isinstance(query, tuple):
        # Combined search: #hashtag1 AND #hashtag2
        hashtag1, hashtag2 = query
        search_query = f"#{hashtag1} #{hashtag2} lang:en -is:retweet"
        query_name = f"{hashtag1}+{hashtag2}"
    else:
        # Single hashtag search - use hashtag directly, no #Chicago added
        search_query = f"#{query} lang:en -is:retweet"
        query_name = query
    
    logger.info(f"Searching for tweets: {query_name} (max: {max_results})")
    
    tweets = []
    next_token = None
    max_requests = (max_results // 100) + 1  # Calculate how many requests needed
    import time
    
    try:
        # Twitter API v2 requires start_time to be at least 10 seconds in the past
        # Use UTC time and 1 day ago to ensure we're well within the limit
        utc_now = datetime.now(timezone.utc)
        start_time = (utc_now - timedelta(days=1)).isoformat().replace('+00:00', 'Z')
        
        # Paginate to get more tweets
        for request_num in range(max_requests):
            if len(tweets) >= max_results:
                break
            
            # Calculate how many tweets to get in this request
            remaining = max_results - len(tweets)
            request_size = min(100, remaining)  # API limit is 100 per request
            
            # Build query parameters
            query_params = {
                'query': search_query,
                'max_results': request_size,
                'start_time': start_time,
                'tweet_fields': ['created_at', 'public_metrics', 'author_id', 'text'],
                'expansions': ['author_id'],
                'user_fields': ['username']
            }
            
            # Add pagination token if we have one
            if next_token:
                query_params['next_token'] = next_token
            
            # Search tweets
            response = client.search_recent_tweets(**query_params)
            
            if not response.data:
                logger.info(f"No more tweets found for {query_name} (got {len(tweets)} total)")
                break
            
            # Get user data
            users = {user.id: user.username for user in response.includes.get('users', [])} if response.includes else {}
            
            # Process tweets
            for tweet in response.data:
                author_username = users.get(tweet.author_id, 'unknown')
                metrics = tweet.public_metrics
                
                tweet_dict = {
                    'tweet_id': tweet.id,
                    'url': f"https://twitter.com/{author_username}/status/{tweet.id}",
                    'date': tweet.created_at.isoformat() if tweet.created_at else None,
                    'content': tweet.text,
                    'user': author_username,
                    'retweet_count': metrics.get('retweet_count', 0),
                    'like_count': metrics.get('like_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0),
                    'hashtags': ', '.join([word for word in tweet.text.split() if word.startswith('#')]),
                    'coordinates': None,
                    'place': None
                }
                tweets.append(tweet_dict)
            
            logger.info(f"Collected {len(tweets)}/{max_results} tweets for {query_name} (request {request_num + 1})")
            
            # Check for next page
            if response.meta and 'next_token' in response.meta:
                next_token = response.meta['next_token']
            else:
                logger.info(f"No more pages available for {query_name}")
                break
            
            # Small delay between pagination requests to avoid rate limits
            if request_num < max_requests - 1:  # Don't sleep after last request
                time.sleep(1)
        
        logger.info(f"Collected {len(tweets)} tweets for {query_name}")
        
    except tweepy.TooManyRequests as e:
        logger.warning(f"Rate limit reached for {query_name}. Waiting...")
        logger.warning(f"Rate limit will reset. You can run the script again later.")
        # Don't raise - just return what we have so far
        return tweets
    except tweepy.BadRequest as e:
        # Handle invalid start_time or other bad requests
        logger.error(f"Bad request for {query_name}: {e}")
        # Try without start_time (will get most recent tweets from last 7 days)
        try:
            logger.info(f"Retrying {query_name} without start_time parameter...")
            next_token = None
            
            # Retry with pagination but without start_time
            for request_num in range(max_requests):
                if len(tweets) >= max_results:
                    break
                
                remaining = max_results - len(tweets)
                request_size = min(100, remaining)
                
                query_params = {
                    'query': search_query,
                    'max_results': request_size,
                    # Remove start_time - will get most recent tweets (last 7 days)
                    'tweet_fields': ['created_at', 'public_metrics', 'author_id', 'text'],
                    'expansions': ['author_id'],
                    'user_fields': ['username']
                }
                
                if next_token:
                    query_params['next_token'] = next_token
                
                response = client.search_recent_tweets(**query_params)
                
                if not response.data:
                    logger.info(f"No more tweets found for {query_name} (retry, got {len(tweets)} total)")
                    break
                
                users = {user.id: user.username for user in response.includes.get('users', [])} if response.includes else {}
                
                for tweet in response.data:
                    author_username = users.get(tweet.author_id, 'unknown')
                    metrics = tweet.public_metrics
                    
                    tweet_dict = {
                        'tweet_id': tweet.id,
                        'url': f"https://twitter.com/{author_username}/status/{tweet.id}",
                        'date': tweet.created_at.isoformat() if tweet.created_at else None,
                        'content': tweet.text,
                        'user': author_username,
                        'retweet_count': metrics.get('retweet_count', 0),
                        'like_count': metrics.get('like_count', 0),
                        'reply_count': metrics.get('reply_count', 0),
                        'quote_count': metrics.get('quote_count', 0),
                        'hashtags': ', '.join([word for word in tweet.text.split() if word.startswith('#')]),
                        'coordinates': None,
                        'place': None
                    }
                    tweets.append(tweet_dict)
                
                logger.info(f"Collected {len(tweets)}/{max_results} tweets for {query_name} (retry request {request_num + 1})")
                
                if response.meta and 'next_token' in response.meta:
                    next_token = response.meta['next_token']
                else:
                    break
                
                if request_num < max_requests - 1:
                    time.sleep(1)
            
            logger.info(f"Collected {len(tweets)} tweets for {query_name} (retry successful)")
            
        except Exception as retry_error:
            logger.error(f"Retry also failed for {query_name}: {retry_error}")
            return []
    except tweepy.Unauthorized:
        logger.error("Twitter API authentication failed. Check your credentials.")
    except Exception as e:
        logger.error(f"Error searching tweets for {query_name}: {e}")
    
    return tweets


def process_tweets_to_dataframe(all_tweets: List[dict]) -> pd.DataFrame:
    """
    Convert list of tweet dictionaries to DataFrame
    
    Args:
        all_tweets: List of tweet dictionaries
    
    Returns:
        DataFrame with tweet data
    """
    if not all_tweets:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_tweets)
    
    # Remove duplicates based on tweet_id
    if 'tweet_id' in df.columns:
        df = df.drop_duplicates(subset=['tweet_id'])
    
    logger.info(f"Processed {len(df)} unique tweets")
    
    return df


def main():
    """Main function to collect and save tweet data"""
    logger.info("Starting Twitter data collection using Twitter API v2")
    
    try:
        # Initialize Twitter client
        client = get_twitter_client()
        logger.info("Twitter API client initialized successfully")
    except ValueError as e:
        logger.error(str(e))
        logger.error("\nTo get Twitter API credentials:")
        logger.error("1. Go to https://developer.twitter.com/")
        logger.error("2. Create a developer account and app")
        logger.error("3. Get your Bearer Token or API keys")
        logger.error("4. Create a .env file in the project root with:")
        logger.error("   TWITTER_BEARER_TOKEN=your_bearer_token_here")
        return
    
    all_tweets = []
    
    # Search tweets for each hashtag
    import time
    for i, hashtag in enumerate(HASHTAGS):
        try:
            tweets = search_tweets(client, hashtag, TWEETS_PER_HASHTAG)
            all_tweets.extend(tweets)
            
            # Add delay between hashtags to avoid rate limits
            if i < len(HASHTAGS) - 1:  # Don't sleep after last hashtag
                time.sleep(5)  # 5 second delay between hashtags (increased for safety)
        except Exception as e:
            logger.error(f"Failed to collect tweets for {hashtag}: {e}")
            logger.info("Continuing with next hashtag...")
            continue
    
    if not all_tweets:
        logger.warning("No tweets collected.")
        return
    
    # Process tweets to DataFrame
    df = process_tweets_to_dataframe(all_tweets)
    
    if df.empty:
        logger.warning("No tweet data to save")
        return
    
    # Save raw data
    output_path = PROJECT_ROOT / "data" / "raw" / "tweets_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} tweets to {output_path}")
    
    # Print summary
    logger.info("\n=== Data Summary ===")
    logger.info(f"Total tweets: {len(df)}")
    if 'date' in df.columns and not df['date'].isna().all():
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    if 'hashtags' in df.columns:
        logger.info(f"Hashtags collected: {', '.join(HASHTAGS)}")


if __name__ == "__main__":
    main()

