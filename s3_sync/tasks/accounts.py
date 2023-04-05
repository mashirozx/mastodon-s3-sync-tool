from json import loads as JSONLoads
from s3_sync.services.s3 import sync_file
from s3_sync.utils.logger import logger
from s3_sync.utils.config import *

# id	username	domain	private_key	public_key	created_at	updated_at	note	display_name	uri	url	avatar_file_name	avatar_content_type	avatar_file_size	avatar_updated_at	header_file_name	header_content_type	header_file_size	header_updated_at	avatar_remote_url	locked	header_remote_url	last_webfingered_at	inbox_url	outbox_url	shared_inbox_url	followers_url	protocol	memorial	moved_to_account_id	featured_collection_url	fields	actor_type	discoverable	also_known_as	silenced_at	suspended_at	hide_collections	avatar_storage_schema_version	header_storage_schema_version	devices_url	sensitized_at	suspension_origin	trendable	reviewed_at	requested_review_at

query = "SELECT id, avatar_file_name, avatar_content_type, avatar_remote_url, header_file_name, header_content_type, header_remote_url FROM accounts ORDER BY id LIMIT 100;"


# {"original":{"width":1291,"height":1269,"size":"1291x1269","aspect":1.0173364854215918},"small":{"width":403,"height":396,"size":"403x396","aspect":1.0176767676767677}}


def accounts(account: tuple, index: int, total: int):
    (
        id,
        avatar_file_name, avatar_content_type, avatar_remote_url,
        header_file_name, header_content_type, header_remote_url
    ) = account
    logger.info(f"[account] processing {id}")
    logger.info(f"[account] progress: {index+1}/{total}")
    try:
        if (avatar_file_name):
            is_remote_avatar = bool(avatar_remote_url)
            sync_file(
                prefix="/accounts/avatars",
                style='original',
                id=id,
                file_name=avatar_file_name,
                cached=is_remote_avatar
            )
            if avatar_content_type not in ('image/jpeg', 'image/png'):
                sync_file(
                    prefix="/accounts/avatars",
                    style='static',
                    id=id,
                    file_name=avatar_file_name,
                    cached=is_remote_avatar
                )
        if (header_file_name):
            is_remote_header = bool(header_remote_url)
            sync_file(
                prefix="/accounts/headers",
                style='original',
                id=id,
                file_name=header_file_name,
                cached=is_remote_header
            )
            if header_content_type not in ('image/jpeg', 'image/png'):
                sync_file(
                    prefix="/accounts/headers",
                    style='static',
                    id=id,
                    file_name=header_file_name,
                    cached=is_remote_header
                )
        logger.info(f"[account] synced {id}")
    except Exception as e:
        logger.critical(f"[account] sync failed {id}")
        logger.error(e)
    finally:
        return id
