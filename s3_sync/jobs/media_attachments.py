from s3_sync.services.pg import pg_query
from s3_sync.celery import media_attachments_task
from s3_sync.tasks.media_attachments import query, media_attachments

media_attachment_records = pg_query(query)

total = len(media_attachment_records)

print(f"total attachments: {total}")


for index, media_attachment in enumerate(media_attachment_records):
    result = media_attachments_task.delay(media_attachment, index, total)
    # media_attachments(media_attachment, index, total)
    # result.get()
    print(f"[attachments] added {media_attachment[0]} - {index+1}/{total}")
