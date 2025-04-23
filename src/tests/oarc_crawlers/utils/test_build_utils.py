"""Tests for the build_utils module."""
import os
import subprocess
import sys
import asyncio
from unittest import mock
import pytest

from oarc_crawlers.utils.build_utils import BuildUtils


def test_clean_build_directories():
    """Test cleaning build directories."""
    with mock.patch("subprocess.run") as mock_run:
        # Test successful cleanup on Windows
        with mock.patch("os.name", "nt"):
            result = BuildUtils.clean_build_directories()
            assert result is True
            assert mock_run.call_count == 4
            # Check that Windows commands were used
            assert any("rmdir /s /q dist" in str(call) for call in mock_run.call_args_list)
        
        mock_run.reset_mock()
        
        # Test successful cleanup on Unix
        with mock.patch("os.name", "posix"):
            result = BuildUtils.clean_build_directories()
            assert result is True
            assert mock_run.call_count == 2
            # Check that Unix command was used
            assert any("rm -rf dist build *.egg-info" in str(call) for call in mock_run.call_args_list)
        
        mock_run.reset_mock()
        
        # Test failure
        mock_run.side_effect = Exception("Test error")
        result = BuildUtils.clean_build_directories()
        assert result is False


def test_build_package():
    """Test building a package."""
    with mock.patch("subprocess.run") as mock_run:
        # Test successful build
        result = BuildUtils.build_package()
        assert result is True
        mock_run.assert_called_once_with([sys.executable, "-m", "build"], check=True)
        
        # Test build failure with CalledProcessError
        mock_run.reset_mock()
        mock_run.side_effect = subprocess.CalledProcessError(1, "build")
        
        with pytest.raises(SystemExit) as excinfo:
            BuildUtils.build_package()
        assert excinfo.value.code == 1
        
        # Test build failure with generic exception
        mock_run.reset_mock()
        mock_run.side_effect = Exception("Test error")
        
        with pytest.raises(SystemExit) as excinfo:
            BuildUtils.build_package()
        assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_publish_package_success():
    """Test publishing package successfully."""
    mock_process = mock.AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (b"Upload successful", b"")
    
    with mock.patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
        # Test publishing to PyPI
        result = await BuildUtils.publish_package(
            username="testuser",
            password="testpass",
            config_file="/path/to/config"
        )
        
        assert result["success"] is True
        assert "Package published successfully" in result["message"]
        assert "Upload successful" in result["output"]
        
        # Check that correct command was executed
        mock_exec.assert_called_once()
        cmd_args = mock_exec.call_args[0]
        assert "twine" in cmd_args
        assert "upload" in cmd_args
        assert "--username" in cmd_args
        assert "--password" in cmd_args
        assert "--config-file" in cmd_args


@pytest.mark.asyncio
async def test_publish_package_failure():
    """Test publishing package with failure."""
    mock_process = mock.AsyncMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = (b"", b"Upload failed")
    
    with mock.patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
        # Test publishing to TestPyPI
        result = await BuildUtils.publish_package(
            test=True,
            username="testuser"
        )
        
        assert result["success"] is False
        assert "Error publishing package" in result["message"]
        assert "Upload failed" in result["error"]
        
        # Check that command included TestPyPI repository
        mock_exec.assert_called_once()
        cmd_args = mock_exec.call_args[0]
        assert "--repository" in cmd_args
        assert "testpypi" in cmd_args


@pytest.mark.asyncio
async def test_publish_package_exception():
    """Test publishing package with exception."""
    with mock.patch("asyncio.create_subprocess_exec", side_effect=Exception("Connection error")) as mock_exec:
        result = await BuildUtils.publish_package()
        
        assert result["success"] is False
        assert "Error publishing package" in result["message"]
        assert "Connection error" in result["error"]
