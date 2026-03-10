"""
ChromaDB service layer for managing collections and documents.

This module provides a high-level interface for interacting with ChromaDB
instances, abstracting away the low-level ChromaDB client operations.
"""

import importlib
from typing import Dict, List, Optional, Any
from pathlib import Path

from django.conf import settings
from loguru import logger

import chromadb
from chromadb.utils import embedding_functions


def _get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for texts using the configured embedding function.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors
    """
    embedding_function_path = getattr(settings, "CHROMADB_VIZ_EMBEDDING_FUNCTION", None)

    if not embedding_function_path:
        # Fall back to default ChromaDB embedding function
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        return default_ef(texts)

    try:
        # Load the embedding function from the path
        module_path, function_name = embedding_function_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        embedding_function = getattr(module, function_name)

        # Call the function with the texts
        embeddings = embedding_function(texts)
        logger.info(
            f"Generated embeddings for {len(texts)} texts using custom function"
        )
        return embeddings

    except Exception as e:
        logger.error(
            f"Error loading custom embedding function {embedding_function_path}: {e}"
        )
        # Fall back to default embedding function
        if embedding_functions is None:
            raise ImportError("chromadb embedding_functions not available")
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        return default_ef(texts)


class ChromaDBService:
    """Service class for ChromaDB operations."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """Initialize ChromaDB service.

        Args:
            persist_directory: Directory to persist ChromaDB data
            host: ChromaDB server host (for remote connections)
            port: ChromaDB server port (for remote connections)
        """
        if chromadb is None:
            raise ImportError(
                "chromadb is required. Install with: pip install chromadb"
            )

        self.persist_directory = persist_directory or getattr(
            settings, "CHROMADB_PATH", str(Path.home() / ".chroma" / "default")
        )
        self.host = host or getattr(settings, "CHROMADB_HOST", "localhost")
        self.port = port or getattr(settings, "CHROMADB_PORT", 8000)

        # Try to connect to local ChromaDB instance first
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            logger.info(f"Connected to local ChromaDB at {self.persist_directory}")
        except Exception as e:
            logger.warning(f"Failed to connect to local ChromaDB: {e}")
            # Try to connect to remote ChromaDB server
            try:
                self.client = chromadb.HttpClient(host=self.host, port=self.port)
                logger.info(f"Connected to remote ChromaDB at {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to connect to ChromaDB: {e}")
                raise

    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all collections in the ChromaDB instance.

        Returns:
            List of collection dictionaries with metadata
        """
        try:
            collections = self.client.list_collections()
            result = []

            for collection in collections:
                try:
                    count = collection.count()
                    metadata = collection.metadata or {}

                    result.append(
                        {
                            "id": collection.id,
                            "name": collection.name,
                            "count": count,
                            "metadata": metadata,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error getting info for collection {collection.name}: {e}"
                    )
                    result.append(
                        {
                            "id": collection.id,
                            "name": collection.name,
                            "count": 0,
                            "metadata": {},
                            "error": str(e),
                        }
                    )

            return result
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            raise

    def get_collection(self, collection_name: str):
        """Get a specific collection by name.

        Args:
            collection_name: Name of the collection

        Returns:
            ChromaDB collection object
        """
        try:
            return self.client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Error getting collection {collection_name}: {e}")
            raise

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False

    def get_documents(
        self,
        collection_name: str,
        limit: int = 20,
        offset: int = 0,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Get documents from a collection.

        Args:
            collection_name: Name of the collection
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            where: Where clause for filtering

        Returns:
            Dictionary containing documents and metadata
        """
        try:
            collection = self.get_collection(collection_name)

            # Get total count
            total_count = collection.count()

            # Get documents with pagination
            result = collection.get(
                limit=limit,
                offset=offset,
                where=where,
                include=["metadatas", "documents", "embeddings"],
            )

            documents = []
            for i in range(len(result.get("ids", []))):
                doc_id = result["ids"][i] if i < len(result["ids"]) else None
                document = (
                    result["documents"][i]
                    if i < len(result.get("documents", []))
                    else None
                )
                metadata = (
                    result["metadatas"][i]
                    if i < len(result.get("metadatas", []))
                    else {}
                )
                embedding = (
                    result["embeddings"][i]
                    if i < len(result.get("embeddings", []))
                    else None
                )

                documents.append(
                    {
                        "id": doc_id,
                        "document": document,
                        "metadata": metadata,
                        "embedding": embedding[:10].tolist()
                        if embedding is not None
                        else None,  # Show first 10 dimensions
                        "embedding_dim": len(embedding) if embedding is not None else 0,
                    }
                )

            return {
                "documents": documents,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total_count,
                "has_prev": offset > 0,
            }
        except Exception as e:
            logger.error(f"Error getting documents from {collection_name}: {e}")
            raise

    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from a collection.

        Args:
            collection_name: Name of the collection
            document_id: ID of the document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            collection.delete(ids=[document_id])
            logger.info(
                f"Deleted document {document_id} from collection {collection_name}"
            )
            return True
        except Exception as e:
            logger.error(
                f"Error deleting document {document_id} from {collection_name}: {e}"
            )
            return False

    def search_documents(
        self, collection_name: str, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents in a collection using semantic search.

        Args:
            collection_name: Name of the collection
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        try:
            collection = self.get_collection(collection_name)

            # Generate embeddings using the configured embedding function
            embeddings = _get_embeddings([query])

            results = collection.query(
                query_embeddings=embeddings,
                n_results=limit,
                include=["metadatas", "documents", "distances"],
            )

            search_results = []
            for i in range(len(results.get("ids", [])[0])):
                search_results.append(
                    {
                        "id": results["ids"][0][i]
                        if i < len(results["ids"][0])
                        else None,
                        "document": results["documents"][0][i]
                        if i < len(results["documents"][0])
                        else None,
                        "metadata": results["metadatas"][0][i]
                        if i < len(results["metadatas"][0])
                        else {},
                        "distance": results["distances"][0][i]
                        if i < len(results["distances"][0])
                        else None,
                    }
                )

            return search_results
        except Exception as e:
            logger.error(f"Error searching documents in {collection_name}: {e}")
            raise


# Global service instance (can be overridden in Django settings)
_chromadb_service = None


def get_chromadb_service() -> ChromaDBService:
    """Get the global ChromaDB service instance."""
    global _chromadb_service
    if _chromadb_service is None:
        _chromadb_service = ChromaDBService()
    return _chromadb_service
