import requests

class AIInsights:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_ai_insights(self, image_path, ticker, market):
        url = "https://api.example.com/ai-insights"
        files = {'file': open(image_path, 'rb')}
        data = {'ticker': ticker, 'market': market}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.post(url, files=files, data=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Error fetching AI insights")
