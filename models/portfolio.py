import json
from models.stock import Stock


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

    def sort_investments(self, key, reverse=False, period="7d"):
        def get_sort_value(investment):
            if key == "name":
                return investment.name.lower()
            elif key == "symbol":
                return investment.symbol.lower()
            elif key == "shares":
                return investment.shares
            elif key == "purchase_price":
                return investment.purchase_price
            elif key == "current_price":
                return investment.get_current_price()
            elif key == "profit_loss":
                return investment.calculate_profit_loss(investment.get_current_price())
            elif key == "change":
                return investment.calculate_change(period)
            return 0

        self.investments.sort(key=get_sort_value, reverse=reverse)

class PortfolioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
            cls._instance.portfolio = Portfolio()
        return cls._instance