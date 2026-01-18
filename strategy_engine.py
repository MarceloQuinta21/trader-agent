import logging
import pandas as pd
import ta
from google import genai
import config
from datetime import datetime

# Configure Gemini
client = genai.Client(api_key=config.GEMINI_API_KEY)

class TechnicalAnalyzer:
    @staticmethod
    def calculate_indicators(df):
        """Calculates SMA and RSI."""
        if df.empty:
            return df
        
        # Ensure data is sorted
        df = df.sort_index()
        
        # SMA
        sma_indicator = ta.trend.SMAIndicator(close=df['close'], window=config.SMA_PERIOD)
        df['SMA'] = sma_indicator.sma_indicator()
        
        # RSI
        rsi_indicator = ta.momentum.RSIIndicator(close=df['close'], window=config.RSI_PERIOD)
        df['RSI'] = rsi_indicator.rsi()
        
        return df

class SentimentAnalyzer:
    @staticmethod
    def analyze_news(ticker, news_items):
        """Prompts Gemini to analyze news sentiment."""
        if not news_items:
            return {"sentiment": "NEUTRAL", "reasoning": "No news found."}

        # Prepare context from news items (title + summary/link)
        news_text = "\n".join([f"- {item.get('title', 'No Title')} ({item.get('summary', 'No Summary')})" for item in news_items[:5]])
        
        prompt = f"""
        Analyze the sentiment of the following recent news headlines for the stock '{ticker}'.
        Determine if the sentiment is BULLISH, BEARISH, or NEUTRAL for the short-term price action (next 24 hours).
        
        News:
        {news_text}
        
        Return a JSON object with the following keys:
        - "sentiment": "BULLISH", "BEARISH", or "NEUTRAL"
        - "confidence": A score from 0.0 to 1.0
        - "reasoning": A brief explanation.
        
        Output only JSON.
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite', 
                contents=prompt
            )
            # Simple cleaning if the model returns markdown code blocks
            text = response.text.replace('```json', '').replace('```', '').strip()
            import json
            return json.loads(text)
        except Exception as e:
            logging.error(f"Gemini Analysis Failed for {ticker}: {e}")
            return {"sentiment": "NEUTRAL", "reasoning": "Analysis failed."}

class StrategyEngine:
    @staticmethod
    def analyze(ticker, market_data, news_data):
        """Combines Technical and Sentiment signals."""
        logging.info(f"Analyzing {ticker} strategy...")
        
        # 1. Technical Analysis
        df = pd.DataFrame(market_data['history']['day'])
        # Tradier returns date as 'date' string, convert to datetime if needed, or just use as is for sort
        # Assuming 'close' is present
        
        df = TechnicalAnalyzer.calculate_indicators(df)
        last_row = df.iloc[-1]
        
        price = last_row['close']
        sma = last_row['SMA']
        rsi = last_row['RSI']
        
        logging.info(f"{ticker}: Price={price}, SMA={sma}, RSI={rsi}")
        
        # Momentum Signal
        # Bullish: Price > SMA AND 50 < RSI < 70
        is_bullish_momentum = (price > sma) and (config.RSI_LOWER < rsi < config.RSI_UPPER)
        
        if not is_bullish_momentum:
            return {"action": "HOLD", "reason": f"No momentum (RSI={rsi:.1f}, Price vs SMA)"}
            
        # 2. Sentiment Analysis (only checks if technicals are good)
        sentiment = SentimentAnalyzer.analyze_news(ticker, news_data)
        logging.info(f"{ticker} Sentiment: {sentiment}")
        
        if sentiment.get("sentiment") == "BULLISH" and sentiment.get("confidence", 0) > 0.6:
            return {"action": "BUY", "reason": f"Momentum + Bullish News ({sentiment['reasoning']})"}
        
        return {"action": "HOLD", "reason": "Momentum good but Sentiment uncertain"}
