import pandas as pd
from datetime import timedelta
import os

# --- Load Reddit Sentiment ---
reddit_df = pd.read_csv("data/reddit_sentiment.csv", parse_dates=["created_utc"])
reddit_df["date"] = reddit_df["created_utc"].dt.date

# Aggregate sentiment
daily_sentiment = reddit_df.groupby(["date", "subreddit"]).agg({
    "compound": "mean",
    "neg": "mean",
    "neu": "mean",
    "pos": "mean"
}).reset_index().rename(columns={
    "compound": "avg_compound",
    "neg": "avg_neg",
    "neu": "avg_neu",
    "pos": "avg_pos"
})
daily_sentiment["target_date"] = pd.to_datetime(daily_sentiment["date"]) + timedelta(days=1)
daily_sentiment["target_date"] = daily_sentiment["target_date"].dt.date

# --- Load Financial Data ---
finance_df = pd.read_csv("data/financial_data.csv", parse_dates=["Date"])
finance_df["trade_date"] = finance_df["Date"].dt.date

# --- Merge by date ---
merged = finance_df.merge(
    daily_sentiment,
    left_on="trade_date",
    right_on="target_date",
    how="inner"
)

# --- Attempt fallback repair of Open and Close ---
def fill_first_available(df, base_col):
    fallback_cols = [col for col in df.columns if col.startswith(base_col + ".")]
    if fallback_cols:
        for col in fallback_cols:
            df[base_col] = df[base_col].fillna(df[col])
    return df

merged = fill_first_available(merged, "Open")
merged = fill_first_available(merged, "Close")

# --- Report before dropping
print("\n📊 Merged asset counts BEFORE dropna:")
print(merged["asset"].value_counts())
print("\n❌ Missing Open:", merged["Open"].isna().sum())
print("❌ Missing Close:", merged["Close"].isna().sum())

# --- Drop only rows that are still missing key values
merged = merged.dropna(subset=["Open", "Close", "avg_compound"])

# --- Save
os.makedirs("data", exist_ok=True)
merged.to_csv("data/merged_data.csv", index=False)

# --- Final report
print("\n✅ Final merged dataset")
print("Rows:", len(merged))
print("Assets:", merged["asset"].value_counts())
print("Subreddits:", merged["subreddit"].value_counts())
