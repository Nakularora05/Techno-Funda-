import requests
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

class StockAPI:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_stock_info(self, symbol):
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
    def json_to_dataframe(self, data):
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
        
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(f"Stock Price of {stock}")
        plt.legend()
        plt.grid()
        plt.savefig(image_path)
        plt.close()
    
    def get_financial_ratios(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            
            def get_value(df, key):
                return df.loc[key].iloc[0] if key in df.index else None
            
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
        except Exception as e:
            return {"Error": str(e)}

# Main Execution
if __name__ == "__main__":
    api_key = "YOUR_ALPHAVANTAGE_API_KEY"
    stock_api = StockAPI(api_key)
    stock_analyzer = StockAnalyzer()
    
    symbol = input("Enter the stock ticker (e.g., AAPL, TSLA): ").strip().upper()
    
    print("\nFetching stock data...")
    stock_data = stock_api.get_stock_info(symbol)
    df = stock_analyzer.json_to_dataframe(stock_data)
    stock_analyzer.plot_stock_data(df, symbol, "stock_chart.png")
    print("Stock chart saved as 'stock_chart.png'.")
    
    print("\nFetching financial ratios...")
    ratios = stock_analyzer.get_financial_ratios(symbol)
    if "Error" in ratios:
        print("Error fetching data:", ratios["Error"])
    else:
        for key, value in ratios.items():
            print(f"{key}: {value}")
