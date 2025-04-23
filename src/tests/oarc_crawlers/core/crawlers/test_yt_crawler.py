import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
from datetime import datetime

from oarc_crawlers.core.crawlers.yt_crawler import YTCrawler
from oarc_crawlers.utils.crawler_utils import CrawlerUtils

@pytest.fixture
def crawler():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield YTCrawler(data_dir=temp_dir)

class TestYTCrawler:
    def test_init(self, crawler):
        assert crawler.data_dir is not None

    def test_extract_video_info(self):
        mock_video = MagicMock()
        mock_video.title = "Test Video"
        mock_video.video_id = "dQw4w9WgXcQ"
        mock_video.author = "Test Author"
        mock_video.channel_url = "https://youtube.com/channel/test"
        mock_video.description = "Test description"
        mock_video.length = 60
        mock_video.publish_date = datetime(2022, 1, 1)
        mock_video.views = 1000
        mock_video.rating = 4.5
        mock_video.thumbnail_url = "https://img.youtube.com/test"
        mock_video.keywords = ["test", "video"]
        info = CrawlerUtils.extract_video_info(mock_video)
        assert info["title"] == "Test Video"
        assert info["video_id"] == "dQw4w9WgXcQ"
        assert info["author"] == "Test Author"
        assert "timestamp" in info

    @pytest.mark.asyncio
    @patch('oarc_crawlers.core.crawlers.yt_crawler.YouTube')
    @patch('oarc_crawlers.core.crawlers.yt_crawler.ParquetStorage')
    async def test_download_video(self, mock_storage, mock_youtube, crawler):
        mock_yt_instance = MagicMock()
        mock_youtube.return_value = mock_yt_instance
        mock_stream = MagicMock()
        mock_stream.download.return_value = os.path.join(crawler.data_dir, 'test_video.mp4')
        mock_stream.resolution = "720p"
        mock_stream.mime_type = "video/mp4"
        mock_yt_instance.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value = mock_stream
        mock_yt_instance.title = "Test Video"
        mock_yt_instance.video_id = "dQw4w9WgXcQ"
        mock_yt_instance.author = "Test Author"
        mock_yt_instance.channel_url = "https://youtube.com/channel/test"
        mock_yt_instance.description = "Test description"
        mock_yt_instance.length = 60
        mock_yt_instance.publish_date = datetime(2022, 1, 1)
        mock_yt_instance.views = 1000
        mock_yt_instance.rating = 4.5
        mock_yt_instance.thumbnail_url = "https://img.youtube.com/test"
        mock_yt_instance.keywords = ["test", "video"]
        with patch('os.path.getsize', return_value=1024):
            result = await crawler.download_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert result['video_id'] == "dQw4w9WgXcQ"
            assert result['title'] == "Test Video"
            assert result['file_path'].endswith('test_video.mp4')
            assert result['file_size'] == 1024
            assert 'download_time' in result

    @pytest.mark.asyncio
    @patch('oarc_crawlers.core.crawlers.yt_crawler.Playlist')
    @patch('oarc_crawlers.core.crawlers.yt_crawler.YTCrawler.download_video', new_callable=AsyncMock)
    @patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet')
    async def test_download_playlist(self, mock_save, mock_download_video, mock_playlist, crawler):
        mock_playlist_instance = MagicMock()
        mock_playlist.return_value = mock_playlist_instance
        mock_playlist_instance.title = "Test Playlist"
        mock_playlist_instance.playlist_id = "PLTest123"
        mock_playlist_instance.playlist_url = "https://www.youtube.com/playlist?list=PLTest123"
        mock_playlist_instance.owner = "Test Owner"
        mock_playlist_instance.video_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=abcdefghijk"
        ]
        mock_download_video.side_effect = [
            {"video_id": "dQw4w9WgXcQ", "title": "Video 1", "file_path": "/path/to/video1.mp4"},
            {"video_id": "abcdefghijk", "title": "Video 2", "file_path": "/path/to/video2.mp4"}
        ]
        result = await crawler.download_playlist("https://www.youtube.com/playlist?list=PLTest123", max_videos=2)
        assert result['title'] == "Test Playlist"
        assert result['playlist_id'] == "PLTest123"
        assert len(result['videos']) == 2
        assert result['videos_to_download'] == 2
        assert mock_download_video.await_count == 2

    @pytest.mark.asyncio
    @patch('oarc_crawlers.core.crawlers.yt_crawler.Search')
    @patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet')
    async def test_search_videos(self, mock_save, mock_search, crawler):
        mock_search_instance = MagicMock()
        mock_search.return_value = mock_search_instance
        mock_video = MagicMock()
        mock_video.title = "Test Video 1"
        mock_video.video_id = "dQw4w9WgXcQ"
        mock_video.author = "Author 1"
        mock_video.publish_date = None
        mock_video.description = "Description 1"
        mock_video.length = 100
        mock_video.views = 1000
        mock_video.thumbnail_url = "https://example.com/thumb1.jpg"
        mock_search_instance.results = [mock_video]
        result = await crawler.search_videos("test query", limit=1)
        assert result['query'] == "test query"
        assert len(result['results']) == 1
        assert result['results'][0]['title'] == "Test Video 1"
        assert result['results'][0]['video_id'] == "dQw4w9WgXcQ"

    @pytest.mark.asyncio
    @patch('oarc_crawlers.core.crawlers.yt_crawler.YouTube')
    @patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet')
    async def test_extract_captions(self, mock_save, mock_youtube, crawler):
        mock_yt_instance = MagicMock()
        mock_youtube.return_value = mock_yt_instance
        mock_caption = MagicMock()
        mock_caption.code = "en"
        mock_caption.generate_srt_captions.return_value = "1\n00:00:01,000 --> 00:00:05,000\nThis is a test caption."
        mock_captions = MagicMock()
        mock_captions.all.return_value = [mock_caption]
        mock_yt_instance.captions = mock_captions
        mock_yt_instance.title = "Test Video"
        mock_yt_instance.video_id = "dQw4w9WgXcQ"
        with patch('builtins.open', MagicMock()):
            result = await crawler.extract_captions("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert result['video_id'] == "dQw4w9WgXcQ"
            assert result['title'] == "Test Video"
            assert 'captions' in result
            assert 'en' in result['captions']

    @pytest.mark.asyncio
    @patch('pytchat.create')
    @patch('oarc_crawlers.core.storage.parquet_storage.ParquetStorage.save_to_parquet')
    async def test_fetch_stream_chat(self, mock_save, mock_pytchat_create, crawler):
        original_method = crawler.fetch_stream_chat
        
        async def mocked_fetch_chat(video_id, max_messages=10, save_to_file=True, duration=None):
            return {
                'video_id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'timestamp': datetime.now().isoformat(),
                'messages': [{
                    'datetime': "2023-01-01 12:00:00",
                    'timestamp': 1672574400,
                    'author_name': "Test User",
                    'author_id': "user123",
                    'message': "Hello, world!",
                    'type': "textMessage",
                    'is_verified': True,
                    'is_chat_owner': False,
                    'is_chat_sponsor': False,
                    'is_chat_moderator': True,
                    'badges': ["moderator"]
                }],
                'message_count': 1,
                'parquet_path': f"/path/to/{video_id}_chat.parquet",
                'text_path': f"/path/to/{video_id}_chat.txt"
            }
            
        crawler.fetch_stream_chat = mocked_fetch_chat
        
        try:
            result = await crawler.fetch_stream_chat("dQw4w9WgXcQ", max_messages=10, save_to_file=True)
            
            assert result['video_id'] == "dQw4w9WgXcQ"
            assert len(result['messages']) == 1
            assert result['message_count'] == 1
            assert result['messages'][0]['author_name'] == "Test User"
            assert result['messages'][0]['message'] == "Hello, world!"
            assert result['messages'][0]['is_verified'] is True
            assert result['messages'][0]['is_chat_moderator'] is True
            assert 'parquet_path' in result
            assert 'text_path' in result
            
        finally:
            crawler.fetch_stream_chat = original_method
