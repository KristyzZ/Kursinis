import tkinter as tk
from tkinter import messagebox, ttk
from collections import defaultdict
from models.portfolio import PortfolioManager
from models.stock import Stock
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.file_operations import write_to_csv


class PortfolioApp:
    def __init__(self, root):
        self.root = root
        self.manager = PortfolioManager()
        self.portfolio = self.manager.portfolio
        self.portfolio.load_from_file()

        root.title("Investment Portfolio")

        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="Company Name:").grid(row=0, column=0, sticky="e", pady=5)
        self.name_entry = ttk.Entry(main_frame)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Symbol:").grid(row=1, column=0, sticky="e", pady=5)
        self.symbol_entry = ttk.Entry(main_frame)
        self.symbol_entry.grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Shares:").grid(row=2, column=0, sticky="e", pady=5)
        self.shares_entry = ttk.Entry(main_frame)
        self.shares_entry.grid(row=2, column=1, pady=5)

        ttk.Label(main_frame, text="Purchase Price:").grid(row=3, column=0, sticky="e", pady=5)
        self.purchase_price_entry = ttk.Entry(main_frame)
        self.purchase_price_entry.grid(row=3, column=1, pady=5)

        # Buttons
        ttk.Button(main_frame, text="Add Investment", command=self.add_investment).grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(main_frame, text="Show Portfolio", command=self.show_portfolio).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Show Sector Chart", command=self.show_sector_distribution).grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Remove Investment", command=self.remove_investment).grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Update Investment", command=self.update_investment).grid(row=9, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Download Portfolio", command=self.export_portfolio).grid(row=10, column=0, columnspan=2, pady=5, sticky="ew")

    def show_portfolio(self):
        sort_keys = {
            "Name": "name",
            "Symbol": "symbol",
            "Shares": "shares",
            "Purchase Price": "purchase_price",
            "Current Price": "current_price",
            "Profit/Loss": "profit_loss",
            "Change": "change"
        }

        def update_treeview_with_change(period):
            sort_key = sort_keys.get(sort_var.get(), "name")
            yf_period = {
                "daily": "1d",
                "weekly": "7d",
                "monthly": "1mo",
                "yearly": "1y"
            }.get(period, "7d")

            self.portfolio.sort_investments(sort_key, reverse_var.get(), yf_period)

            treeview.delete(*treeview.get_children())
            treeview.heading("Change", text=f"{period.capitalize()} Change")

            total = 0

            for investment in self.portfolio.investments:
                current_price = investment.get_current_price()
                value = investment.calculate_value(current_price)
                profit_loss = investment.calculate_profit_loss(current_price)
                total += value

                change = investment.calculate_change(yf_period)
                change_text = f"{change:+.2f}%" if change is not None else "N/A"

                treeview.insert("", "end", values=(
                    investment.name,
                    investment.symbol,
                    investment.shares,
                    f"${investment.purchase_price:.2f}",
                    f"${current_price:.2f}",
                    f"${profit_loss:.2f}",
                    change_text
                ))

            total_value_var.set(f"Total Portfolio Value: ${total:.2f}")

        portfolio_window = tk.Toplevel(self.root)
        portfolio_window.title("Investment Portfolio")

        ttk.Label(portfolio_window, text="Change Period:").grid(row=0, column=0, sticky="w", padx=10)
        period_var = tk.StringVar(value="weekly")
        period_dropdown = ttk.Combobox(portfolio_window, textvariable=period_var,
                                       values=["daily", "weekly", "monthly", "yearly"], state="readonly")
        period_dropdown.grid(row=0, column=1, sticky="w")

        ttk.Label(portfolio_window, text="Sort by:").grid(row=1, column=0, sticky="w", padx=10)
        sort_var = tk.StringVar(value="Name")
        sort_dropdown = ttk.Combobox(portfolio_window, textvariable=sort_var,
                                     values=list(sort_keys.keys()), state="readonly")
        sort_dropdown.grid(row=1, column=1, sticky="w")

        reverse_var = tk.BooleanVar()
        reverse_check = ttk.Checkbutton(portfolio_window, text="Descending", variable=reverse_var)
        reverse_check.grid(row=1, column=2, sticky="w")

        columns = ("Name", "Symbol", "Shares", "Purchase Price", "Current Price", "Profit/Loss", "Change")
        treeview = ttk.Treeview(portfolio_window, columns=columns, show="headings")
        for col in columns:
            treeview.heading(col, text=col)
            treeview.column(col, anchor="center", width=120)
        treeview.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        total_value_var = tk.StringVar()
        total_label = ttk.Label(portfolio_window, textvariable=total_value_var, font=("Arial", 12, "bold"))
        total_label.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10))

        def on_row_double_click(event):
            selected_item = treeview.selection()[0]
            symbol = treeview.item(selected_item, 'values')[1]
            self.show_stock_chart(symbol)

        treeview.bind("<Double-1>", on_row_double_click)

        period_dropdown.bind("<<ComboboxSelected>>", lambda e: update_treeview_with_change(period_var.get()))
        sort_dropdown.bind("<<ComboboxSelected>>", lambda e: update_treeview_with_change(period_var.get()))
        reverse_check.config(command=lambda: update_treeview_with_change(period_var.get()))

        update_treeview_with_change("weekly")

    def add_investment(self):
        try:
            name = self.name_entry.get()
            symbol = self.symbol_entry.get().upper()
            new_shares = float(self.shares_entry.get())
            new_purchase_price = float(self.purchase_price_entry.get())
            stock_info = yf.Ticker(symbol).info
            sector = stock_info.get("sector", "Unknown")

            existing_stock = next((inv for inv in self.portfolio.investments if inv.symbol == symbol), None)

            if existing_stock:
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
                stock = Stock(name, symbol, new_shares, new_purchase_price, sector)
                self.portfolio.add_investment(stock)
                stock.get_current_price()

                messagebox.showinfo("Added", f"Investment in {name} added!")

            self.portfolio.save_to_file()

            self.clear_inputs()


        except ValueError:
            messagebox.showerror("Error", "Invalid input data!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch stock data.\n{e}")

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
            self.clear_inputs()
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

                    stock_info = yf.Ticker(symbol).info
                    inv.sector = stock_info.get("sector", "Unknown")

                    self.portfolio.save_to_file()
                    messagebox.showinfo("Updated", f"Investment with symbol {symbol} updated.")
                    return
            self.clear_inputs()

            messagebox.showwarning("Not Found", f"No investment found with symbol {symbol}.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input data!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not update investment.\n{e}")

    def export_portfolio(self):
        write_to_csv('portfolio.json', 'Portfolio.csv')
        messagebox.showinfo("Exported", "Portfolio exported to portfolio.csv.")

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.symbol_entry.delete(0, tk.END)
        self.shares_entry.delete(0, tk.END)
        self.purchase_price_entry.delete(0, tk.END)
