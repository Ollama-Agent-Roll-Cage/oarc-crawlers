"""OARC-Crawlers core crawlers package.

This package contains various specialized crawlers for different data sources.
"""

from .arxiv_crawler import ArxivCrawler
from .ddg_crawler import DDGCrawler
from .gh_crawler import GHCrawler
from .web_crawler import WebCrawler
from .yt_crawler import YTCrawler
from .oeis_crawler import OEISCrawler

__all__ = [
    "ArxivCrawler",
    "DDGCrawler",
    "GHCrawler",
    "WebCrawler",
    "YTCrawler",
    "OEISCrawler",
]
