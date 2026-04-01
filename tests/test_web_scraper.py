import unittest
from unittest.mock import patch, MagicMock
from orch.orch.tools.web_scraper import scrape_page

class TestWebScraper(unittest.TestCase):
    @patch("orch.orch.tools.web_scraper.httpx.get")
    def test_scrape_page_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Test Title</title></head><body><p>Test content.</p></body></html>"
        mock_get.return_value = mock_response

        result = scrape_page("http://example.com")
        self.assertIn("Title: Test Title", result)
        self.assertIn("Content Preview:\nTest content.", result)

    @patch("orch.orch.tools.web_scraper.httpx.get")
    def test_scrape_page_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        # httpx raise_for_status will be called
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")

        result = scrape_page("http://example.com/missing")
        self.assertIn("Error scraping 'http://example.com/missing': 404 Not Found", result)

if __name__ == "__main__":
    unittest.main()
