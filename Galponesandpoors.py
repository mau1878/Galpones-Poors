import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Define the tickers
tickers = [
    'BPAT.BA', 'MOLA.BA', 'CTIO.BA', 'MOLI.BA', 'CGPA2.BA', 'BHIP.BA', 
    'PATA.BA', 'LEDE.BA', 'INVJ.BA', 'METR.BA', 'CECO2.BA', 'DGCU2.BA', 
    'GBAN.BA', 'OEST.BA', 'AUSO.BA', 'HAVA.BA', 'MORI.BA', 'CADO.BA', 
    'SAMI.BA', 'INTR.BA', 'SEMI.BA', 'AGRO.BA'
]

# Define Market Cap Weights
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

# Define Volume Weights
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

# Function to fetch the close price for a given ticker and date (or previous available date)
def fetch_close_price(ticker, date):
    df = yf.download(ticker, start=date - timedelta(days=5), end=date + timedelta(days=1))['Close']
    if df.empty:
        return None
    return df.dropna().iloc[-1]

# Function to calculate weighted sum for a given date
def calculate_weighted_sum(date, weights):
    total_sum = 0
    for ticker, weight in weights.items():
        close_price = fetch_close_price(ticker, date)
        if close_price:
            total_sum += close_price * weight
        else:
            st.write(f"No hay datos disponibles para {ticker} en {date}")
    return total_sum

# Streamlit app
st.title("Galpones & Poor's - Data histórica")

# Date selection
selected_date = st.date_input("Selecciona una fecha", value=datetime.today())
previous_date = selected_date - timedelta(days=1)

# Button to fetch data
if st.button('Ingresar'):
    st.write(f"Obteniendo datos para {selected_date} y {previous_date}...")

    # Calculate the Market Cap and Volume weighted sums for the selected and previous dates
    market_cap_sum_selected = calculate_weighted_sum(selected_date, market_cap_weights)
    volume_sum_selected = calculate_weighted_sum(selected_date, volume_weights)
    market_cap_sum_previous = calculate_weighted_sum(previous_date, market_cap_weights)
    volume_sum_previous = calculate_weighted_sum(previous_date, volume_weights)
    
    if market_cap_sum_selected and volume_sum_selected and market_cap_sum_previous and volume_sum_previous:
        # Total sum for the selected date
        total_sum_selected = market_cap_sum_selected + volume_sum_selected
        total_sum_previous = market_cap_sum_previous + volume_sum_previous
        
        st.write(f"Suma total ponderada el {selected_date}: {total_sum_selected:.2f}")
        st.write(f"Suma total ponderada el {previous_date}: {total_sum_previous:.2f}")
        
        # Calculate percentage variation
        percentage_variation = ((total_sum_selected - total_sum_previous) / total_sum_previous) * 100
        st.write(f"Variación porcentual entre {selected_date} y {previous_date}: {percentage_variation:.2f}%")
    else:
        st.write("No se puede calcular la variación porcentual debido a la falta de datos.")
