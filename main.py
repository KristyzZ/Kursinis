from abc import ABC, abstractmethod
import json
import tkinter as tk
from tkinter import messagebox
import yfinance as yf


# Abstract investment class
class Investment(ABC):
    def __init__(self, name, symbol, amount, purchase_price):
        self.name = name
        self.symbol = symbol
        self.amount = amount
        self.purchase_price = purchase_price

    @abstractmethod
    def calculate_value(self, current_price):
        pass

    def calculate_profit_loss(self, current_price):
        return (current_price - self.purchase_price) * self.amount


# Stock class
class Stock(Investment):
    def __init__(self, name, symbol, amount, purchase_price, sector):
        super().__init__(name, symbol, amount, purchase_price)
        self.sector = sector

    def calculate_value(self, current_price):
        return self.amount * current_price

    def get_current_price(self):
        try:
            stock_data = yf.Ticker(self.symbol)
            return stock_data.history(period="1d")['Close'].iloc[-1]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch stock price for {self.symbol}.\n{e}")
            return self.purchase_price


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
        data = [vars(inv) for inv in self.investments]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename="portfolio.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.investments = [Stock(**inv) for inv in data]
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
        self.manager = PortfolioManager()
        self.portfolio = self.manager.portfolio

        root.title("Investment Portfolio")

        tk.Label(root, text="Company Name:").grid(row=0, column=0)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1)

        tk.Label(root, text="Symbol:").grid(row=1, column=0)
        self.symbol_entry = tk.Entry(root)
        self.symbol_entry.grid(row=1, column=1)

        tk.Label(root, text="Quantity:").grid(row=2, column=0)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=2, column=1)

        tk.Label(root, text="Purchase Price:").grid(row=3, column=0)
        self.purchase_price_entry = tk.Entry(root)
        self.purchase_price_entry.grid(row=3, column=1)

        tk.Label(root, text="Sector:").grid(row=4, column=0)
        self.sector_entry = tk.Entry(root)
        self.sector_entry.grid(row=4, column=1)

        tk.Button(root, text="Add Investment", command=self.add_investment).grid(row=5, column=0, columnspan=2)
        tk.Button(root, text="Show Portfolio", command=self.show_portfolio).grid(row=6, column=0, columnspan=2)
        tk.Button(root, text="Update Prices", command=self.update_prices).grid(row=7, column=0, columnspan=2)
        tk.Button(root, text="Save", command=self.portfolio.save_to_file).grid(row=8, column=0, columnspan=2)

    def add_investment(self):
        try:
            name = self.name_entry.get()
            symbol = self.symbol_entry.get().upper()
            amount = int(self.amount_entry.get())
            purchase_price = float(self.purchase_price_entry.get())
            sector = self.sector_entry.get()

            stock = Stock(name, symbol, amount, purchase_price, sector)
            self.portfolio.add_investment(stock)
            messagebox.showinfo("Added", f"Investment in {name} added!")
        except ValueError:
            messagebox.showerror("Error", "Invalid data!")

    def show_portfolio(self):
        portfolio_str = "\n".join(
            [f"{inv.name} ({inv.symbol}): {inv.amount} units at {inv.purchase_price} EUR" for inv in
             self.portfolio.investments])
        messagebox.showinfo("Portfolio", portfolio_str if portfolio_str else "Portfolio is empty")

    def update_prices(self):
        total_value = self.portfolio.get_total_value()
        messagebox.showinfo("Updated", f"Total portfolio value: {total_value:.2f} EUR")


data = yf.Ticker("AAPL")
print(data.info)
print(data.history(period="1d")['Close'].iloc[-1])


if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()
