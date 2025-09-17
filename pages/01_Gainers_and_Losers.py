# import streamlit as st
# import pandas as pd
# import requests
# import re
# from datetime import datetime
# from io import StringIO

# st.markdown("""
#     <style>
#         .dataframe-container {
#             border: 1px solid #333;
#             border-radius: 8px;
#             overflow: hidden;
#             background-color: #1E1E1E;
#         }
#     [data-testid="stSidebar"] {
#         background: black;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.title("🚀 Top Gainers & 🔻 Top Losers")

# # --- Use your provided URLs directly ---
# INDEX_URLS = {
#     "NIFTY 50": {
#         "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/nifty-50_9/",
#         "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/nifty-50_9/"
#     },
#     "BANKNIFTY": {
#         "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/nifty-bank_23/",
#         "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/nifty-bank_23/"
#     },
#     "NIFTY NEXT 50": {
#         "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/nifty-next-50_6/",
#         "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/nifty-next-50_6/"
#     },
#     "ALL STOCKS": {
#         "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/all-companies_-2/",
#         "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/all-companies_-2/"
#     }
# }

# def clean_company_name(name):
#     name = re.split(r'Add to|Portfolio|ACTIONS|\|', str(name))[0]
#     return name.strip()

# def fetch_table(url, gainers=True):
#     headers = {
#         "User-Agent": "Mozilla/5.0",
#         "Referer": "https://www.moneycontrol.com/stocks/marketstats/nsegainer/index.php"
#     }
#     try:
#         resp = requests.get(url, headers=headers, timeout=10)
#         if resp.status_code != 200:
#             return pd.DataFrame()
#         tables = pd.read_html(StringIO(resp.text))
#         for df in tables:
#             if "Company Name" in df.columns:
#                 if "% Chg" in df.columns:
#                     df = df[["Company Name", "Last Price", "% Chg"]].rename(
#                         columns={"% Chg": "% Change"})
#                 elif "% Gain" in df.columns:
#                     df = df[["Company Name", "Last Price", "% Gain"]].rename(
#                         columns={"% Gain": "% Change"})
#                 elif "% Loss" in df.columns:
#                     df = df[["Company Name", "Last Price", "% Loss"]].rename(
#                         columns={"% Loss": "% Change"})
#                 else:
#                     df = df[["Company Name", "Last Price"]]
#                 filter_out = ['5-Day', '10-Day', '30-Day']
#                 df = df[~df['Company Name'].isin(filter_out)].copy()
#                 df['Company Name'] = df['Company Name'].apply(clean_company_name)
#                 df = df[df['Company Name'] != ""].reset_index(drop=True)
#                 # For losers, ensure % Change is negative and sort appropriately
#                 if not gainers and "% Change" in df.columns:
#                     df["% Change"] = df["% Change"].astype(str).str.replace("%", "").astype(float)
#                     df = df.sort_values(by="% Change")
#                 return df
#         return pd.DataFrame()
#     except Exception:
#         return pd.DataFrame()

# def style_gainers(df):
#     styled = df.style \
#         .format({'% Change': '{:+.2f}%'}) \
#         .applymap(lambda x: 'color: #2ecc71' if isinstance(x, float) and x > 0 else 'color: #e74c3c', subset=['% Change']) \
#         .set_properties(**{'background-color': '#1E1E1E', 'color': 'white'}) \
#         .set_table_styles([{
#             'selector': 'th',
#             'props': [('background', '#2E2E2E'), ('color', 'white')]
#         }])
#     return styled

# def style_losers(df):
#     styled = df.style \
#         .format({'% Change': '{:+.2f}%'}) \
#         .applymap(lambda x: 'color: #e74c3c' if isinstance(x, float) and x < 0 else 'color: #2ecc71', subset=['% Change']) \
#         .set_properties(**{'background-color': '#1E1E1E', 'color': 'white'}) \
#         .set_table_styles([{
#             'selector': 'th',
#             'props': [('background', '#2E2E2E'), ('color', 'white')]
#         }])
#     return styled

# index_display = st.selectbox(
#     "Select Market Index",
#     list(INDEX_URLS.keys()),
#     index=0
# )

# col1, col2 = st.columns(2)

# with col1:
#     url_gainer = INDEX_URLS[index_display]["gainer"]
#     if st.button("🔄 Refresh Gainers Data"):
#         st.session_state['gainers_data'] = fetch_table(url_gainer, gainers=True)
#     if 'gainers_data' not in st.session_state or st.session_state.get('last_gainer_url') != url_gainer:
#         st.session_state['gainers_data'] = fetch_table(url_gainer, gainers=True)
#         st.session_state['last_gainer_url'] = url_gainer
#     gainers_df = st.session_state['gainers_data']
#     st.subheader("Top Gainers")
#     if not gainers_df.empty:
#         st.dataframe(style_gainers(gainers_df), use_container_width=True)
#     else:
#         st.info("No data available for this index.")

# with col2:
#     url_loser = INDEX_URLS[index_display]["loser"]
#     if st.button("🔄 Refresh Losers Data"):
#         st.session_state['losers_data'] = fetch_table(url_loser, gainers=False)
#     if 'losers_data' not in st.session_state or st.session_state.get('last_loser_url') != url_loser:
#         st.session_state['losers_data'] = fetch_table(url_loser, gainers=False)
#         st.session_state['last_loser_url'] = url_loser
#     losers_df = st.session_state['losers_data']
#     st.subheader("Top Losers")
#     if not losers_df.empty:
#         st.dataframe(style_losers(losers_df), use_container_width=True)
#     else:
#         st.info("No data available for this index.")

# st.markdown(
#     f"""
#     <hr>
#     <div style='text-align: right; color: gray; font-size: 0.9em;'>
#         Data source: <a href="https://www.moneycontrol.com/stocks/marketstats/nsegainer/index.php" target="_blank">Moneycontrol</a>
#     </div>
#     <div style='text-align:center; font-size:0.95em; color:#B0B0B0;'>
#         Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#     </div>
#     """,
#     unsafe_allow_html=True
# )

import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime
from io import StringIO

st.markdown("""
    <style>
        .dataframe-container {
            border: 1px solid #333;
            border-radius: 8px;
            overflow: hidden;
            background-color: #1E1E1E;
        }
    [data-testid="stSidebar"] {
        background: black;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Top Gainers & 🔻 Top Losers")

# --- Use your provided URLs directly ---
INDEX_URLS = {
    "NIFTY 50": {
        "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/nifty-50_9/",
        "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/nifty-50_9/"
    },
    "BANKNIFTY": {
        "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/nifty-bank_23/",
        "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/nifty-bank_23/"
    },
    "NIFTY NEXT 50": {
        "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/nifty-next-50_6/",
        "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/nifty-next-50_6/"
    },
    "ALL STOCKS": {
        "gainer": "https://www.moneycontrol.com/stocks/marketstats/nse-gainer/all-companies_-2/",
        "loser": "https://www.moneycontrol.com/stocks/marketstats/nse-loser/all-companies_-2/"
    }
}

def clean_company_name(name):
    name = re.split(r'Add to|Portfolio|ACTIONS|\|', str(name))[0]
    return name.strip()

def fetch_table(url, gainers=True):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.moneycontrol.com/stocks/marketstats/nsegainer/index.php"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return pd.DataFrame()
        # tables = pd.read_html(resp.text)
        tables = pd.read_html(StringIO(resp.text))
        for df in tables:
            if "Company Name" in df.columns:
                if "% Chg" in df.columns:
                    df = df[["Company Name", "Last Price", "% Chg"]].rename(
                        columns={"% Chg": "% Change"})
                elif "% Gain" in df.columns:
                    df = df[["Company Name", "Last Price", "% Gain"]].rename(
                        columns={"% Gain": "% Change"})
                elif "% Loss" in df.columns:
                    df = df[["Company Name", "Last Price", "% Loss"]].rename(
                        columns={"% Loss": "% Change"})
                else:
                    df = df[["Company Name", "Last Price"]]
                filter_out = ['5-Day', '10-Day', '30-Day']
                df = df[~df['Company Name'].isin(filter_out)].copy()
                df['Company Name'] = df['Company Name'].apply(clean_company_name)
                df = df[df['Company Name'] != ""].reset_index(drop=True)
                # For losers, ensure % Change is negative and sort appropriately
                if not gainers and "% Change" in df.columns:
                    df["% Change"] = df["% Change"].astype(str).str.replace("%", "").astype(float)
                    df = df.sort_values(by="% Change")
                return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def style_gainers(df):
    styled = df.style \
        .format({'% Change': '{:+.2f}%'}) \
        .applymap(lambda x: 'color: #2ecc71' if isinstance(x, float) and x > 0 else 'color: #e74c3c', subset=['% Change']) \
        .set_properties(**{'background-color': '#1E1E1E', 'color': 'white'}) \
        .set_table_styles([{
            'selector': 'th',
            'props': [('background', '#2E2E2E'), ('color', 'white')]
        }])
    return styled

def style_losers(df):
    styled = df.style \
        .format({'% Change': '{:+.2f}%'}) \
        .applymap(lambda x: 'color: #e74c3c' if isinstance(x, float) and x < 0 else 'color: #2ecc71', subset=['% Change']) \
        .set_properties(**{'background-color': '#1E1E1E', 'color': 'white'}) \
        .set_table_styles([{
            'selector': 'th',
            'props': [('background', '#2E2E2E'), ('color', 'white')]
        }])
    return styled

index_display = st.selectbox(
    "Select Market Index",
    list(INDEX_URLS.keys()),
    index=0
)

col1, col2 = st.columns(2)

with col1:
    url_gainer = INDEX_URLS[index_display]["gainer"]
    if st.button("🔄 Refresh Gainers Data"):
        st.session_state['gainers_data'] = fetch_table(url_gainer, gainers=True)
    if 'gainers_data' not in st.session_state or st.session_state.get('last_gainer_url') != url_gainer:
        st.session_state['gainers_data'] = fetch_table(url_gainer, gainers=True)
        st.session_state['last_gainer_url'] = url_gainer
    gainers_df = st.session_state['gainers_data']
    st.subheader("Top Gainers")
    if not gainers_df.empty:
        st.dataframe(style_gainers(gainers_df), use_container_width=True)
        # st.dataframe(style_gainers(gainers_df), width='stretch')
    else:
        st.info("No data available for this index.")

with col2:
    url_loser = INDEX_URLS[index_display]["loser"]
    if st.button("🔄 Refresh Losers Data"):
        st.session_state['losers_data'] = fetch_table(url_loser, gainers=False)
    if 'losers_data' not in st.session_state or st.session_state.get('last_loser_url') != url_loser:
        st.session_state['losers_data'] = fetch_table(url_loser, gainers=False)
        st.session_state['last_loser_url'] = url_loser
    losers_df = st.session_state['losers_data']
    st.subheader("Top Losers")
    if not losers_df.empty:
        st.dataframe(style_losers(losers_df), use_container_width=True)
        # st.dataframe(style_losers(losers_df), width='stretch')
    else:
        st.info("No data available for this index.")

st.markdown(
    f"""
    <hr>
    <div style='text-align: right; color: gray; font-size: 0.9em;'>
        Data source: <a href="https://www.moneycontrol.com/stocks/marketstats/nsegainer/index.php" target="_blank">Moneycontrol</a>
    </div>
    <div style='text-align:center; font-size:0.95em; color:#B0B0B0;'>
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """,
    unsafe_allow_html=True
)


