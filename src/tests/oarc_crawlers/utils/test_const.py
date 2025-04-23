"""Tests for the const module."""
from oarc_crawlers.utils.const import (
    DEFAULT_LOG_LEVEL,
    VERBOSE_LOG_LEVEL,
    SUCCESS,
    FAILURE,
    ERROR,
    VERSION,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    CONFIG_KEY_DATA_DIR,
    CONFIG_KEY_LOG_LEVEL,
    CONFIG_KEY_MAX_RETRIES,
    CONFIG_KEY_TIMEOUT,
    CONFIG_KEY_USER_AGENT,
    ENV_DATA_DIR,
    ENV_LOG_LEVEL,
    ENV_MAX_RETRIES,
    ENV_TIMEOUT,
    ENV_USER_AGENT,
    ENV_HOME_DIR,
    DEFAULT_CONFIG_FILENAME,
    OARC_DIR,
    CONFIG_DIR,
    CONFIG_SECTION,
    CONFIG_ENV_PREFIX,
    CONFIG_KEYS,
    DATA_SUBDIR,
    TEMP_DIR_PREFIX,
    YOUTUBE_DATA_DIR,
    GITHUB_REPOS_DIR,
    WEB_CRAWLS_DIR,
    ARXIV_PAPERS_DIR,
    ARXIV_SOURCES_DIR,
    ARXIV_COMBINED_DIR,
    DDG_SEARCHES_DIR,
    DEFAULT_HEADERS,
    PYPI_PACKAGE_URL,
    PYPI_JSON_URL,
    YOUTUBE_VIDEO_URL_FORMAT,
    YOUTUBE_CHANNEL_URL_FORMAT,
    YOUTUBE_WATCH_PATTERN,
    YOUTUBE_SHORT_PATTERN,
    YT_FORMAT_MP4,
    YT_FORMAT_WEBM,
    YT_FORMAT_MP3,
    YT_RESOLUTION_HIGHEST,
    YT_RESOLUTION_LOWEST,
    YT_RESOLUTION_720P,
    YT_RESOLUTION_1080P,
    YT_RESOLUTION_480P,
    YT_RESOLUTION_360P,
    YT_RESOLUTION_240P,
    YT_RESOLUTION_144P,
    DDG_BASE_URL,
    DDG_API_PARAMS,
    DDG_IMAGES_PARAMS,
    DDG_NEWS_PARAMS,
    DDG_TEXT_SEARCH_HEADER,
    DDG_IMAGE_SEARCH_HEADER,
    DDG_NEWS_SEARCH_HEADER,
    ARXIV_API_BASE_URL,
    ARXIV_SOURCE_URL_FORMAT,
    ARXIV_ABS_URL_FORMAT,
    ARXIV_PDF_URL_FORMAT,
    ARXIV_NAMESPACES,
    GITHUB_BINARY_EXTENSIONS,
    GITHUB_LANGUAGE_EXTENSIONS,
)


def test_constants_defined():
    """Test that all constants are properly defined."""
    # Log levels
    assert DEFAULT_LOG_LEVEL == "INFO"
    assert VERBOSE_LOG_LEVEL == "DEBUG"
    
    # Status constants
    assert SUCCESS == 0
    assert FAILURE == 1
    assert ERROR == "error"
    assert VERSION == "0.1.5"
    
    # Default values
    assert DEFAULT_MAX_RETRIES == 3
    assert DEFAULT_TIMEOUT == 30
    assert DEFAULT_USER_AGENT == f"OARC-Crawlers/{VERSION}"
    
    # Configuration keys
    assert CONFIG_KEY_DATA_DIR == "data_dir"
    assert CONFIG_KEY_LOG_LEVEL == "log_level"
    assert CONFIG_KEY_MAX_RETRIES == "max_retries"
    assert CONFIG_KEY_TIMEOUT == "timeout"
    assert CONFIG_KEY_USER_AGENT == "user_agent"
    
    # Environment variables
    assert ENV_DATA_DIR == "OARC_DATA_DIR"
    assert ENV_LOG_LEVEL == "OARC_LOG_LEVEL"
    assert ENV_MAX_RETRIES == "OARC_MAX_RETRIES"
    assert ENV_TIMEOUT == "OARC_TIMEOUT"
    assert ENV_USER_AGENT == "OARC_USER_AGENT"
    assert ENV_HOME_DIR == "OARC_HOME_DIR"
    
    # Configuration
    assert DEFAULT_CONFIG_FILENAME == "crawlers.ini"
    assert OARC_DIR == ".oarc"
    assert CONFIG_DIR == "config"
    assert CONFIG_SECTION == "oarc-crawlers"
    assert CONFIG_ENV_PREFIX == "OARC_"
    
    # Path-related constants
    assert DATA_SUBDIR == "data"
    assert TEMP_DIR_PREFIX == "oarc-crawlers"
    assert YOUTUBE_DATA_DIR == "youtube_data"
    assert GITHUB_REPOS_DIR == "github_repos"
    assert WEB_CRAWLS_DIR == "crawls"
    assert ARXIV_PAPERS_DIR == "papers"
    assert ARXIV_SOURCES_DIR == "sources"
    assert ARXIV_COMBINED_DIR == "combined"
    assert DDG_SEARCHES_DIR == "searches"
    
    # Default headers
    assert DEFAULT_HEADERS == {"User-Agent": DEFAULT_USER_AGENT}
    
    # URLs
    assert PYPI_PACKAGE_URL == "https://pypi.org/project/{package}/"
    assert PYPI_JSON_URL == "https://pypi.org/pypi/{package}/json"
    assert YOUTUBE_VIDEO_URL_FORMAT == "https://www.youtube.com/watch?v={video_id}"
    assert YOUTUBE_CHANNEL_URL_FORMAT == "https://www.youtube.com/channel/{channel_id}"
    assert YOUTUBE_WATCH_PATTERN == "youtube.com/watch"
    assert YOUTUBE_SHORT_PATTERN == "youtu.be/"
    
    # YouTube format constants
    assert YT_FORMAT_MP4 == "mp4"
    assert YT_FORMAT_WEBM == "webm"
    assert YT_FORMAT_MP3 == "mp3"
    
    # YouTube resolution constants
    assert YT_RESOLUTION_HIGHEST == "highest"
    assert YT_RESOLUTION_LOWEST == "lowest"
    assert YT_RESOLUTION_720P == "720p"
    assert YT_RESOLUTION_1080P == "1080p"
    assert YT_RESOLUTION_480P == "480p"
    assert YT_RESOLUTION_360P == "360p"
    assert YT_RESOLUTION_240P == "240p"
    assert YT_RESOLUTION_144P == "144p"
    
    # DuckDuckGo API constants
    assert DDG_BASE_URL == "https://api.duckduckgo.com/"
    assert DDG_API_PARAMS == "format=json&pretty=1"
    assert DDG_IMAGES_PARAMS == "iax=images&ia=images"
    assert DDG_NEWS_PARAMS == "ia=news"
    assert DDG_TEXT_SEARCH_HEADER == "# DuckDuckGo Search Results"
    assert DDG_IMAGE_SEARCH_HEADER == "# DuckDuckGo Image Search Results"
    assert DDG_NEWS_SEARCH_HEADER == "# DuckDuckGo News Search Results"
    
    # ArXiv API constants
    assert ARXIV_API_BASE_URL == "http://export.arxiv.org/api/query"
    assert ARXIV_SOURCE_URL_FORMAT == "https://arxiv.org/e-print/{arxiv_id}"
    assert ARXIV_ABS_URL_FORMAT == "https://arxiv.org/abs/{arxiv_id}"
    assert ARXIV_PDF_URL_FORMAT == "https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # Dictionary constants
    assert isinstance(CONFIG_KEYS, dict)
    assert CONFIG_KEYS[CONFIG_KEY_DATA_DIR] == ENV_DATA_DIR
    assert isinstance(ARXIV_NAMESPACES, dict)
    assert ARXIV_NAMESPACES['atom'] == 'http://www.w3.org/2005/Atom'
    assert isinstance(GITHUB_BINARY_EXTENSIONS, set)
    assert '.png' in GITHUB_BINARY_EXTENSIONS
    assert isinstance(GITHUB_LANGUAGE_EXTENSIONS, dict)
    assert GITHUB_LANGUAGE_EXTENSIONS['.py'] == 'Python'
