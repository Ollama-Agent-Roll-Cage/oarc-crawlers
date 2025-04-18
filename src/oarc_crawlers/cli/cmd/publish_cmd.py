"""Publish command module for OARC Crawlers.

This module provides CLI commands for publishing OARC Crawlers packages
to PyPI or TestPyPI, including optional build steps and credential handling.
"""
import click

from oarc_crawlers.cli.help_texts import PUBLISH_HELP, PUBLISH_PYPI_HELP
from oarc_crawlers.decorators import asyncio_run, handle_error
from oarc_crawlers.utils.build_utils import BuildUtils
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import BuildError, PublishError
from oarc_crawlers.utils.log import log, enable_debug_logging

@click.group(help=PUBLISH_HELP)
def publish():
    """Group of commands for publishing OARC Crawlers packages to PyPI or TestPyPI."""
    pass

@publish.command(help=PUBLISH_PYPI_HELP)
@click.option('--test', is_flag=True, help='Upload to TestPyPI instead of PyPI')
@click.option('--build/--no-build', default=True, help='Build the package before publishing')
@click.option('--username', help='PyPI username (if not using keyring)')
@click.option('--password', help='PyPI password (if not using keyring)')
@click.option('--config-file', help='Path to PyPI config file (.pypirc)')
@click.option('--verbose', is_flag=True, help='Show detailed error information',
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def pypi(test, build, username, password, config_file):
    """
    Publish the OARC Crawlers package to PyPI or TestPyPI.

    This command optionally builds the package before uploading it to the specified
    repository. Credentials can be provided via command-line options or a .pypirc config file.

    Args:
        test (bool): If True, upload to TestPyPI instead of PyPI.
        build (bool): If True, build the package before publishing.
        username (str): PyPI username (optional, overrides keyring/config).
        password (str): PyPI password (optional, overrides keyring/config).
        config_file (str): Path to .pypirc config file (optional).

    Returns:
        int: SUCCESS constant if publishing completes successfully.

    Raises:
        BuildError: If the build step fails.
        PublishError: If publishing fails.
    """
    if build:
        click.echo("Building package first...")
        log.debug("Running build step before publishing")
        result = BuildUtils.build_package()
        if not result:
            raise BuildError("Build failed, aborting publish")
    
    target = 'TestPyPI' if test else 'PyPI'
    click.echo(f"Publishing to {target}...")
    
    log.debug(f"Publishing with credentials: username={username is not None}, " +
             f"password={password is not None}, config_file={config_file}")
    
    result = await BuildUtils.publish_package(
        test=test, 
        username=username, 
        password=password,
        config_file=config_file
    )
    
    if result["success"]:
        click.secho(f"✓ {result['message']}", fg='green')
        log.debug("Publication completed successfully")
        return SUCCESS
    else:
        raise PublishError(f"Publishing failed: {result['message']}")
