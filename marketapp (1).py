from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights
import streamlit as st
import os
import tempfile
import yahoo_fin.stock_info as si  # Added Yahoo Finance for fundamental analysis

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "page1"
    st.session_state.ticker = "RELIANCE"
    st.session_state.market = "BSE"
    st.session_state.analysis_type = "Technical Analysis"
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False

# Set page configuration for better UI
st.set_page_config(page_title="📊 Stock Insight AI - Technical & Fundamental Analysis", 
                   page_icon="📈", layout="wide")

def page1():
    """Input Page"""
    st.title("Stock Insight AI - Technical & Fundamental Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker)
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], 
                                               index=["BSE", "NASDAQ"].index(st.session_state.market))

    # Dropdown for selecting analysis type
    st.session_state.analysis_type = st.selectbox("Select Analysis Type", 
                                                  ["Technical Analysis", "Fundamental Analysis", "Both"])

    st.sidebar.header("About")
    st.sidebar.write("""
        **Stock Insight AI** is an AI-powered stock analysis tool that:
        - Fetches real-time stock data.
        - Performs trend and pattern analysis.
        - Provides AI-generated insights.
        - Retrieves fundamental data from Yahoo Finance.

        **Steps to use:**
        1. Enter the stock ticker symbol (e.g., RELIANCE).
        2. Select the market (BSE or NASDAQ).
        3. Choose the analysis type (Technical, Fundamental, or Both).
        4. Click "Submit" to analyze.
    """)

    if st.button("Submit"):
        st.session_state.page = "page2"
        st.session_state.internal_results_available = False
        st.rerun()

def page2():
    """Analysis Page"""
    st.title(f"Analysis for {st.session_state.ticker} ({st.session_state.market})")

    stock = st.session_state.ticker
    market = st.session_state.market
    analysis_type = st.session_state.analysis_type

    if not st.session_state.internal_results_available:
        with st.spinner("🔍 Analyzing... Please wait..."):
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{market}_{stock}.png")
            st.session_state.image_path = image_path

            try:
                stock_api_obj = StockAPI("1UJ6ACYM0P4MHORZ")  # Stock API
                stock_analyzer_obj = StockAnalyzer()  # Stock Analyzer
                ai_insights_obj = AIInsights("AIzaSyAVi1v80vt41mTjZED6BaMs5-74HKFkSk0")  # AI Insights

                # Fetching stock data
                market_data = stock_api_obj.get_stock_info(stock)  # FIXED: Removed the extra argument

                if "Time Series (Daily)" not in market_data:
                    st.error("⚠️ Unable to fetch stock data. API limit might be reached.")
                    return

                # Convert JSON data to DataFrame
                df = stock_analyzer_obj.json_to_dataframe(market_data, stock, market)

                # Generate stock chart
                if analysis_type in ["Technical Analysis", "Both"]:
                    stock_analyzer_obj.plot_stock_data(df, stock, market, image_path)

                # AI Insights Handling
                try:
                    if analysis_type in ["Technical Analysis", "Both"]:
                        response = ai_insights_obj.get_ai_insights(image_path, stock, market)
                        st.session_state.ai_insights = "\n".join(
                            [part.text for candidate in response.candidates for part in candidate.content.parts]
                        )
                    else:
                        st.session_state.ai_insights = "AI Insights not required for Fundamental Analysis."
                except Exception as ai_error:
                    st.warning(f"⚠️ AI Insights could not be fetched: {ai_error}")
                    st.session_state.ai_insights = "AI Insights unavailable."

                # Fundamental Analysis
                if analysis_type in ["Fundamental Analysis", "Both"]:
                    try:
                        fundamentals = si.get_quote_table(stock)
                        st.session_state.fundamentals = fundamentals
                    except Exception as fund_error:
                        st.warning(f"⚠️ Unable to fetch fundamental data: {fund_error}")
                        st.session_state.fundamentals = None

                st.session_state.internal_results_available = True

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                return

    # Display results
    if st.session_state.internal_results_available:
        if analysis_type in ["Technical Analysis", "Both"]:
            st.subheader("📊 Technical Chart Analysis")
            st.image(st.session_state.image_path, caption=f"{stock} Chart", use_column_width=True)
        
        st.subheader("🧠 AI Insights")
        st.write(st.session_state.ai_insights)

        if analysis_type in ["Fundamental Analysis", "Both"]:
            st.subheader("📈 Fundamental Analysis (Yahoo Finance)")
            if st.session_state.fundamentals:
                st.write(st.session_state.fundamentals)
            else:
                st.write("⚠️ Fundamental data unavailable.")

        if st.button("🔙 Back"):
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()

# Route between pages
if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
