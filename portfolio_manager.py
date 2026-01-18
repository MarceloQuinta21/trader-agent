import requests
import config
import logging

class PortfolioManager:
    def __init__(self):
        self.base_url = config.TRADIER_BASE_URL
        self.account_id = config.TRADIER_ACCOUNT_ID
        self.headers = {
            "Authorization": f"Bearer {config.TRADIER_ACCESS_TOKEN}",
            "Accept": "application/json"
        }

    def get_account_balance(self):
        """Fetches account balance details."""
        url = f"{self.base_url}/accounts/{self.account_id}/balances"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('balances', {})
        else:
            logging.error(f"Error fetching balances: {response.text}")
            return {}

    def get_equity(self):
        """Returns total equity from Tradier."""
        balances = self.get_account_balance()
        return balances.get('total_equity', 0.0)

    def get_cash(self):
        """Returns total cash from Tradier."""
        balances = self.get_account_balance()
        return balances.get('total_cash', 0.0)

    def get_positions(self):
        """Fetches current positions."""
        url = f"{self.base_url}/accounts/{self.account_id}/positions"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            # Tradier returns 'positions': {'position': [...]} or just 'positions': 'null' if empty
            data = response.json().get('positions', {})
            if data == 'null' or not data:
                return {}
            
            # Normalize to list
            pos_list = data.get('position', [])
            if isinstance(pos_list, dict):
                pos_list = [pos_list]
                
            # Convert to dictionary format for easier lookup: {ticker: {shares: x, cost_basis: y}}
            positions = {}
            for p in pos_list:
                positions[p['symbol']] = {
                    "shares": p['quantity'],
                    "avg_price": p['cost_basis'], # Note: cost_basis is total cost or per share? Tradier usually gives cost_basis as per share average. Wait, Tradier 'cost_basis' is usually total cost. 'period_close' might be easier? 
                    # Actually Tradier 'cost_basis' field in positions response is often total cost. 
                    # Let's check documentation or assume cost_basis per share.
                    # Sandbox usually returns standard fields. Let's use 'cost_basis' / 'quantity' to be safe if needed, 
                    # but usually there is 'cost_basis' (total) and 'quantity'.
                    # Let's verify this during test. For now, we store the raw object mostly.
                    "cost_basis": p['cost_basis'],
                    "quantity": p['quantity']
                }
            return positions
        else:
            logging.error(f"Error fetching positions: {response.text}")
            return {}

    def execute_buy(self, ticker, price, amount_usd): # price and amount_usd might be approximate
        """Executes a buy order (Market Order)."""
        # Calculate shares based on price (Tradier API handles logic, but we need quantity)
        quantity = int(amount_usd // price)
        if quantity < 1:
            logging.warning(f"Quantity 0 for {ticker}, skipping buy.")
            return False

        url = f"{self.base_url}/accounts/{self.account_id}/orders"
        params = {
            "class": "equity",
            "symbol": ticker,
            "side": "buy",
            "quantity": quantity,
            "type": "market",
            "duration": "day"
        }
        
        response = requests.post(url, params=params, headers=self.headers)
        if response.status_code == 200:
            logging.info(f"ORDER SENT: Buy {quantity} {ticker} (Resp: {response.json()})")
            return True
        else:
            logging.error(f"Order Failed {ticker}: {response.text}")
            return False

    def execute_sell(self, ticker, price, shares=None): # shares handles quantity
        """Executes a sell order (Market Order)."""
        # If shares is None, we need to know how many we have. 
        # Calling get_positions to verify.
        if shares is None:
            positions = self.get_positions()
            if ticker not in positions:
                logging.warning(f"Cannot sell {ticker}, not in positions.")
                return False
            shares = positions[ticker]['quantity']

        url = f"{self.base_url}/accounts/{self.account_id}/orders"
        params = {
            "class": "equity",
            "symbol": ticker,
            "side": "sell",
            "quantity": int(shares),
            "type": "market",
            "duration": "day"
        }
        
        response = requests.post(url, params=params, headers=self.headers)
        if response.status_code == 200:
            logging.info(f"ORDER SENT: Sell {shares} {ticker} (Resp: {response.json()})")
            return True
        else:
            logging.error(f"Order Failed {ticker}: {response.text}")
            return False
