"""
ToolManager - A high-level wrapper for
This class provides an easy way to create and use FastMCP servers and clients
anywhere in your application.

Author: @Borcherdingl, RawsonK
Date: 4/18/2025
"""

from typing import Any, Callable, Dict, List
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Client

from oarc_log import log
from oarc_decorators import MCPError

from oarc_crawlers.utils.mcp_utils import MCPUtils


class MCPManager:
    """
    ToolManager provides a high-level interface for managing FastMCP servers and clients.

    This class simplifies the registration and orchestration of tools, resources, and prompts
    for FastMCP-based applications. It also provides convenient methods for running the server,
    installing for deployment, and interacting as a client.

    Typical usage:
        tm = ToolManager("MyServer", dependencies=["requests"])
        @tm.add_tool
        async def hello(name: str) -> str:
            return f"Hello, {name}!"
        tm.run()
    """

    def __init__(self, name: str = "MCPWrapper", dependencies: List[str] = None):
        """
        Initialize the FastMCPWrapper with a name and optional dependencies.
        
        Args:
            name: Name of the MCP server
            dependencies: List of dependencies needed when deployed via `fastmcp install`
        """
        self.name = name
        self.dependencies = dependencies or []
        self.mcp = FastMCP(name, dependencies=self.dependencies)
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        log.debug(f"Initialized MCPManager with name '{name}' and {len(self.dependencies)} dependencies")
        
    def add_tool(self, func: Callable = None, **kwargs) -> Callable:
        """
        Add a function as a tool to the MCP server.
        This can be used as a decorator or a method.
        
        Args:
            func: The function to add as a tool
            **kwargs: Additional keyword arguments to pass to mcp.tool()
            
        Returns:
            The decorated function
        """
        if func is None:
            return lambda f: self.add_tool(f, **kwargs)
        
        decorated = self.mcp.tool(**kwargs)(func)
        self.tools[func.__name__] = decorated
        log.debug(f"Added tool: {func.__name__}")
        return decorated
    
    def add_resource(self, uri: str, func: Callable = None, **kwargs) -> Callable:
        """
        Add a function as a resource to the MCP server.
        This can be used as a decorator or a method.
        
        Args:
            uri: The URI for the resource
            func: The function to add as a resource
            **kwargs: Additional keyword arguments to pass to mcp.resource()
            
        Returns:
            The decorated function
        """
        if func is None:
            return lambda f: self.add_resource(uri, f, **kwargs)
        
        decorated = self.mcp.resource(uri, **kwargs)(func)
        self.resources[uri] = decorated
        log.debug(f"Added resource: {uri}")
        return decorated
    
    def add_prompt(self, func: Callable = None, **kwargs) -> Callable:
        """
        Add a function as a prompt to the MCP server.
        This can be used as a decorator or a method.
        
        Args:
            func: The function to add as a prompt
            **kwargs: Additional keyword arguments to pass to mcp.prompt()
            
        Returns:
            The decorated function
        """
        if func is None:
            return lambda f: self.add_prompt(f, **kwargs)
        
        decorated = self.mcp.prompt(**kwargs)(func)
        self.prompts[func.__name__] = decorated
        log.debug(f"Added prompt: {func.__name__}")
        return decorated
    
    def run(self, transport: str = None, **kwargs):
        """
        Run the MCP server.
        
        Args:
            transport: The transport method to use (e.g., 'sse', 'ws')
            **kwargs: Additional keyword arguments to pass to mcp.run()
        """
        log.info(f"Starting MCP server '{self.name}' with transport '{transport or 'default'}'")
        return self.mcp.run(transport=transport, **kwargs)
    
    def install(self, script_path: str = None, name: str = None, with_deps: List[str] = None):
        """
        Install the MCP server for use with Claude Desktop.
        This is a helper method that executes the CLI command.
        
        Args:
            script_path: The path to the script file
            name: Custom name for the server in Claude
            with_deps: Additional dependencies to install
            
        Returns:
            bool: True if successful
            
        Raises:
            MCPError: If installation fails
        """
        try:
            log.info(f"Installing MCP server '{name or self.name}'")
            
            # Use MCPUtils for installation
            combined_deps = list(self.dependencies)
            if with_deps:
                combined_deps.extend(with_deps)
                
            if script_path is None:
                # Generate script content using MCPUtils
                script_content = MCPUtils.generate_mcp_script(self.name, combined_deps)
                script_content += "\n# Add tools, resources, and prompts\n"
                
                # Add generated code for tools, resources, and prompts
                if self.tools:
                    script_content += MCPUtils.generate_tool_code(self.tools)
                if self.resources:
                    script_content += MCPUtils.generate_resource_code(self.resources)
                if self.prompts:
                    script_content += MCPUtils.generate_prompt_code(self.prompts)
                    
                # Use MCPUtils to install with generated content
                return MCPUtils.install_mcp_with_content(
                    script_content,
                    name=name,
                    mcp_name=self.name,
                    dependencies=combined_deps
                )
            else:
                # Use existing script file
                return MCPUtils.install_mcp(
                    script_path=script_path,
                    name=name,
                    mcp_name=self.name,
                    dependencies=combined_deps
                )
        except Exception as e:
            log.error(f"Failed to install MCP server: {str(e)}")
            raise MCPError(f"Failed to install MCP server: {str(e)}")
        
    @asynccontextmanager
    async def client_session(self, transport=None, sampling_handler=None, **kwargs):
        """
        Create a client session to interact with the MCP server.
        
        Args:
            transport: The transport method to use
            sampling_handler: Handler for LLM sampling requests
            **kwargs: Additional keyword arguments to pass to Client constructor
            
        Yields:
            An MCP Client instance
        """
        log.debug(f"Creating MCP client session with transport '{transport or 'default'}'")
        async with Client(self.mcp, transport=transport, sampling_handler=sampling_handler, **kwargs) as client:
            log.debug("MCP client session established")
            yield client
            log.debug("MCP client session closed")
            
    async def call_tool(self, tool_name: str, params: Dict[str, Any], transport=None, **kwargs):
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters to pass to the tool
            transport: The transport method to use
            **kwargs: Additional keyword arguments to pass to Client constructor
            
        Returns:
            The result of the tool call
        """
        log.debug(f"Calling tool '{tool_name}' with parameters: {params}")
        async with self.client_session(transport=transport, **kwargs) as client:
            result = await client.call_tool(tool_name, params)
            log.debug(f"Tool '{tool_name}' call completed")
            return result
            
    async def read_resource(self, uri: str, transport=None, **kwargs):
        """
        Read a resource from the MCP server.
        
        Args:
            uri: URI of the resource to read
            transport: The transport method to use
            **kwargs: Additional keyword arguments to pass to Client constructor
            
        Returns:
            The content of the resource
        """
        log.debug(f"Reading resource '{uri}'")
        async with self.client_session(transport=transport, **kwargs) as client:
            result = await client.read_resource(uri)
            log.debug(f"Resource '{uri}' read completed")
            return result
            
    async def get_prompt(self, prompt_name: str, params: Dict[str, Any] = None, transport=None, **kwargs):
        """
        Get a prompt from the MCP server.
        
        Args:
            prompt_name: Name of the prompt to get
            params: Parameters to pass to the prompt
            transport: The transport method to use
            **kwargs: Additional keyword arguments to pass to Client constructor
            
        Returns:
            The content of the prompt
        """
        log.debug(f"Getting prompt '{prompt_name}' with parameters: {params or {}}") 
        async with self.client_session(transport=transport, **kwargs) as client:
            result = await client.get_prompt(prompt_name, params or {})
            log.debug(f"Prompt '{prompt_name}' request completed")
            return result
            
    def mount(self, prefix: str, other_wrapper):
        """
        Mount another FastMCPWrapper onto this one with a prefix.
        
        Args:
            prefix: The prefix to use for the mounted wrapper
            other_wrapper: Another FastMCPWrapper instance to mount
        """
        log.info(f"Mounting MCP server '{other_wrapper.name}' at prefix '{prefix}'")
        self.mcp.mount(prefix, other_wrapper.mcp)
        return self
