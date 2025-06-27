import pandas as pd
from scripts.summary_generator import summarize_with_groq

# Load your saved Reddit sentiment CSV
df = pd.read_csv("data/reddit_sentiment.csv", parse_dates=["created_utc"])

# Filter for one subreddit + a date range (e.g. r/cryptocurrency in early June)
subreddit = "cryptocurrency"
start_date = "2025-06-09"
end_date = "2025-06-15"

filtered = df[
    (df["subreddit"] == subreddit) &
    (df["created_utc"] >= start_date) &
    (df["created_utc"] <= end_date)
]

# Rename 'title' to 'text' so Groq summary function works
filtered = filtered.rename(columns={"title": "text"})

# Run summary
summary = summarize_with_groq(filtered, subreddit)
print("\n--- Reddit Summary ---")
print(summary)
