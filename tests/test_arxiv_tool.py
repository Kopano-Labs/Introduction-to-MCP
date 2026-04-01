import unittest
from unittest.mock import patch, MagicMock
from orch.orch.tools.arxiv import search_arxiv

class TestArxivTool(unittest.TestCase):
    @patch("orch.orch.tools.arxiv.httpx.get")
    def test_search_arxiv_success(self, mock_get):
        # Mocking the arXiv API response (XML format)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Deep Learning in Physics</title>
    <link href="http://arxiv.org/abs/1234.5678" rel="alternate" type="text/html"/>
    <summary>Abstract content here...</summary>
    <author><name>John Doe</name></author>
  </entry>
</feed>"""
        mock_get.return_value = mock_response

        result = search_arxiv("Deep Learning")
        self.assertIn("Title: Deep Learning in Physics", result)
        self.assertIn("URL: http://arxiv.org/abs/1234.5678", result)
        self.assertIn("Abstract content here...", result)
        self.assertIn("Authors: John Doe", result)

    @patch("orch.orch.tools.arxiv.httpx.get")
    def test_search_arxiv_no_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""
        mock_get.return_value = mock_response

        result = search_arxiv("NonExistentTopic12345")
        self.assertIn("No arXiv papers found", result)

    @patch("orch.orch.tools.arxiv.httpx.get")
    def test_search_arxiv_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        result = search_arxiv("Topic")
        self.assertIn("Error performing arXiv search: Network error", result)

if __name__ == "__main__":
    unittest.main()
