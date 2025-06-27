import pandas as pd
from datetime import timedelta
import os

# --- Load Reddit Sentiment ---
reddit_df = pd.read_csv("data/reddit_sentiment.csv", parse_dates=["created_utc"])
reddit_df["date"] = reddit_df["created_utc"].dt.date

# Aggregate sentiment to daily level
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

# --- Load Financial Data (hourly) ---
finance_df = pd.read_csv("data/financial_data.csv", parse_dates=["Datetime"])

# --- Fill fallback values before aggregation
def fill_first_available(df, base_col):
    fallback_cols = [col for col in df.columns if col.startswith(base_col + ".")]
    for col in fallback_cols:
        df[base_col] = df[base_col].fillna(df[col])
    return df

for col in ["Open", "Close", "High", "Low", "Volume"]:
    finance_df = fill_first_available(finance_df, col)

# Extract date only from hourly datetime
finance_df["Date"] = finance_df["Datetime"].dt.date


# Aggregate financials to daily level (by asset)
daily_finance = finance_df.groupby(["Date", "asset"]).agg({
    "Open": "first",
    "Close": "last",
    "High": "max",
    "Low": "min",
    "Volume": "sum",
    "pct_change": "sum"
}).reset_index()
daily_finance["trade_date"] = pd.to_datetime(daily_finance["Date"]).dt.date

# --- Merge daily finance + sentiment ---
merged = daily_finance.merge(
    daily_sentiment,
    left_on="trade_date",
    right_on="target_date",
    how="inner"
)

# --- Repair fallback columns if present (legacy columns)
def fill_first_available(df, base_col):
    fallback_cols = [col for col in df.columns if col.startswith(base_col + ".")]
    if fallback_cols:
        for col in fallback_cols:
            df[base_col] = df[base_col].fillna(df[col])
    return df

merged = fill_first_available(merged, "Open")
merged = fill_first_available(merged, "Close")

# --- Add data quality flag
merged["data_quality"] = merged[["Open", "Close"]].notna().all(axis=1)

# --- Diagnostics
print("\n📊 Merged asset counts BEFORE dropna:")
print(merged["asset"].value_counts())
print("❌ Missing Open:", merged["Open"].isna().sum())
print("❌ Missing Close:", merged["Close"].isna().sum())

# --- Drop only if Close or sentiment is missing
merged = merged.dropna(subset=["Close", "avg_compound"])

# --- Save merged output
os.makedirs("data", exist_ok=True)
merged.to_csv("data/merged_data.csv", index=False)

# --- Final report
print("\n✅ Final merged dataset")
print("Rows:", len(merged))
print("Assets:", merged['asset'].value_counts())
print("Subreddits:", merged['subreddit'].value_counts())
