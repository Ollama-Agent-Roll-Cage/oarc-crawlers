import pytest
import asyncio
import sys
import tempfile
import pathlib
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock, call, PropertyMock

# Keep only standard library imports at the top level
# Imports from the project will be moved inside the patch context

# --- Mock Setup ---
mock_log = MagicMock()
mock_yt_crawler = AsyncMock()
mock_gh_crawler = AsyncMock()
mock_ddg_crawler = AsyncMock()
mock_web_crawler = AsyncMock()
mock_arxiv_crawler = AsyncMock()
mock_mcp_utils = MagicMock()
mock_client_error = type('ClientError', (Exception,), {})

MockMCPError = type('MockMCPError', (Exception,), {})
MockTransportError = type('MockTransportError', (Exception,), {})

# --- Mock FastMCP Instance Creation ---
def create_mock_fastmcp_instance(*args, **kwargs):
    instance = MagicMock(name="MockFastMCPInstance")
    instance.name = kwargs.get("name", "DefaultMockName")
    instance.dependencies = kwargs.get("dependencies", [])
    instance.tool_registrations = {}

    def mock_tool(*tool_args, **tool_kwargs):
        def decorator(func):
            name = tool_kwargs.get('name', func.__name__)
            instance.tool_registrations[func.__name__] = {
                'func': func,
                'args': tool_args,
                'kwargs': tool_kwargs,
                'registered_name': name
            }
            return func
        return decorator

    instance.tool = mock_tool
    instance.configure_vscode = MagicMock()
    instance.start_server = AsyncMock()
    instance.__file__ = "/mock/path/to/mcp_server.py"
    return instance

# --- Global Patches ---
patch_fastmcp = patch('oarc_crawlers.core.mcp.mcp_server.FastMCP', side_effect=create_mock_fastmcp_instance)

modules_to_mock = {
    'oarc_log': MagicMock(log=mock_log),
    'aiohttp.client_exceptions': MagicMock(ClientError=mock_client_error),
    'oarc_utils.decorators': MagicMock(singleton=lambda cls: cls),
    'oarc_utils.errors': MagicMock(MCPError=MockMCPError, TransportError=MockTransportError),
    'oarc_crawlers.utils.mcp_utils': MagicMock(MCPUtils=mock_mcp_utils),
    'github': MagicMock(),
    'git': MagicMock(),
}

patch_yt = patch('oarc_crawlers.core.mcp.mcp_server.YTCrawler', return_value=mock_yt_crawler)
patch_gh = patch('oarc_crawlers.core.mcp.mcp_server.GHCrawler', return_value=mock_gh_crawler)
patch_ddg = patch('oarc_crawlers.core.mcp.mcp_server.DDGCrawler', return_value=mock_ddg_crawler)
patch_web = patch('oarc_crawlers.core.mcp.mcp_server.WebCrawler', return_value=mock_web_crawler)
patch_arxiv = patch('oarc_crawlers.core.mcp.mcp_server.ArxivCrawler', return_value=mock_arxiv_crawler)

with patch.dict(sys.modules, modules_to_mock):
    from oarc_crawlers.utils.const import FAILURE, VERSION as ACTUAL_VERSION
    MCPError = sys.modules['oarc_utils.errors'].MCPError
    TransportError = sys.modules['oarc_utils.errors'].TransportError

    @pytest.fixture
    def mcp_server():
        mock_log.reset_mock()
        mock_yt_crawler.reset_mock()
        mock_gh_crawler.reset_mock()
        mock_ddg_crawler.reset_mock()
        mock_web_crawler.reset_mock()
        mock_arxiv_crawler.reset_mock()
        mock_mcp_utils.reset_mock()

        with patch_fastmcp as mock_fastmcp_class_global, \
             patch_yt, patch_gh, patch_ddg, patch_web, patch_arxiv, \
             patch('os.environ', {}):
            if mock_fastmcp_class_global.return_value:
                 mock_fastmcp_class_global.return_value.configure_vscode.reset_mock()
                 mock_fastmcp_class_global.return_value.start_server.reset_mock()
                 mock_fastmcp_class_global.return_value.tool_registrations = {}
            mock_fastmcp_class_global.reset_mock()

            from oarc_crawlers.core.mcp import MCPServer

            server = MCPServer(data_dir="/test/data", name="TestServer", port=9999)

            assert server.data_dir == "/test/data"
            assert server.port == 9999
            mock_fastmcp_class_global.assert_called_once()
            mock_instance = mock_fastmcp_class_global.return_value
            assert server.mcp == mock_instance

            yield server, mock_instance

def test_mcp_server_init(mcp_server):
    server, mock_instance = mcp_server
    mock_fastmcp_class_global = patch_fastmcp.target
    mock_fastmcp_class_global.assert_called_once_with(
        name="TestServer",
        dependencies=[
            "pytube", "beautifulsoup4", "pandas", "pyarrow",
            "aiohttp", "gitpython", "pytchat"
        ],
        description="OARC's dynamic webcrawler module collection providing YouTube, GitHub, DuckDuckGo, web crawling, and ArXiv paper extraction capabilities.",
        version=ACTUAL_VERSION
    )
    assert server.mcp == mock_instance
    assert mock_instance.name == "TestServer"

def test_register_tools(mcp_server):
    server, mock_instance = mcp_server
    expected_tools = [
        'download_youtube_video', 'download_youtube_playlist', 'extract_youtube_captions',
        'clone_github_repo', 'analyze_github_repo', 'find_similar_code',
        'ddg_text_search', 'ddg_image_search', 'ddg_news_search',
        'crawl_webpage', 'crawl_documentation',
        'fetch_arxiv_paper', 'download_arxiv_source'
    ]

    registered_func_names = mock_instance.tool_registrations.keys()
    for tool_name in expected_tools:
        assert tool_name in registered_func_names, f"Tool function {tool_name} not found in registrations"

    youtube_reg = mock_instance.tool_registrations.get('download_youtube_video')
    assert youtube_reg is not None, "YouTube tool registration details not found"
    assert 'func' in youtube_reg
    assert 'kwargs' in youtube_reg
    assert youtube_reg['kwargs'].get('name') == 'download_youtube_video'
    assert 'description' in youtube_reg['kwargs']
    assert youtube_reg['registered_name'] == 'download_youtube_video'

@pytest.mark.asyncio
async def test_tool_download_youtube_video(mcp_server):
    server, mock_instance = mcp_server
    mock_yt_crawler.download_video = AsyncMock(return_value={"status": "success"})

    tool_func = mock_instance.tool_registrations['download_youtube_video']['func']
    result = await tool_func(server, url="https://youtube.com/testVideo", format="mp4", resolution="720p")

    mock_yt_crawler.download_video.assert_awaited_once_with("https://youtube.com/testVideo", "mp4", "720p")
    assert result == {"status": "success"}

@pytest.mark.asyncio
async def test_tool_download_youtube_video_error(mcp_server):
    server, mock_instance = mcp_server
    mock_yt_crawler.download_video = AsyncMock(side_effect=Exception("Test error"))

    tool_func = mock_instance.tool_registrations['download_youtube_video']['func']
    result = await tool_func(server, url="https://youtube.com/badVideo")

    mock_yt_crawler.download_video.assert_awaited_once_with("https://youtube.com/badVideo", "mp4", "highest")
    mock_log.error.assert_called_with("Error downloading video: Test error")
    assert "error" in result
    assert result["error"] == "Test error"

@pytest.mark.asyncio
async def test_tool_download_youtube_playlist(mcp_server):
    server, mock_instance = mcp_server
    mock_yt_crawler.download_playlist = AsyncMock(return_value={"videos": 5})

    tool_func = mock_instance.tool_registrations['download_youtube_playlist']['func']
    result = await tool_func(server, playlist_url="https://youtube.com/playlist", max_videos=10)

    mock_yt_crawler.download_playlist.assert_awaited_once_with("https://youtube.com/playlist", max_videos=10)
    assert result == {"videos": 5}

@pytest.mark.asyncio
async def test_tool_extract_youtube_captions(mcp_server):
    server, mock_instance = mcp_server
    mock_yt_crawler.extract_captions = AsyncMock(return_value={"en": "English captions"})
    tool_func = mock_instance.tool_registrations['extract_youtube_captions']['func']
    result = await tool_func(server, url="https://youtube.com/video", languages=["en", "es"])
    mock_yt_crawler.extract_captions.assert_awaited_once_with("https://youtube.com/video", ["en", "es"])
    assert result == {"en": "English captions"}

@pytest.mark.asyncio
async def test_tool_clone_github_repo(mcp_server):
    server, mock_instance = mcp_server
    mock_gh_crawler.clone_and_store_repo = AsyncMock(return_value="/path/to/repo")
    tool_func = mock_instance.tool_registrations['clone_github_repo']['func']
    result = await tool_func(server, repo_url="https://github.com/user/repo")
    mock_gh_crawler.clone_and_store_repo.assert_awaited_once_with("https://github.com/user/repo")
    assert result == "/path/to/repo"

@pytest.mark.asyncio
async def test_tool_analyze_github_repo(mcp_server):
    server, mock_instance = mcp_server
    mock_gh_crawler.get_repo_summary = AsyncMock(return_value="Repo summary")
    tool_func = mock_instance.tool_registrations['analyze_github_repo']['func']
    result = await tool_func(server, repo_url="https://github.com/user/repo")
    mock_gh_crawler.get_repo_summary.assert_awaited_once_with("https://github.com/user/repo")
    assert result == "Repo summary"

@pytest.mark.asyncio
async def test_tool_find_similar_code(mcp_server):
    server, mock_instance = mcp_server
    mock_gh_crawler.find_similar_code = AsyncMock(return_value="Similar code")
    tool_func = mock_instance.tool_registrations['find_similar_code']['func']
    result = await tool_func(server, repo_url="https://github.com/user/repo", code_snippet="def hello(): pass")
    mock_gh_crawler.find_similar_code.assert_awaited_once_with("https://github.com/user/repo", "def hello(): pass")
    assert result == "Similar code"

@pytest.mark.asyncio
async def test_tool_ddg_text_search(mcp_server):
    server, mock_instance = mcp_server
    mock_ddg_crawler.text_search = AsyncMock(return_value="Search results")
    tool_func = mock_instance.tool_registrations['ddg_text_search']['func']
    result = await tool_func(server, query="test query", max_results=5)
    mock_ddg_crawler.text_search.assert_awaited_once_with("test query", 5)
    assert result == "Search results"

@pytest.mark.asyncio
async def test_tool_ddg_image_search(mcp_server):
    server, mock_instance = mcp_server
    mock_ddg_crawler.image_search = AsyncMock(return_value="Image results")
    tool_func = mock_instance.tool_registrations['ddg_image_search']['func']
    result = await tool_func(server, query="test images", max_results=10)
    mock_ddg_crawler.image_search.assert_awaited_once_with("test images", 10)
    assert result == "Image results"

@pytest.mark.asyncio
async def test_tool_ddg_news_search(mcp_server):
    server, mock_instance = mcp_server
    mock_ddg_crawler.news_search = AsyncMock(return_value="News results")
    tool_func = mock_instance.tool_registrations['ddg_news_search']['func']
    result = await tool_func(server, query="test news", max_results=20)
    mock_ddg_crawler.news_search.assert_awaited_once_with("test news", 20)
    assert result == "News results"

@pytest.mark.asyncio
async def test_tool_crawl_webpage(mcp_server):
    server, mock_instance = mcp_server
    mock_web_crawler.fetch_url_content = AsyncMock(return_value="Page content")
    tool_func = mock_instance.tool_registrations['crawl_webpage']['func']
    result = await tool_func(server, url="https://example.com")
    mock_web_crawler.fetch_url_content.assert_awaited_once_with("https://example.com")
    assert result == "Page content"

@pytest.mark.asyncio
async def test_tool_crawl_documentation(mcp_server):
    server, mock_instance = mcp_server
    mock_web_crawler.crawl_documentation_site = AsyncMock(return_value="Documentation content")
    tool_func = mock_instance.tool_registrations['crawl_documentation']['func']
    result = await tool_func(server, url="https://docs.example.com")
    mock_web_crawler.crawl_documentation_site.assert_awaited_once_with("https://docs.example.com")
    assert result == "Documentation content"

@pytest.mark.asyncio
async def test_tool_fetch_arxiv_paper(mcp_server):
    server, mock_instance = mcp_server
    mock_arxiv_crawler.fetch_paper_info = AsyncMock(return_value={"title": "Paper title"})
    tool_func = mock_instance.tool_registrations['fetch_arxiv_paper']['func']
    result = await tool_func(server, arxiv_id="1234.5678")
    mock_arxiv_crawler.fetch_paper_info.assert_awaited_once_with("1234.5678")
    assert result == {"title": "Paper title"}

@pytest.mark.asyncio
async def test_tool_download_arxiv_source(mcp_server):
    server, mock_instance = mcp_server
    mock_arxiv_crawler.download_source = AsyncMock(return_value={"path": "/path/to/source"})
    tool_func = mock_instance.tool_registrations['download_arxiv_source']['func']
    result = await tool_func(server, arxiv_id="1234.5678")
    mock_arxiv_crawler.download_source.assert_awaited_once_with("1234.5678")
    assert result == {"path": "/path/to/source"}

@pytest.mark.asyncio
@patch('asyncio.sleep', new_callable=AsyncMock)
async def test_start_server_success(mock_sleep, mcp_server):
    server, mock_instance = mcp_server
    mock_sleep.side_effect = asyncio.CancelledError("Stop loop")

    with pytest.raises(asyncio.CancelledError):
        await server.start_server()

    mock_instance.configure_vscode.assert_called_once_with(
        server_name=mock_instance.name,
        port=server.port,
        supports_streaming=True
    )

    mock_instance.start_server.assert_awaited_once_with(
        port=server.port,
        transport="ws"
    )

    mock_log.info.assert_called_with(f"MCP server started on port {server.port}")
    mock_sleep.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_start_server_client_error(mcp_server):
    server, mock_instance = mcp_server
    mock_instance.configure_vscode.side_effect = mock_client_error("Connection problem")

    with pytest.raises(TransportError, match="Connection error: Connection problem"):
        await server.start_server()

    mock_log.error.assert_called_with("Client error: Connection problem")
    mock_instance.start_server.assert_not_awaited()

@pytest.mark.asyncio
async def test_start_server_other_error(mcp_server):
    server, mock_instance = mcp_server
    test_exception = ValueError("Config error")
    mock_instance.configure_vscode.side_effect = test_exception

    with pytest.raises(MCPError, match=f"MCP server error: {test_exception}"):
        await server.start_server()

    mock_log.error.assert_called_with(f"Unexpected error: {test_exception}")
    mock_instance.start_server.assert_not_awaited()

@patch('asyncio.run')
@patch('oarc_crawlers.core.mcp.mcp_server.MCPServer.start_server', new_callable=AsyncMock)
def test_run_success(mock_start_server_method, mock_asyncio_run, mcp_server):
    server, _ = mcp_server
    mock_asyncio_run.return_value = "Server result"

    result = server.run(transport="ws")

    mock_asyncio_run.assert_called_once()
    mock_start_server_method.assert_called_once()
    assert result == "Server result"

@patch('asyncio.run')
@patch('sys.exit')
def test_run_keyboard_interrupt(mock_sys_exit, mock_asyncio_run, mcp_server):
    server, _ = mcp_server
    mock_asyncio_run.side_effect = KeyboardInterrupt()

    server.run()

    mock_log.error.assert_called_with("Server stopped by user")
    mock_sys_exit.assert_called_once_with(FAILURE)

@patch('asyncio.run')
def test_run_mcp_error(mock_asyncio_run, mcp_server):
    server, _ = mcp_server
    test_exception = MockTransportError("Transport failed")
    mock_asyncio_run.side_effect = test_exception

    with pytest.raises(MCPError, match=f"MCP server error: {test_exception}"):
        server.run()

@patch('asyncio.run')
def test_run_unexpected_error(mock_asyncio_run, mcp_server):
    server, _ = mcp_server
    test_exception = ValueError("Unexpected error")
    mock_asyncio_run.side_effect = test_exception

    with pytest.raises(MCPError, match=f"Unexpected error in MCP server: {test_exception}"):
        server.run()

def test_install(mcp_server):
    server, mock_instance = mcp_server
    mock_mcp_utils_class = sys.modules['oarc_crawlers.utils.mcp_utils'].MCPUtils
    mock_mcp_utils_class.install_mcp.return_value = True

    result = server.install(name="CustomInstall")

    import oarc_crawlers.core.mcp.mcp_server
    expected_script_path = oarc_crawlers.core.mcp.mcp_server.__file__

    mock_mcp_utils_class.install_mcp.assert_called_once_with(
        script_path=expected_script_path,
        name="CustomInstall",
        mcp_name=server.mcp.name,
        dependencies=server.mcp.dependencies
    )

    assert result is True
    mock_log.info.assert_called_with("MCP server installed as 'CustomInstall'")
