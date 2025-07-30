import streamlit as st


st.set_page_config(
    page_title="Market Analytics Suite",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: black;
    }

    </style>
    <div style='background: linear-gradient(90deg, #00CED1, #1E90FF); padding: 2rem; border-radius: 1rem; margin-bottom: 2rem;'>
        <h1 style="color: black; margin: 0; font-size: 2.5em;">📈 Market Analytics Suite</h1>
        <p style="color: black; margin: 0.5em 0 0; font-size: 1.1em;">Navigate using the sidebar to access PCR Analysis or Top Gainers & Losers.</p>
    </div>
""", unsafe_allow_html=True)

st.info("Select a page from the sidebar.")
