"""Configuration management commands for OARC Crawlers."""

import click
from pathlib import Path

from oarc_crawlers.cli.help_texts import CONFIG_HELP, ARGS_VERBOSE_HELP
from oarc_crawlers.decorators import handle_error
from oarc_crawlers.config.config_manager import ConfigManager
from oarc_crawlers.config.config_editor import ConfigEditor
from oarc_crawlers.utils.log import enable_debug_logging


@click.command(help=CONFIG_HELP)
@click.argument('config_file', required=False)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@handle_error
def config(config_file, verbose):
    """
    Manage OARC Crawlers configuration interactively.
    
    CONFIG_FILE is an optional path to a specific configuration file.
    If not provided, the default configuration file will be used or created.
    
    This command launches an interactive menu-based interface for:
    • Viewing current configuration settings
    • Editing configuration values
    • Creating new configuration files
    • Resetting to default values
    • Setting environment variables
    
    Args:
        config_file (str, optional): Path to configuration file.
        verbose (bool): Whether to enable verbose output.
    """
    # If a specific file is provided, make sure it exists
    if config_file:
        config_path = Path(config_file).resolve()
        if not config_path.exists():
            if not click.confirm(f"Config file {config_path} doesn't exist. Create it?"):
                return 0
            # Use the ConfigManager class directly - singleton decorator handles instance
            ConfigManager().create_config_file(config_path, force=True)
    
    # Launch the interactive editor
    ConfigEditor().run()
    return 0
