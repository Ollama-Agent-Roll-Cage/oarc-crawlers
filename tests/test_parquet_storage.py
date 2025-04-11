import os
import tempfile
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path to import modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.parquet_storage import ParquetStorage

class TestParquetStorage(unittest.TestCase):
    """Test the ParquetStorage class functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, 'test.parquet')
        
        # Test data
        self.test_dict = {
            'name': 'Test Name', 
            'value': 123,
            'list': [1, 2, 3],
            'timestamp': '2025-04-10T12:00:00Z'
        }
        
        self.test_list = [
            {'name': 'Test1', 'value': 123},
            {'name': 'Test2', 'value': 456}
        ]
        
        self.test_df = pd.DataFrame({
            'col1': ['a', 'b', 'c'],
            'col2': [1, 2, 3]
        })
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_save_dict_to_parquet(self):
        """Test saving a dictionary to a parquet file."""
        result = ParquetStorage.save_to_parquet(self.test_dict, self.test_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Verify data was saved correctly
        loaded_df = pd.read_parquet(self.test_file)
        self.assertEqual(loaded_df.shape[0], 1)
        self.assertEqual(loaded_df['name'][0], 'Test Name')
        self.assertEqual(loaded_df['value'][0], 123)
    
    def test_save_list_to_parquet(self):
        """Test saving a list of dictionaries to a parquet file."""
        result = ParquetStorage.save_to_parquet(self.test_list, self.test_file)
        self.assertTrue(result)
        
        # Verify data
        loaded_df = pd.read_parquet(self.test_file)
        self.assertEqual(loaded_df.shape[0], 2)
        self.assertEqual(loaded_df['name'][0], 'Test1')
        self.assertEqual(loaded_df['name'][1], 'Test2')
    
    def test_save_dataframe_to_parquet(self):
        """Test saving a DataFrame to a parquet file."""
        result = ParquetStorage.save_to_parquet(self.test_df, self.test_file)
        self.assertTrue(result)
        
        # Verify data
        loaded_df = pd.read_parquet(self.test_file)
        self.assertEqual(loaded_df.shape, (3, 2))
        self.assertTrue((loaded_df['col1'] == ['a', 'b', 'c']).all())
    
    def test_load_from_parquet(self):
        """Test loading data from a parquet file."""
        # First save some data
        ParquetStorage.save_to_parquet(self.test_dict, self.test_file)
        
        # Load it back
        loaded_df = ParquetStorage.load_from_parquet(self.test_file)
        self.assertIsInstance(loaded_df, pd.DataFrame)
        self.assertEqual(loaded_df['name'][0], 'Test Name')
    
    def test_load_nonexistent_file(self):
        """Test loading from a non-existent file."""
        result = ParquetStorage.load_from_parquet('does_not_exist.parquet')
        self.assertIsNone(result)
    
    def test_append_to_parquet(self):
        """Test appending data to an existing parquet file."""
        # First save initial data
        ParquetStorage.save_to_parquet(self.test_list[0], self.test_file)
        
        # Now append more data
        result = ParquetStorage.append_to_parquet(self.test_list[1], self.test_file)
        self.assertTrue(result)
        
        # Verify the combined data
        loaded_df = pd.read_parquet(self.test_file)
        self.assertEqual(loaded_df.shape[0], 2)
        self.assertEqual(loaded_df['name'].tolist(), ['Test1', 'Test2'])
        
    def test_error_handling(self):
        """Test error handling when saving to an invalid location."""
        # Try to save to an invalid path
        invalid_path = '/invalid/path/test.parquet'
        result = ParquetStorage.save_to_parquet(self.test_dict, invalid_path)
        self.assertFalse(result)