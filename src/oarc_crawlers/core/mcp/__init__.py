"""
OARC-Crawlers MCP Core

This package provides core Model Context Protocol (MCP) integration for OARC-Crawlers,
including high-level server and manager classes for tool orchestration and FastMCP compatibility.
"""

from .mcp_manager import MCPManager
from .mcp_server import MCPServer

__all__ = ["MCPManager", "MCPServer"]