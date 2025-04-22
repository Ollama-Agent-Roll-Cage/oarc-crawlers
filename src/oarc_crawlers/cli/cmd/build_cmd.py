"""Build CLI command module for OARC Crawlers.

Provides commands to build and manage OARC Crawlers packages, including:
    • Cleaning build directories
    • Creating distribution packages

Intended for use via the OARC Crawlers command-line interface.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_utils.decorators import handle_error
from oarc_utils.errors import BuildError

from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_CLEAN_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.utils.build_utils import BuildUtils
from oarc_crawlers.utils.const import SUCCESS


@click.group()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def build(verbose, config):
    """Build operations for package management.

    This group provides commands to build and manage OARC Crawlers packages,
    such as cleaning build directories and creating distribution packages.

    Use --help with subcommands for more details.

    Examples:

      Build the package:

        $ oarc-crawlers build package

      Build the package with cleaning first:

        $ oarc-crawlers build package --clean

      Build with verbose logging:

        $ oarc-crawlers build package --verbose

      Build with custom configuration:

        $ oarc-crawlers build package --config custom_config.ini
    """
    pass


@build.command()
@click.option('--clean/--no-clean', default=False, help=ARGS_CLEAN_HELP)
@handle_error
def package(clean):
    """Build the OARC Crawlers package.

    Creates distributable package files (both source distribution and wheel)
    for the OARC Crawlers project. The package will be built according to the
    specifications in pyproject.toml.

    Args:
        clean (bool): If True, clean build directories before building.

    Returns:
        int: SUCCESS constant if the build completes successfully.

    Raises:
        BuildError: If cleaning or building fails.
    """
    if clean:
        click.echo("Cleaning build directories...")
        log.debug("Running clean operation before build")
        result = BuildUtils.clean_build_directories()
        if not result:
            raise BuildError("Failed to clean build directories")
    
    click.echo("Building package...")
    log.debug("Starting package build process")
    
    result = BuildUtils.build_package()
    if result:
        log.debug("Build completed successfully")
        click.secho("✓ Package built successfully!", fg='green')
        return SUCCESS
    else:
        raise BuildError("Build failed")
