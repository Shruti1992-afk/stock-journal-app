import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Stock Journal", layout="wide")

# Initialize Session State (This holds data while your browser tab is open)
if 'journal' not in st.session_state:
    st.session_state.journal = pd.DataFrame(columns=[
        "Date", "Stock", "Entry", "SL", "Target", "Shares", "Investment", "Checks"
    ])

st.title("📈 Stock Analysis & Journal")
st.info("Note: This app is for 4 users. Since it's on the cloud, please download your journal before closing the tab to save your data permanently.")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("Global Settings")
total_inv = st.sidebar.number_input("Total Investment (Capital)", value=100000, step=5000)

# --- INPUT SECTION ---
col1, col2, col3 = st.columns(3)

with col1:
    stock_name = st.text_input("Stock Name", "RELIANCE")
    entry_price = st.number_input("Entry Price", min_value=1.0, value=2500.0)

with col2:
    trade_date = st.date_input("Trade Date", datetime.now())
    stop_loss_in = st.number_input("Original Stop Loss", min_value=0.0, value=2450.0)

with col3:
    st.write("**Manual Checkpoints**")
    c1 = st.checkbox("Nifty 50: Uptrend & > 50 SMA")
    c2 = st.checkbox("Sensex: Uptrend & > 50 SMA")
    c3 = st.checkbox("Industry: Uptrend & > 50 SMA")
    c4 = st.checkbox("Stock: Uptrend & > 50 SMA")

# --- CALCULATIONS ---
all_checks = all([c1, c2, c3, c4])
risk_per_trade = 0.01 * total_inv
gap = entry_price - stop_loss_in

if gap > 0:
    # Logic: Round( (1% of total inv) / (Entry - SL) )
    num_shares = round(risk_per_trade / gap)
    invested_amt = num_shares * entry_price
    target_price = entry_price * 2
    stop_loss_1 = stop_loss_in * 0.98  # 2% lower than entered SL
else:
    num_shares = invested_amt = target_price = stop_loss_1 = 0

# --- OUTPUT DISPLAY ---
st.divider()
if all_checks:
    st.success("✅ All 50-Day SMA Checkpoints Passed!")
else:
    st.warning("⚠️ One or more SMA Checkpoints are not met.")

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("No. of Shares", num_shares)
res_col1.metric("Investment Amt", f"₹{invested_amt:,.2f}")

res_col2.metric("Target (2x)", f"₹{target_price:,.2f}")
res_col2.metric("Stop Loss 1 (-2%)", f"₹{stop_loss_1:,.2f}")

res_col3.write(f"**Risk Summary**")
res_col3.write(f"Risking: ₹{risk_per_trade:,.2f}")
res_col3.write(f"Price Gap: ₹{gap:,.2f}")

# --- JOURNALING SYSTEM ---
st.divider()
if st.button("Add Trade to Journal"):
    new_entry = {
        "Date": trade_date.strftime("%Y-%m-%d"),
        "Stock": stock_name,
        "Entry": entry_price,
        "SL": stop_loss_in,
        "Target": target_price,
        "Shares": num_shares,
        "Investment": invested_amt,
        "Checks": "Passed" if all_checks else "Failed"
    }
    st.session_state.journal = pd.concat([st.session_state.journal, pd.DataFrame([new_entry])], ignore_index=True)
    st.balloons()

# Display the Table
st.subheader("Current Session Journal")
st.dataframe(st.session_state.journal, use_container_width=True)

# Download Button
if not st.session_state.journal.empty:
    csv = st.session_state.journal.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Journal as Excel (CSV)",
        data=csv,
        file_name=f"trade_journal_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )