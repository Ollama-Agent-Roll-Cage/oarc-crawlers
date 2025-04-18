# VS Code MCP Integration

OARC-Crawlers provides a Model Context Protocol (MCP) server that integrates seamlessly with Visual Studio Code's Copilot Chat and other MCP-compatible tools.

## Quick Start

```bash
# Install the package
pip install oarc-crawlers

# Install and register with VS Code
python -m oarc_crawlers.mcp_api install --name "OARC Crawlers"
```

## Configuration

The MCP server uses WebSocket transport and is configured by default to:
- Run on port 3000
- Support streaming responses
- Use VS Code-compatible error formatting
- Provide tool documentation through introspection

## VS Code Settings

To configure VS Code to use the OARC-Crawlers MCP server:

1. Open VS Code Settings (Ctrl+,)
2. Search for "MCP Server"
3. Add a new server configuration:
   ```json
   {
       "mcp.servers": [
           {
               "name": "OARC Crawlers",
               "port": 3000,
               "transport": "ws"
           }
       ]
   }
   ```

## Available Commands

The server exposes the following tools to VS Code:

### YouTube Operations
- Download videos and playlists
- Extract video captions
- Search for content
```python
# Example in Copilot Chat
Human: Download this video in HD: https://youtube.com/...
Assistant: I'll help you download that video in high resolution using the OARC Crawlers tools.
```

### GitHub Operations
- Clone and analyze repositories
- Find similar code patterns
- Generate repository summaries
```python
# Example in Copilot Chat
Human: Show me the structure of tensorflow/tensorflow
Assistant: I'll analyze the TensorFlow repository structure for you using OARC Crawlers.
```

### Web Crawling
- DuckDuckGo search integration
- Documentation extraction
- ArXiv paper fetching
```python
# Example in Copilot Chat
Human: Find recent papers about transformers
Assistant: I'll search ArXiv for recent transformer papers using OARC Crawlers.
```

## Error Handling

The server provides VS Code-compatible error responses:

```json
{
    "error": {
        "code": "TOOL_ERROR",
        "message": "Failed to download video",
        "details": {
            "url": "https://youtube.com/...",
            "reason": "Video unavailable"
        }
    }
}
```

Common error codes:
- `TRANSPORT_ERROR`: Connection issues
- `CLIENT_ERROR`: Invalid parameters
- `TOOL_ERROR`: Tool execution failed
- `AUTH_ERROR`: Authentication failed

## Development

To run the server in development mode:

```python
from oarc_crawlers import OARCCrawlersMCP

# Initialize with custom configuration
mcp = OARCCrawlersMCP(
    data_dir="./data",
    name="OARC Crawlers (Dev)",
    port=3001  # Use different port for development
)

# Configure for VS Code
mcp.mcp.configure_vscode(
    server_name=mcp.mcp.name,
    port=mcp.port,
    supports_streaming=True
)

# Run server
mcp.run()