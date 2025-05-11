"""Tests for the mcp_utils module."""
import os
import signal
import subprocess
import inspect
import socket
import time
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
        mock_run.assert_called_once()
        
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


def test_is_mcp_running_on_port():
    """Test checking if an MCP server is running on a port."""
    # Mock socket to simulate port check
    with mock.patch("socket.socket") as mock_socket:
        mock_socket_instance = mock_socket.return_value
        
        # Test port in use
        mock_socket_instance.connect_ex.return_value = 0
        assert MCPUtils.is_mcp_running_on_port(3000) is True
        
        # Test port not in use
        mock_socket_instance.connect_ex.return_value = 1
        assert MCPUtils.is_mcp_running_on_port(3000) is False
        
        # Test error handling
        mock_socket_instance.connect_ex.side_effect = Exception("Network error")
        assert MCPUtils.is_mcp_running_on_port(3000) is False


def test_find_mcp_process_on_port():
    """Test finding an MCP server process on a port."""
    # Mock psutil for process detection
    mock_process = mock.MagicMock()
    mock_process.info = {'pid': 12345, 'cmdline': ['python', '-m', 'oarc-crawlers', 'mcp', 'run']}
    
    mock_connection = mock.MagicMock()
    mock_connection.laddr = mock.MagicMock()
    mock_connection.laddr.port = 3000
    
    with mock.patch("oarc_crawlers.utils.mcp_utils.psutil.process_iter") as mock_process_iter:
        # Test process found
        mock_process_iter.return_value = [mock_process]
        mock_process.connections.return_value = [mock_connection]
        
        result = MCPUtils.find_mcp_process_on_port(3000)
        assert result is mock_process
        
        # Test no process found
        mock_process.connections.return_value = []
        result = MCPUtils.find_mcp_process_on_port(3000)
        assert result is None
        
        # Test process found but not matching port
        mock_connection.laddr.port = 4000
        mock_process.connections.return_value = [mock_connection]
        result = MCPUtils.find_mcp_process_on_port(3000)
        assert result is None


def test_find_all_mcp_processes():
    """Test finding all MCP server processes."""
    # Mock psutil for process detection
    mock_process1 = mock.MagicMock()
    mock_process1.info = {'pid': 12345, 'cmdline': ['python', '-m', 'oarc-crawlers', 'mcp', 'run']}
    
    mock_process2 = mock.MagicMock()
    mock_process2.info = {'pid': 12346, 'cmdline': ['python', '-m', 'oarc-crawlers', 'mcp', 'run']}
    
    mock_other_process = mock.MagicMock()
    mock_other_process.info = {'pid': 12347, 'cmdline': ['python', '-m', 'something-else']}
    
    with mock.patch("oarc_crawlers.utils.mcp_utils.psutil.process_iter") as mock_process_iter:
        # Test processes found
        mock_process_iter.return_value = [mock_process1, mock_process2, mock_other_process]
        
        result = MCPUtils.find_all_mcp_processes()
        assert len(result) == 2
        assert mock_process1 in result
        assert mock_process2 in result
        assert mock_other_process not in result
        
        # Test no processes found
        mock_process_iter.return_value = [mock_other_process]
        result = MCPUtils.find_all_mcp_processes()
        assert len(result) == 0


def test_terminate_process():
    """Test terminating a process."""
    # Import signal directly in test to avoid platform-specific issues
    import signal
    
    # Mock the platform module for consistent testing
    with mock.patch("os.kill") as mock_kill, \
         mock.patch("psutil.pid_exists") as mock_pid_exists, \
         mock.patch("time.sleep") as mock_sleep, \
         mock.patch("subprocess.run") as mock_run:
        
        # Test successful termination
        mock_pid_exists.side_effect = [True, False]  # Process exists, then doesn't
        
        result = MCPUtils.terminate_process(12345)
        
        assert result is True
        # Check kill was called but don't check with which signal as it's platform-dependent
        mock_kill.assert_called_once()
        assert mock_pid_exists.call_count == 2
        assert mock_sleep.call_count == 1
        
        # Test termination requiring force
        mock_kill.reset_mock()
        mock_pid_exists.reset_mock()
        mock_pid_exists.side_effect = [True, True, True, True, True, True]  # Process never dies gracefully
        
        # Force = False
        result = MCPUtils.terminate_process(12345, force=False)
        
        assert result is False
        mock_kill.assert_called_once()  # Don't check signal, it's platform-dependent
        
        # Force = True
        mock_kill.reset_mock()
        mock_pid_exists.reset_mock()
        mock_run.reset_mock()
        # Process exists during wait loop (5 calls), then doesn't exist after force kill (6th call)
        mock_pid_exists.side_effect = [True, True, True, True, True, False] 
        
        # Setup the mock to simulate successful taskkill on Windows or kill on Unix
        if hasattr(signal, 'SIGKILL'):
            # Unix path
            result = MCPUtils.terminate_process(12345, force=True)
            assert mock_kill.call_count == 2 # SIGTERM then SIGKILL
        else:
            # Windows path
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = MCPUtils.terminate_process(12345, force=True)
            # On Windows, it might try os.kill(0) then taskkill
            assert mock_kill.call_count >= 1 or mock_run.called

        assert result is True # Should now return True as pid_exists returns False after force
        
        # Test error handling
        mock_kill.reset_mock()
        mock_run.reset_mock()
        mock_pid_exists.reset_mock() # Clear side effect
        mock_kill.side_effect = Exception("Permission denied")
        mock_run.side_effect = Exception("Command failed")
        
        result = MCPUtils.terminate_process(12345)
        
        assert result is False


def test_stop_mcp_server_on_port():
    """Test stopping an MCP server on a port."""
    # Test no server running
    with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.is_mcp_running_on_port") as mock_is_running:
        mock_is_running.return_value = False
        
        result = MCPUtils.stop_mcp_server_on_port(3000)
        assert result is True
    
    # Test server running but process not found
    with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.is_mcp_running_on_port") as mock_is_running, \
         mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.find_mcp_process_on_port") as mock_find_process:
        mock_is_running.return_value = True
        mock_find_process.return_value = None
        
        result = MCPUtils.stop_mcp_server_on_port(3000)
        assert result is True
    
    # Test server running and process found and terminated
    with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.is_mcp_running_on_port") as mock_is_running, \
         mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.find_mcp_process_on_port") as mock_find_process, \
         mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.terminate_process") as mock_terminate:
        mock_is_running.return_value = True
        
        mock_process = mock.MagicMock()
        mock_process.info = {'pid': 12345}
        mock_find_process.return_value = mock_process
        
        mock_terminate.return_value = True
        
        result = MCPUtils.stop_mcp_server_on_port(3000)
        assert result is True
        mock_terminate.assert_called_once_with(12345, False)
        
        # Test termination failure
        mock_terminate.return_value = False
        
        result = MCPUtils.stop_mcp_server_on_port(3000)
        assert result is False


def test_stop_all_mcp_servers():
    """Test stopping all MCP servers."""
    # Test no servers found
    with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.find_all_mcp_processes") as mock_find_all:
        mock_find_all.return_value = []
        
        success_count, error_count = MCPUtils.stop_all_mcp_servers()
        assert success_count == 0
        assert error_count == 0
    
    # Test servers found and terminated
    with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.find_all_mcp_processes") as mock_find_all, \
         mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.terminate_process") as mock_terminate:
        
        mock_process1 = mock.MagicMock()
        mock_process1.info = {'pid': 12345}
        
        mock_process2 = mock.MagicMock()
        mock_process2.info = {'pid': 12346}
        
        mock_find_all.return_value = [mock_process1, mock_process2]
        
        # Both succeed
        mock_terminate.side_effect = [True, True]
        
        success_count, error_count = MCPUtils.stop_all_mcp_servers()
        assert success_count == 2
        assert error_count == 0
        assert mock_terminate.call_count == 2
        
        # One succeeds, one fails
        mock_terminate.reset_mock()
        mock_terminate.side_effect = [True, False]
        
        success_count, error_count = MCPUtils.stop_all_mcp_servers()
        assert success_count == 1
        assert error_count == 1


def test_list_mcp_servers():
    """Test listing all MCP server processes."""
    # Mock psutil for process detection
    mock_process = mock.MagicMock()
    original_cmdline = ['python', '-m', 'oarc-crawlers', 'mcp', 'run', '--port', '3000']
    mock_process.info = {
        'pid': 12345, 
        'cmdline': original_cmdline[:] # Use a copy
    }
    mock_process.create_time.return_value = time.time() - 3600  # Created 1 hour ago
    mock_process.memory_info.return_value = mock.MagicMock(rss=50 * 1024 * 1024)  # 50 MB
    mock_process.cpu_percent.return_value = 2.5
    
    # Mock a connection
    mock_connection = mock.MagicMock()
    mock_connection.laddr = mock.MagicMock(port=3000)
    mock_process.connections.return_value = [mock_connection]
    
    with mock.patch("oarc_crawlers.utils.mcp_utils.MCPUtils.find_all_mcp_processes") as mock_find_all:
        mock_find_all.return_value = [mock_process]
        
        result = MCPUtils.list_mcp_servers()
        assert len(result) == 1
        assert result[0]['pid'] == 12345
        assert result[0]['port'] == 3000
        assert result[0]['status'] == 'running'
        assert result[0]['memory_mb'] > 0
        assert result[0]['cpu_percent'] == 2.5
        assert result[0]['connections'] == 1
        
        # Test with missing values and exceptions
        # Reset side effects and return values for the second run
        mock_process.connections.side_effect = Exception("No permission")
        mock_process.connections.return_value = None # Explicitly set return value after side effect
        mock_process.cpu_percent.side_effect = Exception("Cannot get CPU")
        mock_process.cpu_percent.return_value = None # Explicitly set return value after side effect
        # Modify cmdline for this specific case to prevent fallback port parsing
        mock_process.info['cmdline'] = ['python', '-m', 'oarc-crawlers', 'mcp', 'run'] # No --port arg
        
        result = MCPUtils.list_mcp_servers()
        assert len(result) == 1
        assert result[0]['pid'] == 12345
        # Port should be the default (3000) because cmdline parsing finds 'oarc-crawlers mcp run'
        # but no explicit --port, and connection info failed. If cmdline was empty or different,
        # it might be None. Let's test the default port case.
        assert result[0]['port'] == 3000 # Default port fallback when connection fails and no explicit port arg
        assert result[0]['cpu_percent'] is None  # No CPU due to exception
        assert result[0]['connections'] == 0 # Reset connections count as it failed

        # Restore original cmdline if needed for further tests (though not strictly necessary here)
        mock_process.info['cmdline'] = original_cmdline[:]
        # Reset side effects if needed
        mock_process.connections.side_effect = None
        mock_process.cpu_percent.side_effect = None


def test_format_uptime():
    """Test formatting uptime in seconds to a human-readable string."""
    # Test seconds only
    assert MCPUtils.format_uptime(30) == "30s"
    
    # Test minutes and seconds
    assert MCPUtils.format_uptime(90) == "1m 30s"
    
    # Test hours, minutes, seconds
    assert MCPUtils.format_uptime(3661) == "1h 1m 1s"
    
    # Test days, hours, minutes, seconds
    assert MCPUtils.format_uptime(90061) == "1d 1h 1m 1s"
    
    # Test with zero
    assert MCPUtils.format_uptime(0) == "0s"
