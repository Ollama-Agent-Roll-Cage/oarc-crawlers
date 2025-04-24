import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

import oarc_crawlers.cli.cmd.mcp_cmd as mcp_cmd
from oarc_crawlers.utils.const import SUCCESS, ERROR

@pytest.fixture
def runner():
    return CliRunner()

def test_mcp_group_help(runner):
    result = runner.invoke(mcp_cmd.mcp, ["--help"])
    assert result.exit_code == 0
    assert "mcp" in result.output

def test_mcp_run_success(runner):
    # Since we removed the @asyncio_run decorator, we can use a regular mock
    def fake_run(*args, **kwargs):
        return 0
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.run", new=fake_run):
        result = runner.invoke(mcp_cmd.mcp, ["run"])
        assert result.exit_code == 0

def test_mcp_run_error(runner):
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.run", side_effect=Exception("fail")):
        result = runner.invoke(mcp_cmd.mcp, ["run"])
        assert result.exit_code != 0

def test_mcp_install_success(runner):
    # Since we removed the @asyncio_run decorator, we can use a regular mock
    def fake_install(*args, **kwargs):
        return True
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.install", new=fake_install):
        result = runner.invoke(mcp_cmd.mcp, ["install"])
        assert result.exit_code == 0

def test_mcp_install_error(runner):
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.install", side_effect=Exception("fail")):
        result = runner.invoke(mcp_cmd.mcp, ["install"])
        assert result.exit_code != 0

def test_mcp_stop_all_success(runner):
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.stop_all_mcp_servers", return_value=(2, 0)):
        # Mock sys.exit to prevent the test from exiting
        with patch("sys.exit"):
            result = runner.invoke(mcp_cmd.mcp, ["stop", "--all"])
            assert "Successfully stopped 2 MCP server(s)" in result.output

def test_mcp_stop_port_success(runner):
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.stop_mcp_server_on_port", return_value=True):
        # Mock sys.exit to prevent the test from exiting
        with patch("sys.exit"):
            result = runner.invoke(mcp_cmd.mcp, ["stop", "--port", "5000"])
            assert "MCP server on port 5000 stopped successfully" in result.output

def test_mcp_list_no_servers(runner):
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.list_mcp_servers", return_value=[]):
        result = runner.invoke(mcp_cmd.mcp, ["list"])
        assert "No MCP servers currently running" in result.output
        assert result.exit_code == SUCCESS

def test_mcp_list_with_servers(runner):
    fake_server = {
        'pid': 12345,
        'port': 3000,
        'status': 'running',
        'uptime_sec': 3600,
        'memory_mb': 50.5,
        'cpu_percent': 2.5,
        'connections': 3
    }
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.list_mcp_servers", return_value=[fake_server]):
        with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.format_uptime", return_value="1h 0m 0s"):
            result = runner.invoke(mcp_cmd.mcp, ["list"])
            assert "Found 1 running MCP server(s)" in result.output
            assert "12345" in result.output
            assert "3000" in result.output
            assert "running" in result.output
            assert "50.5 MB" in result.output
            assert result.exit_code == SUCCESS

def test_mcp_list_with_none_values(runner):
    # Test with None values that previously caused the TypeError
    fake_server = {
        'pid': 12345,
        'port': None,  # This was causing the error
        'status': 'running',
        'uptime_sec': 3600,
        'memory_mb': None,  # Also test None for memory
        'cpu_percent': None,
        'connections': 3
    }
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.list_mcp_servers", return_value=[fake_server]):
        with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.format_uptime", return_value="1h 0m 0s"):
            result = runner.invoke(mcp_cmd.mcp, ["list"])
            assert "Found 1 running MCP server(s)" in result.output
            assert "12345" in result.output
            assert "N/A" in result.output  # Check that None values are displayed as N/A
            assert result.exit_code == SUCCESS

def test_mcp_list_json_format(runner):
    fake_server = {
        'pid': 12345,
        'port': 3000,
        'status': 'running',
        'uptime_sec': 3600,
        'memory_mb': 50.5
    }
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.list_mcp_servers", return_value=[fake_server]):
        result = runner.invoke(mcp_cmd.mcp, ["list", "--format", "json"])
        assert '"pid": 12345' in result.output
        assert '"port": 3000' in result.output
        assert result.exit_code == SUCCESS

def test_mcp_list_verbose(runner):
    fake_server = {
        'pid': 12345,
        'port': 3000,
        'status': 'running',
        'uptime_sec': 3600,
        'memory_mb': 50.5,
        'cpu_percent': 2.5,
        'connections': 3
    }
    with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.list_mcp_servers", return_value=[fake_server]):
        with patch("oarc_crawlers.utils.mcp_utils.MCPUtils.format_uptime", return_value="1h 0m 0s"):
            result = runner.invoke(mcp_cmd.mcp, ["list", "--verbose"])
            assert "CPU" in result.output
            assert "Connections" in result.output
            assert "2.5%" in result.output
            assert "3" in result.output
            assert result.exit_code == SUCCESS
