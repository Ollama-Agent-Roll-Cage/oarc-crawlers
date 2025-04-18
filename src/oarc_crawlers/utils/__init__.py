"""Utility modules for OARC Crawlers."""

from .const import (
    SUCCESS,
    ERROR,
    DEFAULT_LOG_LEVEL,
    VERBOSE_LOG_LEVEL,
)
from .log import (
    log,
    get_logger,
    enable_debug_logging,
)
from .error_handler import ErrorHandler
from .errors import (
    OarcCrawlerError,
    NetworkError,
    ResourceNotFoundError,
    AuthenticationError,
    DataExtractionError,
    DownloadError,
    BuildError,
    PublishError,
    ConfigurationError,
)
from .build_utils import BuildUtils

__all__ = [
    # Constants
    "SUCCESS",
    "ERROR",
    "DEFAULT_LOG_LEVEL",
    "VERBOSE_LOG_LEVEL",

    # Logging
    "log",
    "get_logger",
    "enable_debug_logging",

    # Error handling
    "ErrorHandler",
    "OarcCrawlerError",
    "NetworkError",
    "ResourceNotFoundError",
    "AuthenticationError",
    "DataExtractionError",
    "DownloadError",
    "BuildError",
    "PublishError",
    "ConfigurationError",

    # Build utilities
    "BuildUtils",
]
