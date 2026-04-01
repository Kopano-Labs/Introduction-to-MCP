import unittest
import os
import shutil
import tempfile
from pathlib import Path
from orch.orch.tools.security import scan_code_security, scan_dependencies

class TestSecurityTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def test_scan_code_security_vulnerable(self):
        # Create a file with a known security issue (e.g., use of 'eval')
        vulnerable_file = Path("vuln.py")
        vulnerable_file.write_text("eval('import os; os.system(\"ls\")')")
        
        result = scan_code_security("vuln.py")
        self.assertIn("Issue:", result)
        self.assertIn("eval", result.lower())

    def test_scan_code_security_safe(self):
        safe_file = Path("safe.py")
        safe_file.write_text("print('Hello, world!')")
        
        result = scan_code_security("safe.py")
        self.assertIn("No security issues found", result)

    def test_scan_code_security_directory(self):
        os.mkdir("test_src")
        (Path("test_src") / "vuln.py").write_text("exec('print(1)')")
        
        result = scan_code_security("test_src")
        self.assertIn("Issue:", result)
        self.assertIn("exec", result.lower())

    def test_scan_dependencies_no_requirements(self):
        result = scan_dependencies("nonexistent.txt")
        self.assertIn("Error", result)

    def test_scan_dependencies_vulnerable(self):
        # Using an old version of requests with known vulnerabilities for testing
        # Note: This requires 'safety' to be installed and have an internet connection or cached db
        req_file = Path("requirements.txt")
        req_file.write_text("requests==2.0.0")
        
        result = scan_dependencies("requirements.txt")
        # Depending on whether 'safety' is installed, it might return an error or vulnerability report
        if "Safety is not installed" in result:
             self.skipTest("Safety not installed")
        self.assertTrue("vulnerability" in result.lower() or "issue" in result.lower() or "Successfully scanned" in result)

if __name__ == "__main__":
    unittest.main()
