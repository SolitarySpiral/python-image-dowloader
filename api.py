"""Web API functions."""
import struct
import requests
from helpers import sanitize_tag, create_tag_filepath, create_post_filepath

def _get_post_urls(tags: list[str]) -> list[str]:
    """Retrieve the links to all of the posts that contain the tags.

    Args:
        tags: The tags that the posts must contain.

    Returns:
        A list of post urls that contain all of the specified tags.

    """
    if len(tags) == 0:
        return tags
    sanitized_tags = [sanitize_tag(tag) for tag in tags]
    #print(sanitized_tags)
    nozomi_urls  = [create_tag_filepath(sanitized_tag) for sanitized_tag in sanitized_tags]
    #print(nozomi_urls)
    tag_post_ids = [_get_post_ids(nozomi_url) for nozomi_url in nozomi_urls]
    #print(tag_post_ids)
    tag_post_ids = set.intersection(*map(set, tag_post_ids)) # Flatten list of tuples on intersection
    if len(tag_post_ids) == 0:
        print('Нет пересечения для тегов',sanitized_tags)
    post_urls = [create_post_filepath(post_id) for post_id in tag_post_ids]

    return post_urls


def _get_post_ids(tag_filepath_url: str) -> list[int]:
    """Retrieve the .nozomi data file.

    Args:
        tag_filepath_url: The URL to a tag's .nozomi file.

    Returns:
        A list containing all of the post IDs that contain the tag.

    """
    post_ids = []

    try:
        headers = {'Accept-Encoding': 'gzip, deflate, br', 'Content-Type': 'arraybuffer'}
        response = requests.get(tag_filepath_url, headers=headers)
        total_ids = len(response.content) // 4  # divide by the size of uint
        post_ids = list(struct.unpack(f'!{total_ids}I', bytearray(response.content)))
    except Exception as ex:
        raise ex
    return post_ids
