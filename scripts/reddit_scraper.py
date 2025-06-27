import os
import praw
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# === Load environment variables (.env must include Reddit API keys) ===
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("USER_AGENT", "sentiment-dashboard")
)

# === Setup ===
subreddits = [
    "cryptocurrency", "stocks", "investing",
    "StockMarket", "wallstreetbets", "Economics",
    "worldnews", "news"
]
limit = 1000  # per subreddit
cutoff = datetime.now(timezone.utc) - timedelta(days=90)  # last 3 months
analyzer = SentimentIntensityAnalyzer()

# === Collect Posts ===
all_data = []
for sub in subreddits:
    print(f"📥 Scraping r/{sub}...")
    for post in reddit.subreddit(sub).new(limit=limit):
        post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        if post_time < cutoff:
            continue

        # Merge title + selftext
        title = post.title or ""
        body = post.selftext or ""
        full_text = f"{title}\n{body}".strip()

        # Skip empty or deleted posts
        if not full_text or full_text.lower() in ["[deleted]", "[removed]"]:
            continue

        sentiment = analyzer.polarity_scores(full_text)

        all_data.append({
            "subreddit": sub,
            "created_utc": post_time,
            "text": full_text,
            "compound": sentiment["compound"],
            "neg": sentiment["neg"],
            "neu": sentiment["neu"],
            "pos": sentiment["pos"]
        })

# === Save to CSV ===
df = pd.DataFrame(all_data)
os.makedirs("data", exist_ok=True)
df.to_csv("data/reddit_text.csv", index=False)
print(f"✅ Saved {len(df)} posts to data/reddit_sentiment.csv")
