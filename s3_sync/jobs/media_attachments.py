from s3_sync.services.pg import pg_query
from s3_sync.celery import media_attachments_task
from s3_sync.tasks.media_attachments import query, media_attachments
from s3_sync.utils.job_config import *
import signal

media_attachment_records = pg_query(query(limit))

total = len(media_attachment_records)

print(f"total attachments: {total}")

killed = False


def handler(signum, frame):
    global killed
    print("\nSignal handler called with signal", signum)
    killed = True
    exit(130)


signal.signal(signal.SIGINT, handler)

for index, media_attachment in enumerate(media_attachment_records):
    id, file_file_name, thumbnail_file_name, remote_url, file_meta = media_attachment

    if killed:
        print('Loop interrupted by user')
        break
    if file_file_name == None and thumbnail_file_name == None:
        print(
            f"[media_attachments] skipped {id} - {index+1}/{total}")
        continue
    if is_dev_mode:
        print(
            f"[attachments] start {id} - {index+1}/{total}")
        result = media_attachments(media_attachment, index, total)
        if (result):
            print(str(result))
        print(
            f"[attachments] {'skipped' if killed else 'done'} {id} - {index+1}/{total}")
    else:
        result = media_attachments_task.delay(
            media_attachment, index, total)
        # result.get()
        print(
            f"[attachments] added {id} - {index+1}/{total}")
