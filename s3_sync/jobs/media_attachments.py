from s3_sync.services.pg import pg_query
from s3_sync.celery import media_attachments_task

query = "SELECT id, file_file_name, thumbnail_file_name, processing, processing FROM media_attachments ORDER BY id LIMIT 100;"

attachments = pg_query(query)

total = len(attachments)

print(f"total attachments: {total}")


for index, attachment in enumerate(attachments):
    result = media_attachments_task.delay(attachment, index, total)
    # result.get()
    print(f"added {attachment[0]} - {index+1}/{total}")
