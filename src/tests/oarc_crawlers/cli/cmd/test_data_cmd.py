import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

import oarc_crawlers.cli.cmd.data_cmd as data_cmd

@pytest.fixture
def runner():
    return CliRunner()

def test_data_group_help(runner):
    result = runner.invoke(data_cmd.data, ["--help"])
    assert result.exit_code == 0
    assert "data" in result.output

def test_data_view_success(runner):
    with patch("oarc_crawlers.utils.data_utils.DataUtils.view_parquet", return_value="ok"):
        result = runner.invoke(data_cmd.data, ["view", "file.parquet"])
        assert result.exit_code == 0

def test_data_view_fail(runner):
    with patch("oarc_crawlers.utils.data_utils.DataUtils.view_parquet", side_effect=Exception("fail")):
        result = runner.invoke(data_cmd.data, ["view", "file.parquet"])
        assert result.exit_code != 0
