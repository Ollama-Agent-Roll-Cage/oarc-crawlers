"""
OARC Crawlers CLI

This module defines the main command-line interface for the OARC Crawlers toolkit.
It aggregates all subcommands and provides global options.
"""

import click

from oarc_crawlers.cli.cmd import (
    arxiv, build, ddg, gh, publish, web, youtube, mcp
)
from oarc_crawlers.cli.help_texts import MAIN_HELP
from oarc_crawlers.utils.log import enable_debug_logging

@click.group(help=MAIN_HELP)
@click.version_option(version="0.1.5")
@click.option('--verbose', is_flag=True, help='Enable verbose error output',
              callback=enable_debug_logging)
def cli(verbose):
    """OARC Crawlers CLI."""
    # Set up global verbose flag for error handling
    ctx = click.get_current_context()
    ctx.obj = {'verbose': verbose}

# Add commands
cli.add_command(arxiv)
cli.add_command(build)
cli.add_command(ddg)
cli.add_command(gh)
cli.add_command(publish)
cli.add_command(web)
cli.add_command(youtube)
cli.add_command(mcp)

if __name__ == "__main__":
    cli()
