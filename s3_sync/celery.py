from celery import Celery
from s3_sync.base import NAME
from s3_sync.tasks.accounts import accounts
from s3_sync.tasks.custom_emojis import custom_emojis
from s3_sync.tasks.media_attachments import media_attachments
from s3_sync.tasks.preview_cards import preview_cards
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


@app.task
def accounts_task(*args):
    return accounts(*args)


@app.task
def custom_emojis_task(*args):
    return custom_emojis(*args)


@app.task
def preview_cards_task(*args):
    return preview_cards(*args)
