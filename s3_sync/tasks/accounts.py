from json import loads as JSONLoads
from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import has_error, log_error, logger
from s3_sync.utils.config import *

# id	username	domain	private_key	public_key	created_at	updated_at	note	display_name	uri	url	avatar_file_name	avatar_content_type	avatar_file_size	avatar_updated_at	header_file_name	header_content_type	header_file_size	header_updated_at	avatar_remote_url	locked	header_remote_url	last_webfingered_at	inbox_url	outbox_url	shared_inbox_url	followers_url	protocol	memorial	moved_to_account_id	featured_collection_url	fields	actor_type	discoverable	also_known_as	silenced_at	suspended_at	hide_collections	avatar_storage_schema_version	header_storage_schema_version	devices_url	sensitized_at	suspension_origin	trendable	reviewed_at	requested_review_at

query = f"SELECT id, avatar_file_name, avatar_content_type, avatar_remote_url, header_file_name, header_content_type, header_remote_url FROM accounts WHERE id>0 ORDER BY id {limit};"


def accounts(account: tuple, index: int, total: int):
    (
        id,
        avatar_file_name, avatar_content_type, avatar_remote_url,
        header_file_name, header_content_type, header_remote_url
    ) = account

    logger.info(f"[account] processing {id}")
    logger.info(f"[account] progress: {index+1}/{total}")

    errors = []

    try:
        if (avatar_file_name):
            is_remote_avatar = bool(avatar_remote_url)
            success, error = sync_file(
                prefix="/accounts/avatars",
                style='original',
                id=id,
                file_name=avatar_file_name,
                cached=is_remote_avatar
            )
            log_error(success, error, errors)
            if avatar_content_type not in ('image/jpeg', 'image/png'):
                success, error = sync_file(
                    prefix="/accounts/avatars",
                    style='static',
                    id=id,
                    file_name=avatar_file_name,
                    cached=is_remote_avatar
                )
                log_error(success, error, errors)
        if (header_file_name):
            is_remote_header = bool(header_remote_url)
            success, error = sync_file(
                prefix="/accounts/headers",
                style='original',
                id=id,
                file_name=header_file_name,
                cached=is_remote_header
            )
            log_error(success, error, errors)
            if header_content_type not in ('image/jpeg', 'image/png'):
                success, error = sync_file(
                    prefix="/accounts/headers",
                    style='static',
                    id=id,
                    file_name=header_file_name,
                    cached=is_remote_header
                )
                log_error(success, error, errors)

        if has_error(errors):
            raise Exception(str(errors))
        else:
            logger.info(f"[account] synced {id}")
    except Exception as e:
        logger.warning(
            f"[account] sync failed {id}", str(errors)
        )
    finally:
        if has_error(errors):
            raise Exception(('[account]', id, 'With Error', str(errors)))
        else:
            return ('[account]', id, 'OK')
