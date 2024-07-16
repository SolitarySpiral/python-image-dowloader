"""Web API functions."""

import logging
import struct
import time
from helpers import sanitize_tag, create_tag_filepath, create_post_filepath, tag_counts
from itertools import chain
import aiohttp
import aiofiles

# from main imported
import requests
import os
import re
import shutil
from datetime import datetime
from dacite import from_dict
from pathlib import Path
from data import Post
from exceptions import InvalidTagFormat
from rule34Py import rule34Py

r34Py = rule34Py()
# end main imported
# semaphoreNozomiFile = asyncio.Semaphore(16)


headersNozomi = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://nozomi.la/",
    "Upgrade-Insecure-Requests": "1",
}


headersR34 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://wimg.rule34.xxx/",
    "Upgrade-Insecure-Requests": "1",
}


async def async_nozomi_download_file(
    session, semaphoreNozomi, url: str, blacklist: list[str], relevant_post_date=None
):
    filepath = Path.cwd()
    relevant_post_date = relevant_post_date or datetime.strptime(
        "1900-01-01", "%Y-%m-%d"
    )
    filepath.mkdir(parents=True, exist_ok=True)

    try:
        async with session.get(url) as response:
            post_data = await response.json()
        current_post = from_dict(data_class=Post, data=post_data)
        post_date = datetime.strptime(current_post.date, "%Y-%m-%d %H:%M:%S-%f")
        norm_post_date = post_date.strftime("%Y-%m-%d %H%M%S")

        if post_date > relevant_post_date:
            current_post_tag_list = [
                tag.tag
                for tag_list in [
                    current_post.artist,
                    current_post.character,
                    current_post.copyright,
                    current_post.general,
                ]
                for tag in tag_list
                if tag.tag
            ]
            for tag in current_post_tag_list:
                tag_counts[tag] += 1

            if not set(current_post_tag_list).intersection(blacklist):
                for nozomi_img_counter, media_meta_data in enumerate(
                    current_post.imageurls, start=1
                ):
                    filename = re.sub(
                        "[<>/:#%]",
                        "",
                        f"{norm_post_date}-{nozomi_img_counter}-{media_meta_data.dataid}.{media_meta_data.type}",
                    )
                    image_filepath = filepath.joinpath(filename)
                    print(media_meta_data.imageurl, image_filepath)

                    if not os.path.exists(image_filepath):
                        async with semaphoreNozomi, session.get(
                            media_meta_data.imageurl, headers=headersNozomi
                        ) as r:
                            async with aiofiles.open(image_filepath, "wb") as f:
                                async for chunk in r.content.iter_chunked(1024):
                                    await f.write(chunk)
                        print("File is downloaded", image_filepath)
            else:
                print("Post in blacklist", current_post.postid)
    except aiohttp.ClientError as e:
        return e
    except Exception as ex:
        return ex


async def async_r34_download_file(session, semaphore34, url, file_name):
    # res = requests.get(url, stream = True)
    try:
        file_name = re.sub("[/:+#%]", "", file_name)
        if os.path.exists(file_name):
            print("File already exist", file_name)
        else:
            # print('File not exists', file_name)
            async with semaphore34:
                async with session.get(url, headers=headersR34) as r:
                    assert r.status == 200
                    # with open(file_name, 'wb') as f:
                    async with aiofiles.open(file_name, "wb") as f:
                        # await shutil.copyfileobj(r.raw, f)
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            await f.write(chunk)
            print("File is downloaded", file_name)
    except aiohttp.ClientError as e:
        return e
    except Exception as ex:
        return ex


def get_urls_list(
    positive_tags: list[str],
    extra_tags: list[str] = None,
    downloads_dir: Path = Path("./"),
) -> list[str]:
    extra_tags = extra_tags or []

    try:
        positive_post_urls = obtain_urls_from_tags(positive_tags)
        extra_post_urls = obtain_urls_from_tags(extra_tags)

        relevant_post_urls = sort_and_combine_urls(positive_post_urls, extra_post_urls)
        existing_postids = load_existing_postids(downloads_dir)
        filtered_urls = filter_urls(relevant_post_urls, existing_postids)

        return filtered_urls

    except Exception as e:
        raise e


# Helper functions for get_urls_list
def obtain_urls_from_tags(tags: list[str]) -> set:
    return set(_get_post_urls(tags))


def sort_and_combine_urls(positive_post_urls: set, extra_post_urls: set) -> list[str]:
    return sorted(positive_post_urls | extra_post_urls)


def load_existing_postids(downloads_dir: Path) -> set:
    postids_file = downloads_dir.joinpath("postids.txt")
    if postids_file.exists():
        with open(postids_file, "r") as f:
            return set(f.read().splitlines())
    return set()


def filter_urls(relevant_post_urls: list[str], existing_postids: set) -> list[str]:
    return [
        url
        for url in relevant_post_urls
        if get_postid_from_url(url) not in existing_postids
    ]


def _get_post_ids(tag_filepath_url: str) -> list[int]:
    """
    Retrieve the .nozomi data file and extract post IDs.
    Args:
        tag_filepath_url: The URL to a tag's .nozomi file.
    Returns:
        A list containing all of the post IDs that contain the tag.
    """
    try:
        response = fetch_nozomi_file(tag_filepath_url)
        content = response.content

        validate_content_length(content)
        post_ids = unpack_content(content)

    except requests.HTTPError as http_err:
        handle_http_error(http_err)
        return []

    except Exception as e:
        handle_general_error(tag_filepath_url, e)

    return post_ids


# Helper functions for _get_post_ids
def fetch_nozomi_file(tag_filepath_url: str) -> requests.Response:
    headers = {"Accept-Encoding": "gzip, deflate, br"}
    response = requests.get(tag_filepath_url, headers=headers, stream=True)
    response.raise_for_status()
    return response


def validate_content_length(content: bytes) -> None:
    if len(content) % 4 != 0:
        raise ValueError(
            "Data size is not a multiple of 4, which is required for unpacking 32-bit integers."
        )


def unpack_content(content: bytes) -> list[int]:
    total_ids = len(content) // 4
    return list(struct.unpack(f"!{total_ids}I", content))


def handle_http_error(http_err: requests.HTTPError) -> None:
    print(f"HTTP error occurred: {http_err}")


def handle_general_error(tag_filepath_url: str, error: Exception) -> None:
    raise RuntimeError(
        f"An error occurred when processing the .nozomi file from {tag_filepath_url}: {error}"
    )


def _get_post_urls(tags: list[str]) -> list[str]:
    """
    Retrieve the links to all of the posts that contain the tags.

    Args:
        tags: The tags that the posts must contain.

    Returns:
        A list of post urls that contain all of the specified tags.
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


# Helper functions for _get_post_urls
def count_post_ids(tag_post_ids: list[int]) -> dict[int, int]:
    post_id_count = {}
    for post_id in tag_post_ids:
        post_id_count[post_id] = post_id_count.get(post_id, 0) + 1
    return post_id_count


def find_unique_post_ids(post_id_count: dict[int, int], tag_count: int) -> list[int]:
    return [
        post_id
        for post_id, count in post_id_count.items()
        if count >= 2 or tag_count == 1
    ]


# Utility function to extract postid from the URL
def get_postid_from_url(url: str) -> str:
    # Assuming `postid` is the last numeric segment of the URL before `.json`
    parts = url.split("/")
    return parts[-1].replace(".json", "")


def r34_urls_files_list(
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
    print(positive_tags, extra_tags, negative_tags)

    try:
        if extra_tags is None or extra_tags == []:
            print("gone out extra")
            extra_tags = list()
            search_pos = r34Py.search(positive_tags, negative_tags)
            # print('search_pos =',search_pos)
            for result in search_pos:
                norm_post_date = datetime.strftime(result.date, "%Y-%m-%d %H%M%S")
                # print(post_date, relevant_post_date)
                if result.video != "":
                    c.append(result.fileurl)
                    c.append(f"{norm_post_date}-{result.id}-{result.video}")
                    d.append(c)
                    c = []
                else:
                    c.append(result.fileurl)
                    c.append(f"{norm_post_date}-{result.id}-{result.image}")
                    d.append(c)
                    c = []
        else:
            print("went to extra")
            search_ext = []
            search_pos = r34Py.search(positive_tags, negative_tags)
            for tag in extra_tags:
                smal_search_ext = r34Py.search(tag, negative_tags)
                for post in smal_search_ext:
                    search_ext.append(post)
            for result in search_pos:
                norm_post_date = datetime.strftime(result.date, "%Y-%m-%d %H%M%S")
                if result.video != "":
                    c.append(result.fileurl)
                    c.append(f"{norm_post_date}-{result.id}-{result.video}")
                    d.append(c)
                    c = []
                else:
                    c.append(result.fileurl)
                    c.append(f"{norm_post_date}-{result.id}-{result.image}")
                    d.append(c)
                    c = []
            for result in search_ext:
                norm_post_date = datetime.strftime(result.date, "%Y-%m-%d %H%M%S")
                if result.video != "":
                    c.append(result.fileurl)
                    c.append(f"{norm_post_date}-{result.id}-{result.video}")
                    e.append(c)
                    c = []
                else:
                    c.append(result.fileurl)
                    c.append(f"{norm_post_date}-{result.id}-{result.image}")
                    e.append(c)
                    c = []
        extra_nointersection = []
        for i in range(len(e)):
            if e.count(e[i]) == 1 or e[i] not in extra_nointersection:
                extra_nointersection.append(e[i])

        except_intersection = [item for item in extra_nointersection if item not in d]
        rel_list = d + except_intersection

        for i in range(len(rel_list)):
            a, b = rel_list[i]
            relevant_post_urls.append(a)
            relevant_post_filenames.append(b)
        relevant_post_filenames = list(relevant_post_filenames)
        relevant_post_urls = list(relevant_post_urls)

        return relevant_post_urls, relevant_post_filenames
    except InvalidTagFormat as tf:
        raise tf
    except Exception as e:
        logging.exception("error in r34_urls_files_list")
        raise e


def r34_download(url, file_name):
    # res = requests.get(url, stream = True)
    file_name = re.sub("[/:+#%]", "", file_name)
    if os.path.exists(file_name):
        print("File already exists", file_name)
        time.sleep(0.1)
    else:
        print("File not exists", file_name)
        with requests.get(url, stream=True, headers=headersR34) as r:
            with open(file_name, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        # print(r.headers)
        print("File downloaded", file_name)


def download_file(
    url: str, filepath: Path, blacklist: list[str], relevant_post_date=None
):
    if relevant_post_date is None:
        relevant_post_date = datetime.strptime("1900-01-01", "%Y-%m-%d")
    filepath.mkdir(parents=True, exist_ok=True)
    try:
        post_data = requests.get(url).json()
        current_post = from_dict(data_class=Post, data=post_data)
        post_date = datetime.strptime(current_post.date, "%Y-%m-%d %H:%M:%S-%f")
        if post_date > relevant_post_date:
            current_post_tag_list = []
            for i in range(len(current_post.artist)):
                current_post_tag_list.append(current_post.artist[i].tag)
            for i in range(len(current_post.character)):
                current_post_tag_list.append(current_post.character[i].tag)
            for i in range(len(current_post.copyright)):
                current_post_tag_list.append(current_post.copyright[i].tag)
            for i in range(len(current_post.general)):
                current_post_tag_list.append(current_post.general[i].tag)

            for tag in current_post_tag_list:
                if not tag == "":
                    tag_counts[tag] += 1
            if not len(set(current_post_tag_list).intersection(blacklist)) > 0:
                nozomi_img_counter = 1
                for media_meta_data in current_post.imageurls:
                    filename = f"{current_post.date}-{nozomi_img_counter}-{media_meta_data.dataid}.{media_meta_data.type}"
                    filename = re.sub("[<>/:#%]", "", filename)
                    image_filepath = filepath.joinpath(filename)
                    if os.path.exists(image_filepath):
                        print("File already exists", image_filepath)
                    else:
                        print("File not exists", image_filepath)
                        # with requests.session(keepalive=True) as sess:
                        with requests.get(
                            media_meta_data.imageurl, stream=True, headers=headersNozomi
                        ) as r:
                            with open(
                                image_filepath, "wb"
                            ) as f:  # async with aiofiles.open(image_filepath, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                        print("File downloaded", image_filepath)
                        nozomi_img_counter += 1
            else:
                print("Post in black list", current_post.postid)
    except requests.exceptions.RequestException as e:
        return e
    except Exception as ex:
        return ex
