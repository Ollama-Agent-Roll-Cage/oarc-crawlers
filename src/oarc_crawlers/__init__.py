"""OARC Crawlers Package"""

from .arxiv_fetcher import ArxivFetcher
from .beautiful_soup import BSWebCrawler
from .ddg_search import DuckDuckGoSearcher
from .gh_crawler import GitHubCrawler
from .youtube_script import YouTubeDownloader
from .parquet_storage import ParquetStorage
from .mcp_api import OARCCrawlersMCP, default_wrapper

__version__ = '0.1.3'

__all__ = [
    "ArxivFetcher",
    "BSWebCrawler", 
    "DuckDuckGoSearcher",
    "GitHubCrawler",
    "YouTubeDownloader",
    "ParquetStorage",
    "OARCCrawlersMCP",
    "default_wrapper"
]