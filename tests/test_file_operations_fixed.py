import unittest
import os
import json
import tempfile
from utils.file_operations import save_json, load_json, write_to_csv



class TestFileOperations(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.gettempdir()
        self.test_json_file = os.path.join(self.test_dir, "test_portfolio.json")
        self.test_csv_file = os.path.join(self.test_dir, "test_portfolio.csv")
        self.test_data = [
            {
                "type": "stock",
                "name": "Apple",
                "symbol": "AAPL",
                "shares": 10,
                "purchase_price": 150.0,
                "sector": "Technology"
            }
        ]
        with open(self.test_json_file, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f, indent=4)

    def test_save_and_load_json(self):
        save_json(self.test_data, self.test_json_file)
        loaded_data = load_json(self.test_json_file)
        self.assertEqual(loaded_data, self.test_data)

    def test_write_to_csv_creates_file(self):
        write_to_csv(self.test_json_file, self.test_csv_file)
        self.assertTrue(os.path.exists(self.test_csv_file))

        excel_file = self.test_csv_file.replace(".csv", ".xlsx")
        self.assertTrue(os.path.exists(excel_file))

    def tearDown(self):
        for filename in [
            self.test_json_file,
            self.test_csv_file,
            self.test_csv_file.replace(".csv", ".xlsx")
        ]:
            if os.path.exists(filename):
                os.remove(filename)


if __name__ == "__main__":
    unittest.main()
