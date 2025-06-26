import pandas as pd

# Load merged data BEFORE dropna
merged = pd.read_csv("data/merged_data.csv")

# Print asset breakdown before drop
print("\n📊 Full asset counts:")
print(merged["asset"].value_counts(dropna=False))

# Show rows where Open or Close is missing
print("\n❌ Rows missing Open:")
print(merged[merged["Open"].isna()][["Date", "asset", "subreddit"]].head())

print("\n❌ Rows missing Close:")
print(merged[merged["Close"].isna()][["Date", "asset", "subreddit"]].head())
