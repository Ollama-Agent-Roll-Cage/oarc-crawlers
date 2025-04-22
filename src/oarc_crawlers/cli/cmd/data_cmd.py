"""Data management commands for OARC Crawlers.

This module provides CLI commands for managing and viewing data files,
including Parquet file inspection and manipulation.
"""

import click
import pandas as pd

from oarc_log import enable_debug_logging
from oarc_utils.decorators import handle_error
from oarc_utils.errors import ResourceNotFoundError

from oarc_crawlers.utils.const import SUCCESS, FAILURE
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.storage import ParquetStorage
from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_MAX_ROWS_HELP,
)

@click.group()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def data(verbose, config):
    """Data management operations for viewing and manipulating data files.

    This group provides commands to inspect, view, and manage data files,
    such as Parquet file inspection and manipulation.

    Use --help with subcommands for more details.

    Examples:

      View the first 10 rows of a parquet file:

        $ oarc-crawlers data view data/results.parquet

      View the first 20 rows of a parquet file:

        $ oarc-crawlers data view data/results.parquet --max-rows 20

      View parquet file with detailed logging enabled:

        $ oarc-crawlers data view data/results.parquet --verbose

      View parquet file using a custom configuration:

        $ oarc-crawlers data view data/results.parquet --config custom_config.ini
    """
    pass


@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--max-rows', default=10, type=int, help=ARGS_MAX_ROWS_HELP)
@handle_error
def view(file_path, max_rows):
    """View contents of a Parquet file.

    Loads the specified Parquet file, displays its shape, schema, and a sample of rows.

    Args:
        file_path (str): Path to the Parquet file.
        max_rows (int): Maximum number of rows to display from the file.

    Returns:
        int: 0 if successful, 1 if an error occurs.
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
        
        return SUCCESS
        
    except ResourceNotFoundError as e:
        click.secho(f"Error: {str(e)}", fg='red')
        return FAILURE