import unittest
import os
from orch.orch.tools.log_analyzer import analyze_logs

class TestLogAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_log = "test.log"
        with open(self.test_log, "w") as f:
            f.write("2024-03-20 10:00:00 - INFO - Started\n")
            f.write("2024-03-20 10:05:00 - ERROR - Failed to connect\n")
            f.write("2024-03-20 10:10:00 - WARNING - Retrying\n")
            f.write("2024-03-20 10:15:00 - INFO - Connected\n")
            f.write("2024-03-20 10:20:00 - ERROR - Database timeout\n")

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_analyze_logs_success(self):
        result = analyze_logs(self.test_log)
        self.assertIn("Log Summary", result)
        self.assertIn("**Total Lines:** 5", result)
        self.assertIn("INFO: 2", result)
        self.assertIn("ERROR: 2", result)
        self.assertIn("WARNING: 1", result)

    def test_analyze_logs_not_found(self):
        result = analyze_logs("non_existent.log")
        self.assertIn("Error", result)

if __name__ == "__main__":
    unittest.main()
