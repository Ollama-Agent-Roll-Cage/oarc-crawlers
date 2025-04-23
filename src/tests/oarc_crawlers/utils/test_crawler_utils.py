"""Tests for the crawler_utils module."""
import os
from datetime import datetime
from unittest import mock
import pytest

from pytube import YouTube
from oarc_utils.errors import ResourceNotFoundError
from oarc_crawlers.utils.crawler_utils import CrawlerUtils


def test_extract_youtube_id():
    """Test extracting YouTube video IDs from various formats."""
    # Test simple ID
    assert CrawlerUtils.extract_youtube_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Test youtube.com URL
    assert CrawlerUtils.extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Test youtube.com URL with parameters
    assert CrawlerUtils.extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s") == "dQw4w9WgXcQ"
    
    # Test youtu.be short URL
    assert CrawlerUtils.extract_youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Test embed URL
    assert CrawlerUtils.extract_youtube_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Test empty input
    with pytest.raises(ValueError) as excinfo:
        CrawlerUtils.extract_youtube_id("")
    assert "Empty YouTube URL" in str(excinfo.value)
    
    # Test invalid URL
    with pytest.raises(ValueError) as excinfo:
        CrawlerUtils.extract_youtube_id("https://example.com")
    assert "Could not extract YouTube video ID" in str(excinfo.value)


def test_format_timestamp():
    """Test timestamp formatting."""
    # Test with provided datetime
    test_dt = datetime(2023, 1, 1, 12, 0, 0)
    assert CrawlerUtils.format_timestamp(test_dt) == "2023-01-01T12:00:00"
    
    # Test with current time
    with mock.patch("oarc_crawlers.utils.crawler_utils.datetime") as mock_dt:
        mock_now = mock.MagicMock()
        mock_now.isoformat.return_value = "2023-02-01T15:30:45"
        mock_dt.now.return_value = mock_now
        assert CrawlerUtils.format_timestamp() == "2023-02-01T15:30:45"


def test_file_size_format():
    """Test file size formatting."""
    # Test bytes
    assert CrawlerUtils.file_size_format(500) == "500 B"
    
    # Test kilobytes
    assert CrawlerUtils.file_size_format(1500) == "1.5 KB"
    
    # Test megabytes
    assert CrawlerUtils.file_size_format(1500000) == "1.4 MB"
    
    # Test gigabytes
    assert CrawlerUtils.file_size_format(1500000000) == "1.40 GB"


def test_extract_video_info():
    """Test extracting metadata from YouTube object."""
    # Create mock YouTube object
    mock_youtube = mock.MagicMock(spec=YouTube)
    mock_youtube.title = "Test Video"
    mock_youtube.video_id = "test123"
    mock_youtube.author = "Test Author"
    mock_youtube.channel_url = "https://youtube.com/channel/test"
    mock_youtube.description = "Test description"
    mock_youtube.length = 120
    mock_youtube.publish_date.isoformat.return_value = "2023-01-01T12:00:00"
    mock_youtube.views = 1000
    mock_youtube.rating = 4.5
    mock_youtube.thumbnail_url = "https://example.com/thumbnail.jpg"
    mock_youtube.keywords = ["test", "video"]
    
    with mock.patch("oarc_crawlers.utils.crawler_utils.CrawlerUtils.format_timestamp", 
                   return_value="2023-02-01T15:30:45"):
        result = CrawlerUtils.extract_video_info(mock_youtube)
    
    # Check extracted info
    assert result["title"] == "Test Video"
    assert result["video_id"] == "test123"
    assert result["url"] == "https://www.youtube.com/watch?v=test123"
    assert result["author"] == "Test Author"
    assert result["channel_url"] == "https://youtube.com/channel/test"
    assert result["description"] == "Test description"
    assert result["length"] == 120
    assert result["publish_date"] == "2023-01-01T12:00:00"
    assert result["views"] == 1000
    assert result["rating"] == 4.5
    assert result["thumbnail_url"] == "https://example.com/thumbnail.jpg"
    assert result["keywords"] == ["test", "video"]
    assert result["timestamp"] == "2023-02-01T15:30:45"


def test_select_stream_audio_only():
    """Test selecting audio stream from YouTube object."""
    mock_youtube = mock.MagicMock(spec=YouTube)
    mock_stream = mock.MagicMock()
    mock_youtube.streams.filter.return_value.first.return_value = mock_stream
    
    result = CrawlerUtils.select_stream(
        youtube=mock_youtube,
        video_format="mp4",
        resolution="highest",
        extract_audio=True
    )
    
    assert result == mock_stream
    mock_youtube.streams.filter.assert_called_once_with(only_audio=True)


def test_select_stream_audio_not_available():
    """Test selecting audio stream when none available."""
    mock_youtube = mock.MagicMock(spec=YouTube)
    mock_youtube.streams.filter.return_value.first.return_value = None
    mock_youtube.video_id = "test123"
    
    with pytest.raises(ResourceNotFoundError) as excinfo:
        CrawlerUtils.select_stream(
            youtube=mock_youtube,
            video_format="mp4",
            resolution="highest",
            extract_audio=True
        )
    
    assert "No audio stream available" in str(excinfo.value)


def test_select_stream_highest_resolution():
    """Test selecting highest resolution video stream."""
    mock_youtube = mock.MagicMock(spec=YouTube)
    mock_stream = mock.MagicMock()
    mock_youtube.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value = mock_stream
    
    result = CrawlerUtils.select_stream(
        youtube=mock_youtube,
        video_format="mp4",
        resolution="highest",
        extract_audio=False
    )
    
    assert result == mock_stream
    mock_youtube.streams.filter.assert_called_once_with(progressive=True, file_extension="mp4")


def test_select_stream_specific_resolution():
    """Test selecting specific resolution video stream."""
    mock_youtube = mock.MagicMock(spec=YouTube)
    mock_stream = mock.MagicMock()
    mock_youtube.streams.filter.return_value.first.return_value = mock_stream
    
    result = CrawlerUtils.select_stream(
        youtube=mock_youtube,
        video_format="mp4",
        resolution="720p",
        extract_audio=False
    )
    
    assert result == mock_stream
    mock_youtube.streams.filter.assert_called_once_with(res="720p", file_extension="mp4")


def test_select_stream_specific_resolution_not_available():
    """Test fallback when specific resolution is not available."""
    mock_youtube = mock.MagicMock(spec=YouTube)
    mock_youtube.streams.filter.side_effect = [
        mock.MagicMock(first=mock.MagicMock(return_value=None)),
        mock.MagicMock(order_by=mock.MagicMock(
            return_value=mock.MagicMock(
                desc=mock.MagicMock(
                    return_value=mock.MagicMock(
                        first=mock.MagicMock(return_value="fallback_stream")
                    )
                )
            )
        ))
    ]
    
    result = CrawlerUtils.select_stream(
        youtube=mock_youtube,
        video_format="mp4",
        resolution="720p",
        extract_audio=False
    )
    
    assert result == "fallback_stream"
    assert mock_youtube.streams.filter.call_count == 2


def test_format_chat_message_for_file():
    """Test formatting chat message for text file output."""
    # Test regular message
    message = {
        "datetime": "2023-01-01 12:00:00",
        "author_name": "Test User",
        "message": "Hello world",
        "is_verified": False,
        "is_chat_owner": False,
        "is_chat_sponsor": False,
        "is_chat_moderator": False
    }
    
    result = CrawlerUtils.format_chat_message_for_file(message)
    assert result == "[2023-01-01 12:00:00] Test User: Hello world"
    
    # Test message with author tags
    message = {
        "datetime": "2023-01-01 12:00:00",
        "author_name": "Test User",
        "message": "Hello world",
        "is_verified": True,
        "is_chat_owner": True,
        "is_chat_sponsor": False,
        "is_chat_moderator": False
    }
    
    result = CrawlerUtils.format_chat_message_for_file(message)
    assert result == "[2023-01-01 12:00:00] Test User (✓, 👑): Hello world"


def test_sanitize_youtube_url():
    """Test sanitizing YouTube URLs."""
    # Test youtube.com URL
    result = CrawlerUtils.sanitize_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s")
    assert result == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Test youtu.be short URL
    result = CrawlerUtils.sanitize_youtube_url("https://youtu.be/dQw4w9WgXcQ?t=10")
    assert result == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Test invalid youtube.com URL - need to use a URL that would actually fail
    # The function only raises for URLs that don't match watch or short patterns
    with pytest.raises(ResourceNotFoundError):
        CrawlerUtils.sanitize_youtube_url("https://www.youtube.com/channel/123")


def test_get_language_from_extension():
    """Test getting programming language from file extension."""
    assert CrawlerUtils.get_language_from_extension(".py") == "Python"
    assert CrawlerUtils.get_language_from_extension(".js") == "JavaScript"
    assert CrawlerUtils.get_language_from_extension(".unknown") == "Unknown"
