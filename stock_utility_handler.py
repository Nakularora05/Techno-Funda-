import pandas as pd
import requests
import matplotlib.pyplot as plt

class StockAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_stock_info(self, ticker, market):
        url = f"https://api.example.com/stock/{market}/{ticker}?apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Error fetching stock data")

class StockAnalyzer:
    def json_to_dataframe(self, stock_data, ticker, market):
        df = pd.DataFrame(stock_data['historical'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def plot_stock_data(self, df, ticker, market, save_path):
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['close'], label='Closing Price', color='blue')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f"Stock Price Trend for {ticker} ({market})")
        plt.legend()
        plt.savefig(save_path)
        plt.close()
