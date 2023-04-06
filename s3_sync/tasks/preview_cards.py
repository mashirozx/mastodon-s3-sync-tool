from json import loads as JSONLoads
from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import has_error, log_error, logger
from s3_sync.utils.config import *

# id	url	title	description	image_file_name	image_content_type	image_file_size	image_updated_at	type	html	author_name	author_url	provider_name	provider_url	width	height	created_at	updated_at	embed_url	image_storage_schema_version	blurhash	language	max_score	max_score_at	trendable	link_type


def query(limit: str):
    return f"SELECT id, image_file_name, image_content_type FROM preview_cards ORDER BY id {limit};"


def preview_cards(preview_card: tuple, index: int, total: int):
    (
        id,
        image_file_name, image_content_type
    ) = preview_card

    logger.info(f"[preview_card] processing {id}")
    logger.info(f"[preview_card] progress: {index+1}/{total}")

    errors = []

    try:
        if (image_file_name):
            success, error = sync_file(
                prefix="preview_cards/images",
                style='original',
                id=id,
                file_name=image_file_name,
                cached=True
            )
            log_error(success, error, errors)

        if has_error(errors):
            raise Exception(str(errors))
        else:
            logger.info(f"[preview_card] synced {id}")
    except Exception as e:
        logger.warning(
            f"[preview_card] sync failed {id}", str(errors)
        )
    finally:
        if has_error(errors):
            raise Exception(('[preview_card]', id, 'With Error', str(errors)))
        else:
            return ('[preview_card]', id, 'OK')
