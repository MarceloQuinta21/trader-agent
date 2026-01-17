import streamlit as st
import pandas as pd
import json
import os
import sys

# Add parent dir to path to import config/manager if needed, 
# but we mainly rely on portfolio.json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Trading Agent Dashboard", layout="wide")

st.title("🤖 Sentiment-Augmented Momentum Trader")

PORTFOLIO_FILE = "../portfolio.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return None

data = load_portfolio()

if not data:
    st.error("Portfolio file not found. Run the agent first!")
else:
    # Key Metrics
    cash = data.get("cash", 0)
    positions = data.get("positions", {})
    history = data.get("history", [])
    
    # Calculate approximate equity (using last known price from trades isn't accurate, 
    # ideally we fetch live prices calculation here or store 'last_equity' in json)
    # For now, show Cash + Cost Basis of Positions
    
    positions_value = sum([p["shares"] * p["avg_price"] for p in positions.values()])
    total_equity = cash + positions_value
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Equity (Est)", f"${total_equity:,.2f}")
    col2.metric("Cash Available", f"${cash:,.2f}")
    col3.metric("Active Positions", len(positions))
    
    st.divider()
    
    # Active Positions
    st.subheader("Active Positions")
    if positions:
        df_pos = pd.DataFrame.from_dict(positions, orient='index')
        df_pos = df_pos.reset_index().rename(columns={'index': 'Ticker'})
        # Add current value approximate column?
        st.dataframe(df_pos, use_container_width=True)
    else:
        st.info("No active positions.")
        
    st.divider()
    
    # Trade History
    st.subheader("Trade History")
    if history:
        df_hist = pd.DataFrame(history)
        df_hist['date'] = pd.to_datetime(df_hist['date'])
        df_hist = df_hist.sort_values(by='date', ascending=False)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No trades executed yet.")
