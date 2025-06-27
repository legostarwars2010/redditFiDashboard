import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.summary_generator import summarize_with_groq

# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    merged_df = pd.read_csv("data/merged_data.csv", parse_dates=["Date"])
    text_df = pd.read_csv("data/reddit_text.csv", parse_dates=["created_utc"])
    merged_df["Date"] = pd.to_datetime(merged_df["Date"]).dt.tz_localize(None)
    text_df["created_utc"] = pd.to_datetime(text_df["created_utc"]).dt.tz_localize(None)
    return merged_df, text_df

merged_df, text_df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
assets = st.sidebar.multiselect("Select Assets", options=merged_df["asset"].unique(), default=merged_df["asset"].unique())
subreddits = st.sidebar.multiselect("Select Subreddits", options=merged_df["subreddit"].unique(), default=merged_df["subreddit"].unique())
date_range = st.sidebar.date_input("Select Date Range", [])

# Filtered data
if date_range and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0]).tz_localize(None)
    end_date = pd.to_datetime(date_range[1]).tz_localize(None)
    df = merged_df[
        (merged_df["asset"].isin(assets)) &
        (merged_df["subreddit"].isin(subreddits)) &
        (merged_df["Date"] >= start_date) & (merged_df["Date"] <= end_date)
    ]
    text_filtered = text_df[
        (text_df["subreddit"].isin(subreddits)) &
        (text_df["created_utc"] >= start_date) & (text_df["created_utc"] <= end_date)
    ]
else:
    df = merged_df[0:0]
    text_filtered = text_df[0:0]

# Header
st.title("📉 Reddit Sentiment vs. Market Dashboard")
st.write("Compare daily sentiment across subreddits against asset price changes.")

if df.empty:
    st.warning("No sentiment data available for selected subreddit and date range.")
else:
    # 1. Dynamic plain-English summary headline
    if len(assets) == 1 and len(subreddits) == 1:
        avg_sentiment = df["avg_compound"].mean()
        sentiment_trend = "turned bearish" if avg_sentiment < -0.05 else "turned bullish" if avg_sentiment > 0.05 else "remained neutral"
        st.markdown(f"### 📢 Summary: {assets[0]} prices vs sentiment in r/{subreddits[0]} — sentiment {sentiment_trend}.")

    # 2. Summary from Groq
    st.subheader("📝 Summary of Sentiment and News")
    if not text_filtered.empty:
        grouped = text_filtered.groupby("subreddit")
        for name, group in grouped:
            posts_df = group.sort_values("created_utc").copy()
            if "text" not in posts_df.columns:
                if "title" in posts_df.columns:
                    posts_df["text"] = posts_df["title"]
                else:
                    st.warning(f"No usable text found for r/{name}.")
                    continue
            posts_df.rename(columns={"title": "text"}, inplace=True)
            summary = summarize_with_groq(posts_df, name)
            st.markdown(f"**Summary for r/{name}:**")
            st.write(summary)
    else:
        st.info("No post data to summarize in this date range.")

    # 3. Asset Price Over Time (Standalone)
    st.subheader("📈 Asset Price Over Time")
    for asset in assets:
        asset_data = df[df["asset"] == asset]
        if not asset_data.empty:
            fig_price = px.line(
                asset_data,
                x="Date",
                y="Close",
                title=f"{asset} Closing Price Over Time",
                labels={"Close": "Price", "Date": "Date"},
                markers=True
            )
            st.plotly_chart(fig_price, use_container_width=True)

    # 4. Sentiment Over Time (Line)
    st.subheader("📊 Sentiment Over Time")
    sentiment_over_time = df.groupby(["Date", "subreddit"])["avg_compound"].mean().reset_index()
    fig2 = px.line(sentiment_over_time, x="Date", y="avg_compound", color="subreddit",
                   labels={"avg_compound": "Sentiment"}, markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# 5. Emotion Breakdown + Volume Overlay
st.subheader("🧪 Sentiment Emotion Mix and Volume")

# Ensure correct types
expected_cols = ["avg_pos", "avg_neg", "avg_neu", "Volume"]
for col in expected_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Check if all required columns exist
missing_cols = [col for col in expected_cols if col not in df.columns]
if missing_cols:
    st.warning(f"Missing columns for emotion/volume analysis: {', '.join(missing_cols)}")
else:
    sentiment_components = df.groupby("Date").agg({
        "avg_pos": "mean",
        "avg_neg": "mean",
        "avg_neu": "mean",
        "Volume": "mean"
    }).reset_index()

    fig_emotion = go.Figure()
    fig_emotion.add_trace(go.Scatter(x=sentiment_components["Date"], y=sentiment_components["avg_pos"], name="Positive", stackgroup="one"))
    fig_emotion.add_trace(go.Scatter(x=sentiment_components["Date"], y=sentiment_components["avg_neu"], name="Neutral", stackgroup="one"))
    fig_emotion.add_trace(go.Scatter(x=sentiment_components["Date"], y=sentiment_components["avg_neg"], name="Negative", stackgroup="one"))
    fig_emotion.add_trace(go.Bar(x=sentiment_components["Date"], y=sentiment_components["Volume"], name="Volume", marker=dict(color="rgba(200,200,200,0.3)"), yaxis="y2"))
    fig_emotion.update_layout(
        yaxis=dict(title="Sentiment Proportion"),
        yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
        title="Sentiment Emotion Breakdown and Activity Volume"
    )
    st.plotly_chart(fig_emotion, use_container_width=True)

# 6. Sentiment vs Price (Dual Axis)
st.subheader("🪙 Sentiment vs. Asset Price Over Time")
for subreddit in subreddits:
    for asset in assets:
        data = df[(df["subreddit"] == subreddit) & (df["asset"] == asset)]
        if not data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data["Date"], y=data["avg_compound"], name=f"Sentiment ({subreddit})",
                                     yaxis="y1", mode="lines+markers"))
            fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name=f"Close Price ({asset})",
                                     yaxis="y2", mode="lines+markers"))
            fig.update_layout(
                title=f"{subreddit} Sentiment vs. {asset} Close Price",
                xaxis=dict(domain=[0.1, 0.9]),
                yaxis=dict(title="Sentiment", side="left"),
                yaxis2=dict(title="Price", overlaying="y", side="right")
            )
            st.plotly_chart(fig, use_container_width=True)

# 7. Sentiment vs. % Change (Scatter)
st.subheader("📌 Sentiment vs. % Price Change")
st.write("Correlation between sentiment and asset price movement")
fig1 = px.scatter(df, x="avg_compound", y="pct_change", color="subreddit",
                  labels={"avg_compound": "Avg Sentiment", "pct_change": "% Price Change"})
st.plotly_chart(fig1, use_container_width=True)
