# Getting Real Twitter Data - API Setup Guide

This guide explains how to get **real Twitter/X data** using the official Twitter API v2.

## Why Not snscrape?

- `snscrape` is incompatible with Python 3.13
- Twitter/X has made changes that break unofficial scraping tools
- The official API is the reliable way to get real data

## Option 1: Twitter API v2 (Recommended)

### Step 1: Get Twitter Developer Account

1. Go to https://developer.twitter.com/
2. Sign in with your Twitter/X account
3. Apply for a developer account (usually approved quickly for academic/research use)
4. Create a new "App" or "Project"

### Step 2: Get Your API Credentials

You have two options:

#### Option A: Bearer Token (Simplest - Read-only access)

1. In your Twitter Developer Portal, go to your App
2. Navigate to "Keys and Tokens"
3. Under "Bearer Token", click "Generate"
4. Copy the Bearer Token

#### Option B: OAuth 1.0a (Full access - if you need write permissions)

1. In your Twitter Developer Portal, go to your App
2. Navigate to "Keys and Tokens"
3. Copy:
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret

### Step 3: Set Up Credentials

Create a `.env` file in the project root:

```bash
# For Bearer Token (simplest)
TWITTER_BEARER_TOKEN=your_bearer_token_here

# OR for OAuth (if using full API keys)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

**Important**: Add `.env` to `.gitignore` to keep your credentials safe!

### Step 4: Install Tweepy

```bash
pip install tweepy python-dotenv
```

### Step 5: Use the New Script

Instead of `collect_tweets.py`, use:

```python
from data_collection.collect_tweets_tweepy import main as collect_tweets
collect_tweets()
```

Or in the notebook, replace the Twitter collection cell with:

```python
from data_collection.collect_tweets_tweepy import main as collect_tweets_tweepy
collect_tweets_tweepy()
```

## API Limits (Free Tier)

- **500,000 tweets per month**
- **10,000 tweets per day**
- **100 tweets per request** (pagination available)
- **Last 7 days** of tweets only (for recent search)

This is more than enough for the project (we need ~1,000-2,000 tweets).

## Option 2: Use Python 3.12 or Earlier

If you prefer to use snscrape, you can:

1. Create a Python 3.12 virtual environment:
```bash
python3.12 -m venv venv312
source venv312/bin/activate
pip install -r requirements.txt
```

2. Then run the original `collect_tweets.py` script

However, even with Python 3.12, Twitter/X API changes may still cause issues.

## Option 3: Alternative Libraries

Other options (may require different setup):
- `twint` (community-maintained, may have issues)
- `twitter-api-python` (wrapper around official API)

## Recommended Approach

**Use Twitter API v2 with Tweepy** - it's:
- ✅ Official and reliable
- ✅ Works with Python 3.13
- ✅ Free tier is sufficient
- ✅ Proper rate limiting
- ✅ Real-time data

## Troubleshooting

### "No Twitter API credentials found"
- Make sure you created the `.env` file
- Check that the variable names match exactly
- Verify the file is in the project root

### "Rate limit reached"
- The script automatically waits for rate limits
- Free tier allows 10k tweets/day - spread collection over multiple days if needed

### "Unauthorized"
- Check your Bearer Token/API keys are correct
- Make sure your Twitter Developer account is approved
- Verify your app has the right permissions

## Next Steps

1. Get your Twitter API credentials
2. Create the `.env` file
3. Install tweepy: `pip install tweepy python-dotenv`
4. Update your notebook to use `collect_tweets_tweepy.py`
5. Run the collection script

You'll get **real, live Twitter data**!

