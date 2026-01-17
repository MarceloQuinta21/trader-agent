import json
import os
import config
import logging

class PortfolioManager:
    FILE_PATH = "portfolio.json"

    def __init__(self):
        self.portfolio = self.load_portfolio()

    def load_portfolio(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                return json.load(f)
        else:
            return {
                "cash": config.INITIAL_CAPITAL,
                "positions": {},  # "AAPL": {"shares": 10, "avg_price": 150.0}
                "history": []
            }

    def save_portfolio(self):
        with open(self.FILE_PATH, 'w') as f:
            json.dump(self.portfolio, f, indent=4)

    def get_equity(self):
        # Rough estimate: cash + value of positions (need current prices, passed recursively or fetched? 
        # For simplicity, just return cash for buying power checks, or track total separately)
        # To get real equity, we'd need current market prices. 
        # For now, let's just return cash for the purpose of checking buying power.
        return self.portfolio["cash"]

    def execute_buy(self, ticker, price, amount_usd):
        """Executes a paper buy order."""
        if self.portfolio["cash"] < amount_usd:
            logging.warning(f"Insufficient funds to buy {ticker}. Cash: {self.portfolio['cash']}, Needed: {amount_usd}")
            return False

        shares = amount_usd / price
        self.portfolio["cash"] -= amount_usd
        
        if ticker in self.portfolio["positions"]:
            # Average down/up
            pos = self.portfolio["positions"][ticker]
            total_shares = pos["shares"] + shares
            total_cost = (pos["shares"] * pos["avg_price"]) + amount_usd
            pos["shares"] = total_shares
            pos["avg_price"] = total_cost / total_shares
        else:
            self.portfolio["positions"][ticker] = {
                "shares": shares,
                "avg_price": price
            }
            
        self._log_trade("BUY", ticker, price, shares, amount_usd)
        self.save_portfolio()
        logging.info(f"BOUGHT {ticker}: {shares:.2f} shares @ {price:.2f}")
        return True

    def execute_sell(self, ticker, price, shares=None):
        """Executes a paper sell order. If shares is None, sells all."""
        if ticker not in self.portfolio["positions"]:
            logging.warning(f"Cannot sell {ticker}, not in portfolio.")
            return False
            
        pos = self.portfolio["positions"][ticker]
        current_shares = pos["shares"]
        
        if shares is None or shares > current_shares:
            shares = current_shares
            
        amount_usd = shares * price
        
        self.portfolio["cash"] += amount_usd
        pos["shares"] -= shares
        
        if pos["shares"] < 1e-6: # Float tolerance
            del self.portfolio["positions"][ticker]
            
        self._log_trade("SELL", ticker, price, shares, amount_usd)
        self.save_portfolio()
        logging.info(f"SOLD {ticker}: {shares:.2f} shares @ {price:.2f}")
        return True

    def _log_trade(self, action, ticker, price, shares, amount):
        from datetime import datetime
        trade_record = {
            "date": datetime.now().isoformat(),
            "action": action,
            "ticker": ticker,
            "price": price,
            "shares": shares,
            "amount": amount
        }
        self.portfolio["history"].append(trade_record)
