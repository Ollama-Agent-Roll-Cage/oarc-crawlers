"""Error handling utilities for OARC Crawlers."""
import traceback
from typing import Any, Dict

import click

from oarc_crawlers.utils.errors import OarcCrawlerError
from oarc_crawlers.utils.log import log

class ErrorHandler:
    """Handles errors in a consistent way throughout the application."""
    
    @staticmethod
    def handle(error: Exception, verbose: bool = False) -> Dict[str, Any]:
        """Handle an exception and return a structured response.
        
        Args:
            error: The exception to handle
            verbose: Whether to include debug information in the output
            
        Returns:
            A dictionary containing error information
        """
        # Get error details
        error_type = type(error).__name__
        error_message = str(error)
        exit_code = getattr(error, 'exit_code', 1) if isinstance(error, OarcCrawlerError) else 1
        
        # Only log in verbose mode - the report method will handle user output
        if verbose:
            # Log the error with context-aware logger for debugging
            log.error(f"{error_type}: {error_message}")
            log.error(traceback.format_exc())
            
        # Return structured error information
        result = {
            "success": False,
            "error": error_message,
            "error_type": error_type,
            "exit_code": exit_code
        }
        
        if verbose:
            result["traceback"] = traceback.format_exc()
            
        return result
    
    @staticmethod
    def report(error: Exception, verbose: bool = False) -> int:
        """Handle an exception, display it to the user, and return an exit code.
        
        Args:
            error: The exception to handle
            verbose: Whether to include debug information in the output
            
        Returns:
            An exit code suitable for sys.exit()
        """
        result = ErrorHandler.handle(error, verbose)
        
        # Create a visually distinct error message for users
        if isinstance(error, OarcCrawlerError):
            # For expected errors, display a concise message
            click.secho("╔═══════════════════════════════╗", fg="red")
            click.secho("║           ERROR               ║", fg="red", bold=True)
            click.secho("╚═══════════════════════════════╝", fg="red")
            click.secho(f"➤ {result['error']}", fg="red")
        else:
            # For unexpected errors, provide more context
            click.secho("╔═══════════════════════════════╗", fg="red")
            click.secho("║      UNEXPECTED ERROR         ║", fg="red", bold=True)
            click.secho("╚═══════════════════════════════╝", fg="red")
            click.secho(f"➤ {result['error_type']}: {result['error']}", fg="red")
            click.secho("Please report this error to the project maintainers.", fg="yellow")
        
        # Show traceback in verbose mode
        if verbose and "traceback" in result:
            click.echo()
            click.secho("Debug Information:", fg="blue", bold=True)
            click.echo(result["traceback"])
            
        return result["exit_code"]
