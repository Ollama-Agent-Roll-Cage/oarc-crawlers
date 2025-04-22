"""
Configuration management for OARC Crawlers.

This module provides a centralized configuration system that handles defaults,
environment variable overrides, and runtime configuration for the OARC Crawlers
package.
"""

import os
import configparser
import pathlib
from typing import Any, Dict, Optional

from oarc_log import log
from oarc_utils.decorators import singleton

from oarc_crawlers.utils.paths import Paths
from oarc_crawlers.utils.const import (
    CONFIG_SECTION,
    CONFIG_KEY_DATA_DIR,
    CONFIG_KEY_LOG_LEVEL,
    CONFIG_KEY_MAX_RETRIES,
    CONFIG_KEY_TIMEOUT,
    CONFIG_KEY_USER_AGENT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    ENV_DATA_DIR,
    ENV_LOG_LEVEL,
    ENV_MAX_RETRIES,
    ENV_TIMEOUT,
    ENV_USER_AGENT,
)

@singleton
class Config:
    """
    Singleton configuration manager for OARC Crawlers.

    This class centralizes all configuration logic, providing:
      - Default values for all supported settings
      - Automatic overrides from environment variables
      - Optional overrides from configuration files (INI format)
      - Runtime access and mutation of configuration values
      - Ensured type safety and path resolution for key settings

    Examples:
      Get configuration value:
        $ config = Config()
        $ data_dir = config.data_dir
      
      Set configuration value:
        $ Config.set(CONFIG_KEY_TIMEOUT, 60)
    """

    # Default configuration values
    DEFAULTS = {
        CONFIG_KEY_DATA_DIR: str(Paths.get_default_data_dir()),
        CONFIG_KEY_LOG_LEVEL: DEFAULT_LOG_LEVEL,
        CONFIG_KEY_MAX_RETRIES: DEFAULT_MAX_RETRIES,
        CONFIG_KEY_TIMEOUT: DEFAULT_TIMEOUT,
        CONFIG_KEY_USER_AGENT: DEFAULT_USER_AGENT,
    }

    # Environment variable mappings (ENV_VAR_NAME: config_key)
    ENV_VARS = {
        ENV_DATA_DIR: CONFIG_KEY_DATA_DIR,
        ENV_LOG_LEVEL: CONFIG_KEY_LOG_LEVEL,
        ENV_MAX_RETRIES: CONFIG_KEY_MAX_RETRIES, 
        ENV_TIMEOUT: CONFIG_KEY_TIMEOUT,
        ENV_USER_AGENT: CONFIG_KEY_USER_AGENT,
    }
    
    # Storage for config values
    _config: Dict[str, Any] = {}
    

    def __init__(self):
        """Initialize configuration if not already done."""
        # Let the singleton decorator handle instance management
        # Initialize only if this is a fresh instance (first time)
        if not hasattr(self, '_init_done'):
            self.initialize()
            self._init_done = True
    
    
    @classmethod
    def initialize(cls) -> None:
        """
        Initialize configuration with defaults, environment overrides, and config file.

        This method sets up the configuration in the following order:
            1. Loads default values.
            2. Applies environment variable overrides if present.
            3. Loads and applies configuration from a config file if found.
            4. Ensures the data directory is a resolved Path object.
        """
        # Start with defaults
        cls._config = {}
        cls._config.update(cls.DEFAULTS)

        # Override with environment variables if they exist
        for env_var, config_key in cls.ENV_VARS.items():
            if env_var in os.environ:
                cls._config[config_key] = cls._parse_value(os.environ[env_var], cls.DEFAULTS[config_key])

        # Load from config file if it exists
        cls._load_from_config_file()

        # Ensure data_dir is a Path object
        cls._config[CONFIG_KEY_DATA_DIR] = pathlib.Path(cls._config[CONFIG_KEY_DATA_DIR]).resolve()

        log.debug(f"Initialized Config with: {cls._config}")


    @classmethod
    def _parse_value(cls, value: str, default: Any) -> Any:
        """
        Parse a string value into the appropriate type based on the default.
        
        Args:
            value: The string value to parse
            default: The default value to determine the type
            
        Returns:
            The parsed value with the appropriate type
        """
        if isinstance(default, bool):
            return value.lower() in ("yes", "true", "t", "1", "y")
        elif isinstance(default, int):
            try:
                return int(value)
            except (ValueError, TypeError):
                log.warning(f"Could not parse '{value}' as int, using default {default}")
                return default
        elif isinstance(default, float):
            try:
                return float(value)
            except (ValueError, TypeError):
                log.warning(f"Could not parse '{value}' as float, using default {default}")
                return default
        return value

    @classmethod
    def _load_from_config_file(cls, config_file: Optional[str] = None) -> None:
        """
        Load configuration settings from an INI file.

        If a specific config_file path is provided and exists, load configuration from that file.
        Otherwise, search standard locations (as defined by Paths.get_default_config_locations())
        and load the first config file found.

        Args:
            config_file: Optional path to a config file. If not provided,
                 searches in default locations.
        """
        parser = configparser.ConfigParser()

        # If specific file provided, try to load it
        if config_file and pathlib.Path(config_file).exists():
            parser.read(config_file)
            if CONFIG_SECTION in parser:
                log.debug(f"Loading config from specified file: {config_file}")
                cls._update_from_config_section(parser[CONFIG_SECTION])
                return

        # Otherwise, search standard locations
        for path in Paths.get_default_config_locations():
            if path.exists():
                parser.read(path)
                if CONFIG_SECTION in parser:
                    log.debug(f"Loading config from default location: {path}")
                    cls._update_from_config_section(parser[CONFIG_SECTION])
                    break

    @classmethod
    def _update_from_config_section(cls, section):
        """
        Update configuration from a configparser section.

        Updates the class configuration dictionary from a given configparser section.
        Iterates over all default configuration keys, and if a key is present in the provided
        section, parses its value and updates the internal configuration. Ensures that the
        value for the data directory key is always stored as a resolved pathlib.Path object.
        
        Args:
            section (configparser.SectionProxy or dict): The configuration section containing key-value pairs to update.
            
        Side Effects:
            Modifies the class-level _config dictionary with updated values from the section.
        """
        for key in cls.DEFAULTS.keys():
            if key in section:
                value_str = section[key]
                cls._config[key] = cls._parse_value(value_str, cls.DEFAULTS[key])

        # Make sure data_dir is a Path object
        if CONFIG_KEY_DATA_DIR in cls._config and isinstance(cls._config[CONFIG_KEY_DATA_DIR], str):
            cls._config[CONFIG_KEY_DATA_DIR] = pathlib.Path(cls._config[CONFIG_KEY_DATA_DIR]).resolve()

    @classmethod
    def load_from_file(cls, config_file: str) -> None:
        """
        Load configuration from a specific file.
        
        Args:
            config_file: Path to the config file to load.
        """
        log.debug(f"Explicitly loading config from: {config_file}")
        cls._load_from_config_file(config_file)

    @classmethod
    def apply_config_file(cls, ctx=None, param=None, value=None) -> Any:
        """
        Load configuration from a file if specified.
        
        This method can be used both directly and as a Click callback for the --config option.
        
        Args:
            ctx: The click context (optional, for callback usage)
            param: The parameter being processed (optional, for callback usage)
            value: The parameter value (path to config file or None)
                
        Returns:
            The parameter value if used as callback, otherwise None
        """
        # If no value provided, just return (for use as Click callback)
        if value is None:
            return value
            
        # Ensure configuration is initialized
        if not hasattr(cls, '_config'):
            cls.initialize()
            
        # Load the specified config file
        cls.load_from_file(value)
        log.debug(f"Applied configuration from file: {value}")
        
        # If called as a Click callback, return the value
        if ctx is not None:
            return value
            
        return None

    @property
    def data_dir(self) -> pathlib.Path:
        """Get the configured data directory."""
        return self._config[CONFIG_KEY_DATA_DIR]

    @classmethod
    def ensure_data_dir(cls) -> pathlib.Path:
        """
        Ensure the data directory exists and return it.
        
        Returns:
            pathlib.Path: The ensured data directory
        """
        return Paths.ensure_path(cls._config[CONFIG_KEY_DATA_DIR])

    @property
    def log_level(self) -> str:
        """Get the configured log level."""
        return self._config[CONFIG_KEY_LOG_LEVEL]

    @property
    def max_retries(self) -> int:
        """Get the configured max retries for network operations."""
        return self._config[CONFIG_KEY_MAX_RETRIES]

    @property
    def timeout(self) -> int:
        """Get the configured timeout for network operations."""
        return self._config[CONFIG_KEY_TIMEOUT]

    @property
    def user_agent(self) -> str:
        """Get the configured user agent string."""
        return self._config[CONFIG_KEY_USER_AGENT]

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value, or default if not found
        """
        return cls._config.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        cls._config[key] = value
        log.debug(f"Set config {key}={value}")
        
        # Handle special case for data_dir
        if key == CONFIG_KEY_DATA_DIR:
            cls._config[CONFIG_KEY_DATA_DIR] = pathlib.Path(value).resolve()


# Export commonly used functions
apply_config_file = Config.apply_config_file
load_from_file = Config.load_from_file
