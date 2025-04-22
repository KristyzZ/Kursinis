from abc import ABC, abstractmethod

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