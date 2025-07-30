
import streamlit as st
import google.generativeai as genai
import re

# Configure page layout and styling
st.set_page_config(
    page_title="AI Trading Strategist",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: black;
}
.stTextInput input, .stTextArea textarea {
    background: transparent !important;
    border: 1px solid #ced4da rounded !important;
}
.stButton button {
    width: 100%;
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: scale(1.02);
}
.code-output {
    border: 1px solid #e1e4e8;
    border-radius: 4px;
    padding: 1rem;
    margin-top: 1rem;
}
.success-box {
    background: transparent;
    padding: 1rem;
    border-radius: 4px;
    margin: 1rem 0;
    
}
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if "chatbot_enabled" not in st.session_state:
    st.session_state["chatbot_enabled"] = False
if "GEMINI_API_KEY" not in st.session_state:
    st.session_state["GEMINI_API_KEY"] = ""
if "example_strategy" not in st.session_state:
    st.session_state.example_strategy = ""

# --- API Key Input Section ---
if not st.session_state["chatbot_enabled"]:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/5968/5968875.png", width=100)
        st.markdown("## Welcome to AI Trading Strategist")
        api_key = st.text_input("Enter Gemini API Key:", type="password")
        
        if st.button("🔓 Enable AI Features", use_container_width=True):
            if api_key.strip():
                st.session_state["GEMINI_API_KEY"] = api_key.strip()
                st.session_state["chatbot_enabled"] = True
                st.rerun()
            else:
                st.warning("Please enter a valid API key")
                
        st.markdown("---")
        st.markdown("ℹ️ Get your API key from [Google AI Studio](https://ai.google.dev/)")
    with col2:
        st.markdown("### Features Overview")
        st.markdown("""
        - 🐍 **Python Backtesting Strategies**
        - 📊 **TradingView Pine Scripts**
        - 🤖 **AI-Powered Code Generation**
        - ✅ **Production-Ready Output**
        """)
        st.video("https://www.youtube.com/watch?v=your-demo-video")
    st.stop()

# --- Main Application Interface ---
genai.configure(api_key=st.session_state["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_code(response: str) -> str:
    """Improved code extraction with multiple patterns"""
    patterns = [
        r'``````',
        r'``````',
        r'``````'
    ]
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    return response.strip()

def generate_strategy_code(description: str, language: str) -> str:
    """Generates trading strategy code using Gemini"""
    prompt = f"""Generate a complete, ready-to-backtest {language} trading strategy script.
Implement exactly these rules:
{description}

Requirements:
- For Python: Use pandas, TA-Lib/yfinance for backtesting
- For Pine Script: Use v5 syntax for TradingView
- Output ONLY the code, no explanations
- Include all necessary imports/version declarations"""
    
    response = model.generate_content(prompt)
    return extract_code(response.text)

# Sidebar for examples and info
with st.sidebar:
    st.markdown("## 📚 Strategy Examples")
    examples = {
        "RSI + EMA Strategy": "Buy when RSI < 30 and price > 50 EMA. Sell when RSI > 70. Use 2% stop loss.",
        "MACD Crossover": "Buy when MACD crosses above signal line. Sell when crosses below. 1-hour timeframe.",
        "Bollinger Bands": "Buy when price touches lower Bollinger Band. Sell at upper band. 15m timeframe."
    }
    
    for name, strategy in examples.items():
        if st.button(f"★ {name}"):
            st.session_state.example_strategy = strategy

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("## ⚙️ Configuration")
    language = st.radio(
        "**Code Language**",
        ["Python", "Pine Script"],
        horizontal=True,
        help="Select target platform for strategy implementation"
    )
    
    st.markdown("---")
    st.markdown("### 📈 Strategy Parameters")
    st.markdown("ℹ️ Describe your trading rules in detail")

with col2:
    st.markdown("## 📝 Strategy Input")
    strategy_desc = st.text_area(
        "Describe your trading rules:",
        height=200,
        placeholder="Example:\n- Entry/exit conditions\n- Risk management rules\n- Timeframe\n- Indicators used",
        value=st.session_state.example_strategy
    )
    
    st.markdown("---")
    generate_col, clear_col = st.columns([3, 1])
    
    with generate_col:
        generate_clicked = st.button(
            "🚀 Generate Trading Strategy",
            type="primary",
            use_container_width=True
        )
    
    with clear_col:
        if st.button("🔄 Clear Input", use_container_width=True):
            st.session_state.example_strategy = ""
            st.rerun()

# Code generation and output
if generate_clicked:
    if not strategy_desc.strip():
        st.warning("⚠️ Please describe your trading strategy")
        st.stop()
    
    with st.spinner("🔍 Analyzing strategy and generating code..."):
        try:
            code = generate_strategy_code(strategy_desc, language)
            
            st.markdown("## 💻 Generated Strategy Code")
            with st.expander("✨ Code Output", expanded=True):
                st.code(code, language=language.lower())
                st.download_button(
                    label="📥 Download Code",
                    data=code,
                    file_name=f"{language.lower()}_strategy.{'py' if language == 'Python' else 'pine'}",
                    mime="text/plain"
                )
            
            st.markdown('<div class="success-box">✅ Successfully generated production-ready code!</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"""
            ❌ Generation Failed: {str(e)}
            \n**Troubleshooting Tips:**
            - Verify API key validity
            - Check strategy description clarity
            - Ensure network connectivity
            - Try simpler strategy rules
            """)
