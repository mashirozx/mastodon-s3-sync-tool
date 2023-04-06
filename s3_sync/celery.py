from celery import Celery
from s3_sync.base import NAME
from s3_sync.tasks.accounts import accounts
from s3_sync.tasks.media_attachments import media_attachments
from s3_sync.utils.config import *
from s3_sync.utils.logger import logger

app = Celery(
    app=NAME,
    broker=celery_broker,
    backend=celery_backend
)

app.conf.worker_concurrency = celery_concurrency
# app.conf.log_level = celery_log_level
# app.conf.update(
#     CELERYD_LOG_LEVEL=celery_log_level
# )


@app.task
def media_attachments_task(*args):
    return media_attachments(*args)


@app.task
def accounts_task(*args):
    return accounts(*args)
