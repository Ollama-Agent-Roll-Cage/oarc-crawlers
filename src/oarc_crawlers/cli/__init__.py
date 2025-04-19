"""
Command-line interface for OARC Crawlers.

This module provides the main command-line interface and subcommands
for OARC Crawlers.
"""

import click

from oarc_crawlers.cli.help_texts import MAIN_HELP, ARGS_VERBOSE_HELP, ARGS_CONFIG_HELP
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.utils.log import enable_debug_logging
from oarc_crawlers.cli.cmd import (
    arxiv,
    build,
    config,
    ddg,
    gh,
    mcp,
    publish,
    web,
    yt,
)

@click.group(help=MAIN_HELP)
@click.version_option()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def cli(verbose, config):
    """OARC Crawlers CLI."""
    pass

# Add commands
cli.add_command(arxiv)
cli.add_command(build)
cli.add_command(config)
cli.add_command(ddg)
cli.add_command(gh)
cli.add_command(mcp)
cli.add_command(publish)
cli.add_command(web)
cli.add_command(yt)

if __name__ == "__main__":
    cli()
