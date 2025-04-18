"""GitHub command module for OARC Crawlers.

This module provides CLI commands for interacting with GitHub repositories,
including cloning, analyzing, and finding similar code snippets using the OARC Crawlers framework.
"""
import click

from oarc_crawlers.cli.help_texts import (
    GH_HELP,
    GH_CLONE_HELP,
    GH_ANALYZE_HELP,
    GH_FIND_SIMILAR_HELP,
)
from oarc_crawlers.core.crawlers.gh_crawler import GHCrawler
from oarc_crawlers.decorators import asyncio_run, handle_error
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import DataExtractionError
from oarc_crawlers.utils.log import log, enable_debug_logging


@click.group(help=GH_HELP)
def gh():
    """Group of GitHub-related CLI commands: clone, analyze, and find similar code in repositories."""
    pass

@gh.command(help=GH_CLONE_HELP)
@click.option('--url', required=True, help='GitHub repository URL')
@click.option('--output-path', help='Directory to save the cloned repository')
@click.option('--verbose', is_flag=True, help='Show detailed error information',
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def clone(url, output_path):
    """Clone a GitHub repository and store it locally.

    Args:
        url (str): The GitHub repository URL to clone.
        output_path (str, optional): Directory to save the cloned repository.

    Returns:
        int: SUCCESS constant if the operation completes successfully.
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
        # Just re-raise the exception for the error handler to deal with
        raise


@gh.command(help=GH_ANALYZE_HELP)
@click.option('--url', required=True, help='GitHub repository URL')
@click.option('--verbose', is_flag=True, help='Show detailed error information',
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def analyze(url):
    """Analyze and summarize a GitHub repository.

    This command fetches repository metadata, analyzes its contents,
    and provides a summary including languages, topics, and key statistics.
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
@click.option('--url', required=True, help='GitHub repository URL')
@click.option('--code', required=True, help='Code snippet to find similar code for')
@click.option('--language', help='Programming language of the code snippet')
@click.option('--verbose', is_flag=True, help='Show detailed error information',
              callback=enable_debug_logging)
@asyncio_run
@handle_error
async def find_similar(url, code, language):
    """Find code snippets in a GitHub repository that are similar to the provided code.

    Args:
        url (str): The GitHub repository URL to search within.
        code (str): The code snippet to compare against repository contents.
        language (str, optional): Programming language of the code snippet for more accurate matching.

    Returns:
        int: SUCCESS constant if similar code is found and displayed.
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
