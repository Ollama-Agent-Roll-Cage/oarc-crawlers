import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock

import oarc_crawlers.cli.cmd.web_cmd as web_cmd

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_web_crawler():
    with patch("oarc_crawlers.cli.cmd.web_cmd.WebCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        # Return strings for HTML/text extraction
        instance.fetch_url_content = AsyncMock(return_value="<html>sample content</html>")
        instance.extract_text_from_html = AsyncMock(return_value="extracted text")
        instance.crawl_documentation_site = AsyncMock(return_value="docs content")
        instance.extract_pypi_content = AsyncMock(return_value={
            "name": "requests",
            "metadata": {"info": ["version 1.0"]},
            "documentation": "Sample docs"
        })
        yield

def test_web_group_help(runner):
    result = runner.invoke(web_cmd.web, ["--help"])
    assert result.exit_code == 0
    assert "web" in result.output

@pytest.mark.parametrize("subcmd,opts", [
    ("crawl", ["--url", "https://example.com"]),
    ("docs", ["--url", "https://docs.python.org"]),
    ("pypi", ["--package", "requests"]),
])
def test_web_subcommands_run(runner, subcmd, opts):
    result = runner.invoke(web_cmd.web, [subcmd] + opts)
    assert result.exit_code == 0

def test_web_crawl_error(runner):
    with patch("oarc_crawlers.cli.cmd.web_cmd.WebCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.fetch_url_content = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(web_cmd.web, ["crawl", "--url", "bad"])
        assert result.exit_code != 0

def test_web_docs_error(runner):
    with patch("oarc_crawlers.cli.cmd.web_cmd.WebCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.crawl_documentation_site = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(web_cmd.web, ["docs", "--url", "bad"])
        assert result.exit_code != 0

def test_web_pypi_error(runner):
    with patch("oarc_crawlers.cli.cmd.web_cmd.WebCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.fetch_pypi_info = AsyncMock(side_effect=Exception("fail"))
        result = runner.invoke(web_cmd.web, ["pypi", "--package", "bad"])
        assert result.exit_code != 0
