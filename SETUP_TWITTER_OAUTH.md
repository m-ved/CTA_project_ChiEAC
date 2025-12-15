# Setup Twitter OAuth Credentials

## Step 1: Get Your Access Token and Secret

1. Go to **https://developer.twitter.com/en/portal/dashboard**
2. Sign in and select your app/project
3. Navigate to **"Keys and Tokens"** tab
4. Scroll down to **"Access Token and Secret"** section
5. Click **"Generate"** button
6. **Copy both values immediately** (you can only see them once!)

You'll get:
- **Access Token** (starts with something like `1234567890-...`)
- **Access Token Secret** (a long random string)

## Step 2: Create .env File

Create a file named `.env` in your project root with:

```bash
TWITTER_API_KEY=dsh6XidC3s3SPW1O1LSlL61Bz
TWITTER_API_SECRET=aXO3laNCNfDZtFmJ9cy3Cs6gd8L2UomAUVyQ8YN5DA3veWPMYI
TWITTER_ACCESS_TOKEN=paste_your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=paste_your_access_token_secret_here
```

## Step 3: Quick Setup Command

After you get your Access Token and Secret, run this in terminal:

```bash
cd "/Users/mukul/Desktop/chieac project"

cat > .env << 'EOF'
TWITTER_API_KEY=dsh6XidC3s3SPW1O1LSlL61Bz
TWITTER_API_SECRET=aXO3laNCNfDZtFmJ9cy3Cs6gd8L2UomAUVyQ8YN5DA3veWPMYI
TWITTER_ACCESS_TOKEN=YOUR_ACCESS_TOKEN_HERE
TWITTER_ACCESS_TOKEN_SECRET=YOUR_ACCESS_TOKEN_SECRET_HERE
EOF
```

Then edit `.env` and replace:
- `YOUR_ACCESS_TOKEN_HERE` with your actual Access Token
- `YOUR_ACCESS_TOKEN_SECRET_HERE` with your actual Access Token Secret

## Step 4: Test It

Once your `.env` file is set up, test it in your notebook:

```python
from data_collection.collect_tweets_tweepy import main as collect_tweets_tweepy
collect_tweets_tweepy()
```

## Security Note

- Never share your `.env` file
- Never commit it to git (it's already in .gitignore)
- If you accidentally share credentials, regenerate them immediately in Twitter Developer Portal

## Troubleshooting

### "No Twitter API credentials found"
- Make sure `.env` file is in the project root
- Check that all four variables are set
- Verify no extra spaces or quotes around values

### "Unauthorized" error
- Double-check all four credentials are correct
- Make sure you copied the full Access Token and Secret
- Verify your Twitter Developer account is approved

### Rate limit errors
- The script automatically waits for rate limits
- Free tier: 10,000 tweets/day, 500,000/month
- This is more than enough for the project!

