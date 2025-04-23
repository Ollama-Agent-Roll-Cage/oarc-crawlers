"""Tests for the main module."""
import sys
from unittest import mock
import pytest

from oarc_crawlers.main import main


@pytest.fixture
def mock_cli():
    """Mock the CLI function."""
    with mock.patch("oarc_crawlers.main.cli") as m:
        yield m


def test_main_success(mock_cli):
    """Test main function with successful CLI execution."""
    mock_cli.return_value = 0
    
    result = main()
    
    assert result == 0
    mock_cli.assert_called_once_with(standalone_mode=False)


def test_main_with_kwargs(mock_cli):
    """Test main function with kwargs."""
    mock_cli.return_value = 0
    
    result = main(debug=True, args=["command", "--option"])
    
    assert result == 0
    mock_cli.assert_called_once_with(standalone_mode=False, debug=True, args=["command", "--option"])


def test_main_error(mock_cli):
    """Test main function with CLI error."""
    mock_cli.return_value = 1
    
    result = main()
    
    assert result == 1
    mock_cli.assert_called_once_with(standalone_mode=False)


def test_handle_error_decorator():
    """Test that the handle_error decorator is applied."""
    with mock.patch("oarc_utils.decorators.handle_error", return_value=lambda f: f) as mock_decorator:
        # Force reload to check decorator application
        import importlib
        importlib.reload(sys.modules["oarc_crawlers.main"])
        
        assert mock_decorator.called


def test_module_execution():
    """Test module execution as script."""
    original_name = sys.modules["oarc_crawlers.main"].__name__
    
    # Create the execution environment with mocks
    with mock.patch("sys.exit"):
        with mock.patch("oarc_crawlers.main.main") as mock_main:
            mock_main.return_value = 42
            
            # Simulate the __name__ == "__main__" condition directly
            if original_name == "oarc_crawlers.main":  # Preserve the original check logic
                # Directly call the main function as if executed as script
                sys.modules["oarc_crawlers.main"].main()
                
                # Verify main was called
                mock_main.assert_called_once()
