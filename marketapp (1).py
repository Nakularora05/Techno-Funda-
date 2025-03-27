from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights
from yahoo_fin import stock_info as si
import streamlit as st
import os
import tempfile

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "page1"
    st.session_state.ticker = "RELIANCE"
    st.session_state.market = "BSE"
    st.session_state.analysis_type = "Technical Analysis"
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False
    st.session_state.fundamental_data = ""

st.set_page_config(page_title="📊 Stock Insight AI", page_icon="📈", layout="wide")

def fetch_fundamental_data(ticker):
    try:
        data = si.get_quote_table(f"{ticker}.BO" if st.session_state.market == "BSE" else ticker)
        return data
    except Exception as e:
        return f"⚠️ Could not fetch fundamental data: {e}"

def page1():
    """Input Page"""
    st.title("Stock Insight AI")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker)
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], index=["BSE", "NASDAQ"].index(st.session_state.market))
    with col3:
        st.session_state.analysis_type = st.selectbox("Select Analysis Type", ["Technical Analysis", "Fundamental Analysis", "Both"])

    st.sidebar.header("About")
    st.sidebar.write("""
        **Stock Insight AI** is an AI-powered stock analysis tool that:
        - Fetches real-time stock data.
        - Performs trend and pattern analysis.
        - Provides AI-generated insights.
        - Retrieves fundamental financial metrics.
    """)

    if st.button("Submit"):
        st.session_state.page = "page2"
        st.session_state.internal_results_available = False
        st.rerun()

def page2():
    """Analysis Page"""
    st.title(f"{st.session_state.analysis_type} for {st.session_state.ticker} ({st.session_state.market})")
    
    stock = st.session_state.ticker
    market = st.session_state.market
    analysis_type = st.session_state.analysis_type
    
    if not st.session_state.internal_results_available:
        with st.spinner("🔍 Analyzing... Please wait..."):
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{market}_{stock}.png")
            st.session_state.image_path = image_path

            try:
                if analysis_type in ["Technical Analysis", "Both"]:
                    stock_api_obj = StockAPI("1UJ6ACYM0P4MHORZ")
                    stock_analyzer_obj = StockAnalyzer()
                    ai_insights_obj = AIInsights("AIzaSyAVi1v80vt41mTjZED6BaMs5-74HKFkSk0")

                    market_data = stock_api_obj.get_stock_info(stock, market)
                    if "Time Series (Daily)" not in market_data:
                        st.error("⚠️ Unable to fetch stock data. API limit might be reached.")
                        return

                    df = stock_analyzer_obj.json_to_dataframe(market_data, stock, market)
                    stock_analyzer_obj.plot_stock_data(df, stock, market, image_path)

                    try:
                        response = ai_insights_obj.get_ai_insights(image_path, stock, market)
                        st.session_state.ai_insights = "\n".join([part.text for candidate in response.candidates for part in candidate.content.parts])
                    except Exception as ai_error:
                        st.warning(f"⚠️ AI Insights could not be fetched: {ai_error}")
                        st.session_state.ai_insights = "AI Insights unavailable."

                if analysis_type in ["Fundamental Analysis", "Both"]:
                    st.session_state.fundamental_data = fetch_fundamental_data(stock)

                st.session_state.internal_results_available = True

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                return

    if st.session_state.internal_results_available:
        if analysis_type in ["Technical Analysis", "Both"]:
            st.subheader("📊 Chart Analysis")
            st.image(st.session_state.image_path, caption=f"{stock} Chart", use_column_width=True)
            
            st.subheader("🧠 AI Insights")
            st.write(st.session_state.ai_insights)

        if analysis_type in ["Fundamental Analysis", "Both"]:
            st.subheader("📈 Fundamental Analysis")
            if isinstance(st.session_state.fundamental_data, dict):
                for key, value in st.session_state.fundamental_data.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.write(st.session_state.fundamental_data)

        if st.button("🔙 Back"):
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()

# Route between pages
if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
