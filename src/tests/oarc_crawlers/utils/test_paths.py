"""Tests for the paths module."""
import os
import re
import pathlib
import tempfile
import shutil
from unittest import mock
import pytest

from oarc_crawlers.utils.paths import Paths


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def normalize_path(path):
    """Normalize path for platform-independent comparison."""
    return os.path.normpath(path).replace('\\', '/')


def test_ensure_path(temp_dir):
    """Test ensuring a path exists."""
    test_path = os.path.join(temp_dir, "test_dir", "sub_dir")
    result = Paths.ensure_path(test_path)
    assert os.path.exists(test_path)
    assert isinstance(result, pathlib.Path)
    assert normalize_path(str(result)) == normalize_path(test_path)


def test_get_oarc_home_dir():
    """Test retrieving OARC home directory."""
    # Test with environment variable
    with mock.patch.dict(os.environ, {"OARC_HOME_DIR": "/test/path"}):
        with mock.patch("pathlib.Path.resolve", return_value=pathlib.Path("/test/path")):
            result = Paths.get_oarc_home_dir()
            assert normalize_path(str(result)) == normalize_path("/test/path")
    
    # Test default behavior
    with mock.patch.dict(os.environ, clear=True):
        with mock.patch("pathlib.Path.home", return_value=pathlib.Path("/home/user")):
            result = Paths.get_oarc_home_dir()
            assert normalize_path(str(result)) == normalize_path("/home/user")


def test_get_oarc_dir():
    """Test retrieving .oarc directory."""
    with mock.patch("oarc_crawlers.utils.paths.Paths.get_oarc_home_dir", 
                   return_value=pathlib.Path("/home/user")):
        result = Paths.get_oarc_dir()
        assert normalize_path(str(result)) == normalize_path("/home/user/.oarc")


def test_get_default_data_dir():
    """Test retrieving default data directory."""
    # Test with environment variable
    with mock.patch.dict(os.environ, {"OARC_DATA_DIR": "/test/data"}):
        with mock.patch("pathlib.Path.resolve", return_value=pathlib.Path("/test/data")):
            result = Paths.get_default_data_dir()
            assert normalize_path(str(result)) == normalize_path("/test/data")
    
    # Test default behavior
    with mock.patch.dict(os.environ, clear=True):
        with mock.patch("oarc_crawlers.utils.paths.Paths.get_oarc_dir", 
                       return_value=pathlib.Path("/home/user/.oarc")):
            result = Paths.get_default_data_dir()
            assert normalize_path(str(result)) == normalize_path("/home/user/.oarc/data")


def test_get_temp_dir():
    """Test retrieving temporary directory."""
    with mock.patch("tempfile.gettempdir", return_value="/tmp"):
        with mock.patch("oarc_crawlers.utils.paths.Paths.ensure_path") as mock_ensure:
            mock_ensure.return_value = pathlib.Path("/tmp/oarc-crawlers")
            result = Paths.get_temp_dir()
            assert normalize_path(str(result)) == normalize_path("/tmp/oarc-crawlers")
            mock_ensure.assert_called_once_with(pathlib.Path("/tmp/oarc-crawlers"))


def test_sanitize_filename():
    """Test sanitizing filenames."""
    # Test invalid characters
    assert Paths.sanitize_filename("file:name?with*invalid/chars") == "file_name_with_invalid_chars"
    
    # Test spaces
    assert Paths.sanitize_filename("file name with spaces") == "file_name_with_spaces"
    
    # Test trimming
    assert Paths.sanitize_filename(" trim_spaces ") == "trim_spaces"
    
    # Test long filename
    long_name = "a" * 300
    assert len(Paths.sanitize_filename(long_name)) == 250


def test_timestamped_path(temp_dir):
    """Test creating a timestamped path."""
    with mock.patch("oarc_crawlers.utils.paths.datetime") as mock_dt:
        mock_dt.now.return_value.timestamp.return_value = 1234567890
        
        # Test with extension
        result = Paths.timestamped_path(temp_dir, "test_file", "txt")
        assert normalize_path(str(result)) == normalize_path(os.path.join(temp_dir, "test_file_1234567890.txt"))
        
        # Test without extension
        result = Paths.timestamped_path(temp_dir, "test_file")
        assert normalize_path(str(result)) == normalize_path(os.path.join(temp_dir, "test_file_1234567890"))
        
        # Test with dot in extension
        result = Paths.timestamped_path(temp_dir, "test_file", ".json")
        assert normalize_path(str(result)) == normalize_path(os.path.join(temp_dir, "test_file_1234567890.json"))


def test_is_valid_path():
    """Test path validation."""
    # For Windows, use mock to ensure proper behavior
    with mock.patch("os.path.isabs", return_value=True):
        with mock.patch("os.path.dirname", return_value="/valid"):
            assert Paths.is_valid_path("/valid/path") == True
    
        with mock.patch("os.path.dirname", return_value="/invalid"):
            assert Paths.is_valid_path("/invalid/test") == False
    
    # Test with relative paths
    assert Paths.is_valid_path("relative/path") == True


def test_ensure_parent_dir(temp_dir):
    """Test ensuring parent directory exists."""
    test_file_path = os.path.join(temp_dir, "sub_dir", "test_file.txt")
    
    # Test successful path creation
    success, error = Paths.ensure_parent_dir(test_file_path)
    assert success is True
    assert error == ""
    assert os.path.exists(os.path.dirname(test_file_path))
    
    # Test error handling
    with mock.patch("oarc_crawlers.utils.paths.Paths.ensure_path", 
                  side_effect=PermissionError("Permission denied")):
        success, error = Paths.ensure_parent_dir(test_file_path)
        assert success is False
        assert "Permission denied" in error


def test_file_exists(temp_dir):
    """Test checking if a file exists."""
    # Create test file
    test_file = os.path.join(temp_dir, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    
    # Test existing file
    assert Paths.file_exists(test_file) is True
    
    # Test non-existing file
    non_existent_file = os.path.join(temp_dir, "non_existent.txt")
    assert Paths.file_exists(non_existent_file) is False


def test_create_temp_dir():
    """Test creating a temporary directory."""
    with mock.patch("tempfile.mkdtemp") as mock_mkdtemp:
        mock_mkdtemp.return_value = "/tmp/test_temp_dir"
        
        # Test with prefix
        result = Paths.create_temp_dir("test_prefix")
        assert normalize_path(str(result)) == normalize_path("/tmp/test_temp_dir")
        mock_mkdtemp.assert_called_with(prefix="test_prefix")
        
        mock_mkdtemp.reset_mock()
        
        # Test without prefix
        result = Paths.create_temp_dir()
        assert normalize_path(str(result)) == normalize_path("/tmp/test_temp_dir")
        mock_mkdtemp.assert_called_with(prefix="oarc-crawlers")


def test_ensure_temp_dir(temp_dir):
    """Test ensuring a temporary directory exists."""
    # Test with existing directory
    with mock.patch("pathlib.Path.exists", return_value=True):
        with mock.patch("shutil.rmtree") as mock_rmtree:
            result = Paths.ensure_temp_dir(temp_dir)
            assert result == pathlib.Path(temp_dir)
            mock_rmtree.assert_called_once_with(pathlib.Path(temp_dir))
    
    # Test with new directory creation
    with mock.patch("oarc_crawlers.utils.paths.Paths.create_temp_dir") as mock_create:
        mock_create.return_value = pathlib.Path("/tmp/new_temp_dir")
        result = Paths.ensure_temp_dir()
        assert normalize_path(str(result)) == normalize_path("/tmp/new_temp_dir")
        mock_create.assert_called_once_with(None)


def test_cleanup_temp_dir(temp_dir):
    """Test cleaning up a temporary directory."""
    # Test with existing directory
    result = Paths.cleanup_temp_dir(temp_dir)
    assert result is True
    assert not os.path.exists(temp_dir)
    
    # Test with already removed directory
    result = Paths.cleanup_temp_dir(temp_dir)
    assert result is True
    
    # Test with error - but use a simpler approach to avoid mock issues
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch("shutil.rmtree", side_effect=Exception("Test error")):
            # Just test that the function handles errors properly
            result = Paths.cleanup_temp_dir("/fake/path")
            assert result is False


def test_is_binary_file(temp_dir):
    """Test binary file detection."""
    # Test by extension
    assert Paths.is_binary_file("test.png") is True
    assert Paths.is_binary_file("test.jpg") is True
    assert Paths.is_binary_file("test.txt") is False
    
    # Test by content
    binary_file = os.path.join(temp_dir, "binary.dat")
    with open(binary_file, "wb") as f:
        f.write(b"test\x00binary")
    assert Paths.is_binary_file(binary_file) is True
    
    text_file = os.path.join(temp_dir, "text.txt")
    with open(text_file, "w") as f:
        f.write("test text")
    assert Paths.is_binary_file(text_file) is False


def test_youtube_data_dir():
    """Test YouTube data directory paths."""
    with mock.patch("oarc_crawlers.config.config.Config.get_instance") as mock_config:
        mock_config.return_value.data_dir = "/config/data"
        
        result = Paths.youtube_data_dir()
        assert normalize_path(str(result)) == normalize_path("/config/data/youtube_data")
        
        # Test with custom base dir
        result = Paths.youtube_data_dir("/custom/base")
        assert normalize_path(str(result)) == normalize_path("/custom/base/youtube_data")
