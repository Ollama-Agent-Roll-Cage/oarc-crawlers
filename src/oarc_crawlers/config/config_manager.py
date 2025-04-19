"""
Configuration manager for OARC Crawlers.

This module provides functions for managing configuration settings,
including listing, creating, reading, and interactively editing configuration files.
"""

import os
import platform
import shutil
import subprocess
import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import click
from click import echo, style

from oarc_crawlers.config.config import Config
from oarc_crawlers.decorators.singleton import singleton
from oarc_crawlers.utils.const import (
    CONFIG_KEY_DATA_DIR,
    CONFIG_KEY_LOG_LEVEL,
    CONFIG_KEY_MAX_RETRIES,
    CONFIG_KEY_TIMEOUT,
    CONFIG_KEY_USER_AGENT,
    CONFIG_SECTION
)
from oarc_crawlers.utils.paths import Paths


@singleton
class ConfigManager:
    """Manager for OARC Crawlers configuration."""
    

    @classmethod
    def get_config_details(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get configuration details including descriptions, types, and allowed values.
        
        Returns:
            Dictionary with configuration metadata
        """
        return {
            CONFIG_KEY_DATA_DIR: {
                "description": "Directory where data is stored",
                "type": "path",
                "help": "Enter a valid directory path"
            },
            CONFIG_KEY_LOG_LEVEL: {
                "description": "Logging verbosity level",
                "type": "select",
                "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "help": "Select a log level (DEBUG shows the most messages)"
            },
            CONFIG_KEY_MAX_RETRIES: {
                "description": "Maximum number of retry attempts for network operations",
                "type": "int",
                "range": (1, 10),
                "help": "Enter a number between 1 and 10"
            },
            CONFIG_KEY_TIMEOUT: {
                "description": "Timeout in seconds for network operations",
                "type": "int",
                "range": (5, 120),
                "help": "Enter a number between 5 and 120 seconds"
            },
            CONFIG_KEY_USER_AGENT: {
                "description": "User agent string for network requests",
                "type": "string",
                "help": "Enter a user agent string (default: OARC-Crawlers/VERSION)"
            }
        }


    @classmethod
    def find_config_file(cls) -> Optional[Path]:
        """
        Find the configuration file in standard locations.
        
        Returns:
            Path to the config file if found, None otherwise
        """
        return Paths.find_config_file()


    @classmethod
    def get_current_config(cls) -> Dict[str, Any]:
        """
        Get current configuration values.
        
        Returns:
            Dictionary with configuration key-value pairs
        """
        config = Config()
        result = {}
        for key in config.DEFAULTS.keys():
            value = config.get(key)
            # Convert Path objects to strings for display
            if hasattr(value, "__str__"):
                value = str(value)
            result[key] = value
        return result


    @classmethod
    def get_config_source(cls) -> Dict[str, str]:
        """
        Determine the source for each configuration value.
        
        Returns:
            Dictionary mapping config keys to their sources (default, env var, config file)
        """
        result = {}
        config = Config()
        current_config = cls.get_current_config()
        
        # Check each config key
        for key in config.DEFAULTS.keys():
            # Default assumption
            source = "default"
            
            # Check if it came from environment variable
            env_var = next((env for env, k in config.ENV_VARS.items() if k == key), None)
            if env_var and env_var in os.environ:
                source = f"environment variable ({env_var})"
            # Check if it came from config file
            elif cls.find_config_file():
                parser = configparser.ConfigParser()
                parser.read(cls.find_config_file())
                if CONFIG_SECTION in parser and key in parser[CONFIG_SECTION]:
                    source = f"config file ({cls.find_config_file()})"
            
            result[key] = source
        
        return result


    @classmethod
    def create_config_file(cls, config_path: Path, force: bool = False) -> bool:
        """
        Create a new configuration file with current settings.
        
        Args:
            config_path: Path where the config file should be created
            force: Whether to overwrite if the file already exists
            
        Returns:
            True if the file was created, False otherwise
        """
        # Check if file exists and if we should overwrite
        if config_path.exists() and not force:
            return False
            
        # Create config parser and add current settings
        parser = configparser.ConfigParser()
        current_config = Config()
        
        parser[CONFIG_SECTION] = {}
        for key in current_config.DEFAULTS.keys():
            value = current_config.get(key)
            # Handle special cases like Path objects
            if hasattr(value, "__str__"):
                parser[CONFIG_SECTION][key] = str(value)
        
        # Ensure the parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the config file
        with open(config_path, 'w') as f:
            parser.write(f)
        
        return True


    @classmethod
    def display_config_info(cls) -> None:
        """
        Display information about the current configuration.
        
        Shows the config file location (if any) and all current settings with their sources.
        """
        config_file = cls.find_config_file()
        if config_file:
            echo(style(f"Found config file: {config_file}", fg='green'))
        else:
            echo(style("No config file found, using defaults and environment variables", fg='yellow'))
        
        echo("\nCurrent configuration:")
        echo(style("─" * 50, fg='blue'))
        
        current_config = cls.get_current_config()
        sources = cls.get_config_source()
        config_details = cls.get_config_details()
        
        # Display config settings with sources and descriptions
        for key, value in current_config.items():
            source = sources.get(key, "unknown")
            description = config_details.get(key, {}).get("description", "")
            
            echo(f"{style(key, fg='green', bold=True)}: {value}")
            echo(f"  {style('Source:', fg='blue')} {source}")
            if description:
                echo(f"  {style('Description:', fg='blue')} {description}")
            echo("")


    @staticmethod
    def set_env_var_forever(key: str, value: str) -> Tuple[bool, str]:
        """
        Set an environment variable permanently using OS-specific methods.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            Tuple of (success, message)
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                # On Windows, use the 'setx' command
                result = subprocess.run(['setx', key, value], 
                                       capture_output=True, 
                                       text=True)
                if result.returncode == 0:
                    return True, f"Set {key}={value} in Windows environment variables"
                else:
                    return False, f"Failed to set {key}: {result.stderr}"
            
            elif system in ("Linux", "Darwin"):  # Linux or macOS
                # Determine which shell config file to use
                shell = os.environ.get('SHELL', '')
                home = str(Path.home())
                
                if 'zsh' in shell:
                    config_file = f"{home}/.zshrc"
                elif 'bash' in shell:
                    # Check for .bash_profile first on macOS
                    if system == "Darwin" and os.path.exists(f"{home}/.bash_profile"):
                        config_file = f"{home}/.bash_profile"
                    else:
                        config_file = f"{home}/.bashrc"
                else:
                    # Default to .profile for other shells
                    config_file = f"{home}/.profile"
                
                # Create backup of the file
                if os.path.exists(config_file):
                    backup_file = f"{config_file}.bak"
                    shutil.copy2(config_file, backup_file)
                
                # Check if variable already exists in the file
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()
                        
                    # Look for existing variable export
                    var_pattern = f"export {key}="
                    if var_pattern in content:
                        # Variable already exists, update it
                        lines = content.splitlines()
                        updated = False
                        with open(config_file, 'w') as f:
                            for line in lines:
                                if var_pattern in line:
                                    f.write(f'export {key}="{value}"\n')
                                    updated = True
                                else:
                                    f.write(f"{line}\n")
                        
                        if updated:
                            return True, f"Updated {key}={value} in {config_file}"
                    
                # Append variable if it doesn't exist
                with open(config_file, 'a') as f:
                    f.write(f'\n# Added by OARC Crawlers config manager\n')
                    f.write(f'export {key}="{value}"\n')
                    
                return True, f"Added {key}={value} to {config_file}"
                
            else:
                return False, f"Unsupported OS: {system}"
                
        except Exception as e:
            return False, f"Error setting environment variable: {str(e)}"


    @classmethod
    def update_env_vars(cls, config_values: Dict[str, Any]) -> None:
        """
        Ask the user if they want to set environment variables permanently
        and perform the updates if requested.
        
        Args:
            config_values: Dictionary of configuration values
        """
        env_vars_to_update = {}
        
        echo("\n" + style("Would you like to set environment variables permanently?", fg='cyan', bold=True))
        echo(style("This will modify your system environment or shell configuration file.", fg='yellow'))
        echo("The following environment variables will be set:")
        
        # Find corresponding env vars for each config key
        for config_key, value in config_values.items():
            for env_var, config_k in Config.ENV_VARS.items():
                if config_k == config_key:
                    env_vars_to_update[env_var] = str(value)
                    echo(f"  {style(env_var, fg='green')}: {value}")

        if not env_vars_to_update:
            echo(style("No environment variables to update.", fg='yellow'))
            return

        if click.confirm(style("\nProceed with environment variable update?", fg='cyan')):
            successful = []
            failed = []
            
            # Set each environment variable
            for env_var, value in env_vars_to_update.items():
                success, message = cls.set_env_var_forever(env_var, value)
                if success:
                    successful.append(env_var)
                    echo(style(f"✓ {message}", fg='green'))
                else:
                    failed.append(env_var)
                    echo(style(f"✗ {message}", fg='red'))
            
            if successful:
                echo(style(f"\nSuccessfully updated {len(successful)} environment variables.", fg='green'))
                echo("You may need to restart your terminal or log out and back in for changes to take effect.")
            
            if failed:
                echo(style(f"\nFailed to update {len(failed)} environment variables.", fg='red'))
                echo("You can manually set these variables in your environment configuration.")
        else:
            echo(style("\nEnvironment variable update skipped.", fg='yellow'))


    @classmethod
    def interactive_edit_config(cls) -> None:
        """
        Launch an interactive UI to edit configuration settings using PyInquirer.
        """
        from oarc_crawlers.config.config_editor import ConfigEditor
        ConfigEditor.run()
