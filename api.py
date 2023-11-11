"""Web API functions."""
import struct
import requests
from helpers import sanitize_tag, create_tag_filepath, create_post_filepath
from itertools import chain

def _get_post_urls(tags: list[str]) -> list[str]:
    """Retrieve the links to all of the posts that contain the tags.

    Args:
        tags: The tags that the posts must contain.

    Returns:
        A list of post urls that contain all of the specified tags.

    """
    unic_post_ids = []
    if len(tags) == 0:
        return tags
    
    sanitized_tags = [sanitize_tag(tag) for tag in tags]
    #print(sanitized_tags)
    nozomi_urls = []
    for tag in tags:
        if not tag.islower():
            nozomi_urls.append(create_tag_filepath(tag))
        #elif tag.isalpha():
        #    nozomi_urls.append(create_tag_filepath(tag))
        else:
            nozomi_urls.append(create_tag_filepath(sanitize_tag(tag)))
    #nozomi_urls  = [create_tag_filepath(sanitized_tag) for sanitized_tag in sanitized_tags]
    #print(nozomi_urls)
    tag_post_ids = [_get_post_ids(nozomi_url) for nozomi_url in nozomi_urls]
    flat_list = list(chain.from_iterable(tag_post_ids))
    #print(tag_post_ids)
    #print(len(flat_list))
    #for i in range(len(flat_list)):
    #    print(flat_list.count(flat_list[i]))
    if len(tags) == 1:
        for i in range(len(flat_list)): # artist with upper letters
            if not flat_list.count(flat_list[i]) >= 2:
                unic_post_ids.append(flat_list[i])
    else:
        for i in range(len(flat_list)): # artist with upper letters
            if not flat_list.count(flat_list[i]) >= 2:
                unic_post_ids.append(flat_list[i])
            if flat_list.count(flat_list[i]) >= 2:
                unic_post_ids.append(flat_list[i])
    #print(len(unic_post_ids))
    #tag_post_ids = set.intersection(*map(set, tag_post_ids)) # Flatten list of tuples on intersection
    if len(unic_post_ids) == 0:
        print('Нет пересечения для тегов',sanitized_tags)
    post_urls = [create_post_filepath(post_id) for post_id in unic_post_ids]

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
        print(response)
        total_ids = len(response.content) // 4  # divide by the size of uint
        print(total_ids)
        post_ids = list(struct.unpack(f'!{total_ids}I', bytearray(response.content)))
        #print(post_ids)
    except Exception as ex:
        raise ex
    return post_ids
