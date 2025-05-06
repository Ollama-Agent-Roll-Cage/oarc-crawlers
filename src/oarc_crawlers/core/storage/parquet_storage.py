"""
Storage utilities for saving and loading data in Parquet format.

Usage:
    # Save dictionary to parquet
    data = {'name': 'Example', 'value': 42}
    ParquetStorage.save_to_parquet(data, 'output.parquet')

    # Save list of dictionaries
    items = [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}]
    ParquetStorage.save_to_parquet(items, 'items.parquet')

    # Load parquet file
    df = ParquetStorage.load_from_parquet('output.parquet')

    # Append to existing file
    ParquetStorage.append_to_parquet({'name': 'New', 'value': 100}, 'output.parquet')

    # Prepare parquet data for vector embedding
    docs = ParquetStorage.prepare_for_vectors(
        'papers.parquet',
        text_columns=['title', 'abstract'],
        id_column='paper_id',
        separator=' | '
    )

    # Save YouTube/GitHub data with automatic path handling
    ParquetStorage.save_youtube_data(video_data, video_id='abc123', data_type='metadata')
    ParquetStorage.save_github_data(repo_data, owner='user', repo='project')

Author: @BorcherdingL, RawsonK
Date: 4/18/2025
"""

import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Union, Optional, Dict, List, Sequence

from oarc_log import log
from oarc_utils.errors import DataExtractionError

from oarc_crawlers.utils.paths import Paths, PathLike

class ParquetStorage:
    """"Utility class for saving and loading data in Parquet format."""
    
    @staticmethod
    def save_to_parquet(data: Union[Dict, List, pd.DataFrame], file_path: PathLike) -> bool:
        """Save data to a Parquet file.
        
        Args:
            data: Data to save (dict, list, or DataFrame)
            file_path: Path to save the Parquet file
            
        Returns:
            bool: True if successful, False otherwise
        """
        log.debug(f"Saving data to Parquet file: {file_path}")
        
        try:
            # Use Paths directly instead of StorageUtils
            if not Paths.is_valid_path(file_path):
                log.error(f"Invalid file path: {file_path}")
                return False
            
            success, error_message = Paths.ensure_parent_dir(file_path)
            if not success:
                log.error(f"Failed to create directory for {file_path}: {error_message}")
                return False
            
            # Convert to DataFrame if it's a dictionary
            if isinstance(data, dict):
                df = pd.DataFrame([data])
                log.debug("Converted dict to DataFrame")
            elif isinstance(data, list):
                df = pd.DataFrame(data)
                log.debug(f"Converted list of {len(data)} items to DataFrame")
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                log.error(f"Unsupported data type: {type(data)}")
                return False
                
            # Save to Parquet
            pq.write_table(pa.Table.from_pandas(df), str(file_path))
            log.debug(f"Successfully saved data to {file_path}")
            return True
        except Exception as e:
            log.error(f"Failed to save data to Parquet: {str(e)}")
            return False
            
    @staticmethod
    def load_from_parquet(file_path: PathLike) -> Optional[pd.DataFrame]:
        """Load data from a Parquet file.
        
        Args:
            file_path: Path to the Parquet file
            
        Returns:
            pd.DataFrame or None: DataFrame containing the data or None if file not found
            
        Raises:
            DataExtractionError: If loading fails
        """
        log.debug(f"Loading data from Parquet file: {file_path}")
        
        if not Paths.file_exists(file_path):
            log.debug(f"Parquet file not found: {file_path}")
            return None
            
        try:
            table = pq.read_table(str(file_path))
            df = table.to_pandas()
            log.debug(f"Successfully loaded data from {file_path} ({len(df)} rows)")
            return df
        except Exception as e:
            log.error(f"Failed to load Parquet file: {str(e)}")
            raise DataExtractionError(f"Failed to load Parquet file: {str(e)}")
            
    @staticmethod
    def append_to_parquet(data: Union[Dict, List, pd.DataFrame], file_path: PathLike) -> bool:
        """Append data to an existing Parquet file or create a new one.
        
        Args:
            data: Data to append (dict, list, or DataFrame)
            file_path: Path to the Parquet file
            
        Returns:
            bool: True if successful
        """
        log.debug(f"Appending data to Parquet file: {file_path}")
        
        # Load existing data if available
        if Paths.file_exists(file_path):
            existing_df = ParquetStorage.load_from_parquet(file_path)
            if existing_df is None:
                log.error(f"Failed to load existing file: {file_path}")
                return False
                
            # Convert new data to DataFrame
            if isinstance(data, dict):
                new_df = pd.DataFrame([data])
            elif isinstance(data, list):
                new_df = pd.DataFrame(data)
            else:
                new_df = data
                
            # Combine and save
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            log.debug(f"Combined data: {len(existing_df)} existing rows + {len(new_df)} new rows")
            return ParquetStorage.save_to_parquet(combined_df, file_path)
        
        # If file doesn't exist, create new file
        log.debug("File doesn't exist, creating new Parquet file")
        return ParquetStorage.save_to_parquet(data, file_path)

    @staticmethod
    def save_youtube_data(data: Union[Dict, List, pd.DataFrame], 
                         video_id: Optional[str] = None,
                         data_type: str = "metadata",
                         base_dir: Optional[PathLike] = None) -> str:
        """Save YouTube data to the appropriate directory.
        
        Args:
            data: Data to save
            video_id: YouTube video ID (optional)
            data_type: Type of data (metadata, captions, etc.)
            base_dir: Base directory (optional)
            
        Returns:
            str: Path to the saved file or empty string if failed
        """
        try:
            file_path = ""
            
            if data_type == "metadata" and video_id:
                file_path = str(Paths.youtube_metadata_path(base_dir, video_id))
            elif data_type == "captions" and video_id:
                captions_dir = Paths.youtube_captions_dir(base_dir)
                file_path = str(os.path.join(captions_dir, f"{video_id}.parquet"))
            elif data_type == "search":
                search_dir = Paths.youtube_search_dir(base_dir)
                query = data.get('query', 'unknown') if isinstance(data, dict) else 'unknown'
                safe_query = Paths.sanitize_filename(str(query))
                file_path = str(os.path.join(search_dir, f"search_{safe_query}.parquet"))
            elif data_type == "playlist":
                playlists_dir = Paths.youtube_playlists_dir(base_dir)
                playlist_id = data.get('playlist_id', 'unknown') if isinstance(data, dict) else 'unknown'
                file_path = str(os.path.join(playlists_dir, f"{playlist_id}.parquet"))
            else:
                # Generate timestamped path for other types
                youtube_dir = Paths.youtube_data_dir(base_dir)
                file_path = str(Paths.timestamped_path(youtube_dir, data_type, "parquet"))
                
            success = ParquetStorage.save_to_parquet(data, file_path)
            return file_path if success else ""
        except Exception as e:
            log.error(f"Failed to save YouTube data: {str(e)}")
            return ""

    @staticmethod
    def save_github_data(data: Union[Dict, List, pd.DataFrame], 
                        owner: str, 
                        repo: str,
                        base_dir: Optional[PathLike] = None) -> str:
        """Save GitHub repository data.
        
        Args:
            data: Data to save
            owner: Repository owner
            repo: Repository name
            base_dir: Base directory (optional)
            
        Returns:
            str: Path to the saved file or empty string if failed
        """
        try:
            from oarc_crawlers.config.config import Config
            if base_dir is None:
                base_dir = Config.get_instance().data_dir  # Use get_instance() method
                
            file_path = str(Paths.github_repo_data_path(base_dir, owner, repo))
            success = ParquetStorage.save_to_parquet(data, file_path)
            return file_path if success else ""
        except Exception as e:
            log.error(f"Failed to save GitHub data: {str(e)}")
            return ""

    @staticmethod
    def prepare_for_vectors(
        file_path: PathLike,
        text_columns: Union[str, Sequence[str]],
        id_column: Optional[str] = None,
        separator: str = " "
    ) -> List[Dict[str, str]]:
        """Prepare Parquet data for vector embedding.
        
        Args:
            file_path: Path to parquet file
            text_columns: Column(s) to use as text content
            id_column: Column to use as document ID
            separator: String to join multiple text columns
            
        Returns:
            List of dicts with 'text' and optional 'id' keys
        """
        df = ParquetStorage.load_from_parquet(file_path)
        if df is None:
            return []
            
        # Handle single or multiple text columns
        if isinstance(text_columns, str):
            text_columns = [text_columns]
            
        # Combine text columns
        texts = df[text_columns].fillna('').agg(separator.join, axis=1)
        
        # Prepare documents
        documents = []
        for i, text in enumerate(texts):
            doc = {'text': text}
            if id_column and id_column in df:
                doc['id'] = str(df[id_column].iloc[i])
            else:
                doc['id'] = f"doc_{i}"
            documents.append(doc)
            
        return documents