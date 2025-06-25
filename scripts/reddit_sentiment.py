import praw
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = os.getenv("USER_AGENT", "reddit-finance-dashboard")

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=USER_AGENT
)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Subreddits to pull from
subreddits = [
    "worldnews", "news", "investing",
    "stocks", "StockMarket", "Economics",
    "cryptocurrency", "wallstreetbets"
]

# Number of posts per subreddit
limit = 100
all_data = []

# Loop through each subreddit
for sub in subreddits:
    print(f"Fetching from r/{sub}...")
    posts = reddit.subreddit(sub).new(limit=limit)

    for post in posts:
        score = analyzer.polarity_scores(post.title)
        all_data.append({
            "subreddit": sub,
            "title": post.title,
            "created_utc": datetime.utcfromtimestamp(post.created_utc),
            "compound": score["compound"],
            "neg": score["neg"],
            "neu": score["neu"],
            "pos": score["pos"]
        })

# Create DataFrame
df = pd.DataFrame(all_data)

# Save
os.makedirs("data", exist_ok=True)
df.to_csv("data/reddit_sentiment.csv", index=False)
print(f"✅ Saved {len(df)} posts across {len(subreddits)} subreddits to data/reddit_sentiment.csv")
