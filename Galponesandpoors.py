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
def get_weighted_average_and_components(date):
    total = 0
    components = {}
    for ticker, weight in weights.items():
        close_price = fetch_close_price(ticker, date)
        if close_price:
            total += close_price * weight
            components[ticker] = close_price
        else:
            st.write(f"No data available for {ticker} on {date}")
    return total, components

# Streamlit app
st.title("Normalized Weighted Average Close Prices and Component Variations")

# Date selection
selected_date = st.date_input("Select a date", value=datetime.today())
previous_date = selected_date - timedelta(days=1)

# Button to fetch data
if st.button('Enter'):
    st.write(f"Fetching data for {selected_date} and {previous_date}...")

    # Fetch the weighted average for 5 September 2024
    weighted_avg_5sep2024, _ = get_weighted_average_and_components(target_date)
    
    if weighted_avg_5sep2024:
        # Calculate normalization factor for 5 September 2024
        normalization_factor = target_value_5sep2024 / weighted_avg_5sep2024
        st.write(f"Normalization factor based on 5 September 2024: {normalization_factor:.4f}")
        
        # Fetch the weighted averages and components for the selected and previous dates
        weighted_avg_selected, components_selected = get_weighted_average_and_components(selected_date)
        weighted_avg_previous, components_previous = get_weighted_average_and_components(previous_date)
        
        if weighted_avg_selected and weighted_avg_previous:
            # Apply normalization factor
            normalized_selected = weighted_avg_selected * normalization_factor
            normalized_previous = weighted_avg_previous * normalization_factor
            
            st.write(f"Normalized weighted average on {selected_date}: {normalized_selected:.2f}")
            st.write(f"Normalized weighted average on {previous_date}: {normalized_previous:.2f}")
            
            # Calculate percentage variation
            percentage_variation = ((normalized_selected - normalized_previous) / normalized_previous) * 100
            st.write(f"Percentage variation between {selected_date} and {previous_date}: {percentage_variation:.2f}%")
            
            # Calculate percentage variation for each component
            variations = []
            for ticker, price_selected in components_selected.items():
                price_previous = components_previous.get(ticker)
                if price_previous:
                    change = ((price_selected - price_previous) / price_previous) * 100
                    variations.append({
                        'Ticker': ticker,
                        'Weight': weights[ticker],
                        'Variation': change
                    })
            
            # Create a DataFrame for the treemap
            df_variations = pd.DataFrame(variations)
            
            # Create the treemap with Plotly Express
            fig = px.treemap(
                df_variations, 
                path=['Ticker'], 
                values='Weight', 
                color='Variation',
                color_continuous_scale='RdYlGn',
                title="Component Percentage Variations (Size Based on Weight)",
                hover_data={'Weight': True, 'Variation': True}
            )
            
            # Show the treemap
            st.plotly_chart(fig)
        else:
            st.write("Unable to calculate percentage variation due to missing data.")
    else:
        st.write(f"Unable to fetch data for the target normalization date: {target_date}")
