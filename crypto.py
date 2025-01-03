import requests
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide")

@st.cache_data
def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 429:
        st.error("Rate limit exceeded. Please try again later.")
        return pd.DataFrame()
    
    if response.status_code == 200:
        data = response.json()
        crypto_data = []
        for coin in data:
            crypto_data.append({
                "Name": coin.get("name", "N/A"),
                "Symbol": coin.get("symbol", "N/A").upper(),
                "Price (USD)": coin.get("current_price", 0),
                "Market Cap": coin.get("market_cap", 0),
                "24h Volume": coin.get("total_volume", 0),
            })
        return pd.DataFrame(crypto_data)
    else:
        st.error(f"API Error: {response.status_code} - {response.text}")
        return pd.DataFrame()

if "crypto_df" not in st.session_state:
    st.session_state["crypto_df"] = fetch_crypto_data()

crypto_df = st.session_state["crypto_df"]

st.title("📊 Cryptocurrency Dashboard")

st.sidebar.header("Dashboard Settings")
selected_cryptos = st.sidebar.multiselect(
    "Select Cryptocurrencies", 
    options=crypto_df["Name"] if not crypto_df.empty else [],
    default=crypto_df["Name"][:5] if not crypto_df.empty else []
)

data_type = st.sidebar.selectbox(
    "Select Data Type", 
    ["Price (USD)", "Market Cap", "24h Volume"]
)

chart_type = st.sidebar.radio(
    "Select Chart Type", 
    ["Bar Chart", "Line Chart", "Pie Chart"]
)

refresh_button = st.sidebar.button("Refresh Data")

if refresh_button:
    st.session_state["crypto_df"] = fetch_crypto_data()
    crypto_df = st.session_state["crypto_df"]

filtered_data = crypto_df[crypto_df["Name"].isin(selected_cryptos)] if not crypto_df.empty else pd.DataFrame()

if not filtered_data.empty:
    st.subheader(f"Visualization: {data_type} of Selected Cryptocurrencies")
    if chart_type == "Bar Chart":
        fig = px.bar(
            filtered_data, 
            x="Name", 
            y=data_type, 
            color="Name", 
            text=data_type,
            labels={"Name": "Cryptocurrency", data_type: f"{data_type} (USD)"},
            title=f"{data_type} Comparison",
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")

    elif chart_type == "Line Chart":
        fig = px.line(
            filtered_data, 
            x="Name", 
            y=data_type, 
            color="Name",
            markers=True,
            labels={"Name": "Cryptocurrency", data_type: f"{data_type} (USD)"},
            title=f"{data_type} Trend",
        )

    elif chart_type == "Pie Chart":
        fig = px.pie(
            filtered_data, 
            names="Name", 
            values=data_type, 
            title=f"{data_type} Distribution",
        )

    st.plotly_chart(fig, use_container_width=True)

    show_raw_data = st.checkbox("Show Raw Data")
    if show_raw_data:
        st.subheader("📄 Raw Data")
        st.dataframe(filtered_data)
else:
    st.warning("No data available. Please refresh or select cryptocurrencies.")
