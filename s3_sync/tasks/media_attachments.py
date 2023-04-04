from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import logger
from s3_sync.utils.config import *


def media_attachments(attachment: tuple, index: int, total: int):
    id, file_file_name, thumbnail_file_name, processing, processing = attachment
    logger.info(f"processing {id}")
    logger.info(f"progress: {index+1}/{total}")
    try:
        if (file_file_name):
            sync_file(
                prefix="/media_attachments/files",
                style="original",
                id=id,
                file_name=file_file_name
            )
        if (thumbnail_file_name):
            sync_file(
                prefix="/media_attachments/files",
                style="small",
                id=id,
                file_name=thumbnail_file_name
            )
        logger.info(f"synced {id}")
    except Exception as e:
        logger.critical(f"sync failed {id}")
        logger.error(e)
    finally:
        pass
