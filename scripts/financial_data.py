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

# Date range (last 60 days)
end_date = datetime.today()
start_date = end_date - timedelta(days=60)

# Download and label data
all_data = []
for asset_name, ticker in assets.items():
    print(f"📥 Fetching {asset_name} ({ticker})")
    df = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if df.empty:
        print(f"⚠️ No data for {asset_name}, skipping.")
        continue

    df.reset_index(inplace=True)
    df["asset"] = asset_name
    df["ticker"] = ticker
    df["pct_change"] = df["Close"].pct_change()
    all_data.append(df)

# Combine and save
final_df = pd.concat(all_data, ignore_index=True)
os.makedirs("data", exist_ok=True)
final_df.to_csv("data/financial_data.csv", index=False)
print(f"✅ Saved financial data for {len(assets)} assets to data/financial_data.csv ({len(final_df)} rows)")
