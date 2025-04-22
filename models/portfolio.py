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

class PortfolioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
            cls._instance.portfolio = Portfolio()
        return cls._instance