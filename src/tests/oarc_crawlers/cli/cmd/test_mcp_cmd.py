import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock

import oarc_crawlers.cli.cmd.mcp_cmd as mcp_cmd

@pytest.fixture
def runner():
    return CliRunner()

def test_mcp_group_help(runner):
    result = runner.invoke(mcp_cmd.mcp, ["--help"])
    assert result.exit_code == 0
    assert "mcp" in result.output

def test_mcp_run_success(runner):
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = 0
        result = runner.invoke(mcp_cmd.mcp, ["run"])
        assert result.exit_code == 0

def test_mcp_run_error(runner):
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.run", side_effect=Exception("fail")):
        result = runner.invoke(mcp_cmd.mcp, ["run"])
        assert result.exit_code != 0

def test_mcp_install_success(runner):
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.install", new_callable=AsyncMock) as mock_install:
        mock_install.return_value = True
        result = runner.invoke(mcp_cmd.mcp, ["install"])
        assert result.exit_code == 0

def test_mcp_install_error(runner):
    with patch("oarc_crawlers.core.mcp.mcp_server.MCPServer.install", side_effect=Exception("fail")):
        result = runner.invoke(mcp_cmd.mcp, ["install"])
        assert result.exit_code != 0
