import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock

import oarc_crawlers.cli.cmd.arxiv_cmd as arxiv_cmd

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_arxiv_crawler():
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.download_source = AsyncMock(return_value={"source_files": {"main.tex": b"abc"}})
        instance.search = AsyncMock(return_value={"results": [{"title": "Test", "authors": ["A"], "id": "1", "abstract": "abs"}]})
        instance.fetch_paper_with_latex = AsyncMock(return_value={"title": "Test", "authors": ["A"], "abstract": "abs", "has_source_files": True})
        instance.extract_keywords = AsyncMock(return_value={"keywords": [{"keyword": "test", "score": 1.0}], "title": "Test"})
        instance.extract_references = AsyncMock(return_value={"references": [{"key": "ref1", "fields": {"author": "A", "title": "T"}}]})
        instance.extract_math_equations = AsyncMock(return_value={"inline_equation_count": 1, "display_equation_count": 1, "inline_equations": ["x=1"], "display_equations": ["y=2"]})
        instance.fetch_category_papers = AsyncMock(return_value={"papers": [{"title": "T", "authors": ["A"], "arxiv_id": "1", "published": "2020-01-01T00:00:00"}], "parquet_path": "foo.parquet"})
        instance.batch_fetch_papers = AsyncMock(return_value={"papers": [{}], "errors": [], "keywords": [{"keywords": ["kw"]}], "references": [{"reference_count": 1}]})
        instance.generate_citation_network = AsyncMock(return_value={"nodes": {"1": {"title": "T"}}, "edges": [{"source": "1", "target": "2"}]})
        yield

def test_arxiv_group_help(runner):
    result = runner.invoke(arxiv_cmd.arxiv, ["--help"])
    assert result.exit_code == 0
    assert "arxiv" in result.output

@pytest.mark.parametrize("subcmd,opts", [
    ("download", ["--id", "1234"]),
    ("search", ["--query", "quantum"]),
    ("latex", ["--id", "1234"]),
    ("keywords", ["--id", "1234"]),
    ("references", ["--id", "1234"]),
    ("equations", ["--id", "1234"]),
    ("category", ["--category", "cs.AI"]),
    ("batch", ["--ids", "1234"]),
    ("citation-network", ["--ids", "1234"]),
])
def test_arxiv_subcommands_run(runner, subcmd, opts):
    result = runner.invoke(arxiv_cmd.arxiv, [subcmd] + opts)
    assert result.exit_code == 0

def test_arxiv_download_error(runner):
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.download_source = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(arxiv_cmd.arxiv, ["download", "--id", "bad"])
        assert result.exit_code != 0

def test_arxiv_search_no_results(runner):
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.search = AsyncMock(return_value={"results": []})
        result = runner.invoke(arxiv_cmd.arxiv, ["search", "--query", "none"])
        assert "No papers found" in result.output

def test_arxiv_keywords_error(runner):
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.extract_keywords = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(arxiv_cmd.arxiv, ["keywords", "--id", "bad"])
        assert "Error extracting keywords" in result.output

def test_arxiv_references_error(runner):
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.extract_references = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(arxiv_cmd.arxiv, ["references", "--id", "bad"])
        assert "Error extracting references" in result.output

def test_arxiv_equations_error(runner):
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.extract_math_equations = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(arxiv_cmd.arxiv, ["equations", "--id", "bad"])
        assert "Error extracting equations" in result.output

def test_arxiv_category_error(runner):
    with patch("oarc_crawlers.cli.cmd.arxiv_cmd.ArxivCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.fetch_category_papers = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(arxiv_cmd.arxiv, ["category", "--category", "bad"])
        assert result.exit_code != 0

def test_arxiv_batch_invalid_ids(runner):
    result = runner.invoke(arxiv_cmd.arxiv, ["batch", "--ids", ""])
    assert "No valid arXiv IDs provided" in result.output

def test_arxiv_citation_network_invalid_ids(runner):
    result = runner.invoke(arxiv_cmd.arxiv, ["citation-network", "--ids", ""])
    assert "No valid arXiv IDs provided" in result.output
