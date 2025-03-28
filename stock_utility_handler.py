import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np
import openai
import os


class StockAnalyzer:
    def __init__(self):
        pass

    def json_to_dataframe(self, json_data, stock, extra_param=None):
        """Converts stock market JSON data to a Pandas DataFrame."""
        if "Time Series (Daily)" not in json_data:
            raise ValueError("Invalid JSON data format")
        
        data = json_data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df


class StockAPI:
    """Fetches stock data and fundamental analysis."""
    
    def __init__(self, api_key):
        self.api_key = api_key

    def get_stock_info(self, symbol):
        """Fetch stock data from AlphaVantage API."""
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        response = requests.get("https://www.alphavantage.co/query", params=params)
        return response.json()
    
    def get_fundamental_data(self, symbol):
        """Fetch fundamental data from Yahoo Finance."""
        stock = yf.Ticker(symbol)
        fundamentals = {
            "Net Income": stock.info.get("netIncome", "N/A"),
            "ROE": stock.info.get("returnOnEquity", "N/A"),
            "ROA": stock.info.get("returnOnAssets", "N/A"),
            "Debt to Equity": stock.info.get("debtToEquity", "N/A"),
            "Dividend Yield": stock.info.get("dividendYield", "N/A")
        }
        return fundamentals
    
    def get_financial_ratios(self, symbol):
        """Extracts key financial ratios from Yahoo Finance."""
        stock = yf.Ticker(symbol)
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        def get_value(df, key):
            if key in df.index:
                return df.loc[key].iloc[0]
            return None
        
        revenue = get_value(financials, "Total Revenue")
        net_income = get_value(financials, "Net Income")
        total_assets = get_value(balance_sheet, "Total Assets")
        total_liabilities = get_value(balance_sheet, "Total Liabilities Net Minority Interest")
        stockholders_equity = get_value(balance_sheet, "Stockholders Equity")
        invested_capital = get_value(balance_sheet, "Invested Capital")
        ebit = get_value(financials, "EBIT")
        operating_cashflow = get_value(cashflow, "Operating Cash Flow")
        total_debt = get_value(balance_sheet, "Total Debt")
        current_assets = get_value(balance_sheet, "Current Assets")
        current_liabilities = get_value(balance_sheet, "Current Liabilities")
        
        ratios = {
            "ROIC (%)": (net_income / invested_capital) * 100 if net_income and invested_capital else "N/A",
            "ROA (%)": (net_income / total_assets) * 100 if net_income and total_assets else "N/A",
            "Debt-to-Equity": total_liabilities / stockholders_equity if total_liabilities and stockholders_equity else "N/A",
            "Current Ratio": current_assets / current_liabilities if current_assets and current_liabilities else "N/A",
            "EBIT Margin (%)": (ebit / revenue) * 100 if ebit and revenue else "N/A",
            "Operating Cash Flow to Debt": operating_cashflow / total_debt if operating_cashflow and total_debt else "N/A"
        }
        
        return ratios

class StockAnalyzer:
    """Processes stock data and generates charts."""
    
    def json_to_dataframe(self, data):
        """Converts JSON stock data into a DataFrame."""
        time_series = data.get("Time Series (Daily)", {})
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adj Close",
            "6. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)
        return df
    
    def plot_stock_data(self, df, stock, image_path):
        """Plots stock price data along with moving averages."""
        plt.figure(figsize=(14, 8))
        df['MA_7'] = df['Close'].rolling(window=7).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_100'] = df['Close'].rolling(window=100).mean()
        df['MA_200'] = df['Close'].rolling(window=200).mean()
        
        plt.plot(df.index, df['Close'], label=f'{stock} Closing Price', color='blue', alpha=0.7)
        plt.plot(df.index, df['MA_7'], label='7-Day MA', color='orange')
        plt.plot(df.index, df['MA_20'], label='20-Day MA', color='red')
        plt.plot(df.index, df['MA_100'], label='100-Day MA', color='green')
        plt.plot(df.index, df['MA_200'], label='200-Day MA', color='purple')
        
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(f"Stock Price of {stock}")
        plt.legend()
        plt.grid()
        plt.savefig(image_path)
        plt.close()
    
    def analyze_ratios_with_llm(self, ratios):
        """Generates investment insights using OpenAI GPT-4."""
        openai.api_key = os.getenv("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")
        
        prompt = f"""Given these financial ratios:
        {ratios}, provide an investment recommendation."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial expert providing stock investment insights."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    api_key = "JXVWA9W91RARPC46"
    stock_api = StockAPI(api_key)
    stock_analyzer = StockAnalyzer()
    
    symbol = input("Enter the stock ticker (e.g., AAPL, TSLA): ").strip().upper()
    
    stock_data = stock_api.get_stock_info(symbol)
    df = stock_analyzer.json_to_dataframe(stock_data)
    stock_analyzer.plot_stock_data(df, symbol, "stock_chart.png")
    
    fundamentals = stock_api.get_fundamental_data(symbol)
    ratios = stock_api.get_financial_ratios(symbol)
    
    print("\nFinancial Ratios:")
    for key, value in ratios.items():
        print(f"{key}: {value}")
    
    print("\nAnalyzing investment potential using LLM...")
    recommendation = stock_analyzer.analyze_ratios_with_llm(ratios)
    print("\nInvestment Recommendation:")
    print(recommendation)
