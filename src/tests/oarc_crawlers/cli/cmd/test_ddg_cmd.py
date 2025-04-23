import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock

import oarc_crawlers.cli.cmd.ddg_cmd as ddg_cmd

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_ddg_crawler():
    with patch("oarc_crawlers.cli.cmd.ddg_cmd.DDGCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        # Return dictionaries instead of strings
        instance.text_search = AsyncMock(return_value={"results": ["result1"], "count": 1})
        instance.image_search = AsyncMock(return_value={"results": ["image1"], "count": 1})
        instance.news_search = AsyncMock(return_value={"results": ["news1"], "count": 1})
        yield

def test_ddg_group_help(runner):
    result = runner.invoke(ddg_cmd.ddg, ["--help"])
    assert result.exit_code == 0
    assert "ddg" in result.output

@pytest.mark.parametrize("subcmd,opts", [
    ("text", ["--query", "python"]),
    ("images", ["--query", "cats"]),
    ("news", ["--query", "ai"]),
])
def test_ddg_subcommands_run(runner, subcmd, opts):
    result = runner.invoke(ddg_cmd.ddg, [subcmd] + opts)
    assert result.exit_code == 0

def test_ddg_text_error(runner):
    with patch("oarc_crawlers.cli.cmd.ddg_cmd.DDGCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.text_search = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(ddg_cmd.ddg, ["text", "--query", "bad"])
        assert result.exit_code != 0

def test_ddg_images_error(runner):
    with patch("oarc_crawlers.cli.cmd.ddg_cmd.DDGCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.image_search = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(ddg_cmd.ddg, ["images", "--query", "bad"])
        assert result.exit_code != 0

def test_ddg_news_error(runner):
    with patch("oarc_crawlers.cli.cmd.ddg_cmd.DDGCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.news_search = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(ddg_cmd.ddg, ["news", "--query", "bad"])
        assert result.exit_code != 0
