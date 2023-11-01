"""Represents nozomi dataclasses."""

from typing import List, Optional
from dataclasses import dataclass, field

from nozomi.helpers import create_media_filepath


@dataclass(frozen=True)
class MediaMetaData:
    """Metadata for a media file (i.e. an Image, Video, GIF).

    Args:
        is_video (str): Whether the media is a video type.
        type (str): Filetype of the media. This may different from the url type.
        dataid (str): Hash of the media file.
        width (int): Width of the media file.
        height (int): Height of the media file.

    """

    is_video:   str
    type:       str
    dataid:     str
    imageurl:   str = field(init=False)
    width:      int
    height:     int

    def __post_init__(self):
        """Calculate fields after the object is initialized."""
        imageurl = create_media_filepath(self)
        # Set the tag without raising a FrozenClass error.
        object.__setattr__(self, 'imageurl', imageurl)


@dataclass(frozen=True)
class Tag:
    """Tag information.

    Args:
        tagurl (str): URL to the tag's HTML file.
        tag (str): Name of the tag (unsanitized).
        tagname_display (str): The display name of the tag.
        tagtype (str): The type of tag (i.e. character, artist, ...).
        count (int): The total number of posts that have the tag.
        sanitized_tag (str): An additional tag used for testing purposes.

    """

    tagurl:             str
    tag:                str
    tagname_display:    str
    tagtype:            Optional[str]
    count:              Optional[int]
    sanitized_tag:      str = field(init=False)

    def __post_init__(self):
        """Calculate fields after the object is initialized."""
        sanitized_tag = self.tagurl.split('/')[-1].split('-')[0]
        # Set the tag without raising a FrozenClass error.
        object.__setattr__(self, 'sanitized_tag', sanitized_tag)


@dataclass(frozen=True)
class Post(MediaMetaData):
    """Post information.

    Args:
        date (str): The date that the post was uploaded on.
        postid (int): The unique ID of the post.
        general (List[Tag]): A list of the general tags that describe the post.
        copyright (List[Tag]): The various series that the media is based on.
        character (List[Tag]): The characters that are featured in the post.
        artist (List[Tag]): The artists that create the media.
        imageurls (List[MediaMetaData]): The media featured in the post.

    """

    date:       str
    postid:     int
    general:    List[Tag] = field(default_factory=list)
    copyright:  List[Tag] = field(default_factory=list)
    character:  List[Tag] = field(default_factory=list)
    artist:     List[Tag] = field(default_factory=list)
    imageurls:  List[MediaMetaData] = field(default_factory=list)
