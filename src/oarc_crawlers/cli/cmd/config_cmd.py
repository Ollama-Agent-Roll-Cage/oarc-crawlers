"""Configuration CLI command module for OARC Crawlers.

Offers commands to view, edit, and manage configuration settings for OARC Crawlers.
Supports interactive editing and custom configuration file selection via the command line.
"""

import click

from oarc_log import enable_debug_logging
from oarc_utils.decorators import handle_error

from oarc_crawlers.config.config_manager import ConfigManager
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
)

@click.command()
@click.argument('config_file', required=False)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@handle_error
def config(config_file, verbose):
    """Manage configuration settings for OARC Crawlers.

    Launches an interactive configuration editor for OARC Crawlers.
    If a config_file path is provided, that file will be edited; otherwise,
    the default configuration file is used.

    Examples:

      Launch the configuration editor:

        $ oarc-crawlers config

      Edit a specific configuration:

        $ oarc-crawlers config ~/.oarc/custom_config.ini

      Enable verbose logging:

        $ oarc-crawlers config --verbose

    Args:
        config_file (str, optional): Path to the configuration file to edit.
        verbose (bool): Enables verbose output and debug logging.
    """
    ConfigManager.run_config_editor(config_file)
    
    return SUCCESS
