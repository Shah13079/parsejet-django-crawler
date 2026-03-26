"""Crawler project package. Exposes the Celery app on import."""
from .cele import app as celery_app

__all__ = ('celery_app',)