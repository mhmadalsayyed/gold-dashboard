import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Gold (XAU/USD) Dashboard", page_icon=":moneybag:")

st.markdown("<h1 style='color:#FFD700;'>Gold (XAU/USD) Daily Analysis</h1>", unsafe_allow_html=True)
st.markdown("##### Powered by top indicators | Dark Mode")

# Load data safely
symbol = "GC=F"
data = yf.download(symbol, period="7d", interval="1h")

# Validate data
if data.empty or "Close" not in data.columns or data["Close"].isnull().all():
    st.error("Live gold price data is unavailable. Please try again later.")
else:
    try:
        data = data.dropna(subset=["Close"])

        if len(data) < 50:
            st.warning("Not enough historical data to compute indicators.")
        else:
            # Indicators
            data["EMA20"] = data["Close"].ewm(span=20).mean()
            data["EMA50"] = data["Close"].ewm(span=50).mean()
            data["RSI"] = 100 - (100 / (1 + data["Close"].pct_change().rolling(14).mean()))
            data["MACD"] = data["Close"].ewm(span=12).mean() - data["Close"].ewm(span=26).mean()
            data["Signal"] = data["MACD"].ewm(span=9).mean()

            # Latest signal values
            latest = data.iloc[-1]
            rsi_val = round(latest["RSI"], 2) if pd.notna(latest["RSI"]) else "N/A"
            macd_trend = "Buy" if pd.notna(latest["MACD"]) and pd.notna(latest["Signal"]) and latest["MACD"] > latest["Signal"] else "Sell"
            ema_trend = "Bullish" if latest["EMA20"] > latest["EMA50"] else "Bearish"

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                         low=data['Low'], close=data['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], line=dict(color='cyan'), name="EMA 20"))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], line=dict(color='orange'), name="EMA 50"))
            fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=500)

            st.plotly_chart(fig, use_container_width=True)

            # Signal Summary
            summary_df = pd.DataFrame({
                "Indicator": ["EMA Trend", "RSI", "MACD Signal"],
                "Signal": [ema_trend, rsi_val, macd_trend]
            })

            st.markdown("### Signal Summary")
            st.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")

st.markdown("<hr><small style='color:gray;'>Live gold insights powered by Yahoo Finance & Streamlit</small>", unsafe_allow_html=True)
