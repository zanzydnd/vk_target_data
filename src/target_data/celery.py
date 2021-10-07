import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "target_data.settings")

app = Celery("target_data")
app.config_from_object("django_conf::settings", namespace="CELERY")
app.autodiscover_tasks(packages=["main"])
