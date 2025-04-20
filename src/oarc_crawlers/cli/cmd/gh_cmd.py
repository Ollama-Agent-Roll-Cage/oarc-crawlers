"""GitHub CLI command module for OARC Crawlers.

Provides commands to interact with GitHub repositories, including:
    • Cloning repositories
    • Analyzing repository metadata and contents
    • Finding similar code snippets within repositories

Intended for use via the OARC Crawlers command-line interface.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_decorators import (
    asyncio_run, 
    handle_error, 
    DataExtractionError,
)

from oarc_crawlers.cli.help_texts import (
    GH_GROUP_HELP,
    GH_CLONE_HELP,
    GH_ANALYZE_HELP,
    GH_FIND_SIMILAR_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_REPO_URL_HELP,
    ARGS_OUTPUT_PATH_HELP,
    ARGS_CODE_HELP,
    ARGS_LANGUAGE_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.gh_crawler import GHCrawler
from oarc_crawlers.utils.const import SUCCESS


@click.group(help=GH_GROUP_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def gh(verbose, config):
    """
    Group of GitHub-related CLI commands for repository operations.

    This group provides commands to interact with GitHub repositories, including:
      • Cloning repositories
      • Analyzing repository metadata and contents
      • Finding similar code snippets within repositories

    Use --help with subcommands for more details.
    """
    pass


@gh.command(help=GH_CLONE_HELP)
@click.option('--url', required=True, help=ARGS_REPO_URL_HELP)
@click.option('--output-path', help=ARGS_OUTPUT_PATH_HELP)
@asyncio_run
@handle_error
async def clone(url, output_path):
    """Clone a GitHub repository and store it locally.

    Clones the specified GitHub repository and saves it to the given output path.
    If no output path is provided, the repository is stored in the default data directory.

    Args:
        url (str): The GitHub repository URL to clone.
        output_path (str, optional): Directory where the cloned repository will be saved.

    Returns:
        int: SUCCESS constant if the repository is cloned successfully.

    Raises:
        Exception: If cloning fails due to network issues, invalid URL, or permission errors.
    """
    crawler = GHCrawler(data_dir=output_path)
    
    click.echo(f"Cloning repository: {url}")
    log.debug(f"Using output path: {output_path or 'default'}")
    
    try:
        result = await crawler.clone_and_store_repo(url)
        log.debug(f"Clone operation completed successfully")
        click.secho(f"✓ Repository cloned and stored at: {result}", fg='green')
        return SUCCESS
    except Exception as e:
        raise


@gh.command(help=GH_ANALYZE_HELP)
@click.option('--url', required=True, help=ARGS_REPO_URL_HELP)
@asyncio_run
@handle_error
async def analyze(url):
    """Analyze and summarize a GitHub repository.

    Retrieves metadata and analyzes the contents of the specified GitHub repository.
    Provides a summary including primary languages, topics, contributors, and key statistics
    such as stars, forks, and recent activity.

    Args:
        url (str): The GitHub repository URL to analyze.

    Returns:
        int: SUCCESS constant if the analysis completes successfully.

    Raises:
        DataExtractionError: If the repository cannot be analyzed or data extraction fails.
    """
    crawler = GHCrawler()
    
    click.echo(f"Analyzing repository: {url}")
    log.debug(f"Starting analysis on {url}")
    
    result = await crawler.get_repo_summary(url)
    if not result:
        raise DataExtractionError(f"Failed to analyze repository: {url}")
    
    log.debug("Analysis completed successfully")
    click.echo(result)
    return SUCCESS


@gh.command(help=GH_FIND_SIMILAR_HELP)
@click.option('--url', required=True, help=ARGS_REPO_URL_HELP)
@click.option('--code', required=True, help=ARGS_CODE_HELP)
@click.option('--language', help=ARGS_LANGUAGE_HELP)
@asyncio_run
@handle_error
async def find_similar(url, code, language):
    """Search for code snippets in a GitHub repository similar to the provided code.

    This command scans the specified repository for code fragments that closely match
    the given code snippet. Optionally, a programming language can be specified to
    refine the search and improve matching accuracy.

    Args:
        url (str): The GitHub repository URL to search within.
        code (str): The code snippet to compare against repository contents.
        language (str, optional): Programming language of the code snippet for more accurate matching.

    Returns:
        int: SUCCESS constant if similar code is found and displayed.

    Raises:
        DataExtractionError: If no similar code is found or the search fails.
    """
    crawler = GHCrawler()
    
    click.echo(f"Finding similar code in repository: {url}")
    
    if language:
        log.debug(f"Using specified language: {language}")
    
    log.debug(f"Looking for code similar to: {code[:50]}...")
    result = await crawler.find_similar_code(url, code)
    
    if not result:
        raise DataExtractionError(f"Failed to find similar code")
    
    log.debug(f"Found similar code matches")
    click.echo(result)
    return SUCCESS
