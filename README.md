# 📉 Reddit Sentiment vs. Market Dashboard

A Streamlit-based interactive dashboard that visualizes how Reddit sentiment correlates with financial market performance. It integrates news discussion data and asset prices for real-time, interpretable analysis.

## 🔧 Features

- 🧠 **Reddit Sentiment Summarizer** (powered by Groq LLM): AI-generated summaries of subreddit discussions per date and topic.
- 📈 **Asset Price Tracker**: Line chart for each selected asset’s price over time.
- 📊 **Sentiment Trends**: Track sentiment across subreddits using compound scores.
- 🧪 **Emotion Breakdown & Activity Volume**: Stacked area chart of positive/neutral/negative sentiment + Reddit post volume overlay.
- 🪙 **Sentiment vs. Price Comparison**: Dual-axis view of subreddit sentiment vs asset price.
- 📌 **Sentiment vs. % Price Change**: Scatter plot to inspect correlation between sentiment and market reaction.
- 📢 **Dynamic Headline Generator**: Auto-generated title summarizing sentiment shift (bullish/bearish/neutral).

## 📁 Folder Structure

```
reddit-finance-dashboard/
├── dashboard/
│   └── app.py                  # Main Streamlit app
├── data/
│   ├── reddit_text.csv         # Raw Reddit comment/title data (past 90 days)
│   ├── financial_data.csv      # Asset data from yfinance (3-months, intraday if available)
│   └── merged_data.csv         # Final merged dataset for dashboard
├── scripts/
│   ├── reddit_sentiment.py     # Reddit scraping & sentiment preprocessing
│   ├── financial_data.py       # Yahoo Finance fetcher
│   ├── process_data.py         # Merges & processes all data
│   └── summary_generator.py    # Groq summarization interface
├── .env                        # Your Groq API key
├── requirements.txt            # Python dependencies
└── README.md
```

## ▶️ Run the App

```bash
# Activate your virtual environment (if needed)
source .venv/bin/activate         # Mac/Linux
.venv\Scripts\activate            # Windows

# Run the Streamlit app
streamlit run dashboard/app.py
```

## 🧠 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Includes:
- streamlit  
- pandas  
- plotly  
- yfinance  
- openai (or groq)  
- python-dotenv  
