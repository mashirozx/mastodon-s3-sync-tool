from s3_sync.services.pg import pg_query
from s3_sync.celery import media_attachments_task
from s3_sync.tasks.media_attachments import query, media_attachments
from s3_sync.utils.config import is_dev_mode
import signal

media_attachment_records = pg_query(query)

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
    if killed:
        print('Loop interrupted by user')
        break
    if is_dev_mode:
        print(
            f"[attachments] start {media_attachment[0]} - {index+1}/{total}")
        result = media_attachments(media_attachment, index, total)
        if (result):
            print(str(result))
        print(
            f"[attachments] {'skipped' if killed else 'done'} {media_attachment[0]} - {index+1}/{total}")
    else:
        result = media_attachments_task.delay(
            media_attachment, index, total)
        # result.get()
        print(
            f"[attachments] added {media_attachment[0]} - {index+1}/{total}")
