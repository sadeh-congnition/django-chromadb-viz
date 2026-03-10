# Django ChromaDB Viz

A reusable Django app for visualizing and managing local ChromaDB instances. This application provides a clean, modern web interface for browsing collections, viewing documents, and managing your vector database content.

## Features

- **Collection Management**: View all ChromaDB collections with metadata and document counts
- **Document Browsing**: Browse documents within collections with pagination
- **Document Details**: View detailed information about individual documents including content, metadata, and embedding information
- **Search**: Semantic search within collections using ChromaDB's vector search capabilities
- **Interactive UI**: Modern Bootstrap 5 interface with HTMX for smooth interactions
- **Deletion Support**: Safely delete collections and individual documents
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Requirements

- Python 3.8+
- Django 4.0+
- ChromaDB 0.4.0+
- Loguru 0.7.0+

## Installation

### From PyPI (when published)

```bash
pip install django-chromadb-viz
```

### From Source

```bash
git clone https://github.com/yourusername/django-chromadb-viz.git
cd django-chromadb-viz
pip install -e .
```

## Configuration

### 1. Add to Django Settings

Add `'django_chromadb_viz'` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_chromadb_viz',
]
```

### 2. Include URLs

Include the app's URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other paths
    path('chromadb/', include('django_chromadb_viz.urls')),
]
```

### 3. Configure ChromaDB Connection

Add ChromaDB configuration to your `settings.py`:

```python
# ChromaDB settings
CHROMADB_PATH = '/path/to/your/chromadb'  # Default: ~/.chroma/default
CHROMADB_HOST = 'localhost'  # For remote connections
CHROMADB_PORT = 8000  # For remote connections

# UI Settings
CHROMADB_VIZ_ITEMS_PER_PAGE = 20  # Default: 20
CHROMADB_VIZ_MAX_CONTENT_LENGTH = 1000  # Default: 1000

# Security Settings
CHROMADB_VIZ_ALLOW_DELETION = True  # Allow deletion of collections and documents
CHROMADB_VIZ_ALLOW_MODIFICATION = True  # Allow modification of documents
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/chromadb/` to access the ChromaDB visualization interface.

## Usage

### Viewing Collections

The main page shows all collections in your ChromaDB instance:

- Collection name and ID
- Document count
- Metadata (if available)
- Actions to view or delete collections

### Browsing Documents

Click on a collection to view its documents:

- Paginated list of documents
- Content preview
- Metadata display
- Embedding dimension information
- Search functionality

### Document Details

Click on a document to see full details:

- Complete document content
- Full metadata
- Embedding information (first 10 dimensions shown)
- Actions for deletion

### Search

Use the search bar in any collection to perform semantic search:

- Natural language queries
- Vector similarity search
- Results with similarity scores

## Development

### Setting up for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/django-chromadb-viz.git
cd django-chromadb-viz

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install test dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black django_chromadb_viz/
isort django_chromadb_viz/
```

### Linting

```bash
flake8 django_chromadb_viz/
```

## Project Structure

```
django_chromadb_viz/
├── __init__.py
├── apps.py                 # Django app configuration
├── settings.py             # Default settings
├── services.py             # ChromaDB service layer
├── urls.py                # URL configuration
├── views/
│   ├── __init__.py
│   ├── collections.py      # Collection-related views
│   └── documents.py        # Document-related views
├── templates/
│   └── django_chromadb_viz/
│       ├── base.html       # Base template
│       ├── error.html      # Error page
│       ├── collections/
│       │   ├── list.html   # Collections list
│       │   └── detail.html  # Collection detail
│       └── documents/
│           ├── detail.html  # Document detail
│           └── search_results.html  # Search results
└── migrations/             # Database migrations
```

## API Reference

### Services

#### ChromaDBService

Main service class for ChromaDB operations:

```python
from django_chromadb_viz.services import get_chromadb_service

service = get_chromadb_service()
collections = service.get_collections()
documents = service.get_documents('collection_name')
```

### Views

#### Collection Views

- `collection_list`: List all collections
- `collection_detail`: Show collection details and documents
- `delete_collection`: Delete a collection (DELETE request)

#### Document Views

- `document_detail`: Show document details
- `delete_document`: Delete a document (DELETE request)
- `search_documents`: Search documents in a collection

## Security Considerations

- Deletion operations are protected by Django's built-in CSRF protection
- Configure `CHROMADB_VIZ_ALLOW_DELETION` to disable destructive operations
- Consider adding authentication/authorization for production use
- ChromaDB connection settings should be secured in production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Create an issue on GitHub for bug reports or feature requests
- Check the documentation for common questions
- Review the source code for implementation details

## Changelog

### 0.1.0

- Initial release
- Collection browsing and management
- Document viewing and search
- Bootstrap 5 UI with HTMX
- Basic deletion functionality
