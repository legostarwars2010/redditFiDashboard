import os
import praw
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("USER_AGENT", "sentiment-dashboard")  # ✅ fixed key
)

# Sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Target subreddits and timeframe
subreddits = [
    "worldnews", "news", "investing",
    "stocks", "StockMarket", "Economics",
    "cryptocurrency", "wallstreetbets"
]
limit = 1000
cutoff = datetime.now(timezone.utc) - timedelta(days=60)

# Collect and filter posts
all_data = []
for sub in subreddits:
    for post in reddit.subreddit(sub).new(limit=limit):
        post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        if post_time >= cutoff:
            score = analyzer.polarity_scores(post.title)
            all_data.append({
                "subreddit": sub,
                "title": post.title,
                "created_utc": post_time,
                "compound": score["compound"],
                "neg": score["neg"],
                "neu": score["neu"],
                "pos": score["pos"]
            })

# Save to CSV
df = pd.DataFrame(all_data)
os.makedirs("data", exist_ok=True)
df.to_csv("data/reddit_sentiment.csv", index=False)
print(f"✅ Saved {len(df)} recent posts to data/reddit_sentiment.csv")
