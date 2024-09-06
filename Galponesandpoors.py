import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

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

# Target normalization for 5 September 2024
target_value_5sep2024 = 10292.99
target_date = datetime(2024, 9, 5)

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

# Function to generate a DataFrame of normalized weighted averages from selected date to present
def get_normalized_weighted_averages(start_date):
    current_date = datetime.today()
    date_range = pd.date_range(start=start_date, end=current_date, freq='B')  # 'B' for business days
    
    data = []
    
    for date in date_range:
        weighted_avg = get_weighted_average(date)
        if weighted_avg is not None:
            data.append({'Date': date, 'Weighted Average': weighted_avg})
    
    df = pd.DataFrame(data)
    
    # Fetch weighted average for 5 September 2024 and normalize values
    weighted_avg_5sep2024 = get_weighted_average(target_date)
    if weighted_avg_5sep2024:
        normalization_factor = target_value_5sep2024 / weighted_avg_5sep2024
        df['Normalized Weighted Average'] = df['Weighted Average'] * normalization_factor
    else:
        st.write(f"Unable to fetch data for the target normalization date: {target_date}")
    
    return df

# Streamlit app
st.title("Normalized Weighted Average Close Prices with Trendline")

# Date selection
selected_date = st.date_input("Select a date", value=datetime.today())

# Button to fetch data
if st.button('Enter'):
    st.write(f"Fetching data from {selected_date} to present...")
    
    # Get normalized weighted averages for the selected date to today
    df_normalized = get_normalized_weighted_averages(selected_date)
    
    if not df_normalized.empty:
        # Plot the normalized weighted averages over time
        fig = px.line(df_normalized, x='Date', y='Normalized Weighted Average', 
                      title='Normalized Weighted Average Over Time',
                      labels={'Normalized Weighted Average': 'Weighted Average (Normalized)'})
        
        st.plotly_chart(fig)
    else:
        st.write("Unable to fetch data or no data available for the selected period.")
