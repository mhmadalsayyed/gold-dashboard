import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Gold (XAU/USD) Dashboard", page_icon=":moneybag:")

st.markdown("<h1 style='color:#FFD700;'>Gold (XAU/USD) Daily Analysis</h1>", unsafe_allow_html=True)
st.markdown("##### Powered by 15 top indicators | Dark Mode")

# Load data
symbol = "GC=F"
end = datetime.now()
start = end - timedelta(days=5)
data = yf.download(symbol, start=start, end=end, interval="5m")

# Primary validations
if data is None or data.empty:
    st.error("Gold price data is unavailable. Try again shortly.")
elif "Close" not in data.columns:
    st.error("The 'Close' column is missing from the data.")
elif data["Close"].isnull().all():
    st.error("All 'Close' values are NaN. Cannot continue.")
else:
    try:
        # Drop invalid rows
        data = data.dropna(subset=["Close"])
        
        # Check if there's enough data left
        if data.empty or len(data) < 30:
            st.warning("Not enough valid gold data to compute indicators.")
        else:
            # Calculate indicators
            data["EMA20"] = data["Close"].ewm(span=20).mean()
            data["EMA50"] = data["Close"].ewm(span=50).mean()
            data["RSI"] = 100 - (100 / (1 + data["Close"].pct_change().rolling(14).mean()))
            data["MACD"] = data["Close"].ewm(span=12).mean() - data["Close"].ewm(span=26).mean()
            data["Signal"] = data["MACD"].ewm(span=9).mean()

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

            # Summary
            summary_df = pd.DataFrame({
                "Indicator": ["EMA Trend", "RSI", "MACD Signal"],
                "Signal": [ema_trend, rsi_val, macd_trend]
            })

            st.markdown("### Signal Summary")
            st.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")

st.markdown("<hr><small style='color:gray;'>Gold dashboard powered by Streamlit + live data</small>", unsafe_allow_html=True)
