"""
OARC-Crawlers MCP API Wrapper
Provides a Model Context Protocol (MCP) interface for the OARC-Crawlers package.
"""
from typing import Dict, List, Optional
import asyncio
import logging
from fastmcp import FastMCP, TransportError, ClientError

from .youtube_script import YouTubeDownloader
from .gh_crawler import GitHubCrawler
from .ddg_search import DuckDuckGoSearcher
from .beautiful_soup import BSWebCrawler
from .arxiv_fetcher import ArxivFetcher
from .parquet_storage import ParquetStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OARCCrawlersMCP:
    """MCP wrapper for OARC-Crawlers providing a unified API."""
    
    def __init__(self, data_dir: Optional[str] = None, name: str = "OARC-Crawlers", port: int = 3000):
        """Initialize the OARC-Crawlers MCP wrapper."""
        self.data_dir = data_dir
        self.port = port
        
        # Initialize MCP server with required configuration
        self.mcp = FastMCP(
            name=name,
            dependencies=[
                "pytube", "beautifulsoup4", "pandas", "pyarrow",
                "aiohttp", "gitpython", "pytchat"
            ],
            description="OARC's dynamic webcrawler module collection providing YouTube, GitHub, DuckDuckGo, web crawling, and ArXiv paper extraction capabilities.",
            version="0.1.4"
        )
        
        # Initialize crawlers
        self.youtube = YouTubeDownloader(data_dir=data_dir)
        self.github = GitHubCrawler(data_dir=data_dir)
        self.ddg = DuckDuckGoSearcher(data_dir=data_dir)
        self.bs = BSWebCrawler(data_dir=data_dir)
        self.arxiv = ArxivFetcher(data_dir=data_dir)
        
        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all crawler tools with MCP."""
        # YouTube tools
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
                logger.error(f"Error downloading video: {e}")
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
        
        # GitHub tools
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
        
        # DuckDuckGo tools
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
        
        # BeautifulSoup tools
        @self.mcp.tool()
        async def crawl_webpage(url: str) -> str:
            """Crawl and extract content from a webpage."""
            return await self.bs.fetch_url_content(url)
            
        @self.mcp.tool()
        async def crawl_documentation(url: str) -> str:
            """Crawl and extract content from a documentation site."""
            return await self.bs.crawl_documentation_site(url)
        
        # ArXiv tools
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
            
            logger.info(f"MCP server started on port {self.port}")
            
            # Keep server running
            while True:
                await asyncio.sleep(1)
                
        except TransportError as e:
            logger.error(f"Transport error: {e}")
            raise
        except ClientError as e:
            logger.error(f"Client error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def run(self, transport: str = "ws", **kwargs):
        """Run the MCP server."""
        try:
            return asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Error running server: {e}")
            raise
    
    def install(self, name: str = None):
        """Install the MCP server for VS Code integration."""
        import subprocess
        try:
            cmd = ["fastmcp", "install", __file__, "--vscode"]
            if name:
                cmd.extend(["--name", name])
            subprocess.run(cmd, check=True)
            logger.info(f"MCP server installed as '{name or self.mcp.name}'")
        except subprocess.CalledProcessError as e:
            logger.error(f"Installation failed: {e}")
            raise

# Create default instance
default_wrapper = OARCCrawlersMCP()

if __name__ == "__main__":
    default_wrapper.run()