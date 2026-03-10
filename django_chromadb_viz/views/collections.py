"""Views for managing ChromaDB collections."""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from loguru import logger

from ..services import get_chromadb_service


def collection_list(request):
    """Display list of all collections."""
    try:
        service = get_chromadb_service()
        collections = service.get_collections()

        context = {
            "collections": collections,
            "title": "ChromaDB Collections",
        }
        return render(request, "django_chromadb_viz/collections/list.html", context)
    except Exception as e:
        logger.error(f"Error loading collections: {e}")
        messages.error(request, f"Error loading collections: {e}")
        return render(
            request,
            "django_chromadb_viz/error.html",
            {"error": str(e), "title": "Error"},
        )


@require_http_methods(["DELETE"])
def delete_collection(request, collection_name):
    """Delete a collection."""
    if not getattr(request, "allow_deletion", True):
        return JsonResponse(
            {"success": False, "error": "Deletion not allowed"}, status=403
        )

    try:
        service = get_chromadb_service()
        success = service.delete_collection(collection_name)

        if success:
            messages.success(
                request, f"Collection '{collection_name}' deleted successfully."
            )
            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {"success": False, "error": "Failed to delete collection"}
            )
    except Exception as e:
        logger.error(f"Error deleting collection {collection_name}: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def collection_detail(request, collection_name):
    """Display details and documents for a specific collection."""
    try:
        service = get_chromadb_service()

        # Get collection info
        collections = service.get_collections()
        collection = next(
            (c for c in collections if c["name"] == collection_name), None
        )

        if not collection:
            raise Http404(f"Collection '{collection_name}' not found")

        # Get pagination parameters
        page = request.GET.get("page", 1)
        limit = request.GET.get("limit", 20)

        try:
            page = int(page)
            limit = int(limit)
        except ValueError:
            page = 1
            limit = 20

        # Calculate offset
        offset = (page - 1) * limit

        # Get documents
        documents_result = service.get_documents(
            collection_name, limit=limit, offset=offset
        )

        # Create paginator
        paginator = Paginator(range(documents_result["total_count"]), limit)
        page_obj = paginator.get_page(page)

        context = {
            "collection": collection,
            "documents": documents_result["documents"],
            "page_obj": page_obj,
            "total_count": documents_result["total_count"],
            "has_next": documents_result["has_next"],
            "has_prev": documents_result["has_prev"],
            "current_page": page,
            "limit": limit,
            "title": f"Collection: {collection_name}",
        }
        return render(request, "django_chromadb_viz/collections/detail.html", context)
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error loading collection {collection_name}: {e}")
        messages.error(request, f"Error loading collection: {e}")
        return redirect("django_chromadb_viz:collection_list")
