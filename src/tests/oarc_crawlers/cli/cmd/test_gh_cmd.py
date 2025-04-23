import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock

import oarc_crawlers.cli.cmd.gh_cmd as gh_cmd

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_gh_crawler():
    with patch("oarc_crawlers.cli.cmd.gh_cmd.GHCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.clone_and_store_repo = AsyncMock(return_value="cloned")
        instance.get_repo_summary = AsyncMock(return_value="summary")
        instance.find_similar_code = AsyncMock(return_value="similar")
        yield

def test_gh_group_help(runner):
    result = runner.invoke(gh_cmd.gh, ["--help"])
    assert result.exit_code == 0
    assert "github" in result.output or "gh" in result.output

@pytest.mark.parametrize("subcmd,opts", [
    ("clone", ["--url", "https://github.com/user/repo"]),
    ("analyze", ["--url", "https://github.com/user/repo"]),
    ("find-similar", ["--url", "https://github.com/user/repo", "--code", "def foo():"]),
])
def test_gh_subcommands_run(runner, subcmd, opts):
    result = runner.invoke(gh_cmd.gh, [subcmd] + opts)
    assert result.exit_code == 0

def test_gh_clone_error(runner):
    with patch("oarc_crawlers.cli.cmd.gh_cmd.GHCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.clone_and_store_repo = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(gh_cmd.gh, ["clone", "--url", "bad"])
        assert result.exit_code != 0

def test_gh_analyze_error(runner):
    with patch("oarc_crawlers.cli.cmd.gh_cmd.GHCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.get_repo_summary = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(gh_cmd.gh, ["analyze", "--url", "bad"])
        assert result.exit_code != 0

def test_gh_find_similar_error(runner):
    with patch("oarc_crawlers.cli.cmd.gh_cmd.GHCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.find_similar_code = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(gh_cmd.gh, ["find-similar", "--url", "bad", "--code", "foo"])
        assert result.exit_code != 0
