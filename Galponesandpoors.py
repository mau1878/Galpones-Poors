import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Define the tickers and their corresponding weights
tickers = {
    'BPAT.BA': 0.12725233385763700, 'MOLA.BA': 0.07128745984222320, 'CTIO.BA': 0.05470948816674060, 
    'MOLI.BA': 0.06165477368929270, 'CGPA2.BA': 0.05071483241529670, 'BHIP.BA': 0.09742755901447200, 
    'PATA.BA': 0.03251201210958140, 'LEDE.BA': 0.05362713511839330, 'INVJ.BA': 0.02923343586598080, 
    'METR.BA': 0.06924419207715150, 'CECO2.BA': 0.05949122450095040, 'DGCU2.BA': 0.06911527847786080, 
    'GBAN.BA': 0.01354670235572050, 'OEST.BA': 0.01316236312954340, 'AUSO.BA': 0.03384100739085280, 
    'HAVA.BA': 0.02640758913660020, 'MORI.BA': 0.02571639166054310, 'CADO.BA': 0.00753227379557035, 
    'SAMI.BA': 0.03427269544463540, 'INTR.BA': 0.00375850282091302, 'SEMI.BA': 0.01721404747879000, 
    'AGRO.BA': 0.04822870165125130
}

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
    for ticker, weight in tickers.items():
        close_price = fetch_close_price(ticker, date)
        if close_price:
            total += close_price * weight
            components[ticker] = close_price
        else:
            st.write(f"No hay datos disponibles para {ticker} en {date}")
    return total, components

# Streamlit app
st.title("Galpones & Poor's - Data histórica")

# Date selection
selected_date = st.date_input("Selecciona una fecha", value=datetime.today())
previous_date = selected_date - timedelta(days=1)

# Button to fetch data
if st.button('Ingresar'):
    st.write(f"Obteniendo datos para {selected_date} y {previous_date}...")

    # Fetch the weighted average for 5 September 2024
    weighted_avg_5sep2024, _ = get_weighted_average_and_components(target_date)
    
    if weighted_avg_5sep2024:
        # Calculate normalization factor for 5 September 2024
        normalization_factor = target_value_5sep2024 / weighted_avg_5sep2024
        st.write(f"Factor de normalización basado en el 5 de septiembre de 2024: {normalization_factor:.4f}")
        
        # Fetch the weighted averages and components for the selected and previous dates
        weighted_avg_selected, components_selected = get_weighted_average_and_components(selected_date)
        weighted_avg_previous, components_previous = get_weighted_average_and_components(previous_date)
        
        if weighted_avg_selected and weighted_avg_previous:
            # Apply normalization factor
            normalized_selected = weighted_avg_selected * normalization_factor
            normalized_previous = weighted_avg_previous * normalization_factor
            
            st.write(f"Promedio ponderado normalizado el {selected_date}: {normalized_selected:.2f}")
            st.write(f"Promedio ponderado normalizado el {previous_date}: {normalized_previous:.2f}")
            
            # Calculate percentage variation
            percentage_variation = ((normalized_selected - normalized_previous) / normalized_previous) * 100
            st.write(f"Variación porcentual entre {selected_date} y {previous_date}: {percentage_variation:.2f}%")
            
            # Calculate percentage variation for each component
            variations = []
            for ticker, price_selected in components_selected.items():
                price_previous = components_previous.get(ticker)
                if price_previous:
                    change = ((price_selected - price_previous) / price_previous) * 100
                    variations.append({
                        'Ticker': ticker,
                        'Peso': tickers[ticker] * 100,  # Convert weight to percentage
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
            st.write("No se puede calcular la variación porcentual debido a la falta de datos.")
    else:
        st.write(f"No se pueden obtener datos para la fecha de normalización objetivo: {target_date}")
