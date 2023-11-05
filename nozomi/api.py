"""Web API functions."""
import os
import logging
import struct
import shutil
from pathlib import Path
from typing import Iterable, List
import asyncio
import requests
from dacite import from_dict

from .data import Post
from .exceptions import InvalidTagFormat, InvalidUrlFormat
from .helpers import sanitize_tag, create_tag_filepath, create_post_filepath, parse_post_id

_LOGGER = logging.getLogger(__name__)


def get_post(url: str) -> Post:
    """Retrieve a single post.

    Args:
        url: The URL of the post to retrieve.

    Returns:
        Post metadata information.

    """
    _LOGGER.debug('Retrieving a post from URL "%s"', url)
    try:
        post_id = parse_post_id(url)
        post_url = create_post_filepath(post_id)
        post_data = requests.get(post_url).json()
        _LOGGER.debug(post_data)
        return from_dict(data_class=Post, data=post_data)
    except InvalidUrlFormat:
        raise
    except Exception as ex:
        _LOGGER.exception(ex)
        raise


def get_posts(urls: List[str]) -> Iterable[Post]:
    """Retrieves multiple posts.

    Args:
        urls: The URLs of the posts to retrieve.

    Yields:
        Post metadata information.
 
    """
    for url in urls:
        yield get_post(url)


def get_posts_with_tags(positive_tags: List[str], negative_tags: List[str] = None, extra_tags: List[str] = None) -> Iterable[Post]:
    """Retrieve all post data that contains and doesn't contain certain tags.

    Args:
        positive_tags: The tags that the posts retrieved must contain.
        negative_tags: Optional, blacklisted tags.

    Yields:
        A post in JSON format, which contains the positive tags and doesn't contain the negative
        tags.

    """
    if negative_tags is None:
        negative_tags = list()
    if extra_tags is None:
        extra_tags = list()
    _LOGGER.debug('Retrieving posts with positive_tags=%s and negative_tags=%s and extra_tags=%s',
                  str(positive_tags), str(negative_tags), str(extra_tags))
    try:
        positive_post_urls = _get_post_urls(positive_tags)
        negative_post_urls = _get_post_urls(negative_tags)
        extra_post_urls = _get_post_urls(extra_tags)
        #relevant_post_urls = [x for x in positive_post_urls if x not in negative_post_urls]
        relevant_post_urls = set(positive_post_urls + list(set(extra_post_urls) - set(positive_post_urls))) - set(negative_post_urls)
        #relevant_post_urls = set(positive_post_urls) - set(negative_post_urls)

        for post_url in relevant_post_urls:
            post_data = requests.get(post_url).json()
            _LOGGER.debug(post_data)
            yield from_dict(data_class=Post, data=post_data)
    except InvalidTagFormat:
        raise
    except Exception as ex:
        _LOGGER.exception(ex)
        raise


async def download_media(post: Post, filepath: Path) -> List[str]:
    """Download all media on a post and save it.

    Args:
        post: The post to download.
        filepath: The file directory to save the media. The directory will be created if it doesn't
            already exist.

    Returns:
        The names of the images downloaded.

    """
    images_downloaded = []
    filepath.mkdir(parents=True, exist_ok=True)
    #print("Мы внутри downloadmedia")
    for media_meta_data in post.imageurls:
        filename = f'{media_meta_data.dataid}.{media_meta_data.type}'
        image_filepath = filepath.joinpath(filename)
        #tasks = [asyncio.create_task(_download_media(media_meta_data.imageurl, image_filepath))]
        #done, pending = await asyncio.wait(tasks)
        #for task in done:
        #   result = task.result()
        #coros = [_download_media(media_meta_data.imageurl, image_filepath)]
        #results = await asyncio.gather(*coros, return_exceptions=True)
        await _download_media(media_meta_data.imageurl, image_filepath)
        images_downloaded.append(filename)
    #print("Мы закончили downloadmedia")
    return images_downloaded


async def _download_media(image_url: str, filepath: Path):
    """Download an image and save it.

    Args:
        image_url: The image URL.
        filepath: The file directory to save the media. The directory will be created if it doesn't
            already exist.

    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://nozomi.la/',
        'Upgrade-Insecure-Requests': '1'
    }
    if os.path.exists(filepath):
        print('File already exists', filepath)
    else:
        print('File not exists %s', filepath)
        with requests.get(image_url, stream=True, headers=headers) as r:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        _LOGGER.debug('Image downloaded %s', filepath)
        print('File downloaded ', filepath)


def _get_post_urls(tags: List[str]) -> List[str]:
    """Retrieve the links to all of the posts that contain the tags.

    Args:
        tags: The tags that the posts must contain.

    Returns:
        A list of post urls that contain all of the specified tags.

    """
    if len(tags) == 0:
        return tags
    _LOGGER.debug('Retrieving all URLs that contain the tags %s', str(tags))
    sanitized_tags = [sanitize_tag(tag) for tag in tags]
    nozomi_urls  = [create_tag_filepath(sanitized_tag) for sanitized_tag in sanitized_tags]
    tag_post_ids = [_get_post_ids(nozomi_url) for nozomi_url in nozomi_urls]
    tag_post_ids = set.intersection(*map(set, tag_post_ids)) # Flatten list of tuples on intersection
    post_urls = [create_post_filepath(post_id) for post_id in tag_post_ids]
    _LOGGER.debug('Got %d post urls containing the tags %s', len(tags), str(tags))
    return post_urls


def _get_post_ids(tag_filepath_url: str) -> List[int]:
    """Retrieve the .nozomi data file.

    Args:
        tag_filepath_url: The URL to a tag's .nozomi file.

    Returns:
        A list containing all of the post IDs that contain the tag.

    """
    post_ids = []

    _LOGGER.debug('Getting post IDs from %s', tag_filepath_url)
    try:
        headers = {'Accept-Encoding': 'gzip, deflate, br', 'Content-Type': 'arraybuffer'}
        response = requests.get(tag_filepath_url, headers=headers)
        _LOGGER.debug('RESPONSE: %s', response)
        total_ids = len(response.content) // 4  # divide by the size of uint
        _LOGGER.info('Unpacking .nozomi file... Expecting %d post ids.', total_ids)
        post_ids = list(struct.unpack(f'!{total_ids}I', bytearray(response.content)))
        _LOGGER.debug('Unpacked data... Got %d total post ids! %s', len(post_ids), str(post_ids))
    except Exception as ex:
        _LOGGER.exception(ex)
    return post_ids
