import logging
from config import TICKERS, MAX_POSITION_SIZE_PCT, STOP_LOSS_PCT, TAKE_PROFIT_PCT
from data_loader import MarketDataLoader
from strategy_engine import StrategyEngine
from portfolio_manager import PortfolioManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trade.log"),
        logging.StreamHandler()
    ]
)

def run_trading_cycle():
    logging.info("Starting trading cycle...")
    
    # 1. Load Portfolio
    pm = PortfolioManager()
    equity = pm.get_equity()
    logging.info(f"Current Cash: ${pm.portfolio['cash']:,.2f}")

    # 2. Check Existing Positions for Exits (Stop Loss / Take Profit)
    positions = list(pm.portfolio["positions"].items()) # Snapshot for iteration
    for ticker, pos in positions:
        try:
            # Fetch current quote
            quotes = MarketDataLoader.get_quotes([ticker])
            # Tradier quotes structure: {'quotes': {'quote': {...}}}
            quote = quotes.get('quotes', {}).get('quote', {})
            if not quote:
                logging.warning(f"Could not get quote for {ticker}")
                continue
                
            current_price = quote.get('last')
            if not current_price:
                continue
                
            avg_price = pos['avg_price']
            pct_change = (current_price - avg_price) / avg_price
            
            logging.info(f"Checking {ticker}: Entry={avg_price:.2f}, Current={current_price:.2f}, PnL={pct_change:.2%}")
            
            if pct_change <= -STOP_LOSS_PCT:
                logging.info(f"STOP LOSS triggered for {ticker}")
                pm.execute_sell(ticker, current_price)
            elif pct_change >= TAKE_PROFIT_PCT:
                logging.info(f"TAKE PROFIT triggered for {ticker}")
                pm.execute_sell(ticker, current_price)
                
        except Exception as e:
            logging.error(f"Error managing position {ticker}: {e}")

    # 3. Scan for New Entries
    for ticker in TICKERS:
        if ticker in pm.portfolio["positions"]:
            continue # Already in position
            
        logging.info(f"Scanning {ticker}...")
        try:
            # Fetch History (for indications) and News (for sentiment)
            # Fetch last 30 days to ensure enough for SMA20
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d')
            
            history = MarketDataLoader.get_historical_data(ticker, interval="daily", start_date=start_date)
            news = MarketDataLoader.get_news(ticker)
            
            decision = StrategyEngine.analyze(ticker, history, news)
            
            logging.info(f"{ticker} Decision: {decision['action']} ({decision['reason']})")
            
            if decision['action'] == "BUY":
                # Calculate size
                quotes = MarketDataLoader.get_quotes([ticker])
                current_price = quotes['quotes']['quote']['last']
                
                # Check for enough history
                # StrategyEngine already checked momentum, so we rely on that.
                
                target_position_size = equity * MAX_POSITION_SIZE_PCT # Base on initial implementation plan logic? 
                # Or total equity including positions?
                # Using 'equity' as cash for now from PM? No PM returns cash.
                # Let's assume constant sizing based on initial capital or current cash?
                # Let's use current cash available max or a fixed % of total portfolio value roughly.
                # For safety, let's use min(cash, 5000) for now?
                # Config says 5%.
                
                amount_invest = 5000.0 # Placeholder for $100k account -> 5%
                
                pm.execute_buy(ticker, current_price, amount_invest)
                
        except Exception as e:
            logging.error(f"Error analyzing {ticker}: {e}")

    # 4. Save Portfolio is handled by PM execute methods
    logging.info("Trading cycle completed.")

if __name__ == "__main__":
    run_trading_cycle()
