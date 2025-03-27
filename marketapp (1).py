from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights

import streamlit as st
import os
import tempfile

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = "page1"
    st.session_state.ticker = "RELIANCE"
    st.session_state.market = "BSE"
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False

# Set page configuration for better UI
st.set_page_config(page_title="📊 Stock Insight AI - Technical Analysis", page_icon="📈", layout="wide")

# Page 1: Input Page
def page1():
    st.title('Stock Insight AI - Technical Analysis')

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker, key="ticker_input")
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], index=["BSE", "NASDAQ"].index(st.session_state.market), key="market_input")

    st.sidebar.header("About")
    st.sidebar.write("""
        **Stock Insight AI** is an advanced technical analysis tool powered by AI insights and real-time market data.

        **What this tool does:**
        - Fetches real-time stock data from BSE and NASDAQ.
        - Analyzes stock trends and patterns using AI.
        - Generates visual charts for technical analysis.
        - Provides AI-powered insights for better decision-making.

        **Steps to perform the search:**
        1. Enter the stock ticker symbol (e.g., RELIANCE).
        2. Select the market (BSE or NASDAQ).
        3. Click "Submit" to initiate the analysis.

        📌 **Copyright © 2025 Nakul Arora & Mohit Vaidya**
    """)

    st.markdown("---")

    if st.button('Submit', use_container_width=True):
        st.session_state.page = "page2"
        st.session_state.internal_results_available = False
        st.rerun()

# Page 2: Analysis Page
def page2():
    st.title(f"Technical Analysis for {st.session_state.ticker} ({st.session_state.market})")

    stock = st.session_state.ticker
    market = st.session_state.market

    if not st.session_state.internal_results_available:
        with st.spinner('🔍 Analyzing... Please wait...'):
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{market}_{stock}.png")
            st.session_state.image_path = image_path

            try:
                stock_api_obj = StockAPI("1UJ6ACYM0P4MHORZ")
                stock_analyzer_obj = StockAnalyzer()
                ai_insights_obj = AIInsights("AIzaSyAVi1v80vt41mTjZED6BaMs5-74HKFkSk0")

                market_data = stock_api_obj.get_stock_info(stock, market)

                df = stock_analyzer_obj.json_to_dataframe(market_data, stock, market)

                stock_analyzer_obj.plot_stock_data(df, stock, market, image_path)

                response = ai_insights_obj.get_ai_insights(image_path, stock, market)

                st.session_state.ai_insights = ""
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        print(part.text)
                        st.session_state.ai_insights += part.text

                st.session_state.internal_results_available = True

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                return

    if st.session_state.internal_results_available:
        st.subheader("📊 Chart Analysis")
        st.image(st.session_state.image_path, caption=f"{stock} Chart", use_column_width=True)

        st.subheader("🧠 AI Insights")
        st.write(st.session_state.ai_insights)

        if st.button("🔙 Back", use_container_width=True):
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()

# Route between pages
if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
