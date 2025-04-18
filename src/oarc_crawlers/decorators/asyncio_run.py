"""
Async utility decorators for OARC.

This module provides decorators for working with asynchronous code,
particularly for integrating async functions with synchronous interfaces like Click.
"""

import asyncio
from functools import wraps

def asyncio_run(f):
    """
    Decorator to convert an async function to a Click command.
    
    This decorator wraps an async function and provides a synchronous interface
    by running the function in the asyncio event loop. This is particularly useful
    for Click commands, which expect synchronous functions.
    
    Args:
        f: The async function to wrap
        
    Returns:
        A synchronous function that runs the async function in the event loop
    
    Example:
        @click.command()
        @click.option('--url', required=True)
        @asyncio_run
        async def download(url):
            result = await downloader.download_video(url)
            return result
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper
