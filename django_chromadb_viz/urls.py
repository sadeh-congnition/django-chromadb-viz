"""URL configuration for django_chromadb_viz."""

from django.urls import path
from . import views

app_name = "django_chromadb_viz"

urlpatterns = [
    # Collection URLs
    path("", views.collections.collection_list, name="collection_list"),
    path(
        "collections/<str:collection_name>/",
        views.collections.collection_detail,
        name="collection_detail",
    ),
    path(
        "collections/<str:collection_name>/delete/",
        views.collections.delete_collection,
        name="delete_collection",
    ),
    # Document URLs
    path(
        "collections/<str:collection_name>/documents/<str:document_id>/",
        views.documents.document_detail,
        name="document_detail",
    ),
    path(
        "collections/<str:collection_name>/documents/<str:document_id>/delete/",
        views.documents.delete_document,
        name="delete_document",
    ),
    path(
        "collections/<str:collection_name>/search/",
        views.documents.search_documents,
        name="search_documents",
    ),
]
