"""OARC-Crawlers storage package.

This package provides storage solutions for crawler data.
"""

from .parquet_storage import ParquetStorage
from .ingest_anything_storage import IngestAnythingStorage

__all__ = ["ParquetStorage", "IngestAnythingStorage"]
