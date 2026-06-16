
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

import unittest
import os
from kopano.tools.viz_tool import generate_plot

class TestVizTool(unittest.TestCase):
    def tearDown(self):
        if os.path.exists("test_plot.png"):
            os.remove("test_plot.png")

    def test_generate_plot_success(self):
        data = {"A": 10, "B": 20, "C": 15}
        result = generate_plot(data, title="Test Plot", output_path="test_plot.png")
        self.assertIn("successfully", result)
        self.assertTrue(os.path.exists("test_plot.png"))

    def test_generate_plot_invalid_data(self):
        result = generate_plot("invalid", title="Fail")
        self.assertIn("Error", result)

if __name__ == "__main__":
    unittest.main()
