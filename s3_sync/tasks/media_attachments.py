from json import loads as JSONLoads
from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import logger
from s3_sync.utils.config import *

query = "SELECT id, file_file_name, thumbnail_file_name, remote_url, file_meta FROM media_attachments ORDER BY id LIMIT 100;"


def media_attachments(attachment: tuple, index: int, total: int):
    id, file_file_name, thumbnail_file_name, remote_url, file_meta = attachment
    logger.info(f"[media_attachments] processing {id}")
    logger.info(f"[media_attachments] progress: {index+1}/{total}")
    success = True
    error = None
    try:
        is_remote = bool(remote_url)
        # meta = file_meta[0] if file_meta else {}
        meta = file_meta if file_meta else {}
        has_small = ("small" in meta) if meta else False
        if (file_file_name):
            success, error = sync_file(
                prefix="/media_attachments/files",
                style='original',
                id=id,
                file_name=file_file_name,
                cached=is_remote
            )
            if (has_small):
                success, error = sync_file(
                    prefix="/media_attachments/files",
                    style='small',
                    id=id,
                    file_name=file_file_name,
                    cached=is_remote
                )
        if (thumbnail_file_name):
            success, error = sync_file(
                prefix="/media_attachments/thumbnails",
                style="original",
                id=id,
                file_name=thumbnail_file_name,
                cached=is_remote
            )

        if not success:
            raise Exception(error)
        else:
            logger.info(f"[media_attachments] synced {id}")
    except Exception:
        logger.critical(f"[media_attachments] sync failed {id}", str(error))
    finally:
        if not success:
            raise Exception((id, 'With Error', str(error)))
        else:
            return (id, 'OK')
