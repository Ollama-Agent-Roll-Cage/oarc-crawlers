"""
MCP (Model Context Protocol) utility functions

This module provides utility functions for working with MCP servers and clients.
"""
import subprocess
import tempfile
import inspect
from typing import List, Dict, Any, Optional

from oarc_log import log
from oarc_utils.errors import MCPError


class MCPUtils:
    """Utility functions for MCP server and client operations."""

    @staticmethod
    def install_mcp(script_path: Optional[str] = None, name: str = None, 
                   mcp_name: str = "OARC-Crawlers", dependencies: List[str] = None):
        """
        Install an MCP server for VS Code integration.
        
        Args:
            script_path: The path to the script file
            name: Custom name for the server in VS Code
            mcp_name: The name of the MCP server
            dependencies: Additional dependencies to install
            
        Returns:
            bool: True if successful, False otherwise
        """
        dependencies = dependencies or []
        try:
            if script_path is None:
                # Create a temporary script file
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
                    script_path = temp.name
                    with open(script_path, 'w') as f:
                        f.write(MCPUtils.generate_mcp_script(mcp_name, dependencies))
            
            cmd = ["fastmcp", "install", script_path, "--vscode"]
            if name:
                cmd.extend(["--name", name])
                
            # Add dependencies
            for dep in dependencies:
                cmd.extend(["--with", dep])
                
            log.debug(f"Running install command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            log.info(f"MCP server installed as '{name or mcp_name}'")
            return True
            
        except subprocess.CalledProcessError as e:
            log.error(f"Installation failed: {e}")
            raise MCPError(f"Failed to install MCP server: {str(e)}")
        except Exception as e:
            log.error(f"Unexpected error during installation: {e}")
            raise MCPError(f"Unexpected error during MCP server installation: {str(e)}")

    @staticmethod
    def install_mcp_with_content(script_content: str, name: str = None, 
                                mcp_name: str = "OARC-Crawlers", dependencies: List[str] = None):
        """
        Install an MCP server using provided script content.
        
        Args:
            script_content: The content of the script file
            name: Custom name for the server in VS Code
            mcp_name: The name of the MCP server
            dependencies: Additional dependencies to install
            
        Returns:
            bool: True if successful
            
        Raises:
            MCPError: If installation fails
        """
        try:
            # Create a temporary script file with the provided content
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
                script_path = temp.name
                with open(script_path, 'w') as f:
                    f.write(script_content)
                    
            log.debug(f"Created temporary script file with {len(script_content)} bytes at {script_path}")
            
            # Use the existing install method
            return MCPUtils.install_mcp(
                script_path=script_path,
                name=name,
                mcp_name=mcp_name,
                dependencies=dependencies
            )
            
        except Exception as e:
            log.error(f"Failed to install MCP server from content: {e}")
            raise MCPError(f"Failed to install MCP server from content: {str(e)}")

    @staticmethod
    def generate_mcp_script(name: str, dependencies: List[str]) -> str:
        """
        Generate MCP server script content.
        
        Args:
            name: Name of the MCP server
            dependencies: List of dependencies
            
        Returns:
            str: Generated script content
        """
        deps_str = ", ".join([f'"{dep}"' for dep in dependencies])
        
        return f"""
from fastmcp import FastMCP
from oarc_crawlers.core.mcp.mcp_server import MCPServer

if __name__ == "__main__":
    # Create and run the MCP server
    server = MCPServer(name="{name}")
    server.run()
"""

    @staticmethod
    def generate_tool_code(tools: Dict[str, Any]) -> str:
        """
        Generate code for tools to be included in the temporary script.
        
        Args:
            tools: Dictionary of tool functions
            
        Returns:
            str: Generated code
        """
        tool_code = []
        for name, func in tools.items():
            if hasattr(func, '__wrapped__'):
                source = inspect.getsource(func.__wrapped__)
            else:
                source = inspect.getsource(func)
            lines = source.split('\n')
            first_line = lines[0]
            indentation = len(first_line) - len(first_line.lstrip())
            decorator = ' ' * indentation + '@mcp.tool()'
            lines.insert(0, decorator)
            tool_code.append('\n'.join(lines))
        return '\n\n'.join(tool_code)

    @staticmethod
    def generate_resource_code(resources: Dict[str, Any]) -> str:
        """
        Generate code for resources to be included in the temporary script.
        
        Args:
            resources: Dictionary of resource functions
            
        Returns:
            str: Generated code
        """
        resource_code = []
        for uri, func in resources.items():
            if hasattr(func, '__wrapped__'):
                source = inspect.getsource(func.__wrapped__)
            else:
                source = inspect.getsource(func)
            lines = source.split('\n')
            first_line = lines[0]
            indentation = len(first_line) - len(first_line.lstrip())
            decorator = f'{" " * indentation}@mcp.resource("{uri}")'
            lines.insert(0, decorator)
            resource_code.append('\n'.join(lines))
        return '\n\n'.join(resource_code)
        
    @staticmethod
    def generate_prompt_code(prompts: Dict[str, Any]) -> str:
        """
        Generate code for prompts to be included in the temporary script.
        
        Args:
            prompts: Dictionary of prompt functions
            
        Returns:
            str: Generated code
        """
        prompt_code = []
        for name, func in prompts.items():
            if hasattr(func, '__wrapped__'):
                source = inspect.getsource(func.__wrapped__)
            else:
                source = inspect.getsource(func)
            lines = source.split('\n')
            first_line = lines[0]
            indentation = len(first_line) - len(first_line.lstrip())
            decorator = ' ' * indentation + '@mcp.prompt()'
            lines.insert(0, decorator)
            prompt_code.append('\n'.join(lines))
        return '\n\n'.join(prompt_code)
