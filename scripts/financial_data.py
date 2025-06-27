import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Define assets and tickers
assets = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F",
    "Crude Oil": "CL=F"
}

# Date range: past 90 days
end_date = datetime.today()
start_date = end_date - timedelta(days=90)

# Set interval
interval = "1h"
chunk_size = timedelta(days=29)  # ~720 hours

# Download in chunks for each asset
all_data = []

for asset_name, ticker in assets.items():
    print(f"📥 Fetching {asset_name} ({ticker})")
    chunk_start = start_date

    while chunk_start < end_date:
        chunk_end = min(chunk_start + chunk_size, end_date)
        print(f" → {chunk_start.date()} to {chunk_end.date()}")

        df = yf.download(
            ticker,
            start=chunk_start.strftime("%Y-%m-%d"),
            end=chunk_end.strftime("%Y-%m-%d"),
            interval=interval,
            progress=False
        )

        if df.empty:
            print(f"⚠️ No data for {asset_name} in this chunk, skipping.")
            chunk_start += chunk_size
            continue

        df.reset_index(inplace=True)
        df["asset"] = asset_name
        df["ticker"] = ticker
        df["pct_change"] = df["Close"].pct_change()
        all_data.append(df)

        chunk_start += chunk_size

# Combine and save
final_df = pd.concat(all_data, ignore_index=True)
os.makedirs("data", exist_ok=True)
final_df.to_csv("data/financial_data.csv", index=False)
print(f"✅ Saved financial data for {len(assets)} assets to data/financial_data.csv ({len(final_df)} rows)")
