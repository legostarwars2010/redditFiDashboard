import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# Define assets and tickers
assets = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F",
    "Crude Oil": "CL=F"
}

# Set date range: last 90 days
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=90)

# Prepare output directory
os.makedirs("data/debug_snapshots", exist_ok=True)

# Download and label data
all_data = []

for asset_name, ticker in assets.items():
    print(f"\n📥 Fetching {asset_name} ({ticker})")

    try:
        df = yf.download(
            ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1h",
            progress=False,
            auto_adjust=False  # disable auto-adjust warning
        )

        if df.empty:
            print(f"⚠️ No data returned for {asset_name}, skipping.")
            continue

        df.reset_index(inplace=True)

        # Flatten multilevel columns if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        # Debug: print column names and snapshot
        print(f"🧪 Flattened columns: {list(df.columns)}")
        print(df.head(2))


        # Save raw snapshot
        debug_path = f"data/debug_snapshots/raw_{ticker.replace('=', '').replace('^', '')}.csv"
        df.to_csv(debug_path, index=False)
        print(f"📁 Raw snapshot saved to: {debug_path}")

        # Normalize date column
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "Date"}, inplace=True)
        elif "index" in df.columns:
            df.rename(columns={"index": "Date"}, inplace=True)

        required_cols = {"Date", "Open", "Close"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            print(f"⚠️ Missing required columns for {asset_name}: {missing_cols}")
            continue

        df["Date"] = pd.to_datetime(df["Date"]).dt.floor("H").dt.tz_localize(None)
        df["asset"] = asset_name
        df["ticker"] = ticker
        df["pct_change"] = df["Close"].pct_change()

        # Keep only necessary columns
        cleaned = df[["Date", "Open", "Close", "pct_change", "asset", "ticker"]].copy()
        all_data.append(cleaned)

    except Exception as e:
        print(f"❌ Error fetching {asset_name}: {e}")

# Save final merged CSV
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.drop_duplicates(subset=["Date", "asset"], inplace=True)
    final_df.dropna(subset=["Open", "Close"], inplace=True)

    os.makedirs("data", exist_ok=True)
    final_df.to_csv("data/financial_data.csv", index=False)

    print("\n✅ Final dataset saved to data/financial_data.csv")
    print(f"📊 Total rows: {len(final_df)}")
    print(f"📈 Assets: {final_df['asset'].value_counts().to_dict()}")
else:
    print("❌ No valid data fetched for any asset.")
