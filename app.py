import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Gold (XAU/USD) Dashboard", page_icon=":moneybag:")

st.title("Gold (XAU/USD) Daily Analysis")
st.subheader("Powered by top indicators | Dark Mode")

# Load data
symbol = "GC=F"
data = yf.download(symbol, period="7d", interval="1h")

# Show basic data structure
st.write("### Raw data preview")
st.dataframe(data.tail())

# Defensive validation
if data is None or data.empty:
    st.error("No data returned. Try again later.")
elif "Close" not in data.columns:
    st.error("Missing 'Close' column in data.")
elif data["Close"].dropna().empty:
    st.error("All 'Close' prices are missing. Cannot proceed.")
else:
    try:
        # Clean data
        data = data.dropna(subset=["Close"])
        if data.empty or len(data) < 30:
            st.warning("Not enough valid candles for indicator calculation.")
        else:
            # Indicators
            close = data["Close"].copy()
            data["EMA20"] = close.ewm(span=20, adjust=False).mean()
            data["EMA50"] = close.ewm(span=50, adjust=False).mean()
            data["RSI"] = 100 - (100 / (1 + close.pct_change().rolling(14).mean()))
            data["MACD"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
            data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

            latest = data.iloc[-1]
            rsi_val = round(latest["RSI"], 2) if pd.notna(latest["RSI"]) else "N/A"
            macd_trend = "Buy" if pd.notna(latest["MACD"]) and pd.notna(latest["Signal"]) and latest["MACD"] > latest["Signal"] else "Sell"
            ema_trend = "Bullish" if latest["EMA20"] > latest["EMA50"] else "Bearish"

            # Plot
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                         low=data['Low'], close=close, name="Price"))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], name="EMA 20"))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], name="EMA 50"))
            fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=500)

            st.plotly_chart(fig, use_container_width=True)

            # Signals
            st.markdown("### Signal Summary")
            st.dataframe(pd.DataFrame({
                "Indicator": ["EMA Trend", "RSI", "MACD Signal"],
                "Signal": [ema_trend, rsi_val, macd_trend]
            }))

    except Exception as e:
        st.error(f"Error during indicator calculation: {e}")
