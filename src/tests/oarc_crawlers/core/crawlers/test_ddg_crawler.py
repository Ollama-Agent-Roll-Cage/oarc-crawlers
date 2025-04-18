import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
from pathlib import Path
import json

from oarc_crawlers import DDGCrawler

class MockResponse:
    def __init__(self, status, text):
        self.status = status
        self._text = text
        
    async def text(self):
        return self._text

class TestDuckDuckGoSearcher(unittest.TestCase):
    """Test the DuckDuckGo search module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.searcher = DDGCrawler(data_dir=self.temp_dir.name)
        
        # Mock JSON responses
        self.mock_text_response = {
            'AbstractText': 'This is a test summary about searching.',
            'RelatedTopics': [
                {'Text': 'Test Topic 1', 'FirstURL': 'https://example.com/1'},
                {'Text': 'Test Topic 2', 'FirstURL': 'https://example.com/2'},
                {'Text': 'Test Topic 3', 'FirstURL': 'https://example.com/3'}
            ]
        }
        
        self.mock_image_response = {
            'Images': [
                {'Image': 'https://example.com/img1.jpg', 'Title': 'Image 1', 'Source': 'Source 1', 'URL': 'https://example.com/1'},
                {'Image': 'https://example.com/img2.jpg', 'Title': 'Image 2', 'Source': 'Source 2', 'URL': 'https://example.com/2'}
            ]
        }
        
        self.mock_news_response = {
            'News': [
                {'Title': 'News 1', 'URL': 'https://example.com/news1', 'Source': 'Source 1', 'Date': '2025-04-10', 'Excerpt': 'News excerpt 1'},
                {'Title': 'News 2', 'URL': 'https://example.com/news2', 'Source': 'Source 2', 'Date': '2025-04-09', 'Excerpt': 'News excerpt 2'}
            ]
        }
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    @patch('aiohttp.ClientSession.get')
    @patch('oarc_crawlers.ddg_search.ParquetStorage')
    async def test_text_search(self, mock_storage, mock_get):
        """Test text search functionality."""
        # Setup mock
        mock_resp = MockResponse(200, json.dumps(self.mock_text_response))
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        # Call the method
        result = await self.searcher.text_search("test query", max_results=2)
        
        # Assert requests were made correctly
        mock_get.assert_called_once()
        self.assertIn('test query', mock_get.call_args[0][0])
        
        # Assert storage was used
        mock_storage.save_to_parquet.assert_called_once()
        
        # Check result formatting
        self.assertIn('# DuckDuckGo Search Results', result)
        self.assertIn('This is a test summary about searching', result)
        self.assertIn('Test Topic 1', result)
        self.assertIn('Test Topic 2', result)
        # Should only include 2 results due to max_results
        self.assertNotIn('Test Topic 3', result)
    
    @patch('aiohttp.ClientSession.get')
    @patch('oarc_crawlers.ddg_search.ParquetStorage')
    async def test_image_search(self, mock_storage, mock_get):
        """Test image search functionality."""
        # Setup mock
        mock_resp = MockResponse(200, json.dumps(self.mock_image_response))
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        # Call the method
        result = await self.searcher.image_search("test images", max_results=1)
        
        # Assert requests were made correctly
        mock_get.assert_called_once()
        self.assertIn('test images', mock_get.call_args[0][0])
        self.assertIn('ia=images', mock_get.call_args[0][0])
        
        # Assert storage was used
        mock_storage.save_to_parquet.assert_called_once()
        
        # Check result formatting
        self.assertIn('# DuckDuckGo Image Search Results', result)
        self.assertIn('![Image 1](https://example.com/img1.jpg)', result)
        # Should only include 1 result due to max_results
        self.assertNotIn('![Image 2]', result)
    
    @patch('aiohttp.ClientSession.get')
    @patch('oarc_crawlers.ddg_search.ParquetStorage')
    async def test_news_search(self, mock_storage, mock_get):
        """Test news search functionality."""
        # Setup mock
        mock_resp = MockResponse(200, json.dumps(self.mock_news_response))
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        # Call the method
        result = await self.searcher.news_search("test news", max_results=1)
        
        # Assert requests were made correctly
        mock_get.assert_called_once()
        self.assertIn('test news', mock_get.call_args[0][0])
        self.assertIn('ia=news', mock_get.call_args[0][0])
        
        # Assert storage was used
        mock_storage.save_to_parquet.assert_called_once()
        
        # Check result formatting
        self.assertIn('# DuckDuckGo News Search Results', result)
        self.assertIn('## News 1', result)
        self.assertIn('**Source:** Source 1', result)
        self.assertIn('**Date:** 2025-04-10', result)
        self.assertIn('News excerpt 1', result)
        # Should only include 1 result due to max_results
        self.assertNotIn('## News 2', result)
    
    @patch('aiohttp.ClientSession.get')
    async def test_error_handling(self, mock_get):
        """Test error handling."""
        # Test HTTP error
        mock_get.return_value.__aenter__.return_value = MockResponse(404, "Not Found")
        result = await self.searcher.text_search("test query")
        self.assertIn("Error: Received status code 404", result)
        
        # Test JSON parsing error
        mock_get.return_value.__aenter__.return_value = MockResponse(200, "Not JSON")
        result = await self.searcher.text_search("test query")
        self.assertIn("Error: Could not parse the search results", result)
        
        # Test exception
        mock_get.side_effect = Exception("Test exception")
        result = await self.searcher.text_search("test query")
        self.assertIn("An error occurred during the search", result)

if __name__ == '__main__':
    unittest.main()