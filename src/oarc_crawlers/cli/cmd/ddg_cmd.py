"""DuckDuckGo command module for OARC Crawlers.

This module defines CLI commands for interacting with DuckDuckGo via the OARC Crawlers framework.
It provides commands for performing text, image, and news searches, supporting configurable options
such as query terms and result limits.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_decorators import (
    asyncio_run, 
    handle_error, 
    NetworkError,
)

from oarc_crawlers.cli.help_texts import (
    ARGS_CONFIG_HELP,
    ARGS_MAX_RESULTS_HELP,
    ARGS_QUERY_HELP,
    ARGS_VERBOSE_HELP,
    DDG_GROUP_HELP,
    DDG_IMAGES_HELP,
    DDG_NEWS_HELP,
    DDG_TEXT_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.crawlers.ddg_crawler import DDGCrawler
from oarc_crawlers.utils.const import ERROR, SUCCESS


@click.group(help=DDG_GROUP_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def ddg(verbose, config):
    """
    Group of DuckDuckGo-related CLI commands for search operations.

    This group provides commands to perform text, image, and news searches using DuckDuckGo.
    Use the available subcommands to specify the type of search and customize options such as query and result limits.
    """
    pass

@ddg.command(help=DDG_TEXT_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--max-results', default=5, type=int, help=ARGS_MAX_RESULTS_HELP)
@asyncio_run
@handle_error
async def text(query, max_results):
    """Perform a DuckDuckGo text search.

    Executes a search query using DuckDuckGo and returns a list of relevant text results.

    Args:
        query (str): The search query string.
        max_results (int): Maximum number of results to return.

    Returns:
        int: SUCCESS constant if the search completes successfully.
    """
    crawler = DDGCrawler()
    
    click.echo(f"Searching DuckDuckGo for: {query}")
    log.debug(f"Using max_results: {max_results}")
    
    result = await crawler.text_search(query, max_results=max_results)
    
    if 'error' in result:
        raise NetworkError(f"Search failed: {result['error']}")
    
    log.debug(f"Got {len(result.get('results', []))} search results")
    click.echo(result)
    return SUCCESS

@ddg.command(help=DDG_IMAGES_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--max-results', default=10, type=int, help=ARGS_MAX_RESULTS_HELP)
@asyncio_run
@handle_error
async def images(query, max_results):
    """Perform a DuckDuckGo image search.

    Executes an image search query using DuckDuckGo and returns a list of relevant image results.

    Args:
        query (str): The search query string.
        max_results (int): Maximum number of image results to return.

    Returns:
        int: SUCCESS constant if the image search completes successfully.
    """
    crawler = DDGCrawler()
    
    click.echo(f"Searching DuckDuckGo images for: {query}")
    log.debug(f"Using max_results: {max_results}")
    
    result = await crawler.image_search(query, max_results=max_results)
    
    if 'error' in result:
        raise NetworkError(f"Image search failed: {result['error']}")
    
    log.debug(f"Got {len(result.get('results', []))} image results")
    click.echo(result)
    return SUCCESS

@ddg.command(help=DDG_NEWS_HELP)
@click.option('--query', required=True, help=ARGS_QUERY_HELP)
@click.option('--max-results', default=20, type=int, help=ARGS_MAX_RESULTS_HELP)
@asyncio_run
@handle_error
async def news(query, max_results):
    """Perform a DuckDuckGo news search.

    Executes a news search query using DuckDuckGo and returns a list of relevant news articles.

    Args:
        query (str): The search query string.
        max_results (int): Maximum number of news articles to return.

    Returns:
        int: SUCCESS constant if the news search completes successfully.
    """
    crawler = DDGCrawler()
    
    click.echo(f"Searching DuckDuckGo news for: {query}")
    log.debug(f"Using max_results: {max_results}")
    
    result = await crawler.news_search(query, max_results=max_results)
    
    if ERROR in result:
        raise NetworkError(f"News search failed: {result['error']}")
    
    log.debug(f"Got {len(result.get('results', []))} news results")
    click.echo(result)
    return SUCCESS
