"""TOML Dependency Updater

This module provides classes for updating Python dependencies in pyproject.toml files
by crawling PyPI to find the latest package versions.

Usage examples:

1. Command line usage:
   ```
   python toml_dependency_updater.py path/to/pyproject.toml
   ```

2. Basic import usage:
   ```python
   import asyncio
   from toml_dependency_updater import TOMLDependencyUpdater
   
   async def main():
       updater = TOMLDependencyUpdater()
       updates = await updater.update_file("path/to/pyproject.toml")
       print(f"Updated {sum(len(pkgs) for pkgs in updates.values())} packages")
   
   asyncio.run(main())
   ```

3. Non-interactive usage (automatically save changes):
   ```python
   async def update_dependencies():
       updater = TOMLDependencyUpdater()
       updates = await updater.update_file(
           "path/to/pyproject.toml", 
           save_changes=True, 
           interactive=False
       )
       return updates
   ```

4. Just check latest versions without updating files:
   ```python
   async def check_versions():
       updater = TOMLDependencyUpdater()
       
       # Single package
       latest_pandas = await updater.get_package_version("pandas")
       
       # Multiple packages
       versions = await updater.get_multiple_versions(["numpy", "requests", "flask"])
       for pkg, version in versions.items():
           print(f"{pkg}: {version}")
   ```

Author: Based on BSWebCrawler by @BorcherdingL
Date: 4/11/2025
"""

import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import aiohttp
import tomli
import tomli_w
from bs4 import BeautifulSoup

# Set up logging
logger = logging.getLogger(__name__)

class PyPIVersionCrawler:
    """Class for crawling PyPI to get the latest package versions."""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """Initialize the PyPI crawler.
        
        Args:
            session: Optional aiohttp client session
        """
        self.session = session
        self._user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    
    async def get_latest_version(self, package_name: str) -> str:
        """Get the latest version of a package from PyPI.
        
        Args:
            package_name: Name of the Python package
            
        Returns:
            str: Latest version string or empty string if not found
        """
        # First try the JSON API
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            headers = {'User-Agent': self._user_agent}
            
            should_close_session = False
            if not self.session:
                self.session = aiohttp.ClientSession()
                should_close_session = True
                
            try:
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        latest_version = data.get('info', {}).get('version', '')
                        logger.info(f"Found latest version of {package_name}: {latest_version}")
                        return latest_version
            finally:
                if should_close_session:
                    await self.session.close()
                    
            # If JSON API fails, fall back to web scraping
            return await self._scrape_pypi_version(package_name)
                    
        except Exception as e:
            logger.error(f"Error getting latest version for {package_name}: {e}")
            return ""
            
    async def _scrape_pypi_version(self, package_name: str) -> str:
        """Scrape PyPI website to find the latest version.
        
        Args:
            package_name: Name of the Python package
            
        Returns:
            str: Latest version string or empty string if not found
        """
        try:
            url = f"https://pypi.org/project/{package_name}/"
            headers = {'User-Agent': self._user_agent}
            
            should_close_session = False
            if not self.session:
                self.session = aiohttp.ClientSession()
                should_close_session = True
                
            try:
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Look for version in the header
                        version_header = soup.select_one('h1.package-header__name')
                        if version_header:
                            version_match = re.search(r'(\d+\.\d+\.\d+[\w\d.-]*)', version_header.text)
                            if version_match:
                                version = version_match.group(1)
                                logger.info(f"Scraped latest version of {package_name}: {version}")
                                return version
                        
                        # Try another common location
                        version_elem = soup.select_one('p.package-header__version')
                        if version_elem:
                            version = version_elem.text.strip()
                            logger.info(f"Scraped latest version of {package_name}: {version}")
                            return version
            finally:
                if should_close_session:
                    await self.session.close()
                    
            logger.warning(f"Could not find version for {package_name}")
            return ""
                    
        except Exception as e:
            logger.error(f"Error scraping version for {package_name}: {e}")
            return ""
    
    async def get_multiple_versions(self, packages: List[str]) -> Dict[str, str]:
        """Get the latest versions for multiple packages.
        
        Args:
            packages: List of package names
            
        Returns:
            Dict mapping package names to their latest versions
        """
        # Create a shared session for multiple requests
        async with aiohttp.ClientSession() as session:
            self.session = session
            tasks = [self.get_latest_version(pkg) for pkg in packages]
            results = await asyncio.gather(*tasks)
            
            return dict(zip(packages, results))


class PyProjectTOMLUpdater:
    """Class for updating dependencies in pyproject.toml files."""
    
    def __init__(self, file_path: Union[str, Path]):
        """Initialize the updater with a pyproject.toml file.
        
        Args:
            file_path: Path to the pyproject.toml file
        """
        self.file_path = Path(file_path)
        self.toml_data = None
        self.crawler = PyPIVersionCrawler()
        
    async def load_toml(self) -> bool:
        """Load and parse the pyproject.toml file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.file_path, "rb") as f:
                self.toml_data = tomli.load(f)
            logger.info(f"Successfully loaded {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading {self.file_path}: {e}")
            return False
    
    def _extract_package_name(self, dependency_str: str) -> Tuple[str, str, str]:
        """Extract the package name from a dependency string.
        
        Args:
            dependency_str: Dependency string like "package>=1.0.0"
            
        Returns:
            Tuple of (package_name, operator, version) or (dependency_str, "", "")
        """
        match = re.match(r'([a-zA-Z0-9_.-]+)([<>=!~^]+)(.+)', dependency_str)
        if match:
            return match.group(1), match.group(2), match.group(3)
        return dependency_str, "", ""
    
    def _get_dependencies(self) -> Dict[str, List[str]]:
        """Extract all dependencies from the pyproject.toml.
        
        Returns:
            Dict mapping dependency section names to lists of dependencies
        """
        result = {}
        
        # Check main dependencies section
        if self.toml_data and "project" in self.toml_data:
            if "dependencies" in self.toml_data["project"]:
                result["dependencies"] = self.toml_data["project"]["dependencies"]
        
        # Check optional dependencies sections
        if (self.toml_data and "project" in self.toml_data and 
            "optional-dependencies" in self.toml_data["project"]):
            for section, deps in self.toml_data["project"]["optional-dependencies"].items():
                result[f"optional-dependencies.{section}"] = deps
        
        return result
    
    async def update_dependencies(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Update all dependencies to their latest versions.
        
        Returns:
            Dict with section names mapping to lists of (package, old_ver, new_ver)
        """
        if not self.toml_data:
            if not await self.load_toml():
                return {}
        
        dependency_sections = self._get_dependencies()
        updates = {}
        
        for section_name, dependencies in dependency_sections.items():
            section_updates = []
            all_packages = []
            
            # Extract all package names
            for dep in dependencies:
                package_name, _, _ = self._extract_package_name(dep)
                all_packages.append(package_name)
            
            # Fetch all versions in parallel
            version_mapping = await self.crawler.get_multiple_versions(all_packages)
            
            # Update each dependency
            new_dependencies = []
            for i, dep in enumerate(dependencies):
                package_name, operator, old_version = self._extract_package_name(dep)
                
                if not operator:  # Simple dependency without version
                    new_dependencies.append(dep)
                    continue
                
                new_version = version_mapping.get(package_name, "")
                if new_version and new_version != old_version:
                    new_dep = f"{package_name}{operator}{new_version}"
                    new_dependencies.append(new_dep)
                    section_updates.append((package_name, old_version, new_version))
                else:
                    new_dependencies.append(dep)
            
            # Update the TOML data
            section_parts = section_name.split('.')
            if len(section_parts) == 1:
                self.toml_data["project"][section_name] = new_dependencies
            else:
                self.toml_data["project"][section_parts[0]][section_parts[1]] = new_dependencies
            
            if section_updates:
                updates[section_name] = section_updates
        
        return updates
    
    def save_toml(self) -> bool:
        """Save the updated pyproject.toml file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a backup of the original file
            backup_path = self.file_path.with_suffix('.toml.bak')
            self.file_path.rename(backup_path)
            
            # Write the updated file
            with open(self.file_path, "wb") as f:
                tomli_w.dump(self.toml_data, f)
            
            logger.info(f"Saved updated {self.file_path}, backup at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving {self.file_path}: {e}")
            
            # Try to restore the original if the save failed
            try:
                if backup_path.exists() and not self.file_path.exists():
                    backup_path.rename(self.file_path)
                    logger.info(f"Restored original file from backup")
            except Exception as restore_error:
                logger.error(f"Error restoring backup: {restore_error}")
                
            return False
    
    def print_updates(self, updates: Dict[str, List[Tuple[str, str, str]]]) -> None:
        """Print a summary of the updates made.
        
        Args:
            updates: Dict with section names mapping to lists of (package, old_ver, new_ver)
        """
        if not updates:
            print("No updates were made.")
            return
        
        print("\nPackage updates:")
        print("-" * 60)
        print(f"{'Package':<30} {'Old Version':<15} {'New Version':<15}")
        print("-" * 60)
        
        for section, packages in updates.items():
            print(f"\n[{section}]")
            for package, old_ver, new_ver in packages:
                print(f"{package:<30} {old_ver:<15} {new_ver:<15}")
        
        print("\nTotal updates:", sum(len(packages) for packages in updates.values()))


class TOMLDependencyUpdater:
    """Main class for updating dependencies in pyproject.toml files.
    
    This class provides a convenient interface for updating Python dependencies
    in pyproject.toml files.
    
    Example usage:
        ```python
        from toml_dependency_updater import TOMLDependencyUpdater
        
        async def update_my_project():
            updater = TOMLDependencyUpdater()
            updates = await updater.update_file("path/to/pyproject.toml")
            if updates:
                print("Dependencies updated!")
        
        asyncio.run(update_my_project())
        ```
    """
    
    def __init__(self, log_level=logging.INFO):
        """Initialize the dependency updater.
        
        Args:
            log_level: Logging level (default: logging.INFO)
        """
        # Configure logging if not already configured
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
    
    async def update_file(self, file_path: Union[str, Path], 
                          save_changes: bool = False, 
                          interactive: bool = True) -> Dict[str, List[Tuple[str, str, str]]]:
        """Update dependencies in a pyproject.toml file.
        
        Args:
            file_path: Path to the pyproject.toml file
            save_changes: Whether to save changes automatically (default: False)
            interactive: Whether to prompt for confirmation before saving (default: True)
            
        Returns:
            Dict with section names mapping to lists of (package, old_ver, new_ver)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Error: File {file_path} does not exist")
            return {}
        
        logger.info(f"Updating dependencies in {file_path}...")
        updater = PyProjectTOMLUpdater(file_path)
        
        if not await updater.load_toml():
            logger.error(f"Failed to load {file_path}")
            return {}
        
        updates = await updater.update_dependencies()
        
        if not updates:
            logger.info("No updates found.")
            return {}
        
        updater.print_updates(updates)
        
        should_save = save_changes
        if interactive and not save_changes:
            save_response = input("\nSave changes to pyproject.toml? [y/N]: ").lower()
            should_save = save_response == 'y'
        
        if should_save:
            if updater.save_toml():
                logger.info("Changes saved successfully.")
            else:
                logger.error("Failed to save changes.")
        else:
            logger.info("Changes not saved.")
        
        return updates
    
    async def get_package_version(self, package_name: str) -> str:
        """Get the latest version of a single package from PyPI.
        
        Args:
            package_name: Name of the Python package
            
        Returns:
            Latest version string or empty string if not found
        """
        crawler = PyPIVersionCrawler()
        return await crawler.get_latest_version(package_name)
    
    async def get_multiple_versions(self, package_names: List[str]) -> Dict[str, str]:
        """Get the latest versions for multiple packages.
        
        Args:
            package_names: List of package names
            
        Returns:
            Dict mapping package names to their latest versions
        """
        crawler = PyPIVersionCrawler()
        return await crawler.get_multiple_versions(package_names)


async def main():
    """Main entry point for the script when used from command line."""
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not file_path:
        print("Usage: python toml_dependency_updater.py <path_to_pyproject.toml>")
        return
    
    updater = TOMLDependencyUpdater()
    await updater.update_file(file_path, interactive=True)


if __name__ == "__main__":
    asyncio.run(main())
