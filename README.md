# RedditFiDashboard 📈🧠

A live dashboard that merges Reddit sentiment from finance-related subreddits with real-time financial data to uncover correlations between public sentiment and market movement.

---

## 🔧 Features
- **Reddit Sentiment Analysis** via VADER
- **Live Financial Data** from `yfinance`
- **Streamlit Dashboard** for interactive exploration
- **Automated ETL** for both Reddit and financials
- **Clean project structure** (`scripts/`, `data/`, `dashboard/`)

---

## 📊 Subreddits Tracked
- r/stocks
- r/investing
- r/wallstreetbets
- r/cryptocurrency
- r/news
- r/worldnews
- r/Economics
- r/StockMarket

---

## 📈 Financial Assets Pulled
- S&P 500 (`^GSPC`)
- NASDAQ (`^IXIC`)
- Dow Jones (`^DJI`)
- Bitcoin (`BTC-USD`)
- Ethereum (`ETH-USD`)
- Gold (`GC=F`)
- Oil (`CL=F`)

---

## 🏁 Getting Started

1. Clone the repo
2. Create `.env` file with Reddit API keys
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
