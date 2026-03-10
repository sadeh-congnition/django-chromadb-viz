"""
Default settings for Django ChromaDB Viz.

These settings can be overridden in your Django project's settings.py.
"""

from pathlib import Path

# Default ChromaDB settings
CHROMADB_PATH = getattr(Path, "home", Path.home)() / ".chroma" / "default"
CHROMADB_HOST = "localhost"
CHROMADB_PORT = 8000

# UI Settings
CHROMADB_VIZ_ITEMS_PER_PAGE = 20
CHROMADB_VIZ_MAX_CONTENT_LENGTH = 1000  # Truncate content display

# Security settings
CHROMADB_VIZ_ALLOW_DELETION = True  # Allow deletion of collections and documents
CHROMADB_VIZ_ALLOW_MODIFICATION = True  # Allow modification of documents
