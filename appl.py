# app.py

import streamlit as st
import yfinance as yf
import feedparser
from newspaper import Article
from transformers import pipeline
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
st.set_page_config(page_title="SentiStock", layout="wide")
# ✅ App title (after set_page_config)
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📊 SentiStock</h1>", unsafe_allow_html=True)
st.markdown("---")




# Load HuggingFace pipelines
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
sentiment_analyzer = pipeline("sentiment-analysis")

# Input: stock tickers
tickers = st.text_input("Enter stock tickers (comma-separated)", "AAPL, TSLA, MSFT").split(',')

# Utility to get news
def get_news_summary_and_sentiment(ticker):
    rss_url = f"https://news.google.com/rss/search?q={ticker.strip()}+stock"
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return "No news found", "NEUTRAL"
    url = feed.entries[0].link
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        if len(text.split()) < 50:
            return f"Title only: {feed.entries[0].title}", "NEUTRAL"
        summary = summarizer(text[:1000], max_length=120, min_length=30, do_sample=False)[0]['summary_text']
        sentiment = sentiment_analyzer(text[:512])[0]['label']
        return summary, sentiment
    except:
        return "Failed to fetch article", "NEUTRAL"

# Loop through tickers
for ticker in tickers:
    ticker = ticker.strip().upper()
    st.subheader(f"📈 {ticker}")

    # News & Sentiment
    with st.spinner("Fetching news..."):
        summary, sentiment = get_news_summary_and_sentiment(ticker)

    

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")
        st.success(summary)
    with col2:
        st.metric("🧠 Sentiment", sentiment)

    # Price & Chart
    stock = yf.Ticker(ticker)
    hist = stock.history(period="7d")

    if not hist.empty:
        st.line_chart(hist['Close'])
        latest_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
        st.metric("💲 Latest Close", f"${latest_price:.2f}", delta=f"{latest_price - prev_close:.2f}")
    else:
        st.warning("⚠️ Couldn't fetch price data.")

    st.divider()
