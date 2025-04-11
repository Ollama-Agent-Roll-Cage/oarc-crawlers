import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import pandas as pd
from pathlib import Path

# Add parent directory to path to import modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.gh_crawler import GitHubCrawler

class TestGitHubCrawler(unittest.TestCase):
    """Test the GitHub crawler module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.crawler = GitHubCrawler(data_dir=self.temp_dir.name)
        
        # Test URLs
        self.repo_url = "https://github.com/username/repo"
        self.repo_url_with_branch = "https://github.com/username/repo/tree/dev"
        self.git_url = "git@github.com:username/repo.git"
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_extract_repo_info_from_url(self):
        """Test extracting repository information from URLs."""
        # Test standard GitHub URL
        owner, repo, branch = GitHubCrawler.extract_repo_info_from_url(self.repo_url)
        self.assertEqual(owner, "username")
        self.assertEqual(repo, "repo")
        self.assertEqual(branch, "main")
        
        # Test URL with branch specified
        owner, repo, branch = GitHubCrawler.extract_repo_info_from_url(self.repo_url_with_branch)
        self.assertEqual(owner, "username")
        self.assertEqual(repo, "repo")
        self.assertEqual(branch, "dev")
        
        # Test git URL
        owner, repo, branch = GitHubCrawler.extract_repo_info_from_url(self.git_url)
        self.assertEqual(owner, "username")
        self.assertEqual(repo, "repo")
        self.assertEqual(branch, "main")
        
        # Test invalid URL
        with self.assertRaises(ValueError):
            GitHubCrawler.extract_repo_info_from_url("https://example.com")
    
    def test_get_repo_dir_path(self):
        """Test getting repository directory path."""
        path = self.crawler.get_repo_dir_path("username", "repo")
        expected_path = Path(f"{self.temp_dir.name}/github_repos/username_repo")
        self.assertEqual(path, expected_path)
    
    def test_is_binary_file(self):
        """Test binary file detection."""
        # Create temporary files
        text_file = os.path.join(self.temp_dir.name, "text.txt")
        with open(text_file, 'w') as f:
            f.write("This is a text file.")
            
        # Test extension-based detection
        self.assertTrue(self.crawler.is_binary_file(os.path.join(self.temp_dir.name, "image.png")))
        self.assertTrue(self.crawler.is_binary_file(os.path.join(self.temp_dir.name, "document.pdf")))
        self.assertFalse(self.crawler.is_binary_file(text_file))
    
    def test_get_language_from_extension(self):
        """Test language detection from file extension."""
        self.assertEqual(GitHubCrawler.get_language_from_extension(".py"), "Python")
        self.assertEqual(GitHubCrawler.get_language_from_extension(".js"), "JavaScript")
        self.assertEqual(GitHubCrawler.get_language_from_extension(".unknown"), "Unknown")

    @patch('git.Repo')
    async def test_clone_repo(self, mock_git):
        """Test cloning a repository."""
        # Setup mock
        mock_repo = MagicMock()
        mock_git.clone_from.return_value = mock_repo
        
        # Test with default temp directory
        with patch('tempfile.mkdtemp', return_value='/tmp/test_dir'):
            result = await self.crawler.clone_repo(self.repo_url)
            mock_git.clone_from.assert_called_once_with(self.repo_url, '/tmp/test_dir')
            self.assertEqual(result, Path('/tmp/test_dir'))
        
        # Test with specified temp directory
        mock_git.reset_mock()
        temp_dir = os.path.join(self.temp_dir.name, "custom_temp_dir")
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.mkdir'):
                result = await self.crawler.clone_repo(self.repo_url, temp_dir)
                mock_git.clone_from.assert_called_once_with(self.repo_url, temp_dir)
        
        # Test with branch checkout
        mock_git.reset_mock()
        with patch('tempfile.mkdtemp', return_value='/tmp/test_dir'):
            result = await self.crawler.clone_repo(self.repo_url_with_branch)
            mock_git.clone_from.assert_called_once_with(self.repo_url_with_branch, '/tmp/test_dir')
            mock_repo.git.checkout.assert_called_once_with('dev')

    @patch('git.Repo')
    async def test_process_repo_to_dataframe(self, mock_git):
        """Test processing repository files to DataFrame."""
        # Create a test repository structure
        repo_dir = os.path.join(self.temp_dir.name, "test_repo")
        os.makedirs(repo_dir)
        
        # Add some sample files
        python_file = os.path.join(repo_dir, "test.py")
        with open(python_file, 'w') as f:
            f.write("def hello():\n    return 'Hello World'")
        
        js_file = os.path.join(repo_dir, "test.js")
        with open(js_file, 'w') as f:
            f.write("function hello() {\n    return 'Hello World';\n}")
        
        # Mock git repository
        mock_repo = MagicMock()
        mock_git.return_value = mock_repo
        
        # Mock git blame
        mock_repo.git.blame.return_value = {
            'commit1': 'author Test Author\nauthor-time 1617111111\n'
        }
        
        # Call the method
        result = await self.crawler.process_repo_to_dataframe(Path(repo_dir))
        
        # Assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape[0], 2)  # Should have 2 files
        self.assertTrue('test.py' in result['file_path'].values)
        self.assertTrue('test.js' in result['file_path'].values)
        
        # Check languages
        python_row = result[result['file_path'] == 'test.py']
        js_row = result[result['file_path'] == 'test.js']
        self.assertEqual(python_row['language'].iloc[0], 'Python')
        self.assertEqual(js_row['language'].iloc[0], 'JavaScript')
        
        # Check content
        self.assertIn("def hello():", python_row['content'].iloc[0])
        self.assertIn("function hello()", js_row['content'].iloc[0])

    @patch('src.gh_crawler.GitHubCrawler.clone_repo')
    @patch('src.gh_crawler.GitHubCrawler.process_repo_to_dataframe')
    @patch('src.gh_crawler.ParquetStorage')
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    async def test_clone_and_store_repo(self, mock_rmtree, mock_mkdtemp, mock_storage, 
                                        mock_process, mock_clone):
        """Test cloning and storing a repository."""
        # Setup mocks
        mock_mkdtemp.return_value = os.path.join(self.temp_dir.name, "temp_clone_dir")
        mock_clone.return_value = Path(os.path.join(self.temp_dir.name, "cloned_repo"))
        
        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'file_path': ['file1.py', 'file2.js'],
            'content': ['content1', 'content2'],
            'language': ['Python', 'JavaScript']
        })
        mock_process.return_value = mock_df
        
        # Call the method
        result = await self.crawler.clone_and_store_repo(self.repo_url)
        
        # Assertions
        mock_mkdtemp.assert_called_once()
        mock_clone.assert_called_once_with(self.repo_url, mock_mkdtemp.return_value)
        mock_process.assert_called_once_with(mock_clone.return_value)
        mock_storage.save_to_parquet.assert_called_once()
        mock_rmtree.assert_called_once_with(mock_mkdtemp.return_value)
        
        # Check return value
        expected_path = f"{self.temp_dir.name}/github_repos/username_repo.parquet"
        self.assertEqual(result, expected_path)

    @patch('src.gh_crawler.GitHubCrawler.clone_and_store_repo')
    @patch('src.gh_crawler.ParquetStorage')
    @patch('os.path.exists')
    async def test_get_repo_summary(self, mock_exists, mock_storage, mock_clone_store):
        """Test getting a repository summary."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'file_path': ['src/file1.py', 'src/file2.py', 'tests/test_file.py', 'README.md'],
            'content': ['content1', 'content2', 'test content', '# README\nThis is a test repository.'],
            'language': ['Python', 'Python', 'Python', 'Markdown'],
            'line_count': [10, 20, 15, 5]
        })
        mock_storage.load_from_parquet.return_value = mock_df
        
        # Call the method
        result = await self.crawler.get_repo_summary(self.repo_url)
        
        # Assertions
        mock_exists.assert_called_once()
        mock_storage.load_from_parquet.assert_called_once()
        self.assertIn("# GitHub Repository Summary: username/repo", result)
        self.assertIn("**Total Files:** 4", result)
        self.assertIn("**Total Lines of Code:** 50", result)
        self.assertIn("**Python:** 3 files", result)
        self.assertIn("**Markdown:** 1 files", result)
        self.assertIn("- src/", result)
        self.assertIn("- tests/", result)
        self.assertIn("# README", result)
        self.assertIn("This is a test repository.", result)
        
        # Test with repo that needs to be cloned
        mock_exists.return_value = False
        mock_clone_store.return_value = f"{self.temp_dir.name}/github_repos/username_repo.parquet"
        result = await self.crawler.get_repo_summary(self.repo_url)
        mock_clone_store.assert_called_once_with(self.repo_url)
    
    @patch('src.gh_crawler.GitHubCrawler.clone_and_store_repo')
    @patch('src.gh_crawler.ParquetStorage')
    @patch('os.path.exists')
    async def test_find_similar_code(self, mock_exists, mock_storage, mock_clone_store):
        """Test finding similar code in a repository."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'file_path': ['file1.py', 'file2.py', 'file3.js'],
            'content': [
                'def test_function():\n    return "Hello World"',
                'def another_function():\n    print("Different")',
                'function jsFunc() {\n    return "Hello World";\n}'
            ],
            'language': ['Python', 'Python', 'JavaScript'],
            'line_count': [2, 2, 3]
        })
        mock_storage.load_from_parquet.return_value = mock_df
        
        # Test code snippet to find
        code_snippet = 'def test_function():\n    return "Hello World"'
        
        # Call the method
        result = await self.crawler.find_similar_code(self.repo_url, code_snippet)
        
        # Assertions
        mock_exists.assert_called_once()
        mock_storage.load_from_parquet.assert_called_once()
        self.assertIn("# Similar Code Findings", result)
        self.assertIn("file1.py", result)
        self.assertIn("100.0% similarity", result)
        self.assertIn("def test_function():", result)
        
        # Test with a JavaScript snippet
        mock_exists.reset_mock()
        mock_storage.reset_mock()
        mock_exists.return_value = True
        code_snippet = 'function jsFunc() {\n    return "Hello World";\n}'
        result = await self.crawler.find_similar_code(self.repo_url, code_snippet)
        self.assertIn("file3.js", result)
        self.assertIn("JavaScript", result)

if __name__ == '__main__':
    unittest.main()