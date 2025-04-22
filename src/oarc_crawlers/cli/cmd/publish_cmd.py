"""Publish command module for OARC Crawlers.

Provides CLI commands to build and publish OARC Crawlers packages to PyPI or TestPyPI.
Supports optional build steps, flexible credential management, and .pypirc configuration.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_utils.decorators import asyncio_run, handle_error
from oarc_utils.errors import BuildError, PublishError

from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.utils.build_utils import BuildUtils
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_TEST_HELP,
    ARGS_BUILD_HELP,
    ARGS_PYPI_USERNAME_HELP,
    ARGS_PYPI_PASSWORD_HELP,
    ARGS_PYPI_CONFIG_FILE_HELP,
)

@click.group()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def publish(verbose, config):
    """Group of commands for building and publishing OARC Crawlers packages.

    This group provides commands to streamline the build and release process, 
    including support for credential management, .pypirc configuration, and 
    publishing to both official and test repositories.

    Examples:

      Publish to PyPI:

        $ oarc-crawlers publish pypi

      Publish to TestPyPI:

        $ oarc-crawlers publish pypi --test

      Publish without rebuilding:

        $ oarc-crawlers publish pypi --no-build
    """
    pass


@publish.command()
@click.option('--test', is_flag=True, help=ARGS_TEST_HELP)
@click.option('--build/--no-build', default=True, help=ARGS_BUILD_HELP)
@click.option('--username', help=ARGS_PYPI_USERNAME_HELP)
@click.option('--password', help=ARGS_PYPI_PASSWORD_HELP)
@click.option('--config-file', help=ARGS_PYPI_CONFIG_FILE_HELP)
@asyncio_run
@handle_error
async def pypi(test, build, username, password, config_file):
    """Publish the OARC Crawlers package to PyPI or TestPyPI.

    Optionally builds the package before uploading to the selected repository.
    Supports flexible credential management via command-line options or a .pypirc config file.

    Examples:

      Publish to PyPI with default settings:

        $ oarc-crawlers publish pypi

      Publish to TestPyPI:

        $ oarc-crawlers publish pypi --test

      Publish with explicit credentials:

        $ oarc-crawlers publish pypi --username myuser --password mypass

      Publish using custom .pypirc:

        $ oarc-crawlers publish pypi --config-file ~/.custom-pypirc

      Publish without rebuilding:

        $ oarc-crawlers publish pypi --no-build

    Args:
        test (bool): If True, publish to TestPyPI; otherwise, publish to PyPI.
        build (bool): If True, build the package before publishing.
        username (str, optional): PyPI username (overrides config if provided).
        password (str, optional): PyPI password (overrides config if provided).
        config_file (str, optional): Path to a .pypirc configuration file.

    Returns:
        int: SUCCESS if publishing is successful.

    Raises:
        BuildError: If the build process fails.
        PublishError: If publishing to the repository fails.
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
