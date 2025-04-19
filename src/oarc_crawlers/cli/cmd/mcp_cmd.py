"""Model Context Protocol (MCP) command module for OARC Crawlers.

This module provides CLI commands for managing the MCP server,
including running the server and installing it for VS Code integration.
"""
import click

from oarc_crawlers.cli.help_texts import (
    MCP_HELP,
    MCP_RUN_HELP,
    MCP_INSTALL_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_PORT_HELP,
    ARGS_TRANSPORT_HELP,
    ARGS_DATA_DIR_HELP,
    ARGS_MCP_NAME_HELP
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.utils.const import SUCCESS, ERROR
from oarc_crawlers.core.mcp.mcp_server import MCPServer
from oarc_crawlers.decorators import asyncio_run, handle_error
from oarc_crawlers.utils.errors import MCPError
from oarc_crawlers.utils.log import log, enable_debug_logging

@click.group(help=MCP_HELP)
def mcp():
    """Group of Model Context Protocol (MCP) CLI commands: run the server and install for VS Code integration."""
    pass

@mcp.command(help=MCP_RUN_HELP)
@click.option('--port', default=3000, help=ARGS_PORT_HELP)
@click.option('--transport', default='ws', help=ARGS_TRANSPORT_HELP)
@click.option('--data-dir', help=ARGS_DATA_DIR_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
def run(port, transport, data_dir, verbose, config):
    """Run the Model Context Protocol (MCP) server for OARC Crawlers.

    Args:
        port (int): The port to run the server on.
        transport (str): The transport method to use ("ws" or "sse").
        data_dir (str): Directory to store server data.
        verbose (bool): Enable verbose/debug logging.
        config (str): Path to configuration file.

    Returns:
        int: SUCCESS if the server starts successfully, ERROR otherwise.
    """
    click.echo(f"Starting MCP server on port {port} with transport '{transport}'")
    log.debug(f"Initializing server with data_dir={data_dir}")
    
    try:
        server = MCPServer(data_dir=data_dir, port=port)
        server.run(transport=transport)
        return SUCCESS
    except MCPError as e:
        click.secho(f"MCP server error: {e}", fg='red')
        return ERROR

@mcp.command(help=MCP_INSTALL_HELP)
@click.option('--name', help=ARGS_MCP_NAME_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
@asyncio_run
@handle_error
def install(name, verbose, config):
    """
    Install the Model Context Protocol (MCP) server for VS Code integration.

    Args:
        name (str): Optional custom name for the server in VS Code.
        verbose (bool): Enable verbose/debug logging.
        config (str): Path to configuration file.

    Returns:
        int: SUCCESS if installation completes successfully, ERROR otherwise.
    """
    click.echo(f"Installing MCP server{' as ' + name if name else ''} for VS Code integration")
    log.debug("Initializing MCPServer for installation")
    
    try:
        server = MCPServer()
        server.install(name=name)
        click.secho(f"✓ MCP server successfully installed{' as ' + name if name else ''}", fg='green')
        return SUCCESS
    except MCPError as e:
        click.secho(f"MCP installation error: {e}", fg='red')
        return ERROR
