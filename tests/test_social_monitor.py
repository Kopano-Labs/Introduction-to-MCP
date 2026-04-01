import unittest
from unittest.mock import patch, MagicMock
from orch.orch.tools.social_monitor import monitor_brand

class TestSocialMonitor(unittest.TestCase):
    @patch("orch.orch.tools.social_monitor.perform_search")
    def test_monitor_brand_reddit(self, mock_perform_search):
        # Setup mock behavior
        mock_perform_search.return_value = "Reddit mention of MyBrand"
        
        result = monitor_brand("MyBrand", platform="reddit")
        
        # Verify that perform_search was called with the correct query for Reddit
        mock_perform_search.assert_called_with('site:reddit.com "MyBrand"')
        self.assertIn("Reddit mention of MyBrand", result)

    @patch("orch.orch.tools.social_monitor.perform_search")
    def test_monitor_brand_x(self, mock_perform_search):
        mock_perform_search.return_value = "X (Twitter) mention of MyBrand"
        
        result = monitor_brand("MyBrand", platform="x")
        
        mock_perform_search.assert_called_with('site:x.com OR site:twitter.com "MyBrand"')
        self.assertIn("X (Twitter) mention of MyBrand", result)

    @patch("orch.orch.tools.social_monitor.perform_search")
    def test_monitor_brand_all(self, mock_perform_search):
        mock_perform_search.return_value = "General results"
        
        result = monitor_brand("MyBrand", platform="all")
        
        # Should call with multiple platforms
        self.assertTrue(mock_perform_search.called)
        self.assertIn("General results", result)

    def test_monitor_brand_invalid_platform(self):
        result = monitor_brand("MyBrand", platform="invalid")
        self.assertIn("Error: Invalid platform", result)

if __name__ == "__main__":
    unittest.main()
