from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights

import streamlit as st
import os
import tempfile

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "page1"
    st.session_state.ticker = "RELIANCE"
    st.session_state.market = "BSE"
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False

# Set page configuration for better UI
st.set_page_config(page_title="📊 Stock Insight AI - Technical Analysis", page_icon="📈", layout="wide")

def page1():
    """Input Page"""
    st.title("Stock Insight AI - Technical Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker)
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], index=["BSE", "NASDAQ"].index(st.session_state.market))

    st.sidebar.header("About")
    st.sidebar.write("""
        **Stock Insight AI** is an AI-powered stock analysis tool that:
        - Fetches real-time stock data.
        - Performs trend and pattern analysis.
        - Provides AI-generated insights.

        **Steps to use:**
        1. Enter the stock ticker symbol (e.g., RELIANCE).
        2. Select the market (BSE or NASDAQ).
        3. Click "Submit" to analyze.
    """)

    if st.button("Submit"):
        st.session_state.page = "page2"
        st.session_state.internal_results_available = False
        st.rerun()

def page2():
    """Analysis Page"""
    st.title(f"Technical Analysis for {st.session_state.ticker} ({st.session_state.market})")
    
    stock = st.session_state.ticker
    market = st.session_state.market

    if not st.session_state.internal_results_available:
        with st.spinner("🔍 Analyzing... Please wait..."):
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{market}_{stock}.png")
            st.session_state.image_path = image_path

            try:
                stock_api_obj = StockAPI("1UJ6ACYM0P4MHORZ")
                stock_analyzer_obj = StockAnalyzer()
                ai_insights_obj = AIInsights("AIzaSyAVi1v80vt41mTjZED6BaMs5-74HKFkSk0")

                market_data = stock_api_obj.get_stock_info(stock, market)
                if "Time Series (Daily)" not in market_data:
                    st.error("⚠️ Unable to fetch stock data. API limit might be reached.")
                    return

                df = stock_analyzer_obj.json_to_dataframe(market_data, stock, market)
                stock_analyzer_obj.plot_stock_data(df, stock, market, image_path)

                # AI Insights Handling
                try:
                    response = ai_insights_obj.get_ai_insights(image_path, stock, market)
                    st.session_state.ai_insights = "\n".join([part.text for candidate in response.candidates for part in candidate.content.parts])
                except Exception as ai_error:
                    st.warning(f"⚠️ AI Insights could not be fetched: {ai_error}")
                    st.session_state.ai_insights = "AI Insights unavailable."

                st.session_state.internal_results_available = True

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                return

    if st.session_state.internal_results_available:
        st.subheader("📊 Chart Analysis")
        st.image(st.session_state.image_path, caption=f"{stock} Chart", use_column_width=True)
        
        st.subheader("🧠 AI Insights")
        st.write(st.session_state.ai_insights)

        if st.button("🔙 Back"):
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()

# Route between pages
if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
