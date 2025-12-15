import tweepy
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def main():
    print("Verifying Twitter API Connectivity...")
    token = os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        print("ERROR: No TWITTER_BEARER_TOKEN found in .env")
        return

    print("Token found. Initializing client...")
    # Don't wait on rate limit, just fail if hit
    client = tweepy.Client(bearer_token=token, wait_on_rate_limit=False)

    print("Attempting to fetch 1 tweet for #Chicago...")
    try:
        response = client.search_recent_tweets(
            query="#Chicago lang:en -is:retweet",
            max_results=10,
            tweet_fields=['created_at', 'author_id']
        )
        
        if response.data:
            print(f"SUCCESS! Found {len(response.data)} tweets.")
            print(f"First tweet: {response.data[0].text[:50]}...")
        else:
            print("WARNING: Request succeeded but returned no data.")
            
    except tweepy.TooManyRequests:
        print("ERROR: Rate Limit Exceeded. You have used up your API quota for now.")
        print("Twitter Free Tier limits you. Please wait 15 minutes before trying again.")
    except tweepy.Unauthorized:
        print("ERROR: Unauthorized. Check your Bearer Token.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
