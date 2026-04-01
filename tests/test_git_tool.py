import os
import shutil
import tempfile
import unittest
from pathlib import Path
from orch.orch.tools.git import git_init, git_add, git_commit, git_status, git_log

class TestGitTool(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the git repository
        self.test_dir = Path(tempfile.mkdtemp())
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        # Restore the old working directory and remove the temporary directory
        os.chdir(self.old_cwd)
        
        def on_error(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)
            
        shutil.rmtree(self.test_dir, onerror=on_error)

    def test_git_init(self):
        result = git_init()
        self.assertIn("Initialized empty Git repository", result)
        self.assertTrue((self.test_dir / ".git").exists())

    def test_git_status(self):
        git_init()
        result = git_status()
        self.assertIn("On branch", result)

    def test_git_add_and_commit(self):
        git_init()
        test_file = self.test_dir / "test.txt"
        test_file.write_text("hello git", encoding="utf-8")
        
        add_result = git_add("test.txt")
        self.assertIn("Successfully added", add_result)
        
        # Need to configure git user for commit to work in some environments
        import subprocess
        subprocess.run(["git", "config", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Your Name"], check=True)
        
        commit_result = git_commit("Initial commit")
        self.assertIn("Initial commit", commit_result)
        self.assertIn("1 file changed", commit_result)

    def test_git_log(self):
        git_init()
        test_file = self.test_dir / "test.txt"
        test_file.write_text("hello git", encoding="utf-8")
        
        # Configure git user
        import subprocess
        subprocess.run(["git", "config", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Your Name"], check=True)
        
        git_add("test.txt")
        git_commit("Initial commit")
        
        log_result = git_log()
        self.assertIn("Initial commit", log_result)
        self.assertIn("Author:", log_result)

if __name__ == "__main__":
    unittest.main()
