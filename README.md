# TSLA Trading Dashboard

This Streamlit dashboard visualizes TSLA stock data with support/resistance levels, candlestick charts, and directional trading signals. It also includes an AI-powered chatbot powered by Google's Gemini API for querying insights from the stock data.

## Features

- 📈 Candlestick chart of TSLA
- ✅ Support/resistance bands
- 🟢 LONG, 🔴 SHORT, 🟡 Neutral markers
- 🤖 Gemini AI chatbot (integrated)
- Streamlit app optimized for performance

## Gemini AI Note

Gemini AI integration is functional but currently unavailable due to quota limits on the free API tier. You can add a new API key with sufficient quota in `.streamlit/secrets.toml` like this:

```toml
GEMINI_API_KEY = "AIzaSyC9fk67k4-ErSFcq8DOlcyND0ytlkb_3xk"
