"""Data management commands for OARC Crawlers.

This module provides CLI commands for managing and viewing data files,
including Parquet file inspection and manipulation.
"""
import click
import pandas as pd

from oarc_crawlers.cli.help_texts import (
    DATA_HELP,
    DATA_VIEW_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_FILE_PATH_HELP,
    ARGS_MAX_ROWS_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.storage import ParquetStorage
from oarc_crawlers.decorators import handle_error
from oarc_crawlers.utils.errors import ResourceNotFoundError
from oarc_crawlers.utils.log import log, enable_debug_logging

@click.group(help=DATA_HELP)
def data():
    """Group of data management CLI commands for viewing and manipulating data files."""
    pass

@data.command(help=DATA_VIEW_HELP)
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--max-rows', default=10, type=int, help=ARGS_MAX_ROWS_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@handle_error
def view(file_path, max_rows, verbose, config):
    """View contents of a Parquet file.

    Args:
        file_path (str): Path to the Parquet file
        max_rows (int): Maximum number of rows to display
        verbose (bool): Enable verbose/debug logging
        config (str): Path to configuration file

    Returns:
        int: 0 if successful

    Raises:
        ResourceNotFoundError: If file not found
    """
    try:
        df = ParquetStorage.load_from_parquet(file_path)
        
        # Display basic file info
        click.echo(f"\nParquet File: {file_path}")
        click.echo(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Display schema
        click.echo("\nSchema:")
        for col, dtype in df.dtypes.items():
            click.echo(f"  • {col}: {dtype}")
        
        # Display sample data
        click.echo(f"\nFirst {min(max_rows, len(df))} rows:")
        pd.set_option('display.max_columns', None)
        click.echo(df.head(max_rows).to_string())
        
        return 0
        
    except ResourceNotFoundError as e:
        click.secho(f"Error: {str(e)}", fg='red')
        return 1