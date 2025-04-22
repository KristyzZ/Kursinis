from abc import ABC, abstractmethod
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import yfinance as yf
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        # Buttons
        ttk.Button(main_frame, text="Add Investment", command=self.add_investment).grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(main_frame, text="Show Portfolio", command=self.show_portfolio).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Show Sector Chart", command=self.show_sector_distribution).grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Remove Investment", command=self.remove_investment).grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Update Investment", command=self.update_investment).grid(row=9, column=0, columnspan=2, pady=5, sticky="ew")

    def show_portfolio(self):
        portfolio_window = tk.Toplevel(self.root)
        portfolio_window.title("Investment Portfolio")

        # Create a treeview to display the portfolio
        columns = ("Name", "Symbol", "Shares", "Purchase Price", "Current Price", "Profit/Loss", "Weekly Change")
        treeview = ttk.Treeview(portfolio_window, columns=columns, show="headings")

        # Set headings
        for col in columns:
            treeview.heading(col, text=col)
            treeview.column(col, anchor="center", width=120)

        treeview.grid(row=0, column=0, padx=10, pady=10)

        for investment in self.portfolio.investments:
            current_price = investment.get_current_price()
            profit_loss = investment.calculate_profit_loss(current_price)

            weekly_change = investment.calculate_weekly_change()
            weekly_text = f"{weekly_change:+.2f}%" if weekly_change is not None else "N/A"

            treeview.insert("", "end", values=(
                investment.name,
                investment.symbol,
                investment.shares,
                f"${investment.purchase_price:.2f}",
                f"${current_price:.2f}",
                f"${profit_loss:.2f}",
                weekly_text  # Add the weekly change here
            ))

        # Double-click event for showing a stock chart (if needed)
        def on_row_double_click(event):
            selected_item = treeview.selection()[0]
            symbol = treeview.item(selected_item, 'values')[1]
            self.show_stock_chart(symbol)

        treeview.bind("<Double-1>", on_row_double_click)

    def add_investment(self):
        try:
            name = self.name_entry.get()
            symbol = self.symbol_entry.get().upper()
            new_shares = float(self.shares_entry.get())
            new_purchase_price = float(self.purchase_price_entry.get())
            stock_info = yf.Ticker(symbol).info
            sector = stock_info.get("sector", "Unknown")

            # Check if investment with the same symbol already exists
            existing_stock = next((inv for inv in self.portfolio.investments if inv.symbol == symbol), None)

            if existing_stock:
                # Merge the new investment with the existing one
                total_shares = existing_stock.shares + new_shares
                total_value = (existing_stock.shares * existing_stock.purchase_price) + (new_shares * new_purchase_price)
                average_price = total_value / total_shares

                existing_stock.shares = total_shares
                existing_stock.purchase_price = average_price
                existing_stock.name = name  # In case name is updated
                existing_stock.sector = sector

                messagebox.showinfo("Updated",
                                    f"Added {new_shares} shares to existing {symbol} investment.\nNew pruchase price: ${average_price:.2f}")
            else:
                # Create new stock if it doesn't exist
                stock = Stock(name, symbol, new_shares, new_purchase_price, sector)
                self.portfolio.add_investment(stock)
                stock.get_current_price()

                messagebox.showinfo("Added", f"Investment in {name} added!")

            # Save the updated portfolio
            self.portfolio.save_to_file()

        except ValueError:
            messagebox.showerror("Error", "Invalid input data!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch stock data.\n{e}")

    def show_stock_chart(self, symbol):
        # Example: Implement functionality to show stock chart
        pass

    def show_sector_distribution(self):
        sector_totals = defaultdict(float)

        for investment in self.portfolio.investments:
            current_price = investment.get_current_price()
            total_value = investment.calculate_value(current_price)
            sector_totals[investment.sector] += total_value

        if not sector_totals:
            messagebox.showinfo("No Data", "No investments to display.")
            return

        sectors = list(sector_totals.keys())
        values = list(sector_totals.values())

        # Plot pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(values, labels=sectors, autopct='%1.1f%%', startangle=140)
        plt.title("Investment Distribution by Sector")
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def show_stock_chart(self, symbol):
        window = tk.Toplevel(self.root)
        window.title(f"{symbol} - Last 7 Days")

        try:
            data = yf.Ticker(symbol).history(period="7d")
            fig, ax = plt.subplots(figsize=(6, 3))
            data["Close"].plot(ax=ax)
            ax.set_title(f"{symbol} - Closing Prices")
            ax.set_ylabel("Price ($)")
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load chart for {symbol}.\n{e}")

    def remove_investment(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showerror("Error", "Please enter the symbol to remove.")
            return

        original_length = len(self.portfolio.investments)
        self.portfolio.remove_investment(symbol)

        if len(self.portfolio.investments) < original_length:
            self.portfolio.save_to_file()
            messagebox.showinfo("Removed", f"Investment with symbol {symbol} removed.")
        else:
            messagebox.showwarning("Not Found", f"No investment found with symbol {symbol}.")

    def update_investment(self):
        try:
            symbol = self.symbol_entry.get().upper()
            for inv in self.portfolio.investments:
                if inv.symbol == symbol:
                    inv.name = self.name_entry.get()
                    inv.shares = float(self.shares_entry.get())
                    inv.purchase_price = float(self.purchase_price_entry.get())

                    # Update sector in case symbol has changed company
                    stock_info = yf.Ticker(symbol).info
                    inv.sector = stock_info.get("sector", "Unknown")

                    self.portfolio.save_to_file()
                    messagebox.showinfo("Updated", f"Investment with symbol {symbol} updated.")
                    return

            messagebox.showwarning("Not Found", f"No investment found with symbol {symbol}.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input data!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not update investment.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()

#Investment types
#unit tests
#login
#export to cvs
#watchlist
#sort
#total summary
#clear search
#choose weekly, monthly, yearly
