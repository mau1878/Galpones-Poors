import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Define the tickers and their corresponding weights
market_cap_weights = {
    'BPAT.BA': 0.42108071666, 'MOLA.BA': 0.02879635058, 'CTIO.BA': 0.24049322400,
    'MOLI.BA': 0.11816957075, 'CGPA2.BA': 0.19553386318, 'BHIP.BA': 0.88003878145,
    'PATA.BA': 0.29335277401, 'LEDE.BA': 0.25797878759, 'INVJ.BA': 0.35974147872,
    'METR.BA': 0.16362380176, 'CECO2.BA': 0.41184682695, 'DGCU2.BA': 0.11871927857,
    'GBAN.BA': 0.09358895622, 'OEST.BA': 0.09386887625, 'AUSO.BA': 0.01787519574,
    'HAVA.BA': 0.00751764759, 'MORI.BA': 0.16537899083, 'CADO.BA': 0.07228444477,
    'SAMI.BA': 0.04174240508, 'INTR.BA': 0.07103085603, 'SEMI.BA': 0.11279377500,
    'AGRO.BA': 0.05859209470
}

volume_weights = {
    'BPAT.BA': 0.04935304991, 'MOLA.BA': 0.007037297678, 'CTIO.BA': 0.04209710744,
    'MOLI.BA': 0.05673758865, 'CGPA2.BA': 0.0756684492, 'BHIP.BA': 1.543532338,
    'PATA.BA': 0.02077294686, 'LEDE.BA': 0.2035283993, 'INVJ.BA': 0.2417695473,
    'METR.BA': 0.5253731343, 'CECO2.BA': 1.222527473, 'DGCU2.BA': 0.492920354,
    'GBAN.BA': 0.02170212766, 'OEST.BA': 0.03269230769, 'AUSO.BA': 0.09754433834,
    'HAVA.BA': 0.03701829834, 'MORI.BA': 0.8199233716, 'CADO.BA': 0.06617647059,
    'SAMI.BA': 0.3888190955, 'INTR.BA': 0.04461538462, 'SEMI.BA': 1.364806867,
    'AGRO.BA': 8.538324421
}

# Function to find the closest previous trading day with available data
def get_closest_trading_day(ticker, date):
    # Download 7 days of data around the selected date to handle weekends/holidays
    start_date = date - timedelta(days=7)
    end_date = date + timedelta(days=1)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df.empty:
        return None, None  # No data available in that range

    # Check for the closest available previous trading day
    valid_days = df.index[df.index <= pd.Timestamp(date)]
    if len(valid_days) > 0:
        closest_date = valid_days[-1]
        return closest_date, df.loc[closest_date]['Close']
    else:
        return None, None

# Function to fetch close price for a given ticker and date
def fetch_close_price(ticker, date):
    closest_date, price = get_closest_trading_day(ticker, date)
    if closest_date:
        return closest_date, price
    return None, None

# Function to calculate weighted sums (for both market cap and volume weights)
def calculate_weighted_sums(date):
    market_cap_sum = 0
    volume_sum = 0
    components = {}
    
    for ticker in market_cap_weights.keys():
        closest_date, close_price = fetch_close_price(ticker, date)
        if close_price:
            market_cap_sum += close_price * market_cap_weights[ticker]
            volume_sum += close_price * volume_weights[ticker]
            components[ticker] = close_price
        else:
            st.write(f"No hay datos disponibles para {ticker} cerca de {date}")
    
    return market_cap_sum, volume_sum, components

# Streamlit app
st.title("Galpones & Poor's - Data histórica con pesos de capitalización y volumen")

# Date selection
selected_date = st.date_input("Selecciona una fecha", value=datetime.today())
previous_date = selected_date - timedelta(days=1)

# Find closest valid trading days
selected_date_closest, _ = fetch_close_price('BPAT.BA', selected_date)  # Use any ticker here
previous_date_closest, _ = fetch_close_price('BPAT.BA', previous_date)  # Use any ticker here

# If the selected date is not a trading day, use the closest trading day
if selected_date_closest:
    final_selected_date = selected_date_closest
else:
    final_selected_date = previous_date

# If the previous date is not a trading day, use the closest trading day before it
if previous_date_closest:
    final_previous_date = previous_date_closest
else:
    final_previous_date = final_selected_date - timedelta(days=1)

# Button to fetch data
if st.button('Ingresar'):
    st.write(f"Obteniendo datos para {final_selected_date} y {final_previous_date}...")

    # Fetch weighted sums for the selected and previous dates
    market_cap_selected, volume_selected, components_selected = calculate_weighted_sums(final_selected_date)
    market_cap_previous, volume_previous, components_previous = calculate_weighted_sums(final_previous_date)
    
    if market_cap_selected and volume_selected and market_cap_previous and volume_previous:
        # Calculate total sums for selected and previous dates
        total_selected = market_cap_selected + volume_selected
        total_previous = market_cap_previous + volume_previous
        
        st.write(f"Suma total el {final_selected_date}: {total_selected:.2f}")
        st.write(f"Suma total el {final_previous_date}: {total_previous:.2f}")
        
        # Calculate percentage variation
        percentage_variation = ((total_selected - total_previous) / total_previous) * 100
        st.write(f"Variación porcentual entre {final_selected_date} y {final_previous_date}: {percentage_variation:.2f}%")
        
        # Calculate percentage variation for each component
        variations = []
        for ticker, price_selected in components_selected.items():
            price_previous = components_previous.get(ticker)
            if price_previous:
                change = ((price_selected - price_previous) / price_previous) * 100
                variations.append({
                    'Ticker': ticker,
                    'Peso': market_cap_weights[ticker] * 100,  # Convert weight to percentage
                    'Variación': change
                })
        
        # Create a DataFrame for the treemap
        df_variations = pd.DataFrame(variations)
        
        # Determine color scale based on value distribution
        max_variation = df_variations['Variación'].max()
        min_variation = df_variations['Variación'].min()
        
        if max_variation > 0:
            if min_variation < 0:
                color_scale = [(0, 'red'), (0.5, 'white'), (1, 'green')]
            else:
                color_scale = [(0, 'lightgreen'), (1, 'darkgreen')]
        else:
            color_scale = [(0, 'darkred'), (1, 'lightcoral')]
        
        # Create the treemap with Plotly Express
        fig = px.treemap(
            df_variations, 
            path=['Ticker'], 
            values='Peso', 
            color='Variación',
            color_continuous_scale=color_scale,
            title="Variaciones porcentuales de los componentes (Tamaño basado en el peso)",
            hover_data={
                'Peso': ':.2f',   # Format weight as a percentage
                'Variación': ':.2f'  # Format variation as a percentage
            }
        )
        
        # Update traces to adjust font sizes
        fig.update_traces(
            textfont=dict(size=15),  # Increase font size for ticker names
            hovertemplate="<b>%{label}</b><br>Peso: %{customdata[0]:.2f}%<br>Variación: %{customdata[1]:.2f}%<extra></extra>"  # Format hover text
        )
        
        # Show the treemap
        st.plotly_chart(fig)
    else:
        st.write("No se puede calcular la variación, datos faltantes.")
