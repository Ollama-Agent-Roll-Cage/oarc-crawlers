"""
MCP (Model Context Protocol) utility functions

This module provides utility functions for working with MCP servers and clients.
"""

import inspect
import os
import signal
import socket
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

import psutil

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
            
            cmd = ["fastmcp", "install", script_path]
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

    @staticmethod
    def is_mcp_running_on_port(port: int) -> bool:
        """
        Check if an MCP server is running on the specified port.
        
        Args:
            port: The port number to check
            
        Returns:
            bool: True if a server is running on the port, False otherwise
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            s.close()
            return result == 0
        except Exception as e:
            log.debug(f"Error checking port {port}: {e}")
            return False

    @staticmethod
    def find_mcp_process_on_port(port: int) -> Optional[psutil.Process]:
        """
        Find the MCP server process running on the specified port.
        
        Args:
            port: The port number to check
            
        Returns:
            Optional[psutil.Process]: The process if found, None otherwise
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'oarc-crawlers' in ' '.join(cmdline) and 'mcp' in cmdline and 'run' in cmdline:
                    # First check if process has connections on this port
                    try:
                        for conn in proc.connections(kind='inet'):
                            if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                                return proc
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                    
                    # As a fallback, check if port is in command line arguments
                    cmd_str = ' '.join(cmdline)
                    port_index = cmd_str.find('--port')
                    if port_index >= 0:
                        port_parts = cmd_str[port_index:].split()
                        if len(port_parts) >= 2:
                            try:
                                if int(port_parts[1]) == port:
                                    return proc
                            except (ValueError, IndexError):
                                pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None

    @staticmethod
    def find_all_mcp_processes() -> List[psutil.Process]:
        """
        Find all running MCP server processes.
        
        Returns:
            List[psutil.Process]: List of found processes
        """
        found_servers = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'oarc-crawlers' in ' '.join(cmdline) and 'mcp' in cmdline and 'run' in cmdline:
                    found_servers.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return found_servers

    @staticmethod
    def terminate_process(pid: int, force: bool = False, timeout: int = 5) -> bool:
        """
        Terminate a process with the given PID.
        
        Args:
            pid: The process ID to terminate
            force: Whether to forcibly terminate the process if graceful shutdown fails
            timeout: Time in seconds to wait for graceful termination
            
        Returns:
            bool: True if process was terminated successfully, False otherwise
        """
        try:
            # Try graceful termination first (SIGTERM)
            if hasattr(signal, 'SIGTERM'):
                os.kill(pid, signal.SIGTERM)
            else:
                # Windows fallback
                os.kill(pid, 0)  # On Windows, signal 0 can be used to terminate a process
            
            log.debug(f"Sent termination signal to process {pid}")
            
            # Wait for the process to die
            for _ in range(timeout):
                if not psutil.pid_exists(pid):
                    log.info(f"Process {pid} stopped successfully")
                    return True
                time.sleep(1)
            
            if force:
                # If still running and force is specified, send SIGKILL or use Windows API
                log.warning(f"Process {pid} still running, forcing termination...")
                try:
                    if hasattr(signal, 'SIGKILL'):
                        # Unix systems
                        os.kill(pid, signal.SIGKILL)
                    elif os.name == 'nt':
                        # Windows: use the taskkill command which is more reliable for force-killing
                        import subprocess
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                      check=True, capture_output=True, timeout=5)
                    else:
                        # Last resort
                        proc = psutil.Process(pid)
                        proc.kill()
                        
                    # Wait to ensure process is actually terminated
                    time.sleep(0.5)
                    if not psutil.pid_exists(pid):
                        log.info(f"Process {pid} forcibly terminated")
                        return True
                    else:
                        log.error(f"Process {pid} still exists after force termination")
                        return False
                except Exception as inner_e:
                    log.error(f"Failed to forcibly terminate process {pid}: {inner_e}")
                    return False
            else:
                log.warning(f"Process {pid} is not responding to termination signal")
                return False
                
        except Exception as e:
            log.error(f"Failed to terminate process {pid}: {e}")
            return False

    @staticmethod
    def stop_mcp_server_on_port(port: int, force: bool = False) -> bool:
        """
        Stop an MCP server running on the specified port.
        
        Args:
            port: The port number the server is running on
            force: Whether to forcibly terminate the process if graceful shutdown fails
            
        Returns:
            bool: True if server was stopped successfully or no server was found, False otherwise
        """
        # Check if the port is in use
        is_port_active = MCPUtils.is_mcp_running_on_port(port)
        
        # Find the specific process
        proc = MCPUtils.find_mcp_process_on_port(port)
        
        if not proc and not is_port_active:
            log.info(f"No MCP server found running on port {port}")
            return True
        
        if is_port_active and not proc:
            # Something's using the port but we couldn't identify it as our MCP server
            log.warning(f"Port {port} is in use but no matching MCP server process found")
            # Try to find any MCP server that might be using this port
            all_mcp_procs = MCPUtils.find_all_mcp_processes()
            if all_mcp_procs:
                log.info(f"Found {len(all_mcp_procs)} MCP servers, attempting to check them")
                for mcp_proc in all_mcp_procs:
                    log.info(f"Checking MCP server with PID {mcp_proc.info['pid']}")
                    cmdline = ' '.join(mcp_proc.info.get('cmdline', []))
                    if f'--port {port}' in cmdline or (port == 3000 and '--port' not in cmdline):
                        log.info(f"Found likely MCP server on port {port} with PID {mcp_proc.info['pid']}")
                        proc = mcp_proc
                        break
            
            if not proc:
                log.info(f"No MCP server process found for port {port}")
                return True
                
        # Terminate the process
        pid = proc.info['pid']
        log.info(f"Found MCP server process (PID: {pid})" + (f" using port {port}" if is_port_active else ""))
        return MCPUtils.terminate_process(pid, force)

    @staticmethod
    def stop_all_mcp_servers(force: bool = False) -> Tuple[int, int]:
        """
        Stop all running MCP server processes.
        
        Args:
            force: Whether to forcibly terminate processes if graceful shutdown fails
            
        Returns:
            Tuple[int, int]: (success_count, error_count)
        """
        found_servers = MCPUtils.find_all_mcp_processes()
        
        if not found_servers:
            log.info("No running MCP servers found")
            return 0, 0
        
        log.info(f"Found {len(found_servers)} MCP server(s) running")
        
        success_count = 0
        error_count = 0
        
        for proc in found_servers:
            # Try to get port information
            port_info = ""
            try:
                for conn in proc.connections(kind='inet'):
                    if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port'):
                        port_info = f" on port {conn.laddr.port}"
                        break
            except:
                pass
            
            log.info(f"Stopping MCP server (PID: {proc.info['pid']}){port_info}...")
            if MCPUtils.terminate_process(proc.info['pid'], force):
                success_count += 1
            else:
                error_count += 1
        
        log.info(f"Successfully stopped {success_count} MCP server(s)")
        if error_count > 0:
            log.warning(f"Failed to stop {error_count} MCP server(s)")
        
        # Ensure all connections and resources are cleaned up
        # Force garbage collection to close any lingering sockets
        import gc
        gc.collect()
            
        return success_count, error_count

    @staticmethod
    def list_mcp_servers() -> List[Dict[str, Any]]:
        """
        List all running MCP server processes with detailed information.
        
        Returns:
            List[Dict]: List of dictionaries containing information about each running MCP server
        """
        found_servers = []
        mcp_processes = MCPUtils.find_all_mcp_processes()
        
        for proc in mcp_processes:
            try:
                # Basic process info
                server_info = {
                    'pid': proc.info['pid'],
                    'port': None,
                    'status': 'running',
                    'uptime_sec': time.time() - proc.create_time(),
                    'cmdline': proc.info.get('cmdline', []),
                    'memory_mb': round(proc.memory_info().rss / (1024 * 1024), 2),  # Convert to MB
                    'cpu_percent': None,
                    'tool_count': None,
                    'connections': 0
                }
                
                # Try to get port information and count connections
                try:
                    connections = proc.connections(kind='inet')
                    server_info['connections'] = len(connections)
                    for conn in connections:
                        if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port'):
                            server_info['port'] = conn.laddr.port
                            break
                except Exception as e:
                    log.debug(f"Error getting connection info for PID {proc.info['pid']}: {e}")
                    
                # Try to get CPU usage
                try:
                    server_info['cpu_percent'] = round(proc.cpu_percent(interval=0.1), 1)
                except Exception as e:
                    log.debug(f"Error getting CPU info for PID {proc.info['pid']}: {e}")
                    
                # Get command line info - extract port number from command line if not found
                if server_info['port'] is None and server_info['cmdline']:
                    cmdline = ' '.join(server_info['cmdline'])
                    port_index = cmdline.find('--port')
                    if port_index >= 0:
                        port_parts = cmdline[port_index:].split()
                        if len(port_parts) >= 2:
                            try:
                                server_info['port'] = int(port_parts[1])
                            except (ValueError, IndexError):
                                # Failed to parse port, fall back to default
                                if 'oarc-crawlers mcp run' in cmdline:
                                    server_info['port'] = 3000  # Default port
                    else:
                        # No explicit port in command, assume default
                        if 'oarc-crawlers mcp run' in cmdline:
                            server_info['port'] = 3000  # Default port
                
                found_servers.append(server_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process disappeared or can't be accessed
                continue
            except Exception as e:
                log.debug(f"Unexpected error processing PID {proc.info.get('pid', 'unknown')}: {e}")
                
        return found_servers

    @staticmethod
    def format_uptime(seconds: float) -> str:
        """
        Format uptime in seconds to a human-readable string
        
        Args:
            seconds: Uptime in seconds
            
        Returns:
            str: Formatted uptime string (e.g. "3d 12h 5m 2s")
        """
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{int(days)}d")
        if hours > 0 or days > 0:
            parts.append(f"{int(hours)}h")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{int(minutes)}m")
        parts.append(f"{int(seconds)}s")
        
        return " ".join(parts)
