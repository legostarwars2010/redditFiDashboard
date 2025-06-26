import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load merged data
@st.cache_data

def load_data():
    return pd.read_csv("data/merged_data.csv", parse_dates=["Date"])

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
assets = st.sidebar.multiselect("Select Assets", options=df["asset"].dropna().unique(), default=df["asset"].dropna().unique())
subs = st.sidebar.multiselect("Select Subreddits", options=df["subreddit"].dropna().unique(), default=df["subreddit"].dropna().unique())
date_range = st.sidebar.date_input("Select Date Range", value=[df["Date"].min(), df["Date"].max()])

# Apply filters
filtered = df[(df["asset"].isin(assets)) &
              (df["subreddit"].isin(subs)) &
              (df["Date"] >= pd.to_datetime(date_range[0])) &
              (df["Date"] <= pd.to_datetime(date_range[1]))]

st.title("📈 Reddit Sentiment vs. Market Dashboard")
st.markdown("Compare daily sentiment across subreddits against asset price changes.")

# --- Chart 1: Sentiment vs. % Change ---
st.subheader("🧠 Sentiment vs. % Change")
if not filtered.empty:
    fig1 = px.scatter(
    filtered,
    x="avg_compound",
    y="pct_change",
    color="subreddit",
    title="Correlation between sentiment and asset price movement"
    # Remove trendline="ols"
)

    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No data available for selected filters.")

# --- Chart 2: Sentiment Over Time ---
st.subheader("📊 Sentiment Over Time")
if not filtered.empty:
    fig2 = px.line(
        filtered,
        x="Date",
        y="avg_compound",
        color="subreddit",
        line_group="subreddit",
        markers=True,
        title="Sentiment Timeline"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Chart 3: Asset Price vs Sentiment (Dual Axis) ---
st.subheader("💹 Sentiment vs. Asset Price Over Time")
for asset in assets:
    for sub in subs:
        subset = filtered[(filtered["asset"] == asset) & (filtered["subreddit"] == sub)]
        if subset.empty:
            continue

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=subset["Date"], y=subset["avg_compound"], name=f"Sentiment ({sub})", yaxis="y1", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=subset["Date"], y=subset["Close"], name=f"Close Price ({asset})", yaxis="y2", mode="lines+markers"))

        fig.update_layout(
            title=f"{sub} Sentiment vs. {asset} Close Price",
            yaxis=dict(title="Sentiment", side="left"),
            yaxis2=dict(title="Price", overlaying="y", side="right"),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig, use_container_width=True)
