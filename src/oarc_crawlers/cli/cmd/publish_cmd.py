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
    PUBLISH_GROUP_HELP,
    PUBLISH_PYPI_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_TEST_HELP,
    ARGS_BUILD_HELP,
    ARGS_PYPI_USERNAME_HELP,
    ARGS_PYPI_PASSWORD_HELP,
    ARGS_PYPI_CONFIG_FILE_HELP,
)

@click.group(help=PUBLISH_GROUP_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def publish(verbose, config):
    """CLI group for building and publishing OARC Crawlers packages to PyPI or TestPyPI.

    This group provides commands to streamline the build and release process, 
    including support for credential management, .pypirc configuration, and 
    publishing to both official and test repositories.
    """
    pass


@publish.command(help=PUBLISH_PYPI_HELP)
@click.option('--test', is_flag=True, help=ARGS_TEST_HELP)
@click.option('--build/--no-build', default=True, help=ARGS_BUILD_HELP)
@click.option('--username', help=ARGS_PYPI_USERNAME_HELP)
@click.option('--password', help=ARGS_PYPI_PASSWORD_HELP)
@click.option('--config-file', help=ARGS_PYPI_CONFIG_FILE_HELP)
@asyncio_run
@handle_error
async def pypi(test, build, username, password, config_file):
    """
    Publish the OARC Crawlers package to PyPI or TestPyPI.

    Optionally builds the package before uploading to the selected repository.
    Supports flexible credential management via command-line options or a .pypirc config file.

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
