"""Celery application configuration for the crawler project."""
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crawler.settings')

app = Celery('crawler')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Karachi')

app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Print the current Celery request for debugging."""
    print(f'Request: {self.request!r}')


# Restart workers after each task to prevent memory leaks;
# disable the broker connection pool for compatibility with Redis.
app.conf.update(
    worker_max_tasks_per_child=1,
    broker_pool_limit=None,
)

