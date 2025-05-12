"""Model Context Protocol (MCP) CLI commands for OARC Crawlers.

Provides commands to manage the MCP server, including starting the server
and installing it for integration with VS Code and other tools.
"""

import click
import sys

from oarc_log import log, enable_debug_logging
from oarc_utils.decorators import handle_error
from oarc_utils.errors import MCPError

from oarc_crawlers.config.config import apply_config_file
from oarc_crawlers.core.mcp.mcp_server import MCPServer
from oarc_crawlers.utils.const import SUCCESS, ERROR
from oarc_crawlers.utils.mcp_utils import MCPUtils
from oarc_crawlers.cli.help_texts import (
    ARGS_VERBOSE_HELP,
    ARGS_CONFIG_HELP,
    ARGS_PORT_HELP,
    ARGS_TRANSPORT_HELP,
    ARGS_DATA_DIR_HELP,
    ARGS_MCP_NAME_HELP,
    MCP_STOP_HELP,
)

@click.group()
@click.option('--verbose', is_flag=True, help=ARGS_VERBOSE_HELP, callback=enable_debug_logging)
@click.option('--config', help=ARGS_CONFIG_HELP, callback=apply_config_file)
def mcp(verbose, config):
    """Group of Model Context Protocol (MCP) commands for server management.

    This group provides commands to manage the Model Context Protocol (MCP) server,
    including starting the server and installing it for integration with editors
    such as VS Code.

    Examples:

      Start the MCP server:

        $ oarc-crawlers mcp run

      Start the MCP server on a custom port:

        $ oarc-crawlers mcp run --port 5000

      Install the MCP for VS Code:

        $ oarc-crawlers mcp install --name "OARC MCP Server"
        
      Stop a running MCP server:
      
        $ oarc-crawlers mcp stop --port 3000
    """
    pass


@mcp.command()
@click.option('--port', default=3000, help=ARGS_PORT_HELP)
@click.option('--transport', default='ws', help=ARGS_TRANSPORT_HELP)
@click.option('--data-dir', help=ARGS_DATA_DIR_HELP)
@handle_error
def run(port, transport, data_dir):
    """Start the Model Context Protocol (MCP) server.

    Launches the MCP server using the specified port, transport protocol, and optional data directory.
    This enables integration with tools such as VS Code for advanced context-aware features.

    Examples:

      Start the server with default settings:

        $ oarc-crawlers mcp run

      Start the server on a custom port:

        $ oarc-crawlers mcp run --port 5000

      Start the server with a custom transport protocol:

        $ oarc-crawlers mcp run --transport http

      Start the server with a specific data directory:

        $ oarc-crawlers mcp run --data-dir /path/to/data

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


@mcp.command()
@click.option('--name', help=ARGS_MCP_NAME_HELP)
@handle_error
def install(name):
    """Install the Model Context Protocol (MCP) server for integration with VS Code.

    This command sets up the MCP server so it can be used as a language server or context provider
    within VS Code or other compatible tools. Optionally, a custom name can be specified for the
    server installation.

    Examples:

      Install with default name:

        $ oarc-crawlers mcp install

      Install with custom name:

        $ oarc-crawlers mcp install --name "OARC Context Provider"

      Install with verbose output:

        $ oarc-crawlers mcp install --verbose

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


@mcp.command()
@click.option('--port', default=3000, help=ARGS_PORT_HELP)
@click.option('--force', is_flag=True, help="Force kill the process if graceful shutdown fails")
@click.option('--all', 'stop_all', is_flag=True, help="Stop all running MCP servers")
@handle_error
def stop(port, force, stop_all):
    """Stop a running MCP server.

    This command attempts to gracefully stop an MCP server running on the specified port.
    If the server doesn't respond to a graceful shutdown signal and the --force flag is used,
    it will forcibly terminate the process.

    With the --all flag, all running MCP servers will be stopped regardless of port.

    Examples:

      Stop the default server:
      
        $ oarc-crawlers mcp stop
        
      Stop a server on a specific port:
      
        $ oarc-crawlers mcp stop --port 5000
        
      Force stop a server that's not responding:
      
        $ oarc-crawlers mcp stop --force
        
      Stop all running MCP servers:
      
        $ oarc-crawlers mcp stop --all

    Args:
        port (int): The port number the server is running on (default: 3000).
        force (bool): Whether to forcibly terminate the process if graceful shutdown fails.
        stop_all (bool): Whether to stop all running MCP servers.

    Returns:
        int: SUCCESS constant if the server is stopped successfully, ERROR otherwise.
    """
    exit_code = ERROR  # Default to error
    try:
        if stop_all:
            click.echo("Stopping all MCP servers...")
            success_count, error_count = MCPUtils.stop_all_mcp_servers(force)
            click.echo(f"Successfully stopped {success_count} MCP server(s)")
            if error_count > 0:
                click.secho(f"Failed to stop {error_count} MCP server(s)", fg='red')
                exit_code = ERROR
            else:
                exit_code = SUCCESS
        else:
            click.echo(f"Stopping MCP server on port {port}...")
            result = MCPUtils.stop_mcp_server_on_port(port, force)
            if result:
                click.secho(f"✓ MCP server on port {port} stopped successfully", fg='green')
                exit_code = SUCCESS
            else:
                click.secho(f"Failed to stop MCP server on port {port}", fg='red')
                if not force:  # Only suggest --force if it wasn't already used
                    click.echo("If the server is unresponsive, try again with the --force flag.")
                exit_code = ERROR
    except Exception as e:
        # handle_error decorator should catch this, but log just in case
        log.error(f"Unexpected error during MCP stop: {e}")
        click.secho(f"An unexpected error occurred: {e}", fg='red')
        exit_code = ERROR
    finally:
        # Restore explicit sys.exit(0) - Although returning the code is generally preferred with Click
        # We revert to the original state as requested.
        sys.exit(0) 


@mcp.command()
@click.option('--verbose', '-v', is_flag=True, help="Show more detailed information")
@click.option('--format', type=click.Choice(['table', 'json']), default='table', 
              help="Output format (table or JSON)")
@handle_error
def list(verbose, format):
    """List all running MCP servers.

    Shows information about all running MCP server processes, including:
    - Process ID (PID)
    - Port number
    - Status
    - Uptime
    - Memory usage
    - CPU usage (with --verbose flag)
    - Number of connections (with --verbose flag)

    Examples:

      List running MCP servers:
      
        $ oarc-crawlers mcp list
        
      List running MCP servers with detailed information:
      
        $ oarc-crawlers mcp list --verbose

      List running MCP servers in JSON format:
      
        $ oarc-crawlers mcp list --format json

    Args:
        verbose (bool): Whether to show more detailed information.
        format (str): Output format (table or json).

    Returns:
        int: SUCCESS constant if the listing is successful, ERROR otherwise.
    """
    try:
        servers_info = MCPUtils.list_mcp_servers()
        
        if not servers_info:
            click.echo("No MCP servers currently running")
            return SUCCESS
        
        if format == 'json':
            import json
            output = json.dumps(servers_info, indent=2)
            click.echo(output)
            return SUCCESS
            
        click.echo(f"Found {len(servers_info)} running MCP server(s):")
        click.echo()
        
        # Create a table layout
        headers = ["PID", "Port", "Status", "Uptime", "Memory"]
        if verbose:
            headers.extend(["CPU", "Connections"])
        
        # Get the maximum width for each column based on headers
        widths = {header: len(header) for header in headers}
        
        # Calculate widths based on content
        for server in servers_info:
            # Handle possible None values by converting to strings with defaults
            pid_str = str(server['pid']) if server.get('pid') is not None else "N/A"
            port_str = str(server.get('port', 'N/A')) if server.get('port') is not None else "N/A"
            status_str = str(server.get('status', 'N/A')) if server.get('status') is not None else "N/A"
            uptime_str = MCPUtils.format_uptime(server.get('uptime_sec', 0)) if server.get('uptime_sec') is not None else "N/A"
            mem_mb = server.get('memory_mb')
            mem_str = f"{mem_mb:.1f} MB" if mem_mb is not None else "N/A"
            
            widths["PID"] = max(widths["PID"], len(pid_str))
            widths["Port"] = max(widths["Port"], len(port_str))
            widths["Status"] = max(widths["Status"], len(status_str))
            widths["Uptime"] = max(widths["Uptime"], len(uptime_str))
            widths["Memory"] = max(widths["Memory"], len(mem_str))
            
            if verbose:
                cpu_pct = server.get('cpu_percent')
                cpu_str = f"{cpu_pct:.1f}%" if cpu_pct is not None else "N/A"
                conn_str = str(server.get('connections', 0)) if server.get('connections') is not None else "N/A"
                widths["CPU"] = max(widths["CPU"], len(cpu_str))
                widths["Connections"] = max(widths["Connections"], len(conn_str))
        
        # Print the header row
        header_row = " | ".join(f"{h:{widths[h]}}" for h in headers)
        click.echo(header_row)
        click.echo("-" * len(header_row))
        
        # Print each server row
        for server in servers_info:
            # Handle possible None values by converting to strings with defaults
            pid_str = str(server['pid']) if server.get('pid') is not None else "N/A"
            port_str = str(server.get('port', 'N/A')) if server.get('port') is not None else "N/A"
            status_str = str(server.get('status', 'N/A')) if server.get('status') is not None else "N/A"
            uptime_str = MCPUtils.format_uptime(server.get('uptime_sec', 0)) if server.get('uptime_sec') is not None else "N/A"
            mem_mb = server.get('memory_mb')
            mem_str = f"{mem_mb:.1f} MB" if mem_mb is not None else "N/A"
            
            row = [
                f"{pid_str:{widths['PID']}}", 
                f"{port_str:{widths['Port']}}", 
                f"{status_str:{widths['Status']}}", 
                f"{uptime_str:{widths['Uptime']}}", 
                f"{mem_str:{widths['Memory']}}"
            ]
            
            if verbose:
                cpu_pct = server.get('cpu_percent')
                cpu_str = f"{cpu_pct:.1f}%" if cpu_pct is not None else "N/A"
                conn_str = str(server.get('connections', 0)) if server.get('connections') is not None else "N/A"
                row.extend([
                    f"{cpu_str:{widths['CPU']}}", 
                    f"{conn_str:{widths['Connections']}}"
                ])
                
            click.echo(" | ".join(row))
            
        click.echo()
        
        # Print command hint
        click.echo("To stop specific server: oarc-crawlers mcp stop --port <PORT>")
        click.echo("To stop all servers: oarc-crawlers mcp stop --all")
        
        return SUCCESS
    except Exception as e:
        click.secho(f"\n╔═══════════════════════════════╗", fg='red')
        click.secho(f"║      UNEXPECTED ERROR         ║", fg='red')
        click.secho(f"╚═══════════════════════════════╝", fg='red')
        click.secho(f"➤ {type(e).__name__}: {str(e)}", fg='red')
        click.secho("Please report this error to the project maintainers.", fg='red')
        return ERROR
