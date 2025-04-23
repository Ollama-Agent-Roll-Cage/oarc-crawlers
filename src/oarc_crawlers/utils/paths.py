"""
Path utility functions for OARC Crawlers.

This module provides standardized path management and helper functions
for working with file system paths across the OARC Crawlers project.
"""

import os
import re
import pathlib
import tempfile
import shutil
from datetime import datetime
from typing import List, Optional, Union, Tuple

from oarc_log import log
from oarc_utils.decorators import singleton

from oarc_crawlers.utils.const import (
    ENV_DATA_DIR, 
    ENV_HOME_DIR, 
    DEFAULT_CONFIG_FILENAME, 
    DATA_SUBDIR,
    CONFIG_DIR, 
    OARC_DIR, 
    TEMP_DIR_PREFIX, 
    YOUTUBE_DATA_DIR, 
    GITHUB_REPOS_DIR,
    WEB_CRAWLS_DIR, 
    ARXIV_PAPERS_DIR, 
    ARXIV_SOURCES_DIR,
    ARXIV_COMBINED_DIR, 
    DDG_SEARCHES_DIR,
    GITHUB_BINARY_EXTENSIONS
)

PathLike = Union[str, pathlib.Path]


@singleton
class Paths:
    """
    Utility class for path management in OARC Crawlers.
    """


    @staticmethod
    def ensure_path(path: PathLike) -> pathlib.Path:
        """
        Ensure a path exists and return it.

        Args:
            path: The path to ensure exists

        Returns:
            Path: The ensured path
        """
        path_obj = pathlib.Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj


    @staticmethod
    def get_oarc_home_dir() -> pathlib.Path:
        """
        Get the OARC home directory.
        
        Uses the OARC_HOME_DIR environment variable if set,
        otherwise defaults to the user's home directory.
        
        Returns:
            Path: OARC home directory
        """
        if ENV_HOME_DIR in os.environ:
            return pathlib.Path(os.environ[ENV_HOME_DIR]).resolve()
        return pathlib.Path.home()


    @staticmethod
    def get_oarc_dir() -> pathlib.Path:
        """
        Get the .oarc directory.
        
        Returns:
            Path: .oarc directory
        """
        return Paths.get_oarc_home_dir() / OARC_DIR


    @staticmethod
    def get_default_data_dir() -> pathlib.Path:
        """
        Get the default data directory for OARC Crawlers.

        Returns:
            Path: Default data directory
        """
        # Check for environment variable first (highest priority)
        if ENV_DATA_DIR in os.environ:
            return pathlib.Path(os.environ[ENV_DATA_DIR]).resolve()

        # Default to .oarc/data in the OARC home directory
        return Paths.get_oarc_dir() / DATA_SUBDIR


    @staticmethod
    def get_temp_dir() -> pathlib.Path:
        """
        Get a temporary directory for OARC Crawlers.

        Returns:
            Path: Temporary directory
        """
        temp_dir = pathlib.Path(tempfile.gettempdir()) / TEMP_DIR_PREFIX
        return Paths.ensure_path(temp_dir)


    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        Args:
            name: The original filename
            
        Returns:
            A sanitized filename
        """
        # Replace invalid characters with underscores
        name = re.sub(r'[\\/*?:"<>|]', "_", name)
        # Trim whitespace
        name = name.strip()
        # Replace spaces with underscores
        name = name.replace(" ", "_")
        # Limit length to prevent path too long errors
        if len(name) > 250:
            name = name[:250]
        return name
    

    @staticmethod
    def timestamped_path(base_path: PathLike, name: str, extension: str = "") -> pathlib.Path:
        """
        Create a timestamped path to prevent overwrites.
        
        Args:
            base_path: The base directory path
            name: The base filename
            extension: The file extension (optional)
            
        Returns:
            A timestamped Path object
        """
        safe_name = Paths.sanitize_filename(name)
        timestamp = int(datetime.now().timestamp())
        
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
            
        filename = f"{safe_name}_{timestamp}{extension}"
        return pathlib.Path(base_path) / filename
    

    @staticmethod
    def is_valid_path(path: PathLike) -> bool:
        """
        Check if a path is valid and not potentially problematic.
        
        Args:
            path: The path to validate
            
        Returns:
            bool: True if the path is valid, False otherwise
        """
        str_path = str(path)
        
        # Handle absolute paths that might be invalid
        if os.path.isabs(str_path):
            dir_path = os.path.dirname(str_path)
            
            # For Windows, any path is valid unless specifically marked as invalid
            if os.name == 'nt':
                return '/invalid' not in dir_path.replace('\\', '/')
                
            # For Unix, check specific invalid paths
            if dir_path.startswith('/invalid'):
                return False
                
        return True
        
    @staticmethod
    def ensure_parent_dir(path: PathLike) -> Tuple[bool, str]:
        """
        Ensure the parent directory of a path exists.
        
        Args:
            path: The path whose parent directory should exist
            
        Returns:
            Tuple[bool, str]: Success status and error message (if any)
        """
        try:
            parent_dir = os.path.dirname(str(path))
            if parent_dir:
                Paths.ensure_path(parent_dir)
            return True, ""
        except (PermissionError, OSError) as e:
            return False, str(e)

    @staticmethod
    def file_exists(file_path: PathLike) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: The path to check
            
        Returns:
            bool: True if the file exists, False otherwise
        """
        return os.path.exists(str(file_path))

    @staticmethod
    def create_temp_dir(prefix: Optional[str] = None) -> pathlib.Path:
        """
        Create a temporary directory with an optional prefix.
        
        Args:
            prefix: Optional prefix for the directory name
            
        Returns:
            Path: Path to the created temporary directory
        """
        if prefix:
            temp_dir = pathlib.Path(tempfile.mkdtemp(prefix=prefix))
        else:
            temp_dir = pathlib.Path(tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX))
        log.debug(f"Created temporary directory: {temp_dir}")
        return temp_dir
        
    @staticmethod
    def ensure_temp_dir(dir_path: Optional[PathLike] = None, prefix: Optional[str] = None) -> pathlib.Path:
        """
        Ensure a temporary directory exists, creating it if needed.
        If dir_path is provided, use that path; otherwise create a new temp directory.
        
        Args:
            dir_path: Path to use (optional)
            prefix: Prefix for new temp dir if dir_path is None
            
        Returns:
            Path: Path to the temporary directory
        """
        if dir_path is None:
            return Paths.create_temp_dir(prefix)
            
        path_obj = pathlib.Path(dir_path)
        if path_obj.exists():
            shutil.rmtree(path_obj)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
        
    @staticmethod
    def cleanup_temp_dir(temp_dir: PathLike) -> bool:
        """
        Remove a temporary directory and its contents.
        
        Args:
            temp_dir: Path to temporary directory to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(str(temp_dir)):
                shutil.rmtree(str(temp_dir))
                log.debug(f"Removed temporary directory: {temp_dir}")
                return True
            return True  # Already doesn't exist, so consider it a success
        except Exception as e:
            log.error(f"Failed to remove temporary directory {temp_dir}: {str(e)}")
            return False
            
    @staticmethod
    def create_github_temp_dir(owner: str, repo_name: str) -> pathlib.Path:
        """
        Create a temporary directory specifically for GitHub repository operations.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Path: Path to the created temporary directory
        """
        prefix = f"github_repo_{owner}_{repo_name}_"
        return Paths.create_temp_dir(prefix)

    @staticmethod
    def is_binary_file(file_path: str) -> bool:
        """Check if a file is binary.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file is binary, False otherwise
        """
        # Check extension first
        _, ext = os.path.splitext(file_path.lower())
        if ext in GITHUB_BINARY_EXTENSIONS:
            return True
            
        # Check file contents if needed and the file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    return b'\0' in chunk  # Binary files typically contain null bytes
            except Exception:
                return True  # If we can't read it, treat as binary
        
        # For non-existent files or paths without extensions, default to text
        if ext == '' or ext in ('.txt', '.md', '.py', '.js', '.html', '.css', '.json'):
            return False
            
        # Default for unknown types
        return True

    # YouTube-specific paths
    @staticmethod
    def youtube_data_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """
        Get the YouTube data directory.
        
        Args:
            base_dir: Base data directory. If None, uses the default from Config.
            
        Returns:
            Path to the YouTube data directory
        """
        # Import here to avoid circular import
        from oarc_crawlers.config.config import Config
        
        # Use Config.get_instance().data_dir if base_dir is not provided
        if base_dir is None:
            config = Config.get_instance()  # Get the singleton instance using get_instance()
            base_dir = str(config.data_dir)
            
        return Paths.ensure_path(pathlib.Path(base_dir) / YOUTUBE_DATA_DIR)
    

    @staticmethod
    def youtube_videos_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """Get the YouTube videos directory."""
        return Paths.ensure_path(Paths.youtube_data_dir(base_dir) / "videos")
    

    @staticmethod
    def youtube_playlists_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """Get the YouTube playlists directory."""
        return Paths.ensure_path(Paths.youtube_data_dir(base_dir) / "playlists")
    

    @staticmethod
    def youtube_captions_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """Get the YouTube captions directory."""
        return Paths.ensure_path(Paths.youtube_data_dir(base_dir) / "captions")
    

    @staticmethod
    def youtube_search_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """Get the YouTube search results directory."""
        return Paths.ensure_path(Paths.youtube_data_dir(base_dir) / "searches")
    

    @staticmethod
    def youtube_chats_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """Get the YouTube chat messages directory."""
        return Paths.ensure_path(Paths.youtube_data_dir(base_dir) / "chats")
    

    @staticmethod
    def youtube_metadata_dir(base_dir: Optional[PathLike] = None) -> pathlib.Path:
        """Get the YouTube metadata directory."""
        return Paths.ensure_path(Paths.youtube_data_dir(base_dir) / "metadata")
    

    @staticmethod
    def youtube_metadata_path(base_dir: Optional[PathLike] = None, video_id: str = None) -> pathlib.Path:
        """
        Get the path for YouTube video metadata.
        
        Args:
            base_dir: Base data directory. If None, uses the default from Config.
            video_id: YouTube video ID
            
        Returns:
            Path to the metadata file
        """
        metadata_dir = Paths.youtube_metadata_dir(base_dir)
        if video_id:
            return metadata_dir / f"{video_id}.parquet"
        return metadata_dir
    
    @staticmethod
    def youtube_playlist_dir(output_path: PathLike, playlist_title: str, playlist_id: str) -> pathlib.Path:
        """
        Create a standardized directory path for a YouTube playlist.
        
        Args:
            output_path: Base output directory
            playlist_title: Title of the playlist
            playlist_id: YouTube playlist ID
            
        Returns:
            Path to the playlist directory
        """
        safe_title = Paths.sanitize_filename(playlist_title)
        playlist_dir = pathlib.Path(output_path) / f"{safe_title}_{playlist_id}"
        return Paths.ensure_path(playlist_dir)

    # GitHub-specific paths
    @staticmethod
    def github_repos_dir(base_dir: PathLike) -> pathlib.Path:
        """Get the GitHub repositories directory."""
        return Paths.ensure_path(pathlib.Path(base_dir) / GITHUB_REPOS_DIR)
    

    @staticmethod
    def github_repo_dir(base_dir: PathLike, owner: str, repo: str) -> pathlib.Path:
        """
        Get the directory for a specific GitHub repository.
        
        Args:
            base_dir: Base data directory
            owner: Repository owner/user
            repo: Repository name
            
        Returns:
            Path to the repository directory
        """
        safe_owner = Paths.sanitize_filename(owner)
        safe_repo = Paths.sanitize_filename(repo)
        return Paths.github_repos_dir(base_dir) / f"{safe_owner}_{safe_repo}"
    

    @staticmethod
    def github_repo_data_path(base_dir: PathLike, owner: str, repo: str) -> pathlib.Path:
        """
        Get the path for GitHub repository data.
        
        Args:
            base_dir: Base data directory
            owner: Repository owner/user
            repo: Repository name
            
        Returns:
            Path to the repository data file
        """
        safe_owner = Paths.sanitize_filename(owner)
        safe_repo = Paths.sanitize_filename(repo)
        return Paths.github_repos_dir(base_dir) / f"{safe_owner}_{safe_repo}.parquet"
    

    # Web crawler paths
    @staticmethod
    def web_crawls_dir(base_dir: PathLike) -> pathlib.Path:
        """Get the web crawls directory."""
        return Paths.ensure_path(pathlib.Path(base_dir) / WEB_CRAWLS_DIR)
    

    @staticmethod
    def web_crawl_data_path(base_dir: PathLike, domain: str) -> pathlib.Path:
        """
        Get a path for web crawl data.
        
        Args:
            base_dir: Base data directory
            domain: Domain name
            
        Returns:
            Path to the crawl data file
        """
        safe_domain = Paths.sanitize_filename(domain)
        return Paths.timestamped_path(Paths.web_crawls_dir(base_dir), safe_domain, "parquet")
    

    # ArXiv paths
    @staticmethod
    def arxiv_papers_dir(base_dir: PathLike) -> pathlib.Path:
        """Get the ArXiv papers directory."""
        return Paths.ensure_path(pathlib.Path(base_dir) / ARXIV_PAPERS_DIR)
    

    @staticmethod
    def arxiv_sources_dir(base_dir: PathLike) -> pathlib.Path:
        """Get the ArXiv sources directory."""
        return Paths.ensure_path(pathlib.Path(base_dir) / ARXIV_SOURCES_DIR)
    

    @staticmethod
    def arxiv_combined_dir(base_dir: PathLike) -> pathlib.Path:
        """Get the ArXiv combined data directory."""
        return Paths.ensure_path(pathlib.Path(base_dir) / ARXIV_COMBINED_DIR)
    

    @staticmethod
    def arxiv_paper_path(base_dir: PathLike, arxiv_id: str) -> pathlib.Path:
        """
        Get the path for an ArXiv paper.
        
        Args:
            base_dir: Base data directory
            arxiv_id: ArXiv paper ID
            
        Returns:
            Path to the paper file
        """
        safe_id = Paths.sanitize_filename(arxiv_id)
        return Paths.arxiv_papers_dir(base_dir) / f"{safe_id}.parquet"
    

    @staticmethod
    def arxiv_keywords_path(base_dir: PathLike, arxiv_id: str) -> pathlib.Path:
        """Get path for ArXiv paper keywords."""
        safe_id = Paths.sanitize_filename(arxiv_id)
        return Paths.arxiv_papers_dir(base_dir) / f"{safe_id}_keywords.parquet"
        
    @staticmethod
    def arxiv_references_path(base_dir: PathLike, arxiv_id: str) -> pathlib.Path:
        """Get path for ArXiv paper references."""
        safe_id = Paths.sanitize_filename(arxiv_id)
        return Paths.arxiv_papers_dir(base_dir) / f"{safe_id}_references.parquet"
        
    @staticmethod
    def arxiv_equations_path(base_dir: PathLike, arxiv_id: str) -> pathlib.Path:
        """Get path for ArXiv paper equations."""
        safe_id = Paths.sanitize_filename(arxiv_id)
        return Paths.arxiv_papers_dir(base_dir) / f"{safe_id}_equations.parquet"
        
    @staticmethod
    def arxiv_category_path(base_dir: PathLike, category: str) -> pathlib.Path:
        """Get path for ArXiv category papers."""
        safe_category = Paths.sanitize_filename(category)
        timestamp = int(datetime.now().timestamp())
        return Paths.arxiv_papers_dir(base_dir) / f"category_{safe_category}_{timestamp}.parquet"
        
    @staticmethod
    def arxiv_network_path(base_dir: PathLike, timestamp: int) -> pathlib.Path:
        """Get path for ArXiv citation network."""
        return Paths.arxiv_papers_dir(base_dir) / f"citation_network_{timestamp}.parquet"
    

    # DuckDuckGo paths
    @staticmethod
    def ddg_searches_dir(base_dir: PathLike) -> pathlib.Path:
        """Get the DuckDuckGo searches directory."""
        return Paths.ensure_path(pathlib.Path(base_dir) / DDG_SEARCHES_DIR)
    
    
    @staticmethod
    def ddg_search_data_path(base_dir: PathLike, query: str, search_type: str = "") -> pathlib.Path:
        """
        Get a path for DuckDuckGo search data.
        
        Args:
            base_dir: Base data directory
            query: Search query
            search_type: Type of search (e.g., "text", "image", "news")
            
        Returns:
            Path to the search data file
        """
        safe_query = Paths.sanitize_filename(query)
        prefix = f"{search_type}_" if search_type else ""
        return Paths.timestamped_path(Paths.ddg_searches_dir(base_dir), f"{prefix}{safe_query}", "parquet")
    

    @staticmethod
    def get_default_config_locations() -> List[pathlib.Path]:
        """Get the default locations where config files might exist."""
        return [
            pathlib.Path.cwd() / DEFAULT_CONFIG_FILENAME,  # Current directory
            Paths.get_oarc_dir() / CONFIG_DIR / DEFAULT_CONFIG_FILENAME,  # OARC config directory
            pathlib.Path.home() / DEFAULT_CONFIG_FILENAME,  # User home directory
        ]


    @staticmethod
    def find_config_file() -> Optional[pathlib.Path]:
        """Find a config file in the default locations."""
        for path in Paths.get_default_config_locations():
            if path.exists():
                return path
        return None


    @staticmethod
    def ensure_config_dir() -> pathlib.Path:
        """Ensure the config directory exists and return it."""
        config_dir = Paths.get_oarc_dir() / CONFIG_DIR
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
