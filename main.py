from abc import ABC, abstractmethod
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import yfinance as yf
import os

# Abstract investment class
class Investment(ABC):
    def __init__(self, name, symbol, shares, purchase_price):
        self.name = name
        self.symbol = symbol
        self.shares = shares
        self.purchase_price = purchase_price

    @abstractmethod
    def calculate_value(self, current_price):
        pass

    def calculate_profit_loss(self, current_price):
        return (current_price - self.purchase_price) * self.shares


# Stock class
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


# Portfolio class
class Portfolio:
    def __init__(self):
        self.investments = []

    def add_investment(self, investment):
        self.investments.append(investment)

    def remove_investment(self, symbol):
        self.investments = [inv for inv in self.investments if inv.symbol != symbol]

    def get_total_value(self):
        return sum(inv.calculate_value(inv.get_current_price()) for inv in self.investments)

    def save_to_file(self, filename="portfolio.json"):
        data = [inv.to_dict() for inv in self.investments]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename="portfolio.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.investments = []
                for inv in data:
                    if inv["type"] == "stock":
                        stock = Stock(
                            inv["name"],
                            inv["symbol"],
                            inv["shares"],
                            inv["purchase_price"],
                            inv["sector"]
                        )
                        self.investments.append(stock)
        except FileNotFoundError:
            pass


# Singleton Portfolio Manager
class PortfolioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
            cls._instance.portfolio = Portfolio()
        return cls._instance


# GUI functionality
class PortfolioApp:
    def __init__(self, root):
        self.root = root
        self.manager = PortfolioManager()
        self.portfolio = self.manager.portfolio
        self.portfolio.load_from_file()

        root.title("Investment Portfolio")
       # root.geometry("400x300")

        # Apply some style
        style = ttk.Style()
        style.theme_use("clam")

        # Main frame with padding
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Company Name
        ttk.Label(main_frame, text="Company Name:").grid(row=0, column=0, sticky="e", pady=5)
        self.name_entry = ttk.Entry(main_frame)
        self.name_entry.grid(row=0, column=1, pady=5)

        # Symbol
        ttk.Label(main_frame, text="Symbol:").grid(row=1, column=0, sticky="e", pady=5)
        self.symbol_entry = ttk.Entry(main_frame)
        self.symbol_entry.grid(row=1, column=1, pady=5)

        # Shares
        ttk.Label(main_frame, text="Shares:").grid(row=2, column=0, sticky="e", pady=5)
        self.shares_entry = ttk.Entry(main_frame)
        self.shares_entry.grid(row=2, column=1, pady=5)

        # Purchase Price
        ttk.Label(main_frame, text="Purchase Price:").grid(row=3, column=0, sticky="e", pady=5)
        self.purchase_price_entry = ttk.Entry(main_frame)
        self.purchase_price_entry.grid(row=3, column=1, pady=5)

        # Sector
        ttk.Label(main_frame, text="Sector:").grid(row=4, column=0, sticky="e", pady=5)
        self.sector_entry = ttk.Entry(main_frame)
        self.sector_entry.grid(row=4, column=1, pady=5)

        # Buttons
        ttk.Button(main_frame, text="Add Investment", command=self.add_investment).grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(main_frame, text="Show Portfolio", command=self.show_portfolio).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")

    def add_investment(self):
        try:
            name = self.name_entry.get()
            symbol = self.symbol_entry.get().upper()
            shares = float(self.shares_entry.get())
            purchase_price = float(self.purchase_price_entry.get())
            sector = self.sector_entry.get()

            stock = Stock(name, symbol, shares, purchase_price, sector)
            self.portfolio.add_investment(stock)

            # Fetch the current price immediately after adding the investment
            stock.get_current_price()

            # Automatically save the portfolio
            self.portfolio.save_to_file()

            messagebox.showinfo("Added", f"Investment in {name} added!")
        except ValueError:
            messagebox.showerror("Error", "Invalid input data!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch stock data.\n{e}")

    def show_portfolio(self):
        portfolio_window = tk.Toplevel(self.root)
        portfolio_window.title("Investment Portfolio")

        # Create a treeview to display the portfolio
        treeview = ttk.Treeview(portfolio_window,
                                columns=("Name", "Symbol", "Shares", "Purchase Price", "Current Price", "Profit/Loss"))
        treeview.heading("#1", text="Name")
        treeview.heading("#2", text="Symbol")
        treeview.heading("#3", text="Shares")
        treeview.heading("#4", text="Purchase Price")
        treeview.heading("#5", text="Current Price")
        treeview.heading("#6", text="Profit/Loss")
        treeview.grid(row=0, column=0, padx=10, pady=10)

        for investment in self.portfolio.investments:
            current_price = investment.get_current_price()  # Ensure current price is fetched
            profit_loss = investment.calculate_profit_loss(current_price)

            treeview.insert("", "end", values=(
                investment.name,
                investment.symbol,
                investment.shares,
                f"${investment.purchase_price:.2f}",
                f"${current_price:.2f}",  # Display current price
                f"${profit_loss:.2f}"
            ))

        portfolio_window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()
