"""Error handling decorator for CLI commands."""
import functools

from oarc_crawlers.utils.error_handler import ErrorHandler

def handle_error(func):
    """Decorator to wrap a Click command and handle exceptions.
    
    This decorator will catch any exceptions raised by the command,
    handle them appropriately, and return a suitable exit code.
    
    Args:
        func: The function to decorate
        
    Returns:
        A wrapped function that handles errors
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        verbose = kwargs.get('verbose', False)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return ErrorHandler.report(e, verbose)
    return wrapped
