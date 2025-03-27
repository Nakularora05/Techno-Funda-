import requests
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

class StockAPI:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_stock_info(self, symbol, market):
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        response = requests.get("https://www.alphavantage.co/query", params=params)
        return response.json()
    
    def get_fundamental_data(self, symbol):
        stock = yf.Ticker(symbol)
        fundamentals = {
            "Net Income": stock.info.get("netIncome", "N/A"),
            "ROE": stock.info.get("returnOnEquity", "N/A"),
            "ROA": stock.info.get("returnOnAssets", "N/A"),
            "Debt to Equity": stock.info.get("debtToEquity", "N/A"),
            "Dividend Yield": stock.info.get("dividendYield", "N/A")
        }
        return fundamentals

class StockAnalyzer:
    def json_to_dataframe(self, data, stock, market):
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
    
    def plot_stock_data(self, df, stock, market, image_path):
        plt.figure(figsize=(14, 8))
        
        # Moving Averages
        df['MA_7'] = df['Close'].rolling(window=7).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_100'] = df['Close'].rolling(window=100).mean()
        df['MA_200'] = df['Close'].rolling(window=200).mean()
        
        plt.plot(df.index, df['Close'], label=f'{stock} Closing Price', color='blue', alpha=0.7)
        plt.plot(df.index, df['MA_7'], label='7-Day MA', color='orange')
        plt.plot(df.index, df['MA_20'], label='20-Day MA', color='red')
        plt.plot(df.index, df['MA_100'], label='100-Day MA', color='green')
        plt.plot(df.index, df['MA_200'], label='200-Day MA', color='purple')
        
        # Fibonacci Retracement
        max_price = df['Close'].max()
        min_price = df['Close'].min()
        diff = max_price - min_price
        levels = [max_price, max_price - 0.236 * diff, max_price - 0.382 * diff,
                  max_price - 0.5 * diff, max_price - 0.618 * diff, min_price]
        
        for level in levels:
            plt.axhline(y=level, linestyle='--', alpha=0.5, color='gray')
        
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(f"Stock Price of {stock} ({market})")
        plt.legend()
        plt.grid()
        plt.savefig(image_path)
        plt.close()
    
    def plot_fundamentals(self, fundamentals, stock):
        metrics = list(fundamentals.keys())
        values = list(fundamentals.values())
        
        plt.figure(figsize=(12, 6))
        plt.bar(metrics, values, color=['blue', 'orange', 'green', 'red', 'purple'])
        plt.xlabel("Fundamental Metrics")
        plt.ylabel("Values")
        plt.title(f"Fundamental Analysis for {stock}")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()

# Usage Example
if __name__ == "__main__":
    api_key = "YOUR_ALPHAVANTAGE_API_KEY"
    stock_api = StockAPI(api_key)
    stock_analyzer = StockAnalyzer()
    
    symbol = "AAPL"
    market = "NASDAQ"
    
    # Fetch stock data
    stock_data = stock_api.get_stock_info(symbol, market)
    df = stock_analyzer.json_to_dataframe(stock_data, symbol, market)
    stock_analyzer.plot_stock_data(df, symbol, market, "stock_chart.png")
    
    # Fetch fundamental data
    fundamentals = stock_api.get_fundamental_data(symbol)
    stock_analyzer.plot_fundamentals(fundamentals, symbol)
