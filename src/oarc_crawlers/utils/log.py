"""
Logging utilities for OARC Crawlers.

This module provides a pre-configured logger and utility functions for logging in the OARC Crawlers project.
The Logger class uses a singleton pattern to ensure logging is initialized only once.
"""
import sys
import logging
import inspect
from typing import Any, Dict, Optional


class ContextAwareLogger:
    """A logger wrapper that automatically determines the calling module."""
    
    def __init__(self, base_logger: logging.Logger):
        """Initialize with a base logger"""
        self._base_logger = base_logger
    
    def _get_caller_module(self) -> str:
        """Determine the calling module name for context-aware logging."""
        # Get the call stack
        stack = inspect.stack()
        # Look for the first frame outside of this module
        for frame in stack[1:]:  # Skip the current frame
            module = inspect.getmodule(frame[0])
            if module and module.__name__ != __name__:
                return module.__name__
        return "unknown"
    
    def debug(self, msg: Any, *args, **kwargs) -> None:
        """Log a debug message with auto-detected module context."""
        caller = self._get_caller_module()
        logger = logging.getLogger(caller)
        logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: Any, *args, **kwargs) -> None:
        """Log an info message with auto-detected module context."""
        caller = self._get_caller_module()
        logger = logging.getLogger(caller)
        logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: Any, *args, **kwargs) -> None:
        """Log a warning message with auto-detected module context."""
        caller = self._get_caller_module()
        logger = logging.getLogger(caller)
        logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: Any, *args, **kwargs) -> None:
        """Log an error message with auto-detected module context."""
        caller = self._get_caller_module()
        logger = logging.getLogger(caller)
        logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: Any, *args, **kwargs) -> None:
        """Log a critical message with auto-detected module context."""
        caller = self._get_caller_module()
        logger = logging.getLogger(caller)
        logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: Any, *args, **kwargs) -> None:
        """Log an exception message with auto-detected module context."""
        caller = self._get_caller_module()
        logger = logging.getLogger(caller)
        logger.exception(msg, *args, **kwargs)


class Logger:
    """Singleton logger manager for the OARC project."""
    
    # Class variable to track initialization state
    _initialized = False
    
    # Storage for logger instances
    _loggers: Dict[str, logging.Logger] = {}
    
    # Shared handler for all loggers
    _handler = None
    
    # Global context-aware logger instance
    _context_logger = None
    
    # Logger name for the main application logger 
    LOGGER_NAME = "oarc-crawlers"
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize logging system if not already initialized."""
        if cls._initialized:
            return
            
        # Set flag first to prevent recursion
        cls._initialized = True
        
        # Get log level from config
        try:
            from oarc_crawlers.config.config import Config
            config = Config()
            log_level_name = config.log_level.upper()
            log_level = getattr(logging, log_level_name, logging.INFO)
        except (ImportError, AttributeError):
            # Fall back to default if config not available
            log_level = logging.INFO
        
        # Configure root logger to output to stderr
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear any existing handlers to avoid duplication
        if root_logger.handlers:
            root_logger.handlers.clear()

        # Add a single handler with proper formatting
        cls._handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        cls._handler.setFormatter(formatter)
        root_logger.addHandler(cls._handler)

        # Create and export the logger to be used by everything in the application
        main_logger = logging.getLogger(cls.LOGGER_NAME)
        main_logger.setLevel(log_level)
        main_logger.propagate = False  # Prevent propagation to avoid duplicate logs

        # Add the same handler to our specific logger
        main_logger.handlers.clear()  # Clear any existing handlers
        main_logger.addHandler(cls._handler)
        
        # Store the main logger
        cls._loggers[cls.LOGGER_NAME] = main_logger
        
        # Create the context-aware logger that will be exported as 'log'
        cls._context_logger = ContextAwareLogger(main_logger)
        
        # Redirect common external loggers
        cls.redirect_external_loggers('TTS', 'whisper', 'gradio', 'uvicorn', 'fastapi')
        
        # Configure all existing loggers to prevent propagation
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            if not logger.handlers and cls._handler:
                logger.addHandler(cls._handler)
            logger.propagate = False
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger with the given name.
        
        Args:
            name (str, optional): The name of the logger. If None, returns the main OARC logger.
            
        Returns:
            logging.Logger: A configured logger instance
        """
        # Ensure logging is initialized
        cls.initialize()
        
        if not name:
            return cls._loggers[cls.LOGGER_NAME]
            
        # Check if we already have this logger
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create a logger with the exact name provided
        new_logger = logging.getLogger(name)
        new_logger.setLevel(logging.INFO)
        new_logger.propagate = False  # Prevent propagation
        
        # Make sure the logger has the handler
        if not new_logger.handlers and cls._handler:
            new_logger.addHandler(cls._handler)
            
        # Store the logger for future use
        cls._loggers[name] = new_logger
        
        return new_logger
    
    @classmethod
    def redirect_external_loggers(cls, *module_names: str, level=logging.WARNING) -> None:
        """
        Redirect logs from external libraries to our central logging system,
        optionally setting them to a less verbose level.
        """
        if not cls._initialized:
            cls.initialize()

        for module_name in module_names:
            if module_name not in cls._loggers:
                ext_logger = logging.getLogger(module_name)
                ext_logger.handlers.clear()
                ext_logger.propagate = False
                if cls._handler:
                    ext_logger.addHandler(cls._handler)
                ext_logger.setLevel(level)
                cls._loggers[module_name] = ext_logger
    
    @classmethod
    def enable_debug_logging(cls, ctx=None, param=None, value=None) -> Any:
        """Enable debug logging level for the oarc-crawlers logger.
        
        This method can be used both directly and as a Click callback for the --verbose option.
        
        Args:
            ctx: The click context (optional, for callback usage)
            param: The parameter being processed (optional, for callback usage)
            value: The parameter value (optional, for callback usage)
            
        Returns:
            The parameter value if used as callback, otherwise None
        """
        # If called as a Click callback and value is False, just return the value
        if ctx is not None and not value:
            return value
            
        # Ensure logging is initialized
        if not cls._initialized:
            cls.initialize()
            
        # Set oarc-crawlers logger to DEBUG level
        oarc_logger = logging.getLogger(cls.LOGGER_NAME)
        oarc_logger.setLevel(logging.DEBUG)
        cls._context_logger.debug("Debug logging enabled")
        
        # If called as a Click callback, return the value
        if ctx is not None:
            return value
        
        return None
    
    @classmethod
    def is_debug_enabled(cls) -> bool:
        """Check if debug logging is enabled."""
        return logging.getLogger(cls.LOGGER_NAME).level == logging.DEBUG


# Initialize the logger singleton
Logger.initialize()

# Export a context-aware log object that automatically determines the calling module
log = Logger._context_logger

# Export the get_logger function for when module-specific loggers are needed
get_logger = Logger.get_logger

# Export the redirect_external_loggers function for additional external loggers
redirect_external_loggers = Logger.redirect_external_loggers

# Export the enable_debug_logging function for CLI verbose mode
enable_debug_logging = Logger.enable_debug_logging

# Initialize and lower verbosity for some noisy modules
Logger.redirect_external_loggers("TTS", "httpx", "gradio", "uvicorn", "fastapi", level=logging.WARNING)
