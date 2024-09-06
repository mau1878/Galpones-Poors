import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Define the tickers and their corresponding weights
tickers = {
    'BPAT.BA': 12.73, 'MOLA.BA': 7.13, 'CTIO.BA': 5.47, 'MOLI.BA': 6.17, 
    'CGPA2.BA': 5.07, 'BHIP.BA': 9.74, 'PATA.BA': 3.25, 'LEDE.BA': 5.36, 
    'INVJ.BA': 2.92, 'METR.BA': 6.92, 'CECO2.BA': 5.95, 'DGCU2.BA': 6.91, 
    'GBAN.BA': 1.35, 'OEST.BA': 1.32, 'AUSO.BA': 3.38, 'HAVA.BA': 2.64, 
    'MORI.BA': 2.57, 'CADO.BA': 0.75, 'SAMI.BA': 3.43, 'INTR.BA': 0.38, 
    'SEMI.BA': 1.72, 'AGRO.BA': 4.82
}

# Normalize weights to sum up to 100%
weights_sum = sum(tickers.values())
weights = {k: v / weights_sum for k, v in tickers.items()}

# Function to fetch the close price for a given ticker and date (or previous available date)
def fetch_close_price(ticker, date):
    df = yf.download(ticker, start=date - timedelta(days=5), end=date + timedelta(days=1))['Close']
    if df.empty:
        return None
    return df.dropna().iloc[-1]

# Function to get weighted average of close prices for a specific date
def get_weighted_average(date):
    total = 0
    for ticker, weight in weights.items():
        close_price = fetch_close_price(ticker, date)
        if close_price:
            total += close_price * weight
        else:
            st.write(f"No data available for {ticker} on {date}")
    return total

# Streamlit app
st.title("Weighted Average Close Prices")

# Date selection
selected_date = st.date_input("Select a date", value=datetime.today())
previous_date = selected_date - timedelta(days=1)

# Button to fetch data
if st.button('Enter'):
    st.write(f"Fetching data for {selected_date} and {previous_date}...")

    # Fetch the weighted averages for the selected and previous dates
    weighted_avg_selected = get_weighted_average(selected_date)
    weighted_avg_previous = get_weighted_average(previous_date)

    if weighted_avg_selected and weighted_avg_previous:
        st.write(f"Weighted average on {selected_date}: {weighted_avg_selected:.2f}")
        st.write(f"Weighted average on {previous_date}: {weighted_avg_previous:.2f}")

        # Calculate percentage variation
        percentage_variation = ((weighted_avg_selected - weighted_avg_previous) / weighted_avg_previous) * 100
        st.write(f"Percentage variation between {selected_date} and {previous_date}: {percentage_variation:.2f}%")
    else:
        st.write("Unable to calculate percentage variation due to missing data.")
