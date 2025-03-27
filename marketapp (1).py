import streamlit as st
import os
import tempfile
from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "page1"
    st.session_state.ticker = "RELIANCE"
    st.session_state.market = "BSE"
    st.session_state.analysis_type = "Technical Analysis"
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False

st.set_page_config(page_title="📊 Stock Insight AI", page_icon="📈", layout="wide")

def page1():
    st.title('Stock Insight AI')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker)
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], index=["BSE", "NASDAQ"].index(st.session_state.market))
    with col3:
        st.session_state.analysis_type = st.selectbox("Select Analysis Type", ["Technical Analysis", "Fundamental Analysis", "Techno-Fundamental Analysis"],
                                                       index=["Technical Analysis", "Fundamental Analysis", "Techno-Fundamental Analysis"].index(st.session_state.analysis_type))
    
    st.markdown("---")
    if st.button('Submit', use_container_width=True):
        st.session_state.page = "page2"
        st.session_state.internal_results_available = False
        st.rerun()

def page2():
    st.title(f"{st.session_state.analysis_type} for {st.session_state.ticker} ({st.session_state.market})")
    stock = st.session_state.ticker
    market = st.session_state.market
    analysis_type = st.session_state.analysis_type
    
    if not st.session_state.internal_results_available:
        with st.spinner('🔍 Analyzing... Please wait...'):
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{market}_{stock}.png")
            st.session_state.image_path = image_path
            
            try:
                stock_api_obj = StockAPI("YOUR_ALPHAVANTAGE_API_KEY")
                stock_analyzer_obj = StockAnalyzer()
                ai_insights_obj = AIInsights("YOUR_GEMINI_API_KEY")
                
                market_data = stock_api_obj.get_stock_info(stock, market)
                df = stock_analyzer_obj.json_to_dataframe(market_data, stock, market)
                
                if analysis_type == "Technical Analysis":
                    stock_analyzer_obj.plot_stock_data(df, stock, market, image_path)
                elif analysis_type == "Fundamental Analysis":
                    fundamentals = stock_api_obj.get_fundamental_data(stock, market)
                    st.subheader("📊 Fundamental Analysis Data")
                    st.write(fundamentals)
                elif analysis_type == "Techno-Fundamental Analysis":
                    stock_analyzer_obj.plot_stock_data(df, stock, market, image_path)
                    fundamentals = stock_api_obj.get_fundamental_data(stock, market)
                    st.subheader("📊 Combined Techno-Fundamental Analysis")
                    st.write(fundamentals)
                
                response = ai_insights_obj.get_ai_insights(image_path, stock, market)
                st.session_state.ai_insights = "".join([part.text for candidate in response.candidates for part in candidate.content.parts])
                
                st.session_state.internal_results_available = True
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                return
    
    if st.session_state.internal_results_available:
        if analysis_type in ["Technical Analysis", "Techno-Fundamental Analysis"]:
            st.subheader("📊 Chart Analysis")
            st.image(st.session_state.image_path, caption=f"{stock} Chart", use_column_width=True)
        st.subheader("🧠 AI Insights")
        st.write(st.session_state.ai_insights)
        if st.button("🔙 Back", use_container_width=True):
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()

if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
