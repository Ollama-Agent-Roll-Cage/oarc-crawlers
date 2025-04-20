"""Model Context Protocol (MCP) CLI commands for OARC Crawlers.

Provides commands to manage the MCP server, including starting the server
and installing it for integration with VS Code and other tools.
"""

import click

from oarc_log import log, enable_debug_logging
from oarc_decorators import (
    asyncio_run, 
    handle_error, 
    MCPError,
)

from oarc_crawlers.cli.help_texts import (
    MCP_GROUP_HELP,
    MCP_RUN_HELP,
    MCP_INSTALL_HELP,
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_PORT_HELP,
    ARGS_TRANSPORT_HELP,
    ARGS_DATA_DIR_HELP,
    ARGS_MCP_NAME_HELP,
)
from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.mcp.mcp_server import MCPServer
from oarc_crawlers.utils.const import SUCCESS, ERROR


@click.group(help=MCP_GROUP_HELP)
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def mcp(verbose, config):
    """Entry point for MCP-related CLI commands.

    This group provides commands to manage the Model Context Protocol (MCP) server,
    including starting the server and installing it for integration with editors
    such as VS Code.
    """
    pass


@mcp.command(help=MCP_RUN_HELP)
@click.option('--port', default=3000, help=ARGS_PORT_HELP)
@click.option('--transport', default='ws', help=ARGS_TRANSPORT_HELP)
@click.option('--data-dir', help=ARGS_DATA_DIR_HELP)
@asyncio_run
@handle_error
def run(port, transport, data_dir):
    """Start the Model Context Protocol (MCP) server.

    Launches the MCP server using the specified port, transport protocol, and optional data directory.
    This enables integration with tools such as VS Code for advanced context-aware features.

    Args:
        port (int): The port number to bind the server (default: 3000).
        transport (str): The transport protocol to use (e.g., 'ws' for WebSocket).
        data_dir (str, optional): Directory for storing server data.

    Returns:
        int: SUCCESS constant if the server starts successfully, ERROR otherwise.

    Raises:
        MCPError: If the server fails to start or encounters a runtime error.
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
@asyncio_run
@handle_error
def install(name):
    """
    Install the Model Context Protocol (MCP) server for integration with VS Code.

    This command sets up the MCP server so it can be used as a language server or context provider
    within VS Code or other compatible tools. Optionally, a custom name can be specified for the
    server installation.

    Args:
        name (str, optional): Custom name for the MCP server installation.

    Returns:
        int: SUCCESS constant if installation completes successfully, ERROR otherwise.

    Raises:
        MCPError: If installation fails or encounters an error.
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
