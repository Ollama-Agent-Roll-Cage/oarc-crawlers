"""
Build utilities for OARC Crawlers.

This module provides static utility methods for cleaning build artifacts,
building the package, and publishing to PyPI or TestPyPI. It supports both
synchronous and asynchronous operations, and handles cross-platform cleanup
of build directories.
"""

import os
import sys
import subprocess
import asyncio


class BuildUtils:
    """
    Static utility methods for building, cleaning, and publishing OARC Crawlers.

    This class provides methods to:
      - Clean build artifacts (dist, build, egg-info)
      - Build the package using PEP 517 build backend
      - Publish the package to PyPI or TestPyPI using Twine (supports async)
    All methods are cross-platform and handle errors gracefully.
    """
    

    @staticmethod
    def clean_build_directories():
        """Clean build directories (dist, build, egg-info).
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("Cleaning build directories...")
            # Ensure build package is installed
            subprocess.run([sys.executable, "-m", "pip", "install", "build"], check=True)
            
            # Clean directories
            if os.name == 'nt':  # Windows
                subprocess.run("if exist dist rmdir /s /q dist", shell=True, check=True)
                subprocess.run("if exist build rmdir /s /q build", shell=True, check=True)
                subprocess.run("for /d %i in (*.egg-info) do rmdir /s /q %i", shell=True, check=True)
            else:  # Unix-like
                subprocess.run("rm -rf dist build *.egg-info", shell=True, check=True)
                
            print("Build directories cleaned successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cleaning build directories: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while cleaning: {e}")
            return False
    

    @staticmethod
    def build_package():
        """Build the package."""
        try:
            subprocess.run([sys.executable, "-m", "build"], check=True)
            print("Package built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error building package: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error building package: {e}")
            sys.exit(1)


    @staticmethod
    async def publish_package(test=False, username=None, password=None, config_file=None):
        """Publish the package to PyPI.
        
        Args:
            test (bool): If True, upload to TestPyPI instead of PyPI
            username (str): PyPI username (if not using keyring or config file)
            password (str): PyPI password (if not using keyring or config file)
            config_file (str): Path to PyPI config file (.pypirc)
            
        Returns:
            dict: Result of the operation with keys 'success' and 'message'
            
        Raises:
            RuntimeError: If the upload fails
        """
        try:
            cmd = ["twine", "upload"]
            if test:
                cmd.extend(["--repository", "testpypi"])
            
            # Add authentication if provided
            if username:
                cmd.extend(["--username", username])
            if password:
                cmd.extend(["--password", password])
            if config_file:
                cmd.extend(["--config-file", config_file])
                
            cmd.extend(["dist/*"])
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return {
                    "success": True,
                    "message": "Package published successfully!",
                    "output": stdout.decode()
                }
            else:
                error_msg = stderr.decode()
                return {
                    "success": False,
                    "message": f"Error publishing package: {error_msg}",
                    "error": error_msg
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error publishing package: {str(e)}",
                "error": str(e)
            }
