
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from datetime import datetime, time
import pytz
from streamlit_autorefresh import st_autorefresh

st.title("📉 PCR Analysis")

# --- Auto-refresh only during market hours (9:15 AM to 3:25 PM IST) ---
india_tz = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(india_tz)
start_time = time(9, 15)   # 9:15 AM
end_time = time(15, 25)    # 3:25 PM

if start_time <= now_ist.time() <= end_time:
    st_autorefresh(interval=30 * 1000, key="datarefresh")

# --- Manual refresh button ---
if st.button("🔄 Refresh"):
    st.rerun()

INDEX_OPTIONS = {
    "NIFTY 50": "NIFTY",
    "BANKNIFTY": "BANKNIFTY",
    "NIFTY NEXT 50": "FINNIFTY",
    "MIDCPNIFTY": "MIDCPNIFTY"
}
index_option = st.selectbox(
    'Select Index',
    list(INDEX_OPTIONS.keys()),
    key="index_option"
)

def create_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    })
    return session

def get_option_chain(symbol='NIFTY'):
    try:
        session = create_session()
        session.get('https://www.nseindia.com/', timeout=10)
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'records' in data and 'data' in data['records']:
                return {
                    'data': data['records']['data'],
                    'underlyingValue': data['records']['underlyingValue']
                }
        st.error(f"Failed to fetch data: Status code {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_expiry_dates(data):
    if data and len(data) > 0:
        expiry_dates = set()
        for item in data:
            if 'expiryDate' in item:
                expiry_dates.add(item['expiryDate'])
        return sorted(list(expiry_dates))
    return []

def calculate_pcr(data):
    pcr_data = []
    for item in data:
        try:
            strike = item['strikePrice']
            ce_oi = item['CE'].get('openInterest', 0) if 'CE' in item else 0
            ce_change_oi = item['CE'].get('changeinOpenInterest', 0) if 'CE' in item else 0
            ce_price = item['CE'].get('lastPrice', 0) if 'CE' in item else 0
            pe_oi = item['PE'].get('openInterest', 0) if 'PE' in item else 0
            pe_change_oi = item['PE'].get('changeinOpenInterest', 0) if 'PE' in item else 0
            pe_price = item['PE'].get('lastPrice', 0) if 'PE' in item else 0
            pcr = pe_change_oi / ce_change_oi if ce_change_oi != 0 else None
            pcr_data.append({
                'Call OI': ce_oi,
                'Call OI Change': ce_change_oi,
                'Call Price': ce_price,
                'Strike Price': strike,
                'Put Price': pe_price,
                'Put OI Change': pe_change_oi,
                'Put OI': pe_oi,
                'PCR': round(pcr, 2) if pcr is not None else None
            })
        except Exception:
            continue
    return pd.DataFrame(pcr_data)

def get_atm_strike(strike_prices, spot_price):
    if not strike_prices:
        return None
    lower = max([s for s in strike_prices if s <= spot_price], default=strike_prices[0])
    higher = min([s for s in strike_prices if s >= spot_price], default=strike_prices[-1])
    interval = strike_prices[1] - strike_prices[0] if len(strike_prices) > 1 else 50
    halfway = lower + interval // 2
    if spot_price <= halfway:
        return lower
    else:
        return higher

def classify_moneyness(strike, atm_strike):
    if strike < atm_strike:
        return 'ITM'
    elif strike == atm_strike:
        return 'ATM'
    else:
        return 'OTM'

def calculate_custom_metrics(df, spot_price, atm_strike):
    if df.empty or spot_price is None or atm_strike is None:
        return 0, 0, 0.0

    strikes = sorted(df['Strike Price'].unique())
    # Find OTM strikes below spot (for calls), excluding ATM
    otm_calls = [s for s in strikes if s > spot_price]
    if atm_strike in otm_calls:
        otm_calls.remove(atm_strike)
    otm_calls_below = [s for s in strikes if s > spot_price][:5]  # 5 strikes above spot (OTM for calls)
    call_oi_changes = df[df['Strike Price'].isin(otm_calls_below)]['Call OI Change'].sum()

    # Find OTM strikes above spot (for puts), including ATM
    otm_puts = [s for s in strikes if s < spot_price]
    otm_puts_above = [s for s in strikes if s < spot_price][-5:]  # 5 strikes below spot (OTM for puts)
    if atm_strike not in otm_puts_above:
        otm_puts_above.append(atm_strike)
    put_oi_changes = df[df['Strike Price'].isin(otm_puts_above)]['Put OI Change'].sum()

    avg_pcr = put_oi_changes / call_oi_changes if call_oi_changes != 0 else 0.0
    return call_oi_changes, put_oi_changes, avg_pcr

if "selected_expiry" not in st.session_state:
    st.session_state.selected_expiry = None

with st.spinner('Fetching data from NSE... Please wait.'):
    option_chain_data = get_option_chain(INDEX_OPTIONS[index_option])

records_data = option_chain_data['data'] if option_chain_data else None
spot_price = option_chain_data['underlyingValue'] if option_chain_data else None

expiry_dates = get_expiry_dates(records_data) if records_data else []
if expiry_dates:
    if st.session_state.selected_expiry not in expiry_dates:
        st.session_state.selected_expiry = expiry_dates[0]
    selected_expiry = st.selectbox(
        'Select Expiry Date',
        expiry_dates,
        index=expiry_dates.index(st.session_state.selected_expiry),
        key="expiry_select"
    )
    st.session_state.selected_expiry = selected_expiry
    filtered_data = [item for item in records_data if item.get('expiryDate') == selected_expiry]
else:
    filtered_data = records_data

if filtered_data:
    df = calculate_pcr(filtered_data)
    if not df.empty:
        df = df.sort_values('Strike Price')
        valid_pcr_df = df.dropna(subset=['PCR']).copy()
        strike_prices = sorted(df['Strike Price'].unique())
        atm_strike = get_atm_strike(strike_prices, spot_price)

        def highlight_moneyness(row):
            call_bg = 'background-color: #23272b; color: #fff'
            put_bg = 'background-color: #23272b; color: #fff'
            default = ''
            styles = [default] * len(row)
            strike = row['Strike Price']
            if atm_strike is not None:
                mny = classify_moneyness(strike, atm_strike)
                if mny == 'ITM':
                    for i in [0,1,2]:
                        styles[i] = call_bg
                elif mny == 'OTM':
                    for i in [4,5,6]:
                        styles[i] = put_bg
                elif mny == 'ATM':
                    for i in [0,1,2]:
                        styles[i] = call_bg
            return styles

        styled_df = df.style.apply(highlight_moneyness, axis=1)\
            .format({
                'Call OI': '{:,}',
                'Call OI Change': '{:,}',
                'Call Price': '₹{:.2f}',
                'Strike Price': '{:.2f}',
                'Put Price': '₹{:.2f}',
                'Put OI Change': '{:,}',
                'Put OI': '{:,}',
                'PCR': '{:.2f}'
            })\
            .background_gradient(subset=['PCR'], cmap='plasma')

        st.dataframe(
            styled_df,
            use_container_width=True
        )

        total_call, total_put, avg_pcr = calculate_custom_metrics(df, spot_price, atm_strike)
        if avg_pcr > 1.4 or total_call < 0:
            signal = "BUY CALL Option / SELL PUT Option"
        elif avg_pcr < 0.8 or total_put < 0:
            signal = "BUY PUT Option / SELL CALL Option"
        else:
            signal = "No Signal"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Call OI Change", f"{total_call:,}")
        col2.metric("Total Put OI Change", f"{total_put:,}")
        col3.metric("Average PCR", f"{avg_pcr:.2f}")
        signal_html = f"""
        <div style='font-weight:600; margin-bottom:0px;'>BUY/SELL Signal</div>
        <div style='margin-top:0px; font-size:2.2em; white-space:pre-line;'>{signal}</div>
        """
        col4.markdown(signal_html, unsafe_allow_html=True)

        st.subheader("PCR by Strike Price")
        st.line_chart(valid_pcr_df.set_index('Strike Price')['PCR'], use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Call OI Change by Strike")
            st.bar_chart(df.set_index('Strike Price')['Call OI Change'], use_container_width=True)
        with col2:
            st.subheader("Put OI Change by Strike")
            st.bar_chart(df.set_index('Strike Price')['Put OI Change'], use_container_width=True)
    else:
        st.warning("No data available for PCR calculation.")
else:
    st.error("Failed to fetch data from NSE. This could be due to market hours or connectivity issues.")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: black;
    }
    </style>
    """
    f"""
    <hr>
    <div style='text-align:center; font-size:0.95em; color:#B0B0B0;'>
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """,
    unsafe_allow_html=True
)
