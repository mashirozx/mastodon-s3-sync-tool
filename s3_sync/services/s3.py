# TODO: use this in Python 3.10
# from mimetypes import guess_type
from magic import from_buffer
import boto3 as aws
from s3_sync.utils.config import *
from s3_sync.utils.logger import logger
from s3_sync.utils.paperclip import generate_id_partition, get_file_extension, replace_file_extension

s3_source = aws.client(
    's3',
    aws_access_key_id=s3_source_access_key,
    aws_secret_access_key=s3_source_secret_key,
    endpoint_url=s3_source_endpoint_url,
)


s3_destination = aws.client(
    's3',
    aws_access_key_id=s3_destination_access_key,
    aws_secret_access_key=s3_destination_secret_key,
    endpoint_url=s3_destination_endpoint_url,
)


def sync_file(prefix: str, style: str, id: int, file_name: str, cached: bool = False) -> tuple([bool, Exception]):
    """sync s3 file from source to target

    Args:
        prefix (str): /account/avatars
        style (str): original|small
        id (int): 1
        file_name (str): 1.jpg
    """
    object_key = f"{prefix}/{generate_id_partition(id)}/{style}/{file_name}"
    cached_object_key = f"/cache{object_key}"

    best_computed_object_key = finally_object_key = object_key if not cached else cached_object_key

    data = None

    try:
        response = s3_source.get_object(
            Bucket=s3_source_bucket, Key=finally_object_key
        )
        data = response['Body'].read()
    except Exception as e:
        logger.info(f"not found {finally_object_key}")
        print(f"not found {finally_object_key}")
        finally_object_key = cached_object_key if not cached else object_key
        try:
            response = s3_source.get_object(
                Bucket=s3_source_bucket, Key=finally_object_key
            )
            data = response['Body'].read()
            logger.info(f"downloaded {finally_object_key}`")
            print(f"downloaded {finally_object_key}`")
        except Exception as e:
            should_retry_as_png = False
            if get_file_extension(file_name) != "png":
                new_file_name = replace_file_extension(file_name, "png")
                logger.info(
                    f"retrying as png {best_computed_object_key} -> {new_file_name}"
                )
                print(
                    f"retrying as png {best_computed_object_key} -> {new_file_name}"
                )
                should_retry_as_png = True
                is_retry_as_png_succeed, e = sync_file(
                    prefix=prefix,
                    style=style,
                    id=id,
                    file_name=new_file_name,
                    cached=cached
                )
            if (should_retry_as_png and is_retry_as_png_succeed):
                logger.info(
                    f"retry as png succeed {best_computed_object_key}"
                )
                print(
                    f"retry as png succeed {best_computed_object_key}"
                )
                return (True, None)
            elif not should_retry_as_png or (should_retry_as_png and not is_retry_as_png_succeed):
                logger.error(
                    f"download failed {best_computed_object_key}", str(e)
                )
                print(
                    f"download failed {best_computed_object_key}", str(e)
                )
                return (False, e)

    try:
        # mime_type = guess_type(data)
        mime_type = from_buffer(data, mime=True) if data else 'empty'
        s3_destination.put_object(
            Bucket=s3_destination_bucket, Key=finally_object_key, Body=data,
            ContentType=mime_type if mime_type != 'empty' else None,
        )
        logger.info(f"uploaded {finally_object_key}")
        print(f"uploaded {finally_object_key}")
        return (True, None)
    except Exception as e:
        logger.error(f"upload failed {finally_object_key}", str(e))
        print(f"upload failed {finally_object_key}", str(e))
        return (False, e)


if __name__ == '__main__':
    sync_file(
        prefix="/media_attachments/files",
        style="original",
        id=104530971904218116,
        file_name="3562dcb3b25b8dd0.jpg",
        cached=False
    )
