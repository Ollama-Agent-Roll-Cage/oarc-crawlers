"""
OARC-Crawlers MCP Tools

This module provides a unified Model Context Protocol (MCP) API wrapper for the OARC-Crawlers package.
It exposes YouTube, GitHub, DuckDuckGo, web crawling, and ArXiv tools as MCP-compatible endpoints,
enabling seamless integration with FastMCP servers and VS Code extensions.

Author: @Borcherdingl, RawsonK
Date: 2025-04-18
"""
import sys
import asyncio
from typing import Dict, List, Optional

from fastmcp import FastMCP
from aiohttp.client_exceptions import ClientError

from oarc_crawlers.core import (
    YTCrawler,
    GHCrawler,
    DDGCrawler,
    WebCrawler,
    ArxivCrawler,
)
from oarc_crawlers.utils.const import FAILURE, VERSION
from oarc_crawlers.utils.errors import MCPError, TransportError
from oarc_crawlers.utils.log import log
from oarc_crawlers.decorators.singleton import singleton

@singleton
class MCPServer:
    """
    MCPTools provides a unified Model Context Protocol (MCP) API for OARC-Crawlers.

    This class exposes YouTube, GitHub, DuckDuckGo, web crawling, and ArXiv tools as
    MCP-compatible endpoints, enabling seamless integration with FastMCP servers,
    VS Code extensions, and other MCP clients.

    It handles initialization, tool registration, server management, and installation
    for streamlined deployment and developer experience.
    """
    
    def __init__(self, data_dir: Optional[str] = None, name: str = "OARC-Crawlers", port: int = 3000):
        """Initialize the OARC-Crawlers MCP wrapper."""
        self.data_dir = data_dir
        self.port = port
        
        # Initialize MCP server with required configuration
        self.mcp = FastMCP(
            name=name,
            dependencies=[
            "pytube",         # YouTube downloading
            "beautifulsoup4", # Web crawling/parsing
            "pandas",         # Data handling
            "pyarrow",        # Parquet storage
            "aiohttp",        # Async HTTP requests
            "gitpython",      # GitHub repo cloning
            "pytchat"         # YouTube live chat
            ],
            description="OARC's dynamic webcrawler module collection providing YouTube, GitHub, DuckDuckGo, web crawling, and ArXiv paper extraction capabilities.",
            version=VERSION
        )
        
        # Initialize our creepy crawlers
        self.youtube = YTCrawler(data_dir=data_dir)
        self.github = GHCrawler(data_dir=data_dir)
        self.ddg = DDGCrawler(data_dir=data_dir)
        self.bs = WebCrawler(data_dir=data_dir)
        self.arxiv = ArxivCrawler(data_dir=data_dir)
        
        # Register OARC-Crawler MCP tools
        self._register_tools()

    def _register_tools(self):
        """Register all crawler tools with MCP."""
        # --- YouTube tools ---
        @self.mcp.tool(
            name="download_youtube_video",
            description="Download a YouTube video with specified format and resolution."
        )
        async def download_youtube_video(url: str, format: str = "mp4", 
                                      resolution: str = "highest") -> Dict:
            """Download a YouTube video."""
            try:
                return await self.youtube.download_video(url, format, resolution)
            except Exception as e:
                log.error(f"Error downloading video: {e}")
                return {"error": str(e)}
            
        @self.mcp.tool()
        async def download_youtube_playlist(playlist_url: str, 
                                         max_videos: int = 10) -> Dict:
            """Download videos from a YouTube playlist."""
            return await self.youtube.download_playlist(playlist_url, 
                                                      max_videos=max_videos)
            
        @self.mcp.tool()
        async def extract_youtube_captions(url: str, 
                                        languages: List[str] = ["en"]) -> Dict:
            """Extract captions from a YouTube video."""
            return await self.youtube.extract_captions(url, languages)
        
        # --- GitHub tools ---
        @self.mcp.tool()
        async def clone_github_repo(repo_url: str) -> str:
            """Clone and analyze a GitHub repository."""
            return await self.github.clone_and_store_repo(repo_url)
            
        @self.mcp.tool()
        async def analyze_github_repo(repo_url: str) -> str:
            """Get a summary analysis of a GitHub repository."""
            return await self.github.get_repo_summary(repo_url)
            
        @self.mcp.tool()
        async def find_similar_code(repo_url: str, code_snippet: str) -> str:
            """Find similar code in a GitHub repository."""
            return await self.github.find_similar_code(repo_url, code_snippet)
        
        # --- DuckDuckGo tools ---
        @self.mcp.tool()
        async def ddg_text_search(query: str, max_results: int = 5) -> str:
            """Perform a DuckDuckGo text search."""
            return await self.ddg.text_search(query, max_results)
            
        @self.mcp.tool()
        async def ddg_image_search(query: str, max_results: int = 10) -> str:
            """Perform a DuckDuckGo image search."""
            return await self.ddg.image_search(query, max_results)
            
        @self.mcp.tool()
        async def ddg_news_search(query: str, max_results: int = 20) -> str:
            """Perform a DuckDuckGo news search."""
            return await self.ddg.news_search(query, max_results)
        
        # ---  Web tools ---
        @self.mcp.tool()
        async def crawl_webpage(url: str) -> str:
            """Crawl and extract content from a webpage."""
            return await self.bs.fetch_url_content(url)
            
        @self.mcp.tool()
        async def crawl_documentation(url: str) -> str:
            """Crawl and extract content from a documentation site."""
            return await self.bs.crawl_documentation_site(url)
        
        # --- ArXiv tools ---
        @self.mcp.tool()
        async def fetch_arxiv_paper(arxiv_id: str) -> Dict:
            """Fetch paper information from ArXiv."""
            return await self.arxiv.fetch_paper_info(arxiv_id)
            
        @self.mcp.tool()
        async def download_arxiv_source(arxiv_id: str) -> Dict:
            """Download LaTeX source files for an ArXiv paper."""
            return await self.arxiv.download_source(arxiv_id)
    
    async def start_server(self):
        """Start the MCP server with proper VS Code integration."""
        try:
            # Configure server for VS Code integration
            self.mcp.configure_vscode(
                server_name=self.mcp.name,
                port=self.port,
                supports_streaming=True
            )
            
            # Start server with WebSocket transport
            await self.mcp.start_server(
                port=self.port,
                transport="ws"  # Use WebSocket transport for VS Code
            )
            
            log.info(f"MCP server started on port {self.port}")
            
            # Keep server running
            while True:
                await asyncio.sleep(1)
                
        except ClientError as e:
            log.error(f"Client error: {e}")
            raise TransportError(f"Connection error: {e}")
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            raise MCPError(f"MCP server error: {e}")

    def run(self, transport: str = "ws", **kwargs):
        """Run the MCP server."""
        try:
            return asyncio.run(self.start_server())
        except KeyboardInterrupt:
            log.error("Server stopped by user")
            sys.exit(FAILURE)
        except (TransportError, MCPError) as e:
            raise MCPError(f"MCP server error: {e}")
        except Exception as e:
            raise MCPError(f"Unexpected error in MCP server: {str(e)}")
    
    def install(self, name: str = None):
        """Install the MCP server for VS Code integration."""
        from oarc_crawlers.utils.mcp_utils import MCPUtils
        return MCPUtils.install_mcp(
            script_path=__file__, 
            name=name, 
            mcp_name=self.mcp.name, 
            dependencies=self.mcp.dependencies
        )
