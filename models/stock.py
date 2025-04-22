import yfinance as yf
from tkinter import messagebox
from models.investment import Investment

class Stock(Investment):
    def __init__(self, name, symbol, shares, purchase_price, sector):
        super().__init__(name, symbol, shares, purchase_price)
        self.sector = sector
        self.current_price = None  # Add current_price attribute to store the real-time stock price

    def calculate_value(self, current_price):
        return self.shares * current_price

    def get_current_price(self):
        try:
            stock_data = yf.Ticker(self.symbol)
            self.current_price = stock_data.history(period="1d")['Close'].iloc[-1]  # Update current_price with real-time price
            return self.current_price
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch stock price for {self.symbol}.\n{e}")
            return self.purchase_price  # Fallback to purchase price if unable to fetch the current price

    def to_dict(self):
        return {
            "type": "stock",
            "name": self.name,
            "symbol": self.symbol,
            "shares": self.shares,
            "purchase_price": self.purchase_price,
            "sector": self.sector
        }

    def calculate_weekly_change(self):
        try:
            stock_data = yf.Ticker(self.symbol).history(period="7d")
            if len(stock_data) >= 2:
                start_price = stock_data["Close"].iloc[0]
                end_price = stock_data["Close"].iloc[-1]
                change = ((end_price - start_price) / start_price) * 100
                return round(change, 2)
        except:
            return None