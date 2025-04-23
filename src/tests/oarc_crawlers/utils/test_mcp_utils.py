"""Tests for the mcp_utils module."""
import os
import tempfile
import subprocess
import inspect
from unittest import mock
import pytest

from oarc_crawlers.utils.mcp_utils import MCPUtils
from oarc_utils.errors import MCPError


def test_install_mcp():
    """Test installing MCP server."""
    with mock.patch("subprocess.run") as mock_run:
        # Test basic installation
        result = MCPUtils.install_mcp(
            script_path="/path/to/script.py",
            name="test-server",
            mcp_name="OARC-Test",
            dependencies=["dep1", "dep2"]
        )
        
        assert result is True
        mock_run.assert_called_once_with(
            ["fastmcp", "install", "/path/to/script.py", "--vscode", 
             "--name", "test-server", "--with", "dep1", "--with", "dep2"],
            check=True
        )
        
        # Test with error
        mock_run.reset_mock()
        mock_run.side_effect = subprocess.CalledProcessError(1, "fastmcp")
        
        with pytest.raises(MCPError) as excinfo:
            MCPUtils.install_mcp(
                script_path="/path/to/script.py",
                name="test-server"
            )
        assert "Failed to install MCP server" in str(excinfo.value)


def test_install_mcp_without_script_path():
    """Test installing MCP server without providing a script path."""
    with mock.patch("tempfile.NamedTemporaryFile") as mock_temp_file:
        # Set up the mock file object
        mock_file = mock.MagicMock()
        mock_file.name = "/tmp/temp_file.py"
        mock_temp_file.return_value.__enter__.return_value = mock_file
        
        # Mock file open and write
        mock_open = mock.mock_open()
        with mock.patch("builtins.open", mock_open):
            with mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                
                # Call the function
                result = MCPUtils.install_mcp(
                    name="test-server",
                    mcp_name="OARC-Test",
                    dependencies=["dep1"]
                )
                
                # Verify the results
                assert result is True
                mock_open.assert_called_once_with("/tmp/temp_file.py", 'w')
                mock_run.assert_called_once()
                assert any("fastmcp" in str(args) for args in mock_run.call_args[0])


def test_install_mcp_with_content():
    """Test installing MCP server with provided script content."""
    with mock.patch("tempfile.NamedTemporaryFile") as mock_temp_file:
        # Set up the mock file object
        mock_file = mock.MagicMock()
        mock_file.name = "/tmp/temp_script.py"
        mock_temp_file.return_value.__enter__.return_value = mock_file
        
        # Mock file open and write
        mock_open = mock.mock_open()
        with mock.patch("builtins.open", mock_open):
            with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.install_mcp") as mock_install:
                mock_install.return_value = True
                
                # Call the function
                result = MCPUtils.install_mcp_with_content(
                    script_content="print('test')",
                    name="test-content-server",
                    dependencies=["dep1", "dep2"]
                )
                
                # Verify the results
                assert result is True
                mock_open.assert_called_once_with("/tmp/temp_script.py", 'w')
                file_handle = mock_open()
                file_handle.write.assert_called_once_with("print('test')")
                mock_install.assert_called_once_with(
                    script_path="/tmp/temp_script.py",
                    name="test-content-server",
                    mcp_name="OARC-Crawlers",
                    dependencies=["dep1", "dep2"]
                )


def test_generate_mcp_script():
    """Test generating MCP server script content."""
    result = MCPUtils.generate_mcp_script("TestServer", ["dep1", "dep2"])
    
    # Check that the generated script contains expected content
    assert "from fastmcp import FastMCP" in result
    assert "from oarc_crawlers.core.mcp.mcp_server import MCPServer" in result
    assert 'server = MCPServer(name="TestServer")' in result
    assert "server.run()" in result


def test_generate_tool_code():
    """Test generating code for tools to be included in a script."""
    # Define the test functions
    def sample_tool():
        """Sample tool function."""
        return "tool result"
    
    def another_tool(param):
        """Another sample tool function with parameter."""
        return f"tool result with {param}"
    
    tools = {
        "sample_tool": sample_tool,
        "another_tool": another_tool
    }
    
    result = MCPUtils.generate_tool_code(tools)
    
    # Check that the generated code contains decorated functions
    assert "@mcp.tool()" in result
    assert "def sample_tool():" in result
    assert "def another_tool(param):" in result
    assert "Sample tool function" in result


def test_generate_resource_code():
    """Test generating code for resources."""
    def sample_resource():
        """Sample resource function."""
        return "resource result"
    
    resources = {
        "/api/resource": sample_resource
    }
    
    result = MCPUtils.generate_resource_code(resources)
    
    # Check that the generated code contains decorated functions
    assert '@mcp.resource("/api/resource")' in result
    assert "def sample_resource():" in result
    assert "Sample resource function" in result


def test_generate_prompt_code():
    """Test generating code for prompts."""
    def sample_prompt():
        """Sample prompt function."""
        return "prompt result"
    
    prompts = {
        "sample_prompt": sample_prompt
    }
    
    result = MCPUtils.generate_prompt_code(prompts)
    
    # Check that the generated code contains decorated functions
    assert "@mcp.prompt()" in result
    assert "def sample_prompt():" in result
    assert "Sample prompt function" in result
