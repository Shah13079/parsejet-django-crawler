release:python manage.py migrate
web: gunicorn crawler.wsgi --log-file -
celery: celery -A crawler.cele worker -l INFO
