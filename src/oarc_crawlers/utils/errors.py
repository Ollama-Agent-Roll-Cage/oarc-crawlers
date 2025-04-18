"""Custom exceptions for OARC Crawlers."""

class OarcCrawlerError(Exception):
    """Base exception for all OARC Crawler errors."""
    exit_code = 1
    

class NetworkError(OarcCrawlerError):
    """Raised when network operations fail."""
    exit_code = 2
    

class ResourceNotFoundError(OarcCrawlerError):
    """Raised when a requested resource is not found."""
    exit_code = 3
    

class AuthenticationError(OarcCrawlerError):
    """Raised when authentication fails."""
    exit_code = 4
    

class DataExtractionError(OarcCrawlerError):
    """Raised when data extraction fails."""
    exit_code = 5
    

class DownloadError(OarcCrawlerError):
    """Raised when a download operation fails."""
    exit_code = 6
    

class BuildError(OarcCrawlerError):
    """Raised during package build operations."""
    exit_code = 7
    

class PublishError(OarcCrawlerError):
    """Raised during package publishing operations."""
    exit_code = 8
    

class ConfigurationError(OarcCrawlerError):
    """Raised when there's a problem with configuration."""
    exit_code = 9


class MCPError(Exception):
    """Base error for MCP operations."""
    pass


class TransportError(MCPError):
    """Error for transport-related issues."""
    pass
