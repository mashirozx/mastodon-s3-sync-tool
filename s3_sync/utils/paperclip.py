import os


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


def replace_file_extension(file_name: str, new_extension: str):
    """replace file extension

    Args:
        file_name (str): 1.jpg
        new_extension (str): png

    Returns:
        string: 1.png
    """
    name, extension = os.path.splitext(file_name)
    return f"{name}.{new_extension}"


def get_file_extension(file_name: str):
    """get file extension

    Args:
        file_name (str): 1.jpg

    Returns:
        string: jpg
    """
    name, extension = os.path.splitext(file_name)
    return extension[1:]
