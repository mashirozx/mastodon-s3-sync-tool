from celery import Celery
from s3_sync.base import NAME
from s3_sync.tasks.media_attachments import media_attachments
from s3_sync.utils.config import *
from s3_sync.utils.logger import logger

app = Celery(
    app=NAME,
    broker=celery_broker,
    backend=celery_backend
)

app.conf.worker_concurrency = celery_concurrency


@app.task
def media_attachments_task(*args):
    return media_attachments(*args)
