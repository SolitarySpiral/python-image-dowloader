"""Helper functions for creating paths and input normalization.

Primarily used by the nozomi API functions for generating the appropriate paths to files, and
ensuring that queries are made in a particular format used by the website.

If this package grows more complex, the functionality can be divided in a more manner. Due to
the simplicity of the current API, there isn't really a point right now.

"""

import re
from typing import ForwardRef

from exceptions import InvalidTagFormat, InvalidUrlFormat


# Prevent circular dependency issues
MediaMetaData = ForwardRef("MediaMetaData")


def sanitize_tag(tag: str) -> str:
    """Remove and replace any invalid characters in the tag.

    Args:
        tag: The search tag.

    Raises:
        InvalidTagFormat: If the tag was not sanitized properly.

    Returns:
        A tag in a valid format.

    """
    try:
        '''
        sanitized_tag = tag
        if not 'artist:' in sanitized_tag:
            sanitized_tag = tag.lower().strip()
            sanitized_tag = re.sub('[/#%]', '', sanitized_tag)
            _validate_tag_sanitized(sanitized_tag)
        '''
        sanitized_tag = tag.lower().strip()
        sanitized_tag = re.sub('[/#%]', '', sanitized_tag)
        _validate_tag_sanitized(sanitized_tag)
    except InvalidTagFormat as tf:
        raise tf
    except Exception as ex:
        raise ex
    return sanitized_tag


def parse_post_id(url: str) -> int:
    """Parse the post ID.

    Args:
        url: The URL of the post ID.

    Raises:
        InvalidUrlFormat: If the URL cannot be parsed because it is not a valid format.

    Returns:
        The ID of the post.

    """
    try:
        post_id = re.search(r"post\/([\s\S]*?)\.html", url).group(1)
        post_id = int(post_id)
    except AttributeError:
        raise InvalidUrlFormat('The provided URL %s could not be parsed.', url)
    except Exception as ex:
        raise ex
    return post_id


def create_media_filepath(media: MediaMetaData) -> str:
    """Build the path to media on the site.

    Args:
        media: The media on a post.

    Returns:
        The URL of the a post's media.

    """
    if media.is_video:
        subdomain = 'v'
        url_type = media.type
    elif media.type == 'gif':
        subdomain = 'g'
        url_type = 'gif'
    else:
        subdomain = 'w'
        url_type = 'webp'
    path = _calculate_post_filepath(media.dataid)
    url_fmt = 'https://{subdomain}.nozomi.la/{hashed_path}.{url_type}'
    url = url_fmt.format(subdomain=subdomain, hashed_path=path, url_type=url_type)
    return url


def create_tag_filepath(sanitized_tag: str) -> str:
    """Build the path to a .nozomi file for a particular tag.

    Every search tag/term has an associated .nozomi file stored in the database. Each file contains
    references to data that is related to the tag. This function builds the path to that file.

    Args:
        sanitized_tag: The sanitized search tag.

    Raises:
        InvalidTagFormat: If the tag was not sanitized before creating a tag filepath.

    Returns:
        The URL of the search tag's associated .nozomi file.

    """
    try:
        _validate_tag_sanitized(sanitized_tag)
        encoded_tag = _encode_tag(sanitized_tag)
    except InvalidTagFormat:
        raise InvalidTagFormat('Tag must be sanitized before creating a filepath.')
    except Exception as ex:
        raise ex
    return f"https://j.nozomi.la/nozomi/{encoded_tag}.nozomi"


def create_post_filepath(post_id: int) -> str:
    """Build the path to a post's JSON file.

    The rules for creating the filepath can be found in the site's javascript file. They appear to
    be arbitrary decisions. The JSON file for the post contains a variety of useful data including
    image data, tags, etc.

    Args:
        post_id: The ID of a post on the website.

    Returns:
        The URL of the post's associated JSON file.

    """
    post_id = str(post_id)
    path = _calculate_post_filepath(post_id)
    return f'https://j.nozomi.la/post/{path}.json'


def _calculate_post_filepath(id: str) -> str:
    """Calculate the filepath for data on a post.

    Args:
        id: Hash of a media file or the post id.

    Returns:
        The URL path of a post's associated file.

    """
    if len(id) < 3:
        path = id
    else:
        path = re.sub('^.*(..)(.)$', r'\g<2>/\g<1>/' + id, id)
    return path


def _validate_tag_sanitized(tag: str) -> None:
    """Validate a search tag is sanitized properly.

    Args:
        tag: The search tag.

    Raises:
        InvalidTagFormat: If the tag is an empty string or begins with an invalid character.

    """
    if not tag:
        raise InvalidTagFormat(f"The tag '{tag}' is invalid. Cannot be empty.")
    if tag[0] == '-':
        raise InvalidTagFormat(f"The tag '{tag}' is invalid. Cannot begin with character '-'")


def _encode_tag(sanitized_tag: str) -> str:
    """Encode a sanitized tag using Nozomi's custom urlencoder.

    Args:
        sanitized_tag: The sanitized search tag.

    Returns:
        The encoded sanitized search tag.

    """
    convert_char_to_hex = lambda c: f"%{format(ord(c.group(0)), 'x')}"
    encoded_tag = re.sub('[;/?:@=&]', convert_char_to_hex, sanitized_tag)
    return encoded_tag
