import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock

import oarc_crawlers.cli.cmd.yt_cmd as yt_cmd

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_yt_crawler():
    with patch("oarc_crawlers.cli.cmd.yt_cmd.YTCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.download_video = AsyncMock(return_value={"success": True})
        instance.download_playlist = AsyncMock(return_value={"success": True})
        instance.extract_captions = AsyncMock(return_value={"captions": {"en": "captions.txt"}, "title": "Test"})
        instance.search_videos = AsyncMock(return_value={"results": [{"title": "Video"}], "result_count": 1})
        instance.fetch_stream_chat = AsyncMock(return_value={"message_count": 1, "text_path": "chat.txt"})
        yield

def test_yt_group_help(runner):
    result = runner.invoke(yt_cmd.yt, ["--help"])
    assert result.exit_code == 0
    assert "youtube" in result.output or "yt" in result.output

@pytest.mark.parametrize("subcmd,opts", [
    ("download", ["--url", "https://youtube.com/watch?v=abc"]),
    ("playlist", ["--url", "https://youtube.com/playlist?list=xyz"]),
    ("captions", ["--url", "https://youtube.com/watch?v=abc"]),
    ("search", ["--query", "python"]),
    ("chat", ["--video-id", "abc"]),
])
def test_yt_subcommands_run(runner, subcmd, opts):
    result = runner.invoke(yt_cmd.yt, [subcmd] + opts)
    assert result.exit_code == 0

def test_yt_download_error(runner):
    with patch("oarc_crawlers.cli.cmd.yt_cmd.YTCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.download_video = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(yt_cmd.yt, ["download", "--url", "bad"])
        assert result.exit_code != 0

def test_yt_playlist_error(runner):
    with patch("oarc_crawlers.cli.cmd.yt_cmd.YTCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.download_playlist = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(yt_cmd.yt, ["playlist", "--url", "bad"])
        assert result.exit_code != 0

def test_yt_captions_error(runner):
    with patch("oarc_crawlers.cli.cmd.yt_cmd.YTCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.extract_captions = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(yt_cmd.yt, ["captions", "--url", "bad"])
        assert result.exit_code != 0

def test_yt_search_no_results(runner):
    with patch("oarc_crawlers.cli.cmd.yt_cmd.YTCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.search_videos = AsyncMock(return_value={"results": [], "result_count": 0})
        result = runner.invoke(yt_cmd.yt, ["search", "--query", "none"])
        assert result.exit_code == 0
        assert "Found 0 videos" in result.output

def test_yt_chat_error(runner):
    with patch("oarc_crawlers.cli.cmd.yt_cmd.YTCrawler") as mock_crawler:
        instance = mock_crawler.return_value
        instance.fetch_stream_chat = AsyncMock(return_value={"error": "fail"})
        result = runner.invoke(yt_cmd.yt, ["chat", "--video-id", "bad"])
        assert result.exit_code != 0
