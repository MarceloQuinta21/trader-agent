import requests
import config

class MarketDataLoader:
    BASE_URL = config.TRADIER_BASE_URL

    @staticmethod
    def get_quotes(symbols):
        """Fetches current quotes for a list of symbols."""
        url = f"{MarketDataLoader.BASE_URL}/markets/quotes"
        headers = {
            "Authorization": f"Bearer {config.TRADIER_ACCESS_TOKEN}",
            "Accept": "application/json"
        }
        params = {"symbols": ",".join(symbols)}
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Tradier API Error: {response.text}")

    @staticmethod
    def get_historical_data(symbol, interval="daily", start_date=None, end_date=None):
        """Fetches historical bars for a symbol."""
        url = f"{MarketDataLoader.BASE_URL}/markets/history"
        headers = {
            "Authorization": f"Bearer {config.TRADIER_ACCESS_TOKEN}",
            "Accept": "application/json"
        }
        params = {
            "symbol": symbol,
            "interval": interval,
            "start": start_date,
            "end": end_date
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Tradier API Error (History): {response.text}")
    
    @staticmethod
    def get_news(symbol):
        """Fetches news using yfinance as a fallback (Tradier has limited news)."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            return ticker.news
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
