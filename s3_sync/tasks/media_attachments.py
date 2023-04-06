from json import loads as JSONLoads
from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import has_error, log_error, logger
from s3_sync.utils.config import *

query = f"SELECT id, file_file_name, thumbnail_file_name, remote_url, file_meta FROM media_attachments ORDER BY id {limit};"


def media_attachments(media_attachment: tuple, index: int, total: int):
    id, file_file_name, thumbnail_file_name, remote_url, file_meta = media_attachment
    logger.info(f"[media_attachments] processing {id}")
    logger.info(f"[media_attachments] progress: {index+1}/{total}")

    errors = []

    try:
        is_remote = bool(remote_url)
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
            log_error(success, error, errors)
            if (has_small):
                success, error = sync_file(
                    prefix="/media_attachments/files",
                    style='small',
                    id=id,
                    file_name=file_file_name,
                    cached=is_remote
                )
                log_error(success, error, errors)
        if (thumbnail_file_name):
            success, error = sync_file(
                prefix="/media_attachments/thumbnails",
                style="original",
                id=id,
                file_name=thumbnail_file_name,
                cached=is_remote
            )
            log_error(success, error, errors)

        if has_error(errors):
            raise Exception(str(errors))
        else:
            logger.info(f"[media_attachments] synced {id}")
    except Exception:
        logger.warning(
            f"[media_attachments] sync with error {id}", str(errors)
        )
    finally:
        if has_error(errors):
            raise Exception(
                ('[media_attachments]', id, 'With Error', str(errors)))
        else:
            return ('[media_attachments]', id, 'OK')
