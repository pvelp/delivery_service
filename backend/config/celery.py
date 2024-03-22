from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger("celery")
logger.setLevel(logging.DEBUG)

app.autodiscover_tasks()
