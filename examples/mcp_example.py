"""
Example usage of OARC-Crawlers MCP API
This example demonstrates how to use the MCP API to interact with various crawlers.
"""

def run_mcp_server():
    """
    Initializes and runs the OARC Crawlers MCP server.
    This demonstrates how to start the server from Python code,
    similar to how the 'oarc-crawlers mcp run' CLI command works.
    """
    # Import the MCPServer class from the core mcp module
    from oarc_crawlers.core.mcp.mcp_server import MCPServer

    # Define server configuration (can be customized)
    server_config = {
        "data_dir": "./mcp_data",  # Directory for server data
        "name": "OARC Crawlers (Programmatic)", # Name for identification, e.g., in VS Code
        "port": 3001,             # Port to listen on (choose a different port if 3000 is in use)
        "transport": "ws"         # Transport protocol ('ws' for WebSocket)
    }

    # Create an instance of the MCPServer
    server = MCPServer(**server_config)

    print(f"Starting MCP server '{server_config['name']}' on {server_config['transport']}://localhost:{server_config['port']}...")
    print(f"Data directory: {server.data_dir.resolve()}")

    try:
        # Run the server (this will block until the server is stopped)
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Execute the function to run the server when the script is run directly
    run_mcp_server()