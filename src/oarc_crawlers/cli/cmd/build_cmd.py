"""
Build command module for OARC Crawlers.

This module provides CLI commands for building and managing the OARC Crawlers package,
including cleaning build directories and packaging the project.
"""
import click

from oarc_crawlers.cli.help_texts import BUILD_HELP, BUILD_PACKAGE_HELP
from oarc_crawlers.decorators import handle_error
from oarc_crawlers.utils.build_utils import BuildUtils
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import BuildError
from oarc_crawlers.utils.log import log, enable_debug_logging


@click.group(help=BUILD_HELP)
def build():
    """Group of build-related CLI commands: clean, package, and manage build artifacts."""
    pass


@build.command(help=BUILD_PACKAGE_HELP)
@click.option('--clean/--no-clean', default=False, help='Clean build directories first')
@click.option('--verbose', is_flag=True, help='Show detailed error information',
              callback=enable_debug_logging)
@handle_error
def package(clean):
    """
    Build the OARC Crawlers package.

    This command optionally cleans build directories before packaging,
    then builds the OARC Crawlers distribution package.

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
