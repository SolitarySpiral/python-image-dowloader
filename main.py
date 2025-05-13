import os
import re
import math
import time
import logging

import aiohttp.client_exceptions
from pytils import numeral
from datetime import datetime
from dacite import from_dict

# for Utils
import hashlib
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# for nozomi getting posts
import requests
import struct
from itertools import chain

# for r34
from bs4 import BeautifulSoup
from post import r34Post

# for downloading
import aiohttp
import asyncio
import aiofiles
from tqdm.asyncio import tqdm

# getting tags from multilist
from multi import get_multi


"""Represents nozomi dataclasses."""
from typing import List, Optional, ForwardRef
from dataclasses import dataclass, field

class NozomiException(Exception):
    """Base Nozomi package exception."""
class InvalidTagFormat(NozomiException):
    """The tag is not in valid format (i.e. empty string)."""
class InvalidUrlFormat(NozomiException):
    """The url is not in valid format."""

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
        imageurl = utils.create_media_filepath(self)
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
    postid:     int
    date:       Optional [str] #= field(default_factory='1990-01-01 00:00:00-00')
    
    general:    List[Tag] = field(default_factory=list)
    copyright:  List[Tag] = field(default_factory=list)
    character:  List[Tag] = field(default_factory=list)
    artist:     List[Tag] = field(default_factory=list)
    imageurls:  List[MediaMetaData] = field(default_factory=list)


"""Main section"""
BASE_DIR = Path('D:/ghd/').resolve()
DOWNLOADS_DIR = BASE_DIR.joinpath("img") #'D:/ghd/img/'
HEADERS_NOZOMI = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://nozomi.la/",
    "Upgrade-Insecure-Requests": "1",
}
HEADERS_R34 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://wimg.rule34.xxx/",
    "Upgrade-Insecure-Requests": "1",
}

logging.basicConfig(
    format='%(asctime)s - %(message)s',datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO
)

logger = logging.getLogger("api_logger")
#logger.disabled = True

loop = asyncio.get_event_loop()


class Utils:
    def create_dir(self, dir_path: Path):
        if not dir_path.exists():
            dir_path.mkdir()

    def remove_dir(self, dir_path: Path):
        if dir_path.exists():
            dir_path.rmdir()
#---
    def handle_photo_processing(self, photos, photos_path, duplicateflag):
        if duplicateflag:
            logging.info("Check for duplicates")
            duplicates_count = self._check_for_duplicates(photos_path)
            logging.info(f"Duplicates removed: {duplicates_count}")
            logging.info(f"Total downloaded: {len(photos) - duplicates_count} photo")
        else:
            logging.info(f"Total downloaded: {len(photos)} photo")

    def _check_for_duplicates(self, path: Path) -> int:
        """Checks files under the given directory path for duplicates and removes them."""
        hashes_by_size = defaultdict(list)  
        hashes_on_1k = defaultdict(list) 

        hashes_full = {}

        files = list(path.glob("*.*"))

        # Populate hashes_by_size
        for file_path in files:
            file_size = file_path.stat().st_size
            hashes_by_size[file_size].append(file_path)

        # Find potential duplicates based on 1K hash.
        def hash_first_1k(file_path):
            small_hash = self._get_hash(file_path, first_chunk_only=True)
            if small_hash:
                file_size = file_path.stat().st_size
                hashes_on_1k[(small_hash, file_size)].append(file_path)

        with ThreadPoolExecutor() as executor:
            executor.map(hash_first_1k, [fp for flist in hashes_by_size.values() for fp in flist if len(flist) > 1])

        # Check full file hash for actual duplicates
        duplicates = []

        def check_full_hash(file_path):
            """ Check full hash (if applicable) and identify duplicates. """
            full_hash = self.get_hash(file_path)
            if full_hash:
                if full_hash in hashes_full:
                    duplicates.append(file_path)
                else:
                    hashes_full[full_hash] = file_path

        files_with_same_1k = [fp for flist in hashes_on_1k.values() for fp in flist if len(flist) > 1]
        with ThreadPoolExecutor() as executor:
            executor.map(check_full_hash, files_with_same_1k)

        # Delete duplicated files
        for file in duplicates:
            file.unlink()

        return len(duplicates)

    def _get_hash(self, filename: Path, first_chunk_only=False, hash_algo=hashlib.sha256):
        hashobj = hash_algo()
        with open(filename, "rb") as file_object:
            if first_chunk_only:
                hashobj.update(file_object.read(1024))
            else:
                # Reading in chunks to handle large files
                for chunk in iter(lambda: file_object.read(4096), b''):
                    hashobj.update(chunk)
            return hashobj.hexdigest()
#---
    def sanitize_tag(self, tag: str) -> str:
        """Remove and replace any invalid characters in the tag.

        Args:
            tag: The search tag.

        Raises:
            InvalidTagFormat: If the tag was not sanitized properly.

        Returns:
            A tag in a valid format.

        """
        try:
            sanitized_tag = tag.lower().strip()
            sanitized_tag = re.sub("[/#%]", "", sanitized_tag)
            self._validate_tag_sanitized(sanitized_tag)
        except InvalidTagFormat as tf:
            raise tf
        except Exception as ex:
            raise ex
        return sanitized_tag
    
    def _validate_tag_sanitized(self, tag: str) -> None:
        """Validate a search tag is sanitized properly.

        Args:
            tag: The search tag.

        Raises:
            InvalidTagFormat: If the tag is an empty string or begins with an invalid character.

        """
        if not tag:
            raise InvalidTagFormat(f"The tag '{tag}' is invalid. Cannot be empty.")
        if tag[0] == "-":
            raise InvalidTagFormat(
                f"The tag '{tag}' is invalid. Cannot begin with character '-'"
            )
#---
    def create_media_filepath(self, media: MediaMetaData) -> str:  # type: ignore
        """Build the path to media on the site.

        Args:
            media: The media on a post.

        Returns:
            The URL of the a post's media.

        """
        if media.is_video:
            subdomain = "v"
            url_type = media.type
        elif media.type == "gif":
            subdomain = "g"
            url_type = "gif"
        else:
            subdomain = "w"
            url_type = "webp"
        path = self._calculate_post_filepath(media.dataid)
        url_fmt = "https://{subdomain}.nozomi.la/{hashed_path}.{url_type}"
        url = url_fmt.format(subdomain=subdomain, hashed_path=path, url_type=url_type)
        return url

    def _calculate_post_filepath(self, id: str) -> str:
        """Calculate the filepath for data on a post.

        Args:
            id: Hash of a media file or the post id.

        Returns:
            The URL path of a post's associated file.

        """
        if len(id) < 3:
            path = id
        else:
            path = re.sub("^.*(..)(.)$", r"\g<2>/\g<1>/" + id, id)
        return path

    def create_post_filepath(self, post_id: int) -> str:
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
        path = self._calculate_post_filepath(post_id)
        return f"https://j.nozomi.la/post/{path}.json"
#---
    def create_tag_filepath(self, sanitized_tag: str) -> str:
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
            self._validate_tag_sanitized(sanitized_tag)
            encoded_tag = self._encode_tag(sanitized_tag)
        except InvalidTagFormat:
            raise InvalidTagFormat("Tag must be sanitized before creating a filepath.")
        except Exception as ex:
            raise ex
        return f"https://j.nozomi.la/nozomi/{encoded_tag}.nozomi"

    def _validate_tag_sanitized(self, tag: str) -> None:
        """Validate a search tag is sanitized properly.

        Args:
            tag: The search tag.

        Raises:
            InvalidTagFormat: If the tag is an empty string or begins with an invalid character.

        """
        if not tag:
            raise InvalidTagFormat(f"The tag '{tag}' is invalid. Cannot be empty.")
        if tag[0] == "-":
            raise InvalidTagFormat(
                f"The tag '{tag}' is invalid. Cannot begin with character '-'"
            )

    def _encode_tag(self, sanitized_tag: str) -> str:
        """Encode a sanitized tag using Nozomi's custom urlencoder.

        Args:
            sanitized_tag: The sanitized search tag.

        Returns:
            The encoded sanitized search tag.

        """

        def convert_char_to_hex(c):
            return f"%{format(ord(c.group(0)), 'x')}"

        encoded_tag = re.sub("[;/?:@=&]", convert_char_to_hex, sanitized_tag)
        return encoded_tag
# Utility function to extract postid from the URL
    def load_existing_postids(self, downloads_dir: Path) -> list[str]:
        postids_file = downloads_dir.joinpath("postids.txt")
        if postids_file.exists():
            with open(postids_file, "r") as f:
                return f.read().splitlines() # return list ['34987990', '34988230', '34979863']

    def filter_urls(self,relevant_post_urls: list[str], existing_postids: list[str]) -> list[str]:
        if not isinstance(existing_postids, list):
            raise ValueError("existing_postids должен быть списком строк")
        return [
            url
            for url in relevant_post_urls
            if self.get_postid_from_url(url) not in existing_postids
        ]

    def get_postid_from_url(self, url: str) -> str:
        # Assuming `postid` is the last numeric segment of the URL before `.json`
        parts = url.split("/")
        return parts[-1].replace(".json", "")
    
    def save_to_file(self, ids, filename):
        with open(filename, "w") as file:
            for id in ids:
                file.write(str(id) + "\n")

class Download:
    def __init__(self) -> None:
        self.sem = asyncio.Semaphore(3)

    async def download_photos(self, photos: list, headers):
        session_timeout = aiohttp.ClientTimeout(total=None)
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=6),
            trust_env = True,
            timeout=session_timeout,
            raise_for_status=True
        ) as session, self.sem:
            filepath = Path.cwd()
            futures = [
                self._download_photo(
                    session, 
                    photo["url"], 
                    filepath.joinpath(photo["filename"]),
                    photo["postid"],
                    filepath,
                    headers
                )
                for photo in photos
            ]
            
            # 1) is slow 2 rps
            #for future in tqdm.as_completed(futures, desc='Getting photos', unit='photos'):
            #    await future

            # 2) gather is better, but no have progressbar
            #await asyncio.gather(*futures)

            # 3) gather wih custom progressbar 1+2
            await self.async_gather_with_progress(*futures)

    async def _download_photo(
            self,
            session: aiohttp.ClientSession, 
            photo_url: str, 
            photo_path: Path,
            postid: str,
            filepath: Path,
            headers):
        try:
            if not photo_path.exists():
                async with session.get(photo_url, headers = headers) as response:
                    if response.status == 200:
                        async with aiofiles.open(photo_path, 'wb') as f:
                            #await f.write(await response.content.read())
                            async for chunk in response.content.iter_any():
                                await f.write(chunk)
                        # Writing postid after successful download
                        postids_file = filepath.joinpath("postids.txt")
                        async with aiofiles.open(postids_file, "a") as f:
                            await f.write(f"{postid}\n")
                    else:
                        logging.error("problem to download file: {}. Error: {}".format(response.status, photo_url))
                        pass
        except aiohttp.client_exceptions.ClientResponseError as e:
            logging.error("ResponseError: {}".format(e))
            pass
        except asyncio.exceptions.__all__ as e:
            logging.error("problem with asyncio: {}".format(e))
            pass
        except Exception as e:
            logging.error("Other error in download_photo: {}".format(e))
            pass

    def download_time_log(self, photos, download_time):
        logging.info(
            "{} {} for {}".format(
                numeral.choose_plural(len(photos), "Downloaded, Downloaded, Downloaded"),
                numeral.get_plural(len(photos), "photograph, photographs, photographs"),
                numeral.get_plural(download_time, "second, seconds, seconds"),
            )
        )

    async def async_gather_with_progress(self, *futures):
        tasks = [asyncio.create_task(future) for future in futures]
        progress_bar = tqdm(total=len(tasks), desc='Getting photos', unit='photos')

        for task in asyncio.as_completed(tasks):
            try:
                await task
            except Exception as e:
                print('Got an exception:', e)

            progress_bar.update(1)

        progress_bar.close()

class NozomiDownloader:
    def __init__(self, huge_tag_list: list) -> None:
        self.huge_tag_list = huge_tag_list
        self.photos = []  # Initialize the photos list
        self.errors = []  # Initialize an error list to store exceptions for review

    async def main(self, duplicateflag: bool =True):
        for i in range(len(self.huge_tag_list)):
            internal_pos, internal_ext, internal_neg = self.huge_tag_list[i]
            time_start = time.time()

            folder_tag = re.sub(r"[<>/;,:\s]", " ", "".join(internal_pos))
            photos_path = DOWNLOADS_DIR.joinpath(folder_tag)
            utils.create_dir(
                photos_path
            ) # Assuming utils.create_dir is previously defined
            logging.info(photos_path)

            logging.info("Requesting a list of urls")

            url_list = self.get_urls_list(
                internal_pos, 
                internal_ext
            )
            logging.info("We have got %s of urls" % len(url_list))

            logging.info("Requesting a list of urls from file")
            urls_from_file = utils.load_existing_postids(photos_path)

            if urls_from_file:
                logging.info("We have got %s of urls from file" % len(urls_from_file))
                logging.info("Filtering a list of urls")
                filtered_urls = utils.filter_urls(url_list, urls_from_file)
                logging.info("Filtered urls now we have %s" % len(filtered_urls))
            else:
                logging.info("No urls from file")
                filtered_urls = url_list

            self.photos = []
            if len(filtered_urls) != 0:
                session_timeout = aiohttp.ClientTimeout(total=None)
                async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(limit=16),
                    timeout=session_timeout
                ) as session:
                    futures = [
                        self.get_posts(session, url, internal_neg) for url in filtered_urls
                    ]

                    for future in tqdm.as_completed(futures, desc='Getting posts', unit='posts'):#tqdm(asyncio.as_completed(futures), total=len(futures)):
                        await future
                
                os.chdir(photos_path)               
                logging.info("Let's start downloading")
                await download.download_photos(self.photos, HEADERS_NOZOMI)
                
            else: logging.info("No relevant urls for downloading")

            time_finish = time.time()

            download.download_time_log(self.photos, (math.ceil(time_finish - time_start)))

            utils.handle_photo_processing(self.photos, photos_path, duplicateflag)

    def get_urls_list(
        self,
        positive_tags: list[str],
        extra_tags: list[str] = None#,
        #downloads_dir: Path = Path("./"),
    ) -> list[str]:
        extra_tags = extra_tags or []

        try:
            positive_post_urls = self._get_post_urls(positive_tags)
            extra_post_urls = self._get_post_urls(extra_tags)
            relevant_post_urls = set(positive_post_urls + list(set(extra_post_urls) - set(positive_post_urls)))
            relevant_post_urls = list(relevant_post_urls)
            relevant_post_urls.sort()
            return relevant_post_urls
        
            #DELETED postids file function
            """
            #positive_post_urls = obtain_urls_from_tags(positive_tags)
            #extra_post_urls = obtain_urls_from_tags(extra_tags)

            #relevant_post_urls = sort_and_combine_urls(positive_post_urls, extra_post_urls)
            #existing_postids = load_existing_postids(downloads_dir)
            #filtered_urls = filter_urls(relevant_post_urls, existing_postids)

            #return filtered_urls
            """
        except Exception as e:
            raise e

    def _get_post_urls(self, tags: list[str]) -> list[str]:
        """
        Retrieve the links to all of the posts that contain the tags.

        Args:
            tags: The tags that the posts must contain.

        Returns:
            A list of post urls that contain all of the specified tags.
        """

        #BUG: skips the list of urls for extra tags and loads few posts as a result
        """
        if not tags:
            return []

        sanitized_tags = [sanitize_tag(tag) for tag in tags]
        nozomi_urls = [
            create_tag_filepath(tag if tag.islower() else sanitize_tag(tag)) for tag in tags
        ]
        tag_post_ids = list(
            chain.from_iterable(_get_post_ids(nozomi_url) for nozomi_url in nozomi_urls)
        )

        post_id_count = count_post_ids(tag_post_ids)
        unic_post_ids = find_unique_post_ids(post_id_count, len(tags))

        if not unic_post_ids:
            print("No intersection for tags.", sanitized_tags)

        return [create_post_filepath(post_id) for post_id in unic_post_ids]
        """
        
        unic_post_ids = []
        if len(tags) == 0:
            return tags
        
        sanitized_tags = [utils.sanitize_tag(tag) for tag in tags]
        nozomi_urls = []
        for tag in tags:
            if not tag.islower():
                nozomi_urls.append(utils.create_tag_filepath(tag))
            #elif tag.isalpha():
            #    nozomi_urls.append(create_tag_filepath(tag))
            else:
                nozomi_urls.append(utils.create_tag_filepath(utils.sanitize_tag(tag)))
        tag_post_ids = [self._get_post_ids(nozomi_url) for nozomi_url in nozomi_urls]
        flat_list = list(chain.from_iterable(tag_post_ids))
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

        if len(unic_post_ids) == 0:
            print('Нет пересечения для тегов',sanitized_tags)
        post_urls = [utils.create_post_filepath(post_id) for post_id in unic_post_ids]

        return post_urls

    def _get_post_ids(self, tag_filepath_url: str) -> list[int]:
        """
        Retrieve the .nozomi data file and extract post IDs.
        Args:
            tag_filepath_url: The URL to a tag's .nozomi file.
        Returns:
            A list containing all of the post IDs that contain the tag.
        """
        post_ids = []
        try:
            #response = fetch_nozomi_file(tag_filepath_url)
            headers = {"Accept-Encoding": "gzip, deflate, br"}
            response = requests.get(tag_filepath_url, headers=headers, stream=True)
            response.raise_for_status()
            
            #validate_content_length(content)
            content = response.content
            if len(content) % 4 != 0:
                raise ValueError(
                    "Data size is not a multiple of 4, which is required for unpacking 32-bit integers."
                )
            
            #post_ids = unpack_content(content)
            total_ids = len(content) // 4
            post_ids = list(struct.unpack(f"!{total_ids}I", content))

        except Exception as e:
            logging.error(tag_filepath_url, e)

        return post_ids

    async def get_posts(self, session, url, internal_neg):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    post_data = await response.json()
                    current_post = from_dict(data_class=Post, data=post_data)

                    # Make sure you're working with a string and it's not None.
                    date_str = current_post.date or "1990-01-01"

                    try:
                        # Try to parse the datetime string with microseconds
                        post_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S-%f")
                    except ValueError:
                        # If the date string does not match, try parsing it as a date without time.
                        post_date = datetime.strptime(date_str, "%Y-%m-%d")

                    # Convert the date to the desired string format
                    normal_post_date = post_date.strftime("%Y-%m-%d %H%M%S")

                    # Flattening and combining tags
                    tag_pool = []
                    for tags in [
                        current_post.artist,
                        current_post.character,
                        current_post.copyright,
                        current_post.general,
                    ]:
                        tag_pool.extend(tags)

                    """#получаем список тегов для сравнения с негативными тегами
                    current_post_tag_list = []
                    for i in range(len(current_post.artist)):
                        current_post_tag_list.append(current_post.artist[i].tag)
                    for i in range(len(current_post.character)):
                        current_post_tag_list.append(current_post.character[i].tag)
                    for i in range(len(current_post.copyright)):
                        current_post_tag_list.append(current_post.copyright[i].tag)
                    for i in range(len(current_post.general)):
                        current_post_tag_list.append(current_post.general[i].tag)
                    """

                    if not set(tag_pool).intersection(internal_neg):
                        # Compile the regex pattern outside the loop
                        invalid_char_re = re.compile(r"[<>/:#%]")
                        # Filter images and extend the list
                        self.photos.extend(
                            {
                                "filename": invalid_char_re.sub(
                                    "",
                                    f"{normal_post_date}-{i+1}-{image.dataid}.{image.type}",
                                ),
                                "url": image.imageurl,
                                "postid": current_post.postid
                            }
                            for i, image in enumerate(current_post.imageurls)
                            if image.imageurl  # Ensure the URL is not empty
                        )
                else:
                    raise Exception(f"Failed to fetch data, status: {response.status}")
        except Exception as e:
            raise e
            self.errors.append(f"Error fetching {url}: {e}")
            #print(f"Error fetching {url}: {e}")
            logging.error('Error fetching %s: %s' % (url, e))

class Rule34Downloader:
    def __init__(self, huge_tag_list: list) -> None:
        self.huge_tag_list = huge_tag_list

    async def main(self, duplicateflag: bool =True):
        for i in range(len(self.huge_tag_list)):
            time_start = time.time()
            internal_pos, internal_ext, internal_neg = self.huge_tag_list[i]
            
            logging.info("Requesting a list of urls")
            urls, filenames, postids = self.r34_urls_files_list(
                internal_pos, internal_ext, internal_neg
            )

            folder_tag = re.sub(r'[<>/;,:\s]', ' ', ''.join(internal_pos))
            folder_tag = 'RULE_34 '+ folder_tag
            folder_tag = folder_tag.rstrip()
            photos_path = DOWNLOADS_DIR.joinpath(folder_tag)
            utils.create_dir(photos_path)
            logging.info(photos_path)
            
            self.photos = []
            logging.info("checking post lengths")
            if len(urls) != len(filenames):
                logging.exception(
                    "the lengths of the list url {} and filenames {} for the tag {} do not match",
                    len(urls),
                    len(filenames),
                    internal_pos,
                )
                exit()

            for i, url in enumerate(urls):
                self.photos.append({
                    "filename": filenames[i],
                    "url": url,
                    "postid": postids[i]
                })
            
            os.chdir(photos_path)               
            logging.info("Let's start downloading")
            await download.download_photos(self.photos, HEADERS_R34)

            time_finish = time.time()

            download.download_time_log(self.photos, (math.ceil(time_finish - time_start)))

            utils.handle_photo_processing(self.photos, photos_path, duplicateflag)

    def r34_urls_files_list(
            self,
            positive_tags: list[str],
            extra_tags: list[str] = None,
            negative_tags: list[str] = None,
        ):

        # if relevant_post_date is None:
        #    relevant_post_date = datetime.strptime("1900-01-01 00:00:00+00:00", '%Y-%m-%d %H:%M:%S%z')
        c = []
        d = []
        e = []
        relevant_post_urls = []
        relevant_post_filenames = []
        relevant_post_ids = []
        print(positive_tags, extra_tags, negative_tags, sep='\n', end='\n\n')

        try:
            if extra_tags is None or extra_tags == []:
                logging.info("gone out extra")
                extra_tags = list()
                search_pos = self.search(positive_tags, negative_tags)
                # print('search_pos =',search_pos)
                for result in search_pos:
                    norm_post_date = datetime.strftime(result.date, "%Y-%m-%d %H%M%S")
                    # print(post_date, relevant_post_date)
                    if result.video != "":
                        c.append(result.fileurl)
                        c.append(f"{norm_post_date}-{result.id}-{result.video}")
                        c.append(result.id)
                        d.append(c)
                        c = []
                    else:
                        c.append(result.fileurl)
                        c.append(f"{norm_post_date}-{result.id}-{result.image}")
                        c.append(result.id)
                        d.append(c)
                        c = []
            else:
                logging.info("went to extra")
                search_ext = []
                search_pos = self.search(positive_tags, negative_tags)
                for tag in extra_tags:
                    smal_search_ext = self.search(tag, negative_tags)
                    for post in smal_search_ext:
                        search_ext.append(post)
                for result in search_pos:
                    norm_post_date = datetime.strftime(result.date, "%Y-%m-%d %H%M%S")
                    if result.video != "":
                        c.append(result.fileurl)
                        c.append(f"{norm_post_date}-{result.id}-{result.video}")
                        c.append(result.id)
                        d.append(c)
                        c = []
                    else:
                        c.append(result.fileurl)
                        c.append(f"{norm_post_date}-{result.id}-{result.image}")
                        c.append(result.id)
                        d.append(c)
                        c = []
                for result in search_ext:
                    norm_post_date = datetime.strftime(result.date, "%Y-%m-%d %H%M%S")
                    if result.video != "":
                        c.append(result.fileurl)
                        c.append(f"{norm_post_date}-{result.id}-{result.video}")
                        c.append(result.id)
                        e.append(c)
                        c = []
                    else:
                        c.append(result.fileurl)
                        c.append(f"{norm_post_date}-{result.id}-{result.image}")
                        c.append(result.id)
                        e.append(c)
                        c = []
            extra_nointersection = []
            for i in range(len(e)):
                if e.count(e[i]) == 1 or e[i] not in extra_nointersection:
                    extra_nointersection.append(e[i])

            except_intersection = [item for item in extra_nointersection if item not in d]
            rel_list = d + except_intersection

            for i in range(len(rel_list)):
                a, b, c = rel_list[i]
                relevant_post_urls.append(a)
                relevant_post_filenames.append(b)
                relevant_post_ids.append(c)
            relevant_post_filenames = list(relevant_post_filenames)
            relevant_post_urls = list(relevant_post_urls)
            relevant_post_ids = list(relevant_post_ids)

            return relevant_post_urls, relevant_post_filenames, relevant_post_ids
        except InvalidTagFormat as tf:
            raise tf
        except Exception as e:
            logging.exception("error in r34_urls_files_list")
            raise e

    def search(self, tags: list, negtags:list = None, page_id: int = None, limit: int = 100, deleted: bool = False,ignore_max_limit: bool = False) -> list:
        """Search for posts

        Args:
            tags (list[str]): Search tags
            page_num (int, optional): Page ID
            ignore_max_limit (bool, optional): If max value should be ignored
            limit (int, optional): Limit for Posts. Max 1000.

        Returns:
            list: Posts result list [empty if error occurs]

        API Docs: https://rule34.xxx/index.php?page=help&topic=dapi
        Tags Cheatsheet: https://rule34.xxx/index.php?page=tags&s=list
        """

        # Check if "limit" is in between 1 and 1000
        if not ignore_max_limit and limit > 1000 or limit <= 0:
            raise Exception("invalid value for \"limit\"\n  value must be between 1 and 1000\n  see for more info:\n  https://github.com/b3yc0d3/rule34Py/blob/master/DOC/usage.md#search")

        counter_pid = 0
        params = [
            #["TAGS", ""],
            ["LIMIT", str(limit)],
            ["NTAGS", "+-".join(negtags)]
        ]
        
        if type(tags) != str:
            params.append(["TAGS", "+".join(tags)])
        else:
            params.append(["TAGS", tags])

        if negtags != []:
            url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit={{LIMIT}}&tags={{TAGS}}+-{{NTAGS}}"
        else:
            url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit={{LIMIT}}&tags={{TAGS}}"
        # Add "page_id"
        if page_id != None:
            url += f"&pid={{PAGE_ID}}"
            params.append(["PAGE_ID", str(page_id)])
        #else:
        #    page_id = 0
        #    url += f"&pid={{PAGE_ID}}"
        #    params.append(["PAGE_ID", str(page_id)])

        
        if deleted:
            #raise Exception("To include deleted images is not Implemented yet!")
            url += "&deleted=show"

        __headers__ = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml, application/json;q=0.9, image/webp, */*;q=0.8'
        }
        
        formatted_url = self._parseUrlParams(url, params)
        logging.info('The first url: %s&pid=%s' % (formatted_url, counter_pid))
        response = requests.get(formatted_url+f'&pid={counter_pid}', headers=__headers__) #&json=1', stream=True
        #print(response.encoding)
        no_pid_url = formatted_url
        res_status = response.status_code
        res_len = len(response.content)
        ret_posts = []
        small_part_posts = []
        time.sleep(0.5)
        # checking if status code is not 200
        # (it's useless currently, becouse rule34.xxx returns always 200 OK regardless of an error)
        # and checking if content lenths is 0 or smaller
        # (curetly the only way to check for a error response)
        #print(res_status)
        #print(response.text)
        #print(response.content)
        if res_status != 200 or res_len <= 0:
            logging.error("An error occurred with status %s" % res_status)
            return ret_posts
        
        soup = BeautifulSoup(response.content, 'xml')

        myposts = soup.find_all("post")#[soup.post]
        for post in myposts:
            _post = r34Post.from_xml(post)
            post_tags = _post.tags
            #print(post_tags)
            for tag in post_tags:
                #print(tag)
                if tag != '':
                    tag_counts[tag] += 1 
            small_part_posts.append(_post)
            #small_part_posts.append(Post.from_xml(post))
        [ret_posts.append(small_part_posts[i]) for i in range(len(small_part_posts))]
        
        while len(small_part_posts) == 100:
            logging.info('Whe have got small_part_posts %s' % len(small_part_posts))
            small_part_posts = []
            counter_pid+=1
            formatted_url = f'{no_pid_url}&pid={counter_pid}'
            logging.info('The next url: %s' % formatted_url)
            try:
                response2 = requests.get(formatted_url,  headers=__headers__)
                #print(response2)
                soup2 = BeautifulSoup (response2.content, 'xml')
                myposts2 = soup2.find_all("post")
                for post in myposts2:
                    _post = r34Post.from_xml(post)
                    post_tags = _post.tags
                    #print(post_tags)
                    for tag in post_tags:
                        #print(tag)
                        if tag != '':
                            tag_counts[tag] += 1 
                    small_part_posts.append(_post)#(Post.from_xml(post))
                logging.info('The second checking small_part_posts %s' % len(small_part_posts))

            except Exception as e:
                logging.exception('error while accessing the dict')
                raise e
            if len(small_part_posts) != 0:
                [ret_posts.append(small_part_posts[i]) for i in range(len(small_part_posts))]
            time.sleep(0.2)
            
        #[ret_posts.append(small_part_posts[i]) for i in range(len(small_part_posts))]
        logging.info('All we have got in search %s' % len(ret_posts))
        return ret_posts

    def _parseUrlParams(self, url: str, params: list) -> str:
            # Usage: _parseUrlParams("domain.com/index.php?v={{VERSION}}", [["VERSION", "1.10"]])
            retURL = url

            for g in params:
                key = g[0]
                value = g[1]

                retURL = retURL.replace("{" + key + "}", value)

            return retURL


# Check if the __name__ is set to __main__ to ensure the script is being run directly
if __name__ == '__main__':
    utils = Utils()
    utils.create_dir(DOWNLOADS_DIR)
    download = Download()
    # Prevent circular dependency issues
    MediaMetaData = ForwardRef("MediaMetaData")
    # defaultdict is used to count tags in total across all posts of a specific group. The following 3 functions are used together.
    tag_counts = defaultdict(int)

    print("1. Download all photos from Nozomi")
    print("2. Download all photos from Rule34.xxx")

    # Enter the main loop for handling user input
    while True:
        # Wait a minimal amount of time for CPU relief
        time.sleep(0.1)

        # Get the downloader type from the user
        downloader_type = input("> ")
        # Validate the downloader type
        if downloader_type in ["1", "2"]:
            # Ask the user for duplicate check preference
            print("Check for duplicates? 1-Yes 2-No")
            duplicate_flag = input("> ")

            # Check which downloader to instantiate based on the downloader type
            if downloader_type == "1":
                downloader = NozomiDownloader(huge_tag_list=get_multi(False))
            else:  # downloader_type must be "2"
                downloader = Rule34Downloader(huge_tag_list=get_multi(True))

            # Print the huge tag list for the user to see
            print(*downloader.huge_tag_list, sep="\n", end="\n\n")

            if duplicate_flag == "1":
                # Run the downloader with the duplicate check
                asyncio.run(downloader.main())
                break
            elif duplicate_flag == "2":
                # Run the downloader without the duplicate check
                asyncio.run(downloader.main(duplicateflag=False))
                break
            else:
                # Log a message for invalid duplicate check selection
                logging.info("Invalid duplicate check selection code")          
        else:
            # Log a message for incorrect downloader type input
            logging.error("Wrong command")