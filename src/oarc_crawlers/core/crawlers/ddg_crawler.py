"""
DuckDuckGo Search API with Extended Capabilities

This module provides an enhanced interface for performing DuckDuckGo text, image, and news searches.
This module also includes functionality to save search results in Parquet format for later analysis.

Author: @BorcherdingL, RawsonK
Date: 4/20/2025
"""

from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, Dict, Any

from oarc_log import log
from oarc_utils.errors import NetworkError, DataExtractionError

from oarc_crawlers.core.storage.parquet_storage import ParquetStorage
from oarc_crawlers.config.config import Config
from oarc_crawlers.utils.const import (
    DDG_TEXT_SEARCH_HEADER,
    DDG_IMAGE_SEARCH_HEADER,
    DDG_NEWS_SEARCH_HEADER,
    DEFAULT_HEADERS,
)
from oarc_crawlers.utils.paths import Paths


class DDGCrawler:
    """Class for performing searches using DuckDuckGo API."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the DuckDuckGo Searcher.
        
        Args:
            data_dir (str, optional): Directory to store data. Defaults to Config's data_dir.
        """
        # Get configuration using get_instance() pattern
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Paths.get_default_data_dir()
        
        self.searches_dir = Paths.ddg_searches_dir(self.data_dir)
        
        # Get headers from config
        self.headers = DEFAULT_HEADERS.copy()
        config = Config.get_instance()
        if config.user_agent:
            self.headers["User-Agent"] = config.user_agent

    async def text_search(self, search_query, max_results=5):
        """Perform an async text search using DuckDuckGo.
        
        Args:
            search_query (str): Query to search for
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted search results in markdown
        """
        # Use the unified search method
        result = await self.search(search_query, search_type="text", max_results=max_results)
        
        # Format the response for text search
        formatted_results = f"{result['header']}\n\n"
        
        # Add results based on available data
        if result['results']:
            formatted_results += "## Results\n\n"
            for item in result['results']:
                title = item.get('title', 'No Title')
                url = item.get('url', '#')
                description = item.get('description', 'No Description')
                formatted_results += f"### [{title}]({url})\n{description}\n\n"
        else:
            formatted_results += "No results found.\n"
            
        # Save the results to parquet storage
        self._save_search_results(search_query, "text", result)
        
        return formatted_results

    async def image_search(self, search_query, max_results=10):
        """Perform an async image search using DuckDuckGo.

        Args:
            search_query (str): Query to search for images
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted image search results in markdown
        """
        # Use the unified search method
        result = await self.search(search_query, search_type="image", max_results=max_results)
        
        # Format the response for image search
        formatted_results = f"{result['header']}\n\n"
        
        # Add results based on available data
        if result['results']:
            for item in result['results']:
                image_url = item.get('image', item.get('thumbnail', ''))
                source_url = item.get('url', '#')
                source = item.get('source', 'Unknown Source')
                title = item.get('title', 'Image')
                
                formatted_results += f"![{title}]({image_url})\n"
                formatted_results += f"[Source: {source}]({source_url})\n\n"
        else:
            formatted_results += "No image results found.\n"
            
        # Save the results to parquet storage
        self._save_search_results(search_query, "image", result)
        
        return formatted_results

    async def news_search(self, search_query, max_results=20):
        """Perform an async news search using DuckDuckGo.
        
        Args:
            search_query (str): Query to search for news
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted news search results in markdown
        """
        # Use the unified search method
        result = await self.search(search_query, search_type="news", max_results=max_results)
        
        # Format the response for news search
        formatted_results = f"{result['header']}\n\n"
        
        # Add results based on available data
        if result['results']:
            for item in result['results']:
                title = item.get('title', 'No Title')
                url = item.get('url', '#')
                source = item.get('source', 'Unknown Source')
                date = item.get('date', 'Unknown Date')
                excerpt = item.get('excerpt', '')
                
                formatted_results += f"## {title}\n"
                formatted_results += f"**Source:** {source}\n"
                formatted_results += f"**Date:** {date}\n"
                if excerpt:
                    formatted_results += f"\n{excerpt}\n"
                formatted_results += f"\n[Read more]({url})\n\n"
        else:
            formatted_results += "No news results found.\n"
            
        # Save the results to parquet storage
        self._save_search_results(search_query, "news", result)
        
        return formatted_results

    def _save_search_results(self, query: str, search_type: str, result: Dict[str, Any]):
        """Save search results to Parquet storage.
        
        Args:
            query (str): The search query
            search_type (str): Type of search
            result (Dict): Search result data
        """
        try:
            # Create search data for storage
            search_data = {
                'query': query,
                'type': search_type,
                'timestamp': datetime.now(UTC).isoformat(),
                'results': result.get('results', []),
                'result_count': len(result.get('results', [])),
            }
            
            # Use path utilities to save the search data
            file_path = Paths.ddg_search_data_path(self.data_dir, query, search_type)
            ParquetStorage.save_to_parquet(search_data, file_path)
            log.debug(f"Saved {search_type} search results for '{query}' to {file_path}")
        except Exception as e:
            log.error(f"Failed to save search results: {e}")

    async def search(self, query: str, search_type: str = "text", max_results: int = 10) -> Dict[str, Any]:
        """Search DuckDuckGo using the specified query and search type.
        
        Args:
            query (str): The search query
            search_type (str): Type of search - 'text', 'image', or 'news'
            max_results (int): Maximum number of results to return
            
        Returns:
            Dict: Search results containing query info and results list
            
        Raises:
            NetworkError: If connection fails
            DataExtractionError: If no results found
        """
        log.debug(f"Performing {search_type} search for '{query}' with max {max_results} results")
        
        try:
            # Create a client instance
            async_ddgs = self._get_ddgs_client()
            
            # Set the appropriate header based on search type
            if search_type == "text":
                header = DDG_TEXT_SEARCH_HEADER
            elif search_type == "image":
                header = DDG_IMAGE_SEARCH_HEADER
            elif search_type == "news":
                header = DDG_NEWS_SEARCH_HEADER
            else:
                raise ValueError(f"Invalid search type: {search_type}")
            
            # Perform the appropriate search based on type
            async with async_ddgs as ddgs:
                if search_type == "text":
                    results = await ddgs.text(query, max_results=max_results)
                elif search_type == "image":
                    results = await ddgs.images(query, max_results=max_results)
                elif search_type == "news":
                    results = await ddgs.news(query, max_results=max_results)
                else:
                    raise ValueError(f"Invalid search type: {search_type}")
                    
                if not results:
                    raise DataExtractionError(f"No {search_type} results found for query: {query}")
                    
                return {
                    "query": query,
                    "search_type": search_type,
                    "results": results,
                    "header": header
                }
                
        except Exception as e:
            if isinstance(e, DataExtractionError):
                raise
            log.error(f"Error during DuckDuckGo search: {str(e)}")
            raise NetworkError(f"Failed to search DuckDuckGo: {str(e)}")
    
    def _get_ddgs_client(self):
        """Get an AsyncDDGS client.
        
        This method exists to make testing easier with mock objects.
        
        Returns:
            An AsyncDDGS instance
        """
        try:
            from duckduckgo_search import AsyncDDGS
            return AsyncDDGS()
        except ImportError:
            log.warning("Could not import AsyncDDGS from duckduckgo_search.")
            # During tests, this will be patched so this error doesn't matter
            # For actual usage, the error will be properly raised and caught in search()
            raise