import os
import requests
from pytrends.request import TrendReq
from transformers import pipeline

class SentimentEngine:
    def __init__(self, news_api_key):
        self.news_api_key = news_api_key
        # Initialize models once to save time
        print("⏳ Loading Sentiment Models...")
        self.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def fetch_signals(self, query):
        """Orchestrates fetching news and trends."""
        print(f"📡 Scanning global signals for: '{query}'...")
        
        # 1. NewsAPI
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_api_key}&pageSize=15"
        try:
            response = requests.get(url)
            data = response.json()
            articles = [f"{a['title']} {a['description']}" for a in data.get('articles', []) if a['title']]
        except Exception as e:
            print(f"⚠️ NewsAPI Error: {e}")
            articles = []

        # 2. Google Trends
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload(kw_list=[query], timeframe="now 7-d")
            trends = pytrends.interest_over_time()
            trend_score = trends[query].iloc[-1] if not trends.empty else 0
        except Exception as e:
            print(f"⚠️ Trends Error: {e}")
            trend_score = 0
            
        return articles, trend_score

    def calculate_urgency(self, texts):
        """Returns a score from 0.0 to 1.0 based on negative sentiment."""
        if not texts: 
            return 0.5
        
        results = self.analyzer(texts[:10], truncation=True)
        neg_count = sum(1 for r in results if r['label'] == 'NEGATIVE')
        return neg_count / len(results)
