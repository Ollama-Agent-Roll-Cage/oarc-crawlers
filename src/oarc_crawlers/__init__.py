"""OARC Crawlers - A collection of web crawlers and data extraction tools."""

__version__ = "0.1.8"
__author__ = "OARC Team"

from oarc_crawlers.core.crawlers.yt_crawler import YTCrawler
from oarc_crawlers.core.crawlers.gh_crawler import GHCrawler
from oarc_crawlers.core.crawlers.arxiv_crawler import ArxivCrawler
from oarc_crawlers.core.crawlers.web_crawler import WebCrawler
from oarc_crawlers.core.crawlers.ddg_crawler import DDGCrawler
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.core.mcp.mcp_server import MCPServer

__all__ = [
    "YTCrawler",
    "GHCrawler", 
    "ArxivCrawler",
    "WebCrawler",
    "DDGCrawler",
    "ParquetStorage",
    "MCPServer",
]
