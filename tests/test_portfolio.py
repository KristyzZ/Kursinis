import unittest
from models.portfolio import Portfolio
from models.stock import Stock


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio()
        self.stock1 = Stock("Apple", "AAPL", 5, 100.0, "Technology")
        self.stock2 = Stock("Google", "GOOGL", 10, 200.0, "Technology")
        self.portfolio.add_investment(self.stock1)
        self.portfolio.add_investment(self.stock2)

    def test_add_investment(self):
        self.assertEqual(len(self.portfolio.investments), 2)
        symbols = [inv.symbol for inv in self.portfolio.investments]
        self.assertIn("AAPL", symbols)
        self.assertIn("GOOGL", symbols)

    def test_remove_investment(self):
        self.portfolio.remove_investment("AAPL")
        symbols = [inv.symbol for inv in self.portfolio.investments]
        self.assertNotIn("AAPL", symbols)

    def test_get_total_value_returns_number(self):
        value = self.portfolio.get_total_value()
        self.assertIsInstance(value, float)

    def test_sort_investments_by_name(self):
        self.portfolio.sort_investments("name")
        self.assertEqual(self.portfolio.investments[0].name, "Apple")

    def test_sort_investments_by_shares_desc(self):
        self.portfolio.sort_investments("shares", reverse=True)
        self.assertEqual(self.portfolio.investments[0].symbol, "GOOGL")


if __name__ == "__main__":
    unittest.main()
