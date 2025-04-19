"""Publish command module for OARC Crawlers.

This module provides CLI commands for publishing OARC Crawlers packages
to PyPI or TestPyPI, including optional build steps and credential handling.
"""
import click

from oarc_crawlers.cli.help_texts import (
    PUBLISH_HELP,
    PUBLISH_PYPI_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_TEST_HELP,
    ARGS_BUILD_HELP,
    ARGS_PYPI_USERNAME_HELP,
    ARGS_PYPI_PASSWORD_HELP,
    ARGS_PYPI_CONFIG_FILE_HELP,
)
from oarc_crawlers.config.config import apply_config_file
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
@click.option('--test', is_flag=True, help=ARGS_TEST_HELP)
@click.option('--build/--no-build', default=True, help=ARGS_BUILD_HELP)
@click.option('--username', help=ARGS_PYPI_USERNAME_HELP)
@click.option('--password', help=ARGS_PYPI_PASSWORD_HELP)
@click.option('--config-file', help=ARGS_PYPI_CONFIG_FILE_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP,
              callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def pypi(test, build, username, password, config_file, verbose, config):
    """
    Publish the OARC Crawlers package to PyPI or TestPyPI.

    This command optionally builds the package before uploading it to the specified
    repository. Credentials can be provided via command-line options or a .pypirc config file.

    Args:
        test (bool): If True, upload to TestPyPI instead of PyPI.
        build (bool): If True, build the package before publishing.
        username (str): PyPI username (optional, overrides keyring/config).
        password (str): PyPI password (optional, overrides keyring/config).
        config-file (str): Path to .pypirc config file (optional).
        verbose (bool): If True, enable verbose logging.
        config (str): Path to additional configuration file.

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
