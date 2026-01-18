# 🤖 Sentiment-Augmented Momentum Trading Agent

A Python-based trading agent that manages a **Tradier Sandbox Paper Trading** portfolio. It combines technical momentum indicators with AI-powered sentiment analysis from **Google Gemini** to execute trades automatically.

## 🚀 Strategy: "News-Confirmed Momentum"
The agent scans a list of top tech stocks every hour and executes the following logic:

1.  **Technical Filter**:
    *   **Price > SMA(20)**: Trend is Up.
    *   **RSI (50-70)**: Healthy Momentum (not overbought).
2.  **Sentiment Confirmation**:
    *   Fetches news headlines for the stock.
    *   Asks **Google Gemini** if the news is "BULLISH".
3.  **Execution**:
    *   **Buy**: If both Technicals and Sentiment are positive.
    *   **Sell**: Validates Stop Loss (-2%) and Take Profit (+4%) on every run.

## 🛠️ Tech Stack
*   **Python 3.9+**
*   **Tradier API**: For Market Data (Price/History) and Paper Trading (Balances/Orders).
*   **Google Gemini API**: For Sentiment Analysis (`google-genai` SDK).
*   **Streamlit**: For the User Dashboard.
*   **GitHub Actions**: For 24/7 Automation (Runs hourly M-F).

## ⚙️ Setup

### 1. Prerequisites
*   A **Tradier Sandbox Account** (Free). You need your **Access Token** and **Account ID**.
*   A **Google Gemini API Key** (Free tier available).

### 2. Installation
```bash
git clone https://github.com/MarceloQuinta21/trader-agent.git
cd trader-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```bash
ANTHROPIC_API_KEY="your_key" # Optional (if using other tools)
GEMINI_API_KEY="your_gemini_key"
TRADIER_SANDBOX_API_KEY="your_tradier_token"
TRADIER_SANDBOX_ACCOUNT_ID="your_tradier_account_id"
```

## 🏃 Usage

### Manual Run
To execute a single trading cycle immediately:
```bash
python main.py
```

### Dashboard
To view your live account balance and positions:
```bash
streamlit run dashboard/app.py
```

### Automation (GitHub Actions)
The agent is configured to run automatically on GitHub Actions.
1.  Push the code to GitHub.
2.  Go to **Settings > Secrets and variables > Actions**.
3.  Add the following Repository Secrets:
    *   `GEMINI_API_KEY`
    *   `TRADIER_ACCESS_TOKEN`
    *   `TRADIER_SANDBOX_ACCOUNT_ID`

## 📂 Project Structure
*   `main.py`: Entry point for the trading logic.
*   `strategy_engine.py`: Encapsulates Technical (TA-Lib) and Sentiment (Gemini) analysis.
*   `portfolio_manager.py`: Connects to Tradier API to check balances and place orders.
*   `config.py`: Configuration settings (Tickers, Risk parameters).
*   `dashboard/`: Streamlit app code.

---
**Disclaimer**: This is for educational purposes and paper trading competitions only. Not financial advice.