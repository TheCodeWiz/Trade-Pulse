import streamlit as st
import pandas as pd
import requests

def fetch_global_indices():
    url = "https://priceapi.moneycontrol.com/technicalCompanyData/globalMarket/getGlobalIndicesListingData?view=overview&deviceType=W"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    json_data = response.json()

    columns = [
        "Symbol", "Name", "LTP", "Change", "Chg%", "High", "Low", "Open", "Prev Close", 
        "52 W High", "52 W Low", "1 Week", "1 Month", "3 Month", "6 Month", "YTD",
        "1 Year", "2 Year", "3 Year", "5 Year", "Technical Rating", "Timestamp", 
        "Flag URL", "Market Status", "Is Open", "Unknown1", "Unknown2"
    ]

    all_rows = []
    for region in json_data.get('dataList', []):
        for row in region.get('data', []):
            all_rows.append(row)

    df = pd.DataFrame(all_rows, columns=columns)

    for col in ["LTP", "Change", "Chg%", "High", "Low", "Open", "Prev Close", "52 W High", "52 W Low"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# Set Streamlit page config for a wider layout
st.set_page_config(page_title="Global Indices Dashboard", page_icon="🌐", layout="wide")

st.title("🌐 Moneycontrol Global Indices Dashboard")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: black;
    }
    </style>
    """
    "<div style='margin-bottom: 15px; color: #555;'>"
    "Live overview of major global indices with performance metrics. Data source: Moneycontrol."
    "</div>",
    unsafe_allow_html=True
)

if st.button("🔄 Refresh Data"):
    st.session_state.indices_df = fetch_global_indices()
    st.success("Data refreshed!")

if "indices_df" not in st.session_state:
    st.session_state.indices_df = fetch_global_indices()

display_columns = [
    "Name", "LTP", "Change", "Chg%", "High", "Low", "Open", "Prev Close",
    "52 W High", "52 W Low", "YTD", "1 Week", "1 Month", "3 Month", "6 Month", 
    "1 Year", "2 Year", "3 Year", "5 Year", "Technical Rating"
]

# Display the table with a large height and width, but not full screen
st.dataframe(
    st.session_state.indices_df[display_columns],
    height=560,
    width=1800
)

st.markdown(
    "<div style='text-align: right; color: gray; font-size: 0.9em;'>"
    "Data source: <a href='https://www.moneycontrol.com/markets/global-indices/' target='_blank'>Moneycontrol</a>"
    "</div>",
    unsafe_allow_html=True
)
