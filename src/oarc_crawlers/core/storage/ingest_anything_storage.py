"""Storage utilities for integrating with ingest-anything.

Provides flexible ingestion of various file types into vector storage with LlamaIndex.

Usage:
    # Initialize storage
    storage = IngestAnythingStorage(
        vector_store=vector_store,
        embedding_model="text-embedding-3-small",
        data_dir="./data"
    )

    # Ingest documents (PDFs, Word docs, etc.)
    result = await storage.ingest_documents(
        files_or_dir="./docs",
        chunker="late",
        save_metadata=True
    )

    # Ingest code files
    result = await storage.ingest_code(
        files_or_dir="./src",
        language="python",
        save_metadata=True
    )

    # Ingest from parquet files
    result = await storage.ingest_from_parquet(
        parquet_file="research_papers.parquet",
        text_columns=["title", "abstract"],
        id_column="paper_id",
        chunker="semantic"
    )

All ingestion operations automatically save metadata to Parquet files for tracking
and analysis. The metadata includes timestamps, file lists, embedding model info,
and chunk counts.
"""

import os
from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime, UTC

from llama_index.core.schema import Document, BaseNode
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.vector_stores.types import VectorStore

from ingest_anything import IngestAnything, IngestCode
from ingest_anything.embeddings import ChonkieAutoEmbedding

from oarc_log import log
from oarc_utils.errors import DataExtractionError
from oarc_crawlers.utils.paths import Paths, PathLike
from oarc_crawlers.core.storage.parquet_storage import ParquetStorage


class IngestAnythingStorage:
    """Storage interface using ingest-anything for document ingestion."""

    def __init__(self, 
                 vector_store: VectorStore,
                 embedding_model: Optional[Union[BaseEmbedding, str]] = "text-embedding-3-small",
                 data_dir: Optional[PathLike] = None):
        """Initialize IngestAnything storage.
        
        Args:
            vector_store: Vector store implementation
            embedding_model: Model for generating embeddings or model name string
            data_dir: Base directory for storage
        """
        self.vector_store = vector_store
        # Initialize embedding model 
        if isinstance(embedding_model, str):
            self.embedding_model = ChonkieAutoEmbedding(embedding_model)
        elif isinstance(embedding_model, BaseEmbedding):
            self.embedding_model = embedding_model 
        else:
            self.embedding_model = ChonkieAutoEmbedding("text-embedding-3-small")
            
        self.data_dir = Path(data_dir) if data_dir else Paths.get_default_data_dir()
        
        # Initialize ingestors
        self.ingestor = IngestAnything(vector_store=vector_store)
        self.code_ingestor = IngestCode(vector_store=vector_store)

    async def ingest_documents(self, 
                             files_or_dir: Union[str, List[str]],
                             chunker: str = "late",
                             save_metadata: bool = True,
                             **kwargs) -> Dict:
        """Ingest documents using ingest-anything.
        
        Args:
            files_or_dir: Path(s) to files or directory to ingest
            chunker: Chunking strategy ("late", "token", "semantic")
            save_metadata: Whether to save ingestion metadata
            **kwargs: Additional arguments for IngestAnything
            
        Returns:
            Dict containing ingestion results and metadata
        """
        try:
            # Perform ingestion
            result = self.ingestor.ingest(
                chunker=chunker,
                files_or_dir=files_or_dir,
                embedding_model=self.embedding_model,
                **kwargs
            )
            
            if save_metadata:
                # Save ingestion metadata
                metadata = {
                    'timestamp': datetime.now(UTC).isoformat(),
                    'files': files_or_dir if isinstance(files_or_dir, list) else [files_or_dir],
                    'chunker': chunker,
                    'embedding_model': str(self.embedding_model),
                    'num_chunks': len(result.get('chunks', [])),
                    'status': 'success'
                }
                
                # Use timestamped path for metadata
                metadata_path = str(Paths.timestamped_path(
                    self.data_dir / 'ingest_metadata', 
                    'document_ingestion', 
                    'parquet'
                ))
                ParquetStorage.save_to_parquet(metadata, metadata_path)
                result['metadata_path'] = metadata_path
                
            return result

        except Exception as e:
            log.error(f"Document ingestion failed: {str(e)}")
            raise DataExtractionError(f"Failed to ingest documents: {str(e)}")

    async def ingest_code(self,
                         files_or_dir: Union[str, List[str]], 
                         language: str,
                         save_metadata: bool = True,
                         **kwargs) -> Dict:
        """Ingest code files using ingest-anything.
        
        Args:
            files_or_dir: Path(s) to code files or directory
            language: Programming language
            save_metadata: Whether to save ingestion metadata
            **kwargs: Additional arguments for IngestCode
            
        Returns:
            Dict containing ingestion results and metadata
        """
        try:
            # Perform code ingestion
            result = self.code_ingestor.ingest(
                files=files_or_dir,
                embedding_model=self.embedding_model,
                language=language,
                **kwargs
            )
            
            if save_metadata:
                # Save ingestion metadata
                metadata = {
                    'timestamp': datetime.now(UTC).isoformat(),
                    'files': files_or_dir if isinstance(files_or_dir, list) else [files_or_dir],
                    'language': language,
                    'embedding_model': str(self.embedding_model),
                    'num_chunks': len(result.get('chunks', [])),
                    'status': 'success'
                }
                
                # Use timestamped path for metadata
                metadata_path = str(Paths.timestamped_path(
                    self.data_dir / 'ingest_metadata',
                    'code_ingestion',
                    'parquet'
                ))
                ParquetStorage.save_to_parquet(metadata, metadata_path)
                result['metadata_path'] = metadata_path
                
            return result

        except Exception as e:
            log.error(f"Code ingestion failed: {str(e)}")
            raise DataExtractionError(f"Failed to ingest code: {str(e)}")

    async def ingest_from_parquet(
        self,
        parquet_file: Union[str, PathLike],
        text_columns: Union[str, Sequence[str]],
        id_column: Optional[str] = None,
        chunker: str = "late",
        save_metadata: bool = True,
        **kwargs
    ) -> Dict:
        """Ingest documents from a Parquet file into vector storage.
        
        Args:
            parquet_file: Path to parquet file
            text_columns: Column(s) containing text to embed
            id_column: Column to use as document ID
            chunker: Chunking strategy
            save_metadata: Whether to save ingestion metadata
            **kwargs: Additional arguments for ingest_documents
            
        Returns:
            Dict containing ingestion results and metadata
        """
        # Convert parquet to ingestion format
        documents = ParquetStorage.prepare_for_vectors(
            parquet_file,
            text_columns=text_columns,
            id_column=id_column
        )
        
        if not documents:
            raise DataExtractionError(f"No documents extracted from {parquet_file}")
            
        # Create a temporary directory and write documents
        temp_dir = Path(self.data_dir) / "temp_ingest"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / "docs.json"
        with open(temp_file, 'w') as f:
            json.dump(documents, f)
            
        try:
            # Ingest the documents
            result = await self.ingest_documents(
                str(temp_file),
                chunker=chunker,
                save_metadata=save_metadata,
                **kwargs
            )
            return result
        finally:
            # Cleanup
            temp_file.unlink(missing_ok=True)
            temp_dir.rmdir()
