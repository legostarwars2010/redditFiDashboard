import pandas as pd

df = pd.read_csv("data/financial_data.csv")
print(df["asset"].value_counts(dropna=False))
