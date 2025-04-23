import tempfile
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from oarc_crawlers import DDGCrawler
from oarc_utils.errors import NetworkError, DataExtractionError

# Change the patch target to the method instead of the import
MOCK_METHOD = 'oarc_crawlers.core.crawlers.ddg_crawler.DDGCrawler._get_ddgs_client'

@pytest.fixture
def crawler():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield DDGCrawler(data_dir=temp_dir)

class TestDDGCrawler:
    """Test the DuckDuckGo search crawler module."""

    @pytest.mark.asyncio
    @patch(MOCK_METHOD)
    async def test_text_search(self, mock_get_client, crawler):
        """Test text search functionality."""
        # Create a mock client
        mock_client = AsyncMock()
        mock_context = AsyncMock()
        mock_client.__aenter__.return_value = mock_context
        mock_get_client.return_value = mock_client
        
        # Set up the mock response
        mock_results = [
            {"title": "Test Title", "url": "https://example.com", "description": "Test Description"}
        ]
        mock_context.text.return_value = mock_results

        # Call the async method
        result = await crawler.search("test query", search_type="text")

        # Use pytest assertions
        assert result['query'] == "test query"
        assert len(result['results']) == 1
        assert result['results'][0]['title'] == "Test Title"
        mock_context.text.assert_called_once_with("test query", max_results=10)

    @pytest.mark.asyncio
    @patch(MOCK_METHOD)
    async def test_image_search(self, mock_get_client, crawler):
        """Test image search functionality."""
        # Create a mock client
        mock_client = AsyncMock()
        mock_context = AsyncMock()
        mock_client.__aenter__.return_value = mock_context
        mock_get_client.return_value = mock_client
        
        # Set up the mock response
        mock_results = [
            {"title": "Test Image", "url": "https://example.com/image.jpg", "source": "Example Source"}
        ]
        mock_context.images.return_value = mock_results

        # Call the async method
        result = await crawler.search("test query", search_type="image", max_results=5)

        # Use pytest assertions
        assert result['query'] == "test query"
        assert len(result['results']) == 1
        assert result['results'][0]['title'] == "Test Image"
        mock_context.images.assert_called_once_with("test query", max_results=5)

    @pytest.mark.asyncio
    @patch(MOCK_METHOD)
    async def test_news_search(self, mock_get_client, crawler):
        """Test news search functionality."""
        # Create a mock client
        mock_client = AsyncMock()
        mock_context = AsyncMock()
        mock_client.__aenter__.return_value = mock_context
        mock_get_client.return_value = mock_client
        
        # Set up the mock response
        mock_results = [
            {"title": "Test News", "url": "https://example.com/news", "source": "News Source", "date": "2025-04-10"}
        ]
        mock_context.news.return_value = mock_results

        # Call the async method
        result = await crawler.search("test query", search_type="news", max_results=3)

        # Use pytest assertions
        assert result['query'] == "test query"
        assert len(result['results']) == 1
        assert result['results'][0]['title'] == "Test News"
        mock_context.news.assert_called_once_with("test query", max_results=3)

    @pytest.mark.asyncio
    @patch(MOCK_METHOD)
    async def test_error_handling(self, mock_get_client, crawler):
        """Test error handling."""
        # Create a mock client
        mock_client = AsyncMock()
        mock_context = AsyncMock()
        mock_client.__aenter__.return_value = mock_context
        mock_get_client.return_value = mock_client
        
        # Simulate network error
        mock_context.text.side_effect = Exception("Network failed")
        with pytest.raises(NetworkError):
            await crawler.search("test query", search_type="text")

        # Simulate no results found
        mock_context.text.side_effect = None  # Reset side effect
        mock_context.text.return_value = []
        with pytest.raises(DataExtractionError):
            await crawler.search("no results query", search_type="text")