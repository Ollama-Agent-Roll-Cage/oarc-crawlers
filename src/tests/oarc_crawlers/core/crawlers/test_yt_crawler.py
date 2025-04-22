import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from oarc_crawlers import YTCrawler
from oarc_crawlers.utils.crawler_utils import CrawlerUtils

@patch('oarc_crawlers.yt_crawler.ParquetStorage')
class TestYTCrawler(unittest.TestCase):
    """Test the YouTube downloader module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        # YTCrawler should accept data_dir parameter
        self.crawler = YTCrawler(data_dir=self.temp_dir.name)
        
        # Mock YouTube video data
        self.mock_video_id = "dQw4w9WgXcQ"
        self.mock_video_url = f"https://www.youtube.com/watch?v={self.mock_video_id}"
        
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
        
    @patch('pytube.YouTube')
    @patch('oarc_crawlers.yt_crawler.ParquetStorage')
    async def test_download_video(self, mock_storage, mock_youtube_class):
        """Test downloading a video."""
        # Setup mock objects
        mock_youtube = mock_youtube_class.return_value
        mock_youtube.video_id = self.mock_video_id
        mock_youtube.title = "Test Video"
        mock_youtube.author = "Test Author"
        mock_youtube.description = "Test Description"
        mock_youtube.length = 100
        mock_youtube.publish_date = None
        mock_youtube.views = 10000
        mock_youtube.rating = 4.5
        mock_youtube.thumbnail_url = "https://example.com/thumbnail.jpg"
        mock_youtube.keywords = ["test", "video"]
        mock_youtube.channel_url = "https://youtube.com/channel/test"
        
        # Setup mock stream
        mock_stream = MagicMock()
        mock_stream.download.return_value = os.path.join(self.temp_dir.name, "test_video.mp4")
        mock_youtube.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value = mock_stream
        
        # Mock the _extract_video_info and _generate_metadata_path methods
        with patch.object(self.crawler, '_extract_video_info') as mock_extract, \
             patch.object(self.crawler, '_generate_metadata_path') as mock_path:
            
            mock_extract.return_value = {
                'title': "Test Video",
                'video_id': self.mock_video_id,
                'url': self.mock_video_url,
                'author': "Test Author"
            }
            mock_path.return_value = os.path.join(self.temp_dir.name, f"{self.mock_video_id}.parquet")
            
            # Create a file to make getsize() work
            with open(os.path.join(self.temp_dir.name, "test_video.mp4"), 'w') as f:
                f.write("test data")
                
            # Call the method
            result = await self.crawler.download_video(self.mock_video_url)
            
            # Assert correct calls were made
            mock_youtube_class.assert_called_once_with(self.mock_video_url)
            mock_youtube.streams.filter.assert_called()
            mock_stream.download.assert_called()
            mock_storage.save_to_parquet.assert_called()
            
            # Check result
            self.assertEqual(result['video_id'], self.mock_video_id)
            self.assertIn('file_path', result)

    @patch('pytube.Playlist')
    @patch('oarc_crawlers.yt_crawler.YouTubeDownloader.download_video')
    @patch('oarc_crawlers.yt_crawler.ParquetStorage')
    async def test_download_playlist(self, mock_storage, mock_download_video, mock_playlist_class):
        """Test downloading a playlist."""
        # Setup mock objects
        mock_playlist = mock_playlist_class.return_value
        mock_playlist.title = "Test Playlist"
        mock_playlist.playlist_id = "PLTest123"
        mock_playlist.playlist_url = "https://www.youtube.com/playlist?list=PLTest123"
        mock_playlist.owner = "Test Owner"
        mock_playlist.video_urls = [
            "https://www.youtube.com/watch?v=video1",
            "https://www.youtube.com/watch?v=video2",
            "https://www.youtube.com/watch?v=video3"
        ]
        
        # Mock the download_video method
        mock_download_video.side_effect = [
            {'video_id': 'video1', 'title': 'Video 1', 'file_path': '/path/to/video1.mp4'},
            {'video_id': 'video2', 'title': 'Video 2', 'file_path': '/path/to/video2.mp4'},
            {'video_id': 'video3', 'title': 'Video 3', 'file_path': '/path/to/video3.mp4'}
        ]
        
        # Call the method with max_videos=2 to test the limit
        result = await self.crawler.download_playlist("https://www.youtube.com/playlist?list=PLTest123", max_videos=2)
        
        # Assertions
        mock_playlist_class.assert_called_once()
        self.assertEqual(mock_download_video.call_count, 2)  # Should only download 2 videos due to max_videos
        mock_storage.save_to_parquet.assert_called_once()
        
        # Check result structure
        self.assertEqual(result['title'], "Test Playlist")
        self.assertEqual(result['playlist_id'], "PLTest123")
        self.assertEqual(len(result['videos']), 2)
        self.assertEqual(result['videos_to_download'], 2)
        
    @patch('pytube.Search')
    @patch('oarc_crawlers.yt_crawler.ParquetStorage')
    async def test_search_videos(self, mock_storage, mock_search_class):
        """Test searching for videos."""
        # Setup mock video objects
        mock_video1 = MagicMock()
        mock_video1.title = "Test Video 1"
        mock_video1.video_id = "video1"
        mock_video1.author = "Author 1"
        mock_video1.description = "Description 1"
        mock_video1.publish_date = None
        mock_video1.length = 100
        mock_video1.views = 1000
        mock_video1.thumbnail_url = "https://example.com/thumb1.jpg"
        
        mock_video2 = MagicMock()
        mock_video2.title = "Test Video 2"
        mock_video2.video_id = "video2"
        mock_video2.author = "Author 2"
        mock_video2.description = "Description 2"
        mock_video2.publish_date = None
        mock_video2.length = 200
        mock_video2.views = 2000
        mock_video2.thumbnail_url = "https://example.com/thumb2.jpg"
        
        # Setup the mock search
        mock_search = mock_search_class.return_value
        mock_search.results = [mock_video1, mock_video2]
        
        # Call the method
        result = await self.crawler.search_videos("test query", limit=1)
        
        # Assertions
        mock_search_class.assert_called_once_with("test query")
        mock_storage.save_to_parquet.assert_called_once()
        
        # Check result structure
        self.assertEqual(result['query'], "test query")
        self.assertEqual(len(result['results']), 1)  # Should only include 1 result due to limit
        self.assertEqual(result['results'][0]['title'], "Test Video 1")
        self.assertEqual(result['results'][0]['video_id'], "video1")
        
    @patch('pytube.YouTube')
    @patch('oarc_crawlers.yt_crawler.ParquetStorage')
    async def test_extract_captions(self, mock_storage, mock_youtube_class):
        """Test extracting captions."""
        # Setup mock objects
        mock_youtube = mock_youtube_class.return_value
        mock_youtube.video_id = self.mock_video_id
        mock_youtube.title = "Test Video"
        
        # Mock the captions
        mock_caption_en = MagicMock()
        mock_caption_en.code = "en"
        mock_caption_en.generate_srt_captions.return_value = "1\n00:00:01,000 --> 00:00:05,000\nThis is a test caption."
        
        mock_captions = MagicMock()
        mock_captions.all.return_value = [mock_caption_en]
        mock_youtube.captions = mock_captions
        
        # Mock the _extract_video_info method
        with patch.object(self.crawler, '_extract_video_info') as mock_extract, \
             patch("builtins.open", unittest.mock.mock_open()) as mock_file:
                
            mock_extract.return_value = {
                'title': "Test Video",
                'video_id': self.mock_video_id,
                'url': self.mock_video_url
            }
                
            # Call the method
            result = await self.crawler.extract_captions(self.mock_video_url)
                
            # Assertions
            mock_youtube_class.assert_called_once_with(self.mock_video_url)
            mock_captions.all.assert_called()
            mock_caption_en.generate_srt_captions.assert_called_once()
            mock_file.assert_called()
            mock_storage.save_to_parquet.assert_called_once()
                
            # Check result structure
            self.assertEqual(result['video_id'], self.mock_video_id)
            self.assertEqual(result['title'], "Test Video")
            self.assertIn('captions', result)
            self.assertIn('en', result['captions'])
    
    def test_generate_metadata_path(self):
        """Test generating the metadata path."""
        video_id = "testVideoId"
        path = self.crawler._generate_metadata_path(video_id)
        expected_path = str(Path(self.temp_dir.name) / "youtube_data" / "metadata" / f"{video_id}.parquet")
        self.assertEqual(path, expected_path)
    
    @patch('pytube.YouTube')
    def test_extract_video_info(self, mock_youtube_class):
        """Test extracting video information."""
        # Test the CrawlerUtils method instead
        mock_youtube = MagicMock()
        mock_youtube.title = "Test Video"
        mock_youtube.video_id = self.mock_video_id
        mock_youtube.author = "Test Author"
        mock_youtube.channel_url = "https://youtube.com/channel/test"
        mock_youtube.description = "Test Description"
        mock_youtube.length = 100
        mock_youtube.publish_date = None
        mock_youtube.views = 10000
        mock_youtube.rating = 4.5
        mock_youtube.thumbnail_url = "https://example.com/thumbnail.jpg"
        mock_youtube.keywords = ["test", "video"]
        
        # Call the method
        result = CrawlerUtils.extract_video_info(mock_youtube)
        
        # Assertions
        self.assertEqual(result['title'], "Test Video")
        self.assertEqual(result['video_id'], self.mock_video_id)
        self.assertEqual(result['author'], "Test Author")
        self.assertEqual(result['channel_url'], "https://youtube.com/channel/test")
        self.assertEqual(result['description'], "Test Description")
        self.assertEqual(result['length'], 100)
        self.assertEqual(result['views'], 10000)
        self.assertEqual(result['rating'], 4.5)
        self.assertEqual(result['thumbnail_url'], "https://example.com/thumbnail.jpg")
        self.assertEqual(result['keywords'], ["test", "video"])

if __name__ == '__main__':
    unittest.main()