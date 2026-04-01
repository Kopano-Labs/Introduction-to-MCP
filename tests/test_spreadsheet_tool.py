import unittest
import pandas as pd
import os
from orch.orch.tools.spreadsheet_tool import clean_spreadsheet

class TestSpreadsheetTool(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_data.csv"
        df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Alice", "Charlie", None],
            "Age": [25, 30, 25, None, 40],
            "City": ["New York", "london", "New York", "Paris", "PARIS"]
        })
        df.to_csv(self.test_csv, index=False)

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists("cleaned_test_data.csv"):
            os.remove("cleaned_test_data.csv")

    def test_clean_spreadsheet_success(self):
        result = clean_spreadsheet(self.test_csv, output_path="cleaned_test_data.csv")
        self.assertIn("successfully", result)
        self.assertTrue(os.path.exists("cleaned_test_data.csv"))
        
        cleaned_df = pd.read_csv("cleaned_test_data.csv")
        # Alice should be unique now (duplicates removed)
        self.assertEqual(len(cleaned_df[cleaned_df["Name"] == "Alice"]), 1)
        # Cities should be consistent (e.g., all lowercase or capitalized) - depends on implementation
        # Let's say we title-case them.
        self.assertIn("London", cleaned_df["City"].values)
        self.assertIn("Paris", cleaned_df["City"].values)

    def test_clean_spreadsheet_file_not_found(self):
        result = clean_spreadsheet("non_existent.csv")
        self.assertIn("Error", result)

if __name__ == "__main__":
    unittest.main()
