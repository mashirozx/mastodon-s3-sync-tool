from json import loads as JSONLoads
from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import has_error, log_error, logger
from s3_sync.utils.config import *

# id	shortcode	domain	image_file_name	image_content_type	image_file_size	image_updated_at	created_at	updated_at	disabled	uri	image_remote_url	visible_in_picker	category_id	image_storage_schema_version

query = f"SELECT id, image_file_name, image_content_type, image_remote_url FROM custom_emojis ORDER BY id {limit};"


def custom_emojis(custom_emoji: tuple, index: int, total: int):
    (
        id,
        image_file_name, image_content_type, image_remote_url
    ) = custom_emoji

    logger.info(f"[custom_emoji] processing {id}")
    logger.info(f"[custom_emoji] progress: {index+1}/{total}")

    errors = []

    try:
        if (image_file_name):
            is_remote = bool(image_remote_url)
            success, error = sync_file(
                prefix="/custom_emojis/images",
                style='original',
                id=id,
                file_name=image_file_name,
                cached=is_remote
            )
            log_error(success, error, errors)
            if image_content_type not in ('image/jpeg', 'image/png'):
                success, error = sync_file(
                    prefix="/custom_emojis/images",
                    style='static',
                    id=id,
                    file_name=image_file_name,
                    cached=is_remote
                )
                log_error(success, error, errors)

        if has_error(errors):
            raise Exception(str(errors))
        else:
            logger.info(f"[custom_emoji] synced {id}")
    except Exception as e:
        logger.warning(
            f"[custom_emoji] sync failed {id}", str(errors)
        )
    finally:
        if has_error(errors):
            raise Exception(('[custom_emoji]', id, 'With Error', str(errors)))
        else:
            return ('[custom_emoji]', id, 'OK')
