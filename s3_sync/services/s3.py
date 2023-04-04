import boto3 as aws
from s3_sync.utils.config import *
from s3_sync.utils.logger import logger

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


def generate_id_partition(id: int):
    """generate id_partition

    Args:
        id (int): activity record id

    Returns:
        string: id_partition 000/001/234
    """
    # Convert the ID to a string and add leading zeros if necessary
    id_str = str(id).zfill(9)

    # Split the ID into 3 groups of 3 digits each
    groups = [id_str[i:i+3] for i in range(0, len(id_str), 3)]

    # Join the groups with slashes to create the partition path
    partition_path = '/'.join(groups)

    return partition_path


def sync_file(prefix: str, style: str, id: int, file_name: str):
    """sync s3 file from source to target

    Args:
        prefix (str): /account/avatars
        style (str): original|small
        id (int): 1
        file_name (str): 1.jpg
    """
    object_key = f"{prefix}/{generate_id_partition(id)}/{style}/{file_name}"

    data = None

    try:
        response = s3_source.get_object(
            Bucket=s3_source_bucket, Key=object_key
        )
        data = response['Body'].read()
        # s3_source.download_file(
        #     Bucket=s3_source_bucket, Key=object_key, Filename=f"{tmp_dir}/{object_key}"
        # )
    except Exception as e:
        logger.info(f"not found {object_key}")
        object_key = f"/cache{object_key}"
        try:
            response = s3_source.get_object(
                Bucket=s3_source_bucket, Key=object_key
            )
            data = response['Body'].read()
            # s3_source.download_file(
            #     Bucket=s3_source_bucket, Key=object_key, Filename=f"{tmp_dir}/{object_key}"
            # )
            logger.info(f"downloaded {object_key}`")
        except Exception as e:
            logger.error(f"download failed {object_key}")
            logger.error(e)
            return

    try:
        s3_destination.put_object(
            Bucket=s3_destination_bucket, Key=object_key, Body=data
        )
        # s3_destination.upload_file(
        #     Bucket=s3_destination_bucket, Key=object_key, Filename=f"{tmp_dir}/{object_key}"
        # )
        logger.info(f"uploaded {object_key}")
    except Exception as e:
        logger.error(f"upload failed {object_key}")
        logger.error(e)

    # clean up
    data = None


if __name__ == '__main__':
    sync_file(
        prefix="/media_attachments/files",
        style="original",
        id=104530971904218116,
        file_name="3562dcb3b25b8dd0.jpg"
    )
