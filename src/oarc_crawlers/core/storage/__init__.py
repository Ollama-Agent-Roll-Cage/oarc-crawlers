"""OARC-Crawlers storage package.

This package provides storage solutions for crawler data.
"""

from .parquet_storage import ParquetStorage

__all__ = ["ParquetStorage"]
