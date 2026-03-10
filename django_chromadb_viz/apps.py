"""Django app configuration for django_chromadb_viz."""

from django.apps import AppConfig


class DjangoChromadbVizConfig(AppConfig):
    """App configuration for Django ChromaDB Viz."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_chromadb_viz"
    verbose_name = "ChromaDB Visualization"

    def ready(self):
        """Initialize app when Django starts."""
        from loguru import logger

        logger.info("Django ChromaDB Viz app initialized")
