import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

import oarc_crawlers.cli.cmd.build_cmd as build_cmd

@pytest.fixture
def runner():
    return CliRunner()

def test_build_group_help(runner):
    result = runner.invoke(build_cmd.build, ["--help"])
    assert result.exit_code == 0
    assert "build" in result.output

def test_build_package_success(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=True):
        result = runner.invoke(build_cmd.build, ["package"])
        assert result.exit_code == 0

def test_build_package_fail(runner):
    with patch("oarc_crawlers.utils.build_utils.BuildUtils.build_package", return_value=False):
        result = runner.invoke(build_cmd.build, ["package"])
        assert result.exit_code != 0
