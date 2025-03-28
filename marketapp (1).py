import streamlit as st
import os
import tempfile
from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights
import yfinance as yf

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "page1"
    st.session_state.ticker = "RELIANCE"
    st.session_state.market = "BSE"
    st.session_state.analysis_type = "Technical Analysis"
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False

# Set page configuration
st.set_page_config(page_title="📊 Stock Insight AI", page_icon="📈", layout="wide")

def main():
    if st.session_state.page == "page1":
        input_page()
    elif st.session_state.page == "page2":
        analysis_page()

def input_page():
    """Input Page"""
    st.title("Stock Insight AI - Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker)
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], index=["BSE", "NASDAQ"].index(st.session_state.market))
    with col3:
        st.session_state.analysis_type = st.selectbox("Select Analysis Type", ["Technical Analysis", "Fundamental Analysis", "Both"])
    
    st.sidebar.header("About")
    st.sidebar.write("""
        **Stock Insight AI**
        - Fetches real-time stock data.
        - Performs trend and pattern analysis.
        - Provides AI-generated insights.
        - Retrieves fundamental financial data.

        **How to Use:**
        1. Enter the stock ticker symbol (e.g., RELIANCE).
        2. Select the market (BSE or NASDAQ).
        3. Choose analysis type (Technical/Fundamental/Both).
        4. Click "Submit" to analyze.
    """)

    if st.button("Submit"):
        st.session_state.page = "page2"
        st.session_state.internal_results_available = False
        st.rerun()

def analysis_page():
    """Analysis Page"""
    st.title(f"{st.session_state.analysis_type} for {st.session_state.ticker} ({st.session_state.market})")
    
    stock = st.session_state.ticker
    analysis_type = st.session_state.analysis_type
    
    if not st.session_state.internal_results_available:
        with st.spinner("🔍 Analyzing... Please wait..."):
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{stock}.png")
            st.session_state.image_path = image_path

            try:
                stock_api_obj = StockAPI("JXVWA9W91RARPC46")
                stock_analyzer_obj = StockAnalyzer()
                ai_insights_obj = AIInsights("AIzaSyAVi1v80vt41mTjZED6BaMs5-74HKFkSk0")

                if analysis_type in ["Technical Analysis", "Both"]:
                    market_data = stock_api_obj.get_stock_info(stock)
                    df = stock_analyzer_obj.json_to_dataframe(market_data)  # Fixed this line
                    stock_analyzer_obj.plot_stock_data(df, stock, image_path)
                    
                    response = ai_insights_obj.get_ai_insights(image_path, stock)
                    st.session_state.ai_insights = "\n".join([part.text for candidate in response.candidates for part in candidate.content.parts])
                
                if analysis_type in ["Fundamental Analysis", "Both"]:
                    stock_info = yf.Ticker(stock).info
                    st.session_state.fundamentals = {
                        "Market Cap": stock_info.get("marketCap", "N/A"),
                        "P/E Ratio": stock_info.get("trailingPE", "N/A"),
                        "52-Week High": stock_info.get("fiftyTwoWeekHigh", "N/A"),
                        "52-Week Low": stock_info.get("fiftyTwoWeekLow", "N/A"),
                    }

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
            for key, value in st.session_state.fundamentals.items():
                st.write(f"**{key}:** {value}")
        
        if st.button("🔙 Back"):
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()

if __name__ == "__main__":
    main()
