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

import streamlit as st
import pandas as pd
import os
import sys

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from portfolio_manager import PortfolioManager

st.set_page_config(page_title="Trading Agent Dashboard", layout="wide")

st.title("🤖 Sentiment-Augmented Momentum Trader (Tradier Sandbox)")

try:
    pm = PortfolioManager()
    
    # Key Metrics
    with st.spinner('Fetching Data from Tradier...'):
        cash = pm.get_cash()
        equity = pm.get_equity()
        positions = pm.get_positions()
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Equity", f"${equity:,.2f}")
    col2.metric("Cash Available", f"${cash:,.2f}")
    col3.metric("Active Positions", len(positions))
    
    st.divider()
    
    # Active Positions
    st.subheader("Active Positions")
    if positions:
        # Convert dict to list for dataframe
        pos_list = []
        for ticker, data in positions.items():
            data['ticker'] = ticker
            pos_list.append(data)
            
        df_pos = pd.DataFrame(pos_list)
        # Reorder columns
        cols = ['ticker', 'quantity', 'cost_basis']
        df_pos = df_pos[cols]
        st.dataframe(df_pos, use_container_width=True)
    else:
        st.info("No active positions.")
        
    # Note: Trade History is harder to get via simple endpoint efficiently without paginating events.
    # For now, we omit history or we could fetch orders endpoint.
    
except Exception as e:
    st.error(f"Error connecting to Tradier: {e}")

