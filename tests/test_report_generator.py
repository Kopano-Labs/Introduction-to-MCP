import unittest
import os
import shutil
import tempfile
from pathlib import Path
from orch.orch.tools.report_generator import generate_report

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def test_generate_report_success(self):
        title = "Test Report"
        sections = {
            "Introduction": "This is a test introduction.",
            "Results": "The results are positive."
        }
        file_name = "test_report.md"
        
        result = generate_report(title, sections, file_name)
        
        self.assertIn("Successfully generated report", result)
        report_path = Path(file_name)
        self.assertTrue(report_path.exists())
        content = report_path.read_text()
        self.assertIn("# Test Report", content)
        self.assertIn("## Introduction", content)
        self.assertIn("This is a test introduction.", content)

    def test_generate_report_no_title(self):
        result = generate_report("", {"Section": "Content"}, "report.md")
        self.assertIn("Error: Title and sections are required", result)

    def test_generate_report_no_sections(self):
        result = generate_report("Title", {}, "report.md")
        self.assertIn("Error: Title and sections are required", result)

if __name__ == "__main__":
    unittest.main()
