import os
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock
import tempfile
import pandas as pd
import pytest
import git
from pathlib import Path

from oarc_crawlers import GHCrawler
from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.crawler_utils import CrawlerUtils
from oarc_utils.errors import NetworkError, ResourceNotFoundError, DataExtractionError

@pytest.fixture
def crawler_fixture():
    with tempfile.TemporaryDirectory() as temp_dir:
        crawler = GHCrawler(data_dir=temp_dir)
        # Set a mock attribute for GitHub API testing
        crawler.github = MagicMock()
        yield crawler, temp_dir

@pytest.fixture
def mock_repo():
    """Create a mock GitHub repository object."""
    repo = MagicMock()
    repo.full_name = "user/repo"
    repo.name = "repo"
    repo.default_branch = "main"
    
    # Mock owner object
    owner = MagicMock()
    owner.login = "user"
    repo.owner = owner
    
    # Mock repository attributes
    repo.description = "Test repository"
    repo.stargazers_count = 10
    repo.forks_count = 5
    repo.created_at = MagicMock(strftime=lambda x: "2023-01-01")
    repo.updated_at = MagicMock(strftime=lambda x: "2023-06-01")
    
    return repo

class TestGitHubCrawler:
    """Test the GitHub crawler module."""

    def test_extract_repo_info_from_url(self, crawler_fixture):
        """Test extracting repository info from URL."""
        crawler, _ = crawler_fixture
        owner, repo, branch = GHCrawler.extract_repo_info_from_url("https://github.com/user/repo")
        assert owner == "user"
        assert repo == "repo"
        assert branch == "main"  # Default branch

        with pytest.raises(ValueError):
            GHCrawler.extract_repo_info_from_url("invalid_url")

    def test_get_repo_dir_path(self, crawler_fixture):
        """Test getting repository directory path."""
        crawler, temp_dir = crawler_fixture
        path = crawler.get_repo_dir_path("user", "repo")
        expected_path = Paths.github_repo_dir(temp_dir, "user", "repo")
        assert path == expected_path

    @pytest.mark.asyncio
    @patch('git.Repo.clone_from')
    async def test_clone_repo(self, mock_clone, crawler_fixture):
        """Test cloning a repository."""
        crawler, temp_dir = crawler_fixture
        repo_url = "https://github.com/user/repo"
        target_dir = os.path.join(temp_dir, "clone_target")
        
        # Reset and set up for successful case
        mock_clone.reset_mock()
        mock_clone.side_effect = None
        
        # Test successful case
        result_path = await crawler.clone_repo(repo_url, target_dir)
        assert result_path == target_dir
        mock_clone.assert_called_once_with(repo_url, target_dir)
        
        # Reset mock for error case
        mock_clone.reset_mock()
        
        # Test ResourceNotFoundError with exact error message matching
        not_found_error = git.GitCommandError("clone", "fatal: repository 'not found")
        mock_clone.side_effect = not_found_error
        
        with pytest.raises(ResourceNotFoundError):
            await crawler.clone_repo("https://github.com/user/nonexistent", target_dir)
            
        # Reset for NetworkError test
        mock_clone.reset_mock()
        network_error = git.GitCommandError("clone", "Could not resolve host: github.com")
        mock_clone.side_effect = network_error
        
        with pytest.raises(NetworkError):
            await crawler.clone_repo(repo_url, target_dir)

    @pytest.mark.asyncio
    async def test_is_binary_file(self, crawler_fixture):
        """Test identifying binary files."""
        _, temp_dir = crawler_fixture
        binary_file = os.path.join(temp_dir, "test.png")
        text_file = os.path.join(temp_dir, "test.txt")
        null_byte_file = os.path.join(temp_dir, "test_null.bin")

        with open(binary_file, "wb") as f:
            f.write(b"dummy binary data")
        with open(text_file, "w") as f:
            f.write("hello world")
        with open(null_byte_file, "wb") as f:
            f.write(b"hello\0world")

        # Await the async method calls
        assert await crawler_fixture[0].is_binary_file(binary_file, None) is True
        assert await crawler_fixture[0].is_binary_file(text_file, "hello world") is False
        assert await crawler_fixture[0].is_binary_file(null_byte_file, None) is True

    def test_get_language_from_extension(self, crawler_fixture):
        """Test getting language from file extension."""
        assert CrawlerUtils.get_language_from_extension(".py") == "Python"
        assert CrawlerUtils.get_language_from_extension(".js") == "JavaScript"
        assert CrawlerUtils.get_language_from_extension(".unknown") == "Unknown"
        assert CrawlerUtils.get_language_from_extension("") == "Unknown"

    @pytest.mark.asyncio
    async def test_process_repo_to_dataframe(self, crawler_fixture):
        """Test processing repository files into a DataFrame."""
        crawler, temp_dir = crawler_fixture
        repo_path = Path(os.path.join(temp_dir, "repo"))
        os.makedirs(os.path.join(repo_path, "subdir"), exist_ok=True)

        with open(os.path.join(repo_path, "file1.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(repo_path, "subdir", "file2.js"), "w") as f:
            f.write("console.log('world');")
        with open(os.path.join(repo_path, "binary.png"), "wb") as f:
            f.write(b"dummy binary\x00data")

        # Process local repo
        df = await crawler.process_repo_to_dataframe(repo_path)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2  # Binary file should be skipped
        assert "file1.py" in df["file_path"].values
        assert os.path.join("subdir", "file2.js") in df["file_path"].values
        assert "Python" in df["language"].values
        assert "JavaScript" in df["language"].values
        # Binary file should be excluded
        assert not any("binary.png" in path for path in df["file_path"].values)

    @pytest.mark.asyncio
    @patch('oarc_crawlers.core.crawlers.gh_crawler.GHCrawler.clone_repo')
    async def test_clone_and_store_repo(self, mock_clone_repo, crawler_fixture, mock_repo):
        """Test the end-to-end process of cloning and storing repo data."""
        crawler, temp_dir = crawler_fixture
        repo_url = "https://github.com/user/repo"
        
        # Set up mocks
        mock_temp_path = os.path.join(temp_dir, "mock_github_temp")
        os.makedirs(mock_temp_path, exist_ok=True)
        mock_clone_repo.return_value = mock_temp_path
        
        # Mock get_repo
        crawler.get_repo = AsyncMock(return_value=mock_repo)
        
        # Mock process_repo_to_dataframe
        mock_df = pd.DataFrame([{'file_path': 'test.py', 'language': 'Python', 'content': 'pass', 'size_bytes': 4}])
        crawler.process_repo_to_dataframe = AsyncMock(return_value=mock_df)
        
        # Create mock for ParquetStorage
        with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_github_data') as mock_save:
            mock_save.return_value = os.path.join(temp_dir, "dummy_path.parquet")
            
            # Execute the method
            result = await crawler.clone_and_store_repo(repo_url)
            
            # Assertions
            assert result["owner"] == "user"
            assert result["repo"] == "repo"
            assert result["num_files"] == 1
            assert result["data_path"] == os.path.join(temp_dir, "dummy_path.parquet")
            
            # Verify the mock calls
            crawler.get_repo.assert_called_once()
            crawler.process_repo_to_dataframe.assert_called_once()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    @patch('os.path.exists')
    @patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.load_from_parquet')
    async def test_get_repo_summary(self, mock_load, mock_exists, crawler_fixture, mock_repo):
        """Test generating a repository summary."""
        crawler, _ = crawler_fixture
        repo_url = "https://github.com/user/repo"
        
        # Set up mocks
        mock_df = pd.DataFrame([
            {'language': 'Python', 'size_bytes': 1000, 'line_count': 50, 'file_path': 'a.py'},
            {'language': 'Python', 'size_bytes': 500, 'line_count': 20, 'file_path': 'b.py'},
            {'language': 'JavaScript', 'size_bytes': 2000, 'line_count': 100, 'file_path': 'c.js'},
            {'language': 'Unknown', 'size_bytes': 100, 'line_count': 5, 'file_path': 'd.txt'}
        ])
        mock_exists.return_value = True  # Pretend file exists to avoid clone_and_store
        mock_load.return_value = mock_df
        
        # Mock get_repo method
        crawler.get_repo = AsyncMock(return_value=mock_repo)
        
        # Execute the method
        summary = await crawler.get_repo_summary(repo_url)
        
        # Assertions
        assert isinstance(summary, str)
        assert "GitHub Repository Summary: user/repo" in summary
        assert "**Total Files:** 4" in summary
        assert "**Total Lines of Code:** 175" in summary
        # Fix the assertion to match the actual format (with bold markdown)
        assert "**Python:** 2 files" in summary
        assert "**JavaScript:** 1 files" in summary

    @pytest.mark.asyncio
    async def test_find_similar_code(self, crawler_fixture):
        """Test finding similar code snippets."""
        crawler, _ = crawler_fixture
        
        # Create test data
        mock_df = pd.DataFrame([
            {'file_path': 'a.py', 'content': 'def func1():\n  print("hello")', 'language': 'Python'},
            {'file_path': 'b.py', 'content': 'def func2():\n  print("world")', 'language': 'Python'},
            {'file_path': 'c.py', 'content': 'def func1_similar():\n  print("hello")', 'language': 'Python'}
        ])
        
        # Mock methods
        with patch('os.path.exists', return_value=True):
            with patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.load_from_parquet', return_value=mock_df):
                results = await crawler.find_similar_code("https://github.com/user/repo", 'def func1():\n  print("hello")')
                
                # Assertions
                assert isinstance(results, list)
                assert len(results) > 0
                assert results[0]['file_path'] == 'a.py'
                assert results[0]['similarity'] > 50  # Should be very similar
                assert results[1]['file_path'] == 'c.py'