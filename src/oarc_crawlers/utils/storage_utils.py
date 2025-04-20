"""
Storage utility functions for OARC crawlers.
"""
from pathlib import Path
from typing import Any, Dict, Optional, Union

from oarc_log import log
from oarc_crawlers.utils.paths import Paths, PathLike

class StorageUtils:
    """Utility methods for storage operations across all OARC crawler modules."""
    
    @staticmethod
    def convert_to_dict(obj: Any) -> Dict:
        """Convert an object to a dictionary if possible."""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return obj
        else:
            raise TypeError(f"Cannot convert {type(obj)} to dictionary")