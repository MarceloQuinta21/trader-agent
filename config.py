import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TRADIER_ACCESS_TOKEN = os.getenv("TRADIER_SANDBOX_API_KEY")

# Tradier Environment
# Sandbox: https://sandbox.tradier.com/v1
# Production: https://api.tradier.com/v1
TRADIER_BASE_URL = "https://sandbox.tradier.com/v1"

# Trading Parameters
INITIAL_CAPITAL = 100000.0
MAX_POSITION_SIZE_PCT = 0.05  # 5% of equity
STOP_LOSS_PCT = 0.02          # 2% loss
TAKE_PROFIT_PCT = 0.04        # 4% gain

# Indicators
SMA_PERIOD = 20
RSI_PERIOD = 14
RSI_LOWER = 50
RSI_UPPER = 70

# Tickers to Monitor (Top Liquid Tech)
TICKERS = [
    "AAPL", "NVDA", "TSLA", "AMD", "MSFT", 
    "AMZN", "GOOGL", "META", "NFLX", "INTC",
    "QCOM", "TXN", "AVGO", "MU", "CSCO",
    "ADBE", "CRM", "PYPL", "UBER", "ABNB"
]
