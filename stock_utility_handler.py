import requests
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import openai
import os

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
    
    def get_financial_ratios(self, symbol):
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
        df['MA_7'] = df['Close'].rolling(window=7).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_100'] = df['Close'].rolling(window=100).mean()
        df['MA_200'] = df['Close'].rolling(window=200).mean()
        
        plt.plot(df.index, df['Close'], label=f'{stock} Closing Price', color='blue', alpha=0.7)
        plt.plot(df.index, df['MA_7'], label='7-Day MA', color='orange')
        plt.plot(df.index, df['MA_20'], label='20-Day MA', color='red')
        plt.plot(df.index, df['MA_100'], label='100-Day MA', color='green')
        plt.plot(df.index, df['MA_200'], label='200-Day MA', color='purple')
        
        max_price = df['Close'].max()
        min_price = df['Close'].min()
        diff = max_price - min_price
        levels = [max_price, max_price - 0.236 * diff, max_price - 0.382 * diff,
                  max_price - 0.5 * diff, max_price - 0.618 * diff, min_price]
        
        for level in levels:
            plt.axhline(y=level, linestyle='--', alpha=0.5, color='gray')
        
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(f"Stock Price of {stock}")
        plt.legend()
        plt.grid()
        plt.savefig(image_path)
        plt.close()
    
  def analyze_ratios_with_llm(self, ratios):
    openai.api_key = os.getenv("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")  # Load API Key from Environment Variable

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
    api_key = "1UJ6ACYM0P4MHORZ"
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
