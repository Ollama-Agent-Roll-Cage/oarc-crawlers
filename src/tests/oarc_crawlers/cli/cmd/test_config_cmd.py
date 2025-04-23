import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

import oarc_crawlers.cli.cmd.config_cmd as config_cmd

@pytest.fixture
def runner():
    return CliRunner()

def test_config_group_help(runner):
    result = runner.invoke(config_cmd.config, ["--help"])
    assert result.exit_code == 0
    assert "config" in result.output

def test_config_run(monkeypatch, runner):
    # Patch ConfigEditor.run to just return
    monkeypatch.setattr("oarc_crawlers.config.config_editor.ConfigEditor.run", lambda *a, **kw: None)
    result = runner.invoke(config_cmd.config)
    assert result.exit_code == 0

def test_config_run_with_file(monkeypatch, runner):
    monkeypatch.setattr("oarc_crawlers.config.config_editor.ConfigEditor.run", lambda *a, **kw: None)
    result = runner.invoke(config_cmd.config, ["myconfig.ini"])
    assert result.exit_code == 0
