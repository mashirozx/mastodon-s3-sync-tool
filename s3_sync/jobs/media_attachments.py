from s3_sync.services.pg import pg_query
from s3_sync.celery import media_attachments_task
from s3_sync.tasks.media_attachments import query, media_attachments

attachments = pg_query(query)

total = len(attachments)

print(f"total attachments: {total}")


for index, attachment in enumerate(attachments):
    result = media_attachments_task.delay(attachment, index, total)
    # media_attachments(attachment, index, total)
    # result.get()
    print(f"[attachments] added {attachment[0]} - {index+1}/{total}")
