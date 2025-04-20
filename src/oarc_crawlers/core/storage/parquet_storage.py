"""
Storage utilities for saving and loading data in Parquet format.

Author: @BorcherdingL, RawsonK
Date: 4/18/2025
"""
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from oarc_log import log
from oarc_utils.errors import ResourceNotFoundError

class ParquetStorage:
    """"Utility class for saving and loading data in Parquet format."""
    
    @staticmethod
    def save_to_parquet(data, file_path):
        """Save data to a Parquet file.
        
        Args:
            data: Data to save (dict, list, or DataFrame)
            file_path (str): Path to save the Parquet file
            
        Returns:
            bool: True if successful
            
        Raises:
            DataExtractionError: If saving fails
        """
        log.debug(f"Saving data to Parquet file: {file_path}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Convert to DataFrame if it's a dictionary
        if isinstance(data, dict):
            df = pd.DataFrame([data])
            log.debug("Converted dict to DataFrame")
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            log.debug(f"Converted list of {len(data)} items to DataFrame")
        else:
            df = data
            
        # Save to Parquet
        pq.write_table(pa.Table.from_pandas(df), file_path)
        log.debug(f"Successfully saved data to {file_path}")
        return True
            
    @staticmethod
    def load_from_parquet(file_path):
        """Load data from a Parquet file.
        
        Args:
            file_path (str): Path to the Parquet file
            
        Returns:
            pd.DataFrame: DataFrame containing the data
            
        Raises:
            ResourceNotFoundError: If file not found
            DataExtractionError: If loading fails
        """
        log.debug(f"Loading data from Parquet file: {file_path}")
        
        if not os.path.exists(file_path):
            log.debug(f"Parquet file not found: {file_path}")
            raise ResourceNotFoundError(f"Parquet file not found: {file_path}")
            
        table = pq.read_table(file_path)
        df = table.to_pandas()
        log.debug(f"Successfully loaded data from {file_path} ({len(df)} rows)")
        return df
            
    @staticmethod
    def append_to_parquet(data, file_path):
        """Append data to an existing Parquet file or create a new one.
        
        Args:
            data: Data to append (dict, list, or DataFrame)
            file_path (str): Path to the Parquet file
            
        Returns:
            bool: True if successful
            
        Raises:
            DataExtractionError: If appending fails
        """
        log.debug(f"Appending data to Parquet file: {file_path}")
        
        # Load existing data if available
        if os.path.exists(file_path):
            existing_df = ParquetStorage.load_from_parquet(file_path)
            
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