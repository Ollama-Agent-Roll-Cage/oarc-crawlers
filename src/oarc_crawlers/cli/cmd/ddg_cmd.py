"""DuckDuckGo command module for OARC Crawlers.

This module provides CLI commands for performing DuckDuckGo searches,
including text, image, and news queries using the OARC Crawlers framework.
"""
import click

from oarc_crawlers.cli.help_texts import (
    DDG_HELP,
    DDG_TEXT_HELP,
    DDG_IMAGES_HELP,
    DDG_NEWS_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_QUERY_HELP,
    ARGS_MAX_RESULTS_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.ddg_crawler import DDGCrawler
from oarc_crawlers.decorators import asyncio_run, handle_error
from oarc_crawlers.utils.const import SUCCESS
from oarc_crawlers.utils.errors import NetworkError
from oarc_crawlers.utils.log import log, enable_debug_logging
from oarc_crawlers.utils.paths import Paths

@click.group(help=DDG_HELP)
def ddg():
    """Group of DuckDuckGo-related CLI commands: text, image, and news search."""
    pass

@ddg.command(help=DDG_TEXT_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--max-results', default=5, type=int, help=ARGS_MAX_RESULTS_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def text(query, max_results, verbose, config):
    """Perform a DuckDuckGo text search.

    Args:
        query (str): The search query string.
        max_results (int): Maximum number of results to return.
        verbose (bool): Whether to enable verbose output.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS constant if the search completes successfully.
    """
    searcher = DDGCrawler()
    
    click.echo(f"Searching DuckDuckGo for: {query}")
    log.debug(f"Using max_results: {max_results}")
    
    result = await searcher.text_search(query, max_results=max_results)
    
    if 'error' in result:
        raise NetworkError(f"Search failed: {result['error']}")
    
    log.debug(f"Got {len(result.get('results', []))} search results")
    click.echo(result)
    return SUCCESS

@ddg.command(help=DDG_IMAGES_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--max-results', default=10, type=int, help=ARGS_MAX_RESULTS_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def images(query, max_results, verbose, config):
    """Perform a DuckDuckGo image search.

    Args:
        query (str): The search query string.
        max_results (int): Maximum number of image results to return.
        verbose (bool): Whether to enable verbose output.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS constant if the image search completes successfully.
    """
    searcher = DDGCrawler()
    
    click.echo(f"Searching DuckDuckGo images for: {query}")
    log.debug(f"Using max_results: {max_results}")
    
    result = await searcher.image_search(query, max_results=max_results)
    
    if 'error' in result:
        raise NetworkError(f"Image search failed: {result['error']}")
    
    log.debug(f"Got {len(result.get('results', []))} image results")
    click.echo(result)
    return SUCCESS

@ddg.command(help=DDG_NEWS_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--max-results', default=20, type=int, help=ARGS_MAX_RESULTS_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
async def news(query, max_results, verbose, config):
    """Perform a DuckDuckGo news search.

    Args:
        query (str): The search query string.
        max_results (int): Maximum number of news results to return.
        verbose (bool): Whether to enable verbose output.
        config (str, optional): Path to configuration file.

    Returns:
        int: SUCCESS constant if the news search completes successfully.
    """
    searcher = DDGCrawler()
    
    click.echo(f"Searching DuckDuckGo news for: {query}")
    log.debug(f"Using max_results: {max_results}")
    
    result = await searcher.news_search(query, max_results=max_results)
    
    if 'error' in result:
        raise NetworkError(f"News search failed: {result['error']}")
    
    log.debug(f"Got {len(result.get('results', []))} news results")
    click.echo(result)
    return SUCCESS
