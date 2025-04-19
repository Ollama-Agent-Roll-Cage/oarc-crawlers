"""Constants for OARC Crawlers."""

# Default log levels
DEFAULT_LOG_LEVEL = "INFO"
VERBOSE_LOG_LEVEL = "DEBUG"

# Status constants
SUCCESS = 0
FAILURE = 1
ERROR = "error"
VERSION = "0.1.5"

# Default values for configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
DEFAULT_USER_AGENT = f"OARC-Crawlers/{VERSION}"

# Configuration key names
CONFIG_KEY_DATA_DIR = "data_dir"
CONFIG_KEY_LOG_LEVEL = "log_level"
CONFIG_KEY_MAX_RETRIES = "max_retries"
CONFIG_KEY_TIMEOUT = "timeout"
CONFIG_KEY_USER_AGENT = "user_agent"

# Environment variable names
ENV_DATA_DIR = "OARC_DATA_DIR"
ENV_LOG_LEVEL = "OARC_LOG_LEVEL"
ENV_MAX_RETRIES = "OARC_MAX_RETRIES"
ENV_TIMEOUT = "OARC_TIMEOUT"
ENV_USER_AGENT = "OARC_USER_AGENT"
ENV_HOME_DIR = "OARC_HOME_DIR"

# Configuration
DEFAULT_CONFIG_FILENAME = "crawlers.ini"
OARC_DIR = ".oarc"
CONFIG_DIR = "config"
CONFIG_SECTION = "oarc-crawlers"
CONFIG_ENV_PREFIX = "OARC_"

# Config keys that match both env vars and config file keys
CONFIG_KEYS = {
    CONFIG_KEY_DATA_DIR: ENV_DATA_DIR,
    CONFIG_KEY_LOG_LEVEL: ENV_LOG_LEVEL,
    CONFIG_KEY_MAX_RETRIES: ENV_MAX_RETRIES,
    CONFIG_KEY_TIMEOUT: ENV_TIMEOUT, 
    CONFIG_KEY_USER_AGENT: ENV_USER_AGENT,
}

# Path-related constants
DATA_SUBDIR = "data"
TEMP_DIR_PREFIX = "oarc-crawlers"
YOUTUBE_DATA_DIR = "youtube_data"
GITHUB_REPOS_DIR = "github_repos"
WEB_CRAWLS_DIR = "crawls"
ARXIV_PAPERS_DIR = "papers"
ARXIV_SOURCES_DIR = "sources"
ARXIV_COMBINED_DIR = "combined"
DDG_SEARCHES_DIR = "searches"

# Default headers for web requests
DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT
}

# URLs
PYPI_PACKAGE_URL = "https://pypi.org/project/{package}/"
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
