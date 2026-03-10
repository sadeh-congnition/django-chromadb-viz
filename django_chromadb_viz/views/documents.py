"""Views for managing ChromaDB documents."""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from loguru import logger

from ..services import get_chromadb_service


def document_detail(request, collection_name, document_id):
    """Display details for a specific document."""
    try:
        service = get_chromadb_service()

        # Get the document
        documents_result = service.get_documents(collection_name, limit=1000)
        document = next(
            (doc for doc in documents_result["documents"] if doc["id"] == document_id),
            None,
        )

        if not document:
            messages.error(
                request,
                f"Document '{document_id}' not found in collection '{collection_name}'",
            )
            return redirect(
                "django_chromadb_viz:collection_detail", collection_name=collection_name
            )

        # Get collection info
        collections = service.get_collections()
        collection = next(
            (c for c in collections if c["name"] == collection_name), None
        )

        context = {
            "collection": collection,
            "document": document,
            "title": f"Document: {document_id}",
        }
        return render(request, "django_chromadb_viz/documents/detail.html", context)
    except Exception as e:
        logger.error(f"Error loading document {document_id}: {e}")
        messages.error(request, f"Error loading document: {e}")
        return redirect(
            "django_chromadb_viz:collection_detail", collection_name=collection_name
        )


@require_http_methods(["DELETE"])
def delete_document(request, collection_name, document_id):
    """Delete a document from a collection."""
    if not getattr(request, "allow_deletion", True):
        return JsonResponse(
            {"success": False, "error": "Deletion not allowed"}, status=403
        )

    try:
        service = get_chromadb_service()
        success = service.delete_document(collection_name, document_id)

        if success:
            messages.success(request, f"Document '{document_id}' deleted successfully.")
            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {"success": False, "error": "Failed to delete document"}
            )
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def search_documents(request, collection_name):
    """Search documents in a collection."""
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": [], "error": "Search query is required"})

    try:
        service = get_chromadb_service()
        results = service.search_documents(collection_name, query, limit=20)

        context = {
            "results": results,
            "query": query,
            "collection_name": collection_name,
        }
        return render(
            request, "django_chromadb_viz/documents/search_results.html", context
        )
    except Exception as e:
        logger.error(f"Error searching documents in {collection_name}: {e}")
        return JsonResponse({"results": [], "error": str(e)})
