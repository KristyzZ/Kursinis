import unittest
from models.stock import Stock


class TestStock(unittest.TestCase):

    def setUp(self):
        self.stock = Stock(
            name="Test Company",
            symbol="AAPL",
            shares=10,
            purchase_price=100.0,
            sector="Technology"
        )

    def test_calculate_value(self):
        value = self.stock.calculate_value(150.0)
        self.assertEqual(value, 1500.0)

    def test_calculate_profit_loss(self):
        profit = self.stock.calculate_profit_loss(150.0)
        self.assertEqual(profit, 50.0)

    def test_to_dict(self):
        data = self.stock.to_dict()
        self.assertEqual(data["name"], "Test Company")
        self.assertEqual(data["symbol"], "AAPL")
        self.assertEqual(data["shares"], 10)
        self.assertEqual(data["purchase_price"], 100.0)
        self.assertEqual(data["sector"], "Technology")

    def test_calculate_change_returns_number_or_none(self):
        result = self.stock.calculate_change("7d")
        self.assertTrue(isinstance(result, float) or result is None)


if __name__ == "__main__":
    unittest.main()
