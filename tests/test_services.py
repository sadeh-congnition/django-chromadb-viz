"""Tests for ChromaDB service layer."""

import pytest
import tempfile
import shutil
from pathlib import Path
from django.test import TestCase

from django_chromadb_viz.services import ChromaDBService, get_chromadb_service


class TestChromaDBService(TestCase):
    """Test cases for ChromaDBService."""

    def setUp(self):
        """Set up test fixtures with real local ChromaDB."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = ChromaDBService(persist_directory=self.temp_dir)
        # Create a test collection for testing
        self.test_collection = self.service.client.get_or_create_collection(
            name="test-collection", metadata={"description": "Test collection"}
        )

    def tearDown(self):
        """Clean up test data."""
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_local_client(self):
        """Test initialization with local client."""
        # Test that service initializes with real ChromaDB client
        self.assertIsNotNone(self.service.client)
        self.assertEqual(self.service.persist_directory, self.temp_dir)

    def test_init_remote_client_fallback(self):
        """Test initialization fallback to remote client."""
        # Create a service with invalid persist directory to trigger fallback
        # but mock the remote client to avoid actual network connection
        import unittest.mock

        with unittest.mock.patch("chromadb.HttpClient") as mock_http_client:
            mock_client = unittest.mock.Mock()
            mock_http_client.return_value = mock_client

            invalid_service = ChromaDBService(
                persist_directory="/invalid/path/that/does/not/exist/xyz123"
            )

            # Should create the mocked HTTP client
            self.assertIsNotNone(invalid_service.client)
            mock_http_client.assert_called_once_with(host="localhost", port=8000)

    def test_get_collections(self):
        """Test getting collections."""
        # Add some test data to the collection
        self.test_collection.add(
            ids=["doc1", "doc2"],
            documents=["Test document 1", "Test document 2"],
            metadatas=[{"type": "test"}, {"type": "test"}],
        )

        collections = self.service.get_collections()

        self.assertGreaterEqual(len(collections), 1)
        test_collection = next(
            (c for c in collections if c["name"] == "test-collection"), None
        )
        self.assertIsNotNone(test_collection)
        self.assertEqual(test_collection["count"], 2)
        self.assertEqual(
            test_collection["metadata"], {"description": "Test collection"}
        )

    def test_get_collection(self):
        """Test getting a specific collection."""
        result = self.service.get_collection("test-collection")

        self.assertIsNotNone(result)
        self.assertEqual(result.name, "test-collection")

    def test_delete_collection(self):
        """Test deleting a collection."""
        # Create a temporary collection to delete
        temp_collection = self.service.client.get_or_create_collection(
            name="temp-collection"
        )

        result = self.service.delete_collection("temp-collection")

        self.assertTrue(result)
        # Verify collection is deleted
        collections = self.service.get_collections()
        temp_exists = any(c["name"] == "temp-collection" for c in collections)
        self.assertFalse(temp_exists)

    def test_delete_collection_error(self):
        """Test deleting a collection with error."""
        # Try to delete a non-existent collection
        result = self.service.delete_collection("non-existent-collection")

        # Should return False when collection doesn't exist
        self.assertFalse(result)

    def test_get_documents(self):
        """Test getting documents from collection."""
        # Add test documents
        self.test_collection.add(
            ids=["doc1", "doc2", "doc3"],
            documents=["Content 1", "Content 2", "Content 3"],
            metadatas=[{"key": "value1"}, {"key": "value2"}, {"key": "value3"}],
        )

        result = self.service.get_documents("test-collection", limit=2, offset=0)

        self.assertEqual(len(result["documents"]), 2)
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(result["documents"][0]["id"], "doc1")
        self.assertEqual(result["documents"][0]["document"], "Content 1")
        self.assertEqual(result["documents"][0]["metadata"], {"key": "value1"})

    def test_delete_document(self):
        """Test deleting a document."""
        # Add a test document
        self.test_collection.add(
            ids=["doc-to-delete"],
            documents=["Document to delete"],
            metadatas=[{"type": "test"}],
        )

        result = self.service.delete_document("test-collection", "doc-to-delete")

        self.assertTrue(result)
        # Verify document is deleted
        documents = self.test_collection.get()
        self.assertNotIn("doc-to-delete", documents["ids"])

    def test_search_documents(self):
        """Test searching documents."""
        # Add test documents
        self.test_collection.add(
            ids=["doc1", "doc2"],
            documents=["This is about cats and pets", "This is about dogs and animals"],
            metadatas=[{"topic": "cats"}, {"topic": "dogs"}],
        )

        result = self.service.search_documents("test-collection", "cats", limit=10)

        self.assertGreater(len(result), 0)
        # Should find the document about cats
        found_cats_doc = any("cats" in doc["document"].lower() for doc in result)
        self.assertTrue(found_cats_doc)
        self.assertEqual(result[0]["id"], "doc1")


class TestGetChromadbService(TestCase):
    """Test cases for get_chromadb_service function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test data."""
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_service_singleton(self):
        """Test that get_chromadb_service returns singleton instance."""
        # Reset the global service instance
        import django_chromadb_viz.services

        django_chromadb_viz.services._chromadb_service = None

        service1 = get_chromadb_service()
        service2 = get_chromadb_service()

        self.assertIs(service1, service2)
        self.assertIsInstance(service1, ChromaDBService)
