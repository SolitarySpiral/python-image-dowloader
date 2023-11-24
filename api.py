"""Web API functions."""
import struct
from helpers import sanitize_tag, create_tag_filepath, create_post_filepath
from itertools import chain
import aiohttp
import aiofiles
import asyncio
#from main imported
import requests
import os, re, shutil
from datetime import datetime
from dacite import from_dict
from pathlib import Path
from data import Post
from exceptions import InvalidTagFormat
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
r34Py = rule34Py()
#end main imported

async def async_nozomi_download_file(url: str, filepath: Path, blacklist: list[str], relevant_post_date = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://nozomi.la/',
        'Upgrade-Insecure-Requests': '1'
    }
    if relevant_post_date is None:
        relevant_post_date = datetime.strptime("1900-01-01", '%Y-%m-%d')
    filepath.mkdir(parents=True, exist_ok=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                post_data = await response.json()
                current_post = from_dict(data_class=Post, data=post_data)
                post_date = datetime.strptime(current_post.date, '%Y-%m-%d %H:%M:%S-%f')
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
                    if not len(set(current_post_tag_list).intersection(blacklist)) > 0:
                        for media_meta_data in current_post.imageurls:
                            filename = f'{current_post.date}{media_meta_data.dataid}.{media_meta_data.type}'
                            filename = re.sub('[<>/:#%]', '', filename)
                            image_filepath = filepath.joinpath(filename)
                            if os.path.exists(image_filepath):
                                print('File already exists', image_filepath)
                            else:
                                print('File not exists', image_filepath)
                                async with session.get(media_meta_data.imageurl, headers=headers) as r:
                                    async with aiofiles.open(image_filepath, 'wb') as f:
                                        while True:
                                            chunk = await r.content.read(1024)
                                            if not chunk:
                                                break
                                            await f.write(chunk)
                                print('File downloaded', image_filepath)
                    else:
                        print('Post in blacklist', current_post.postid)
    except aiohttp.ClientError as e:
        return e
    except Exception as ex:
        return ex

async def async_r34_download_file(url, file_name):
    #res = requests.get(url, stream = True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://wimg.rule34.xxx/',
        'Upgrade-Insecure-Requests': '1'
    }
    file_name = re.sub('[/:+#%]', '', file_name)
    if os.path.exists(file_name):
        print('File already exists', file_name)
    else:
        print('File not exists', file_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as r:
                async with aiofiles.open(file_name, 'wb') as f:
                    while True:
                        chunk = await r.content.read(1024)
                        if not chunk:
                            break
                        await f.write(chunk)
        print('File downloaded', file_name)

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

def get_urls_list(positive_tags: list[str], extra_tags: list[str] = None) -> list[str]:
    if extra_tags is None:
        extra_tags = list()
    try:
        positive_post_urls = _get_post_urls(positive_tags)
        extra_post_urls = _get_post_urls(extra_tags)
        relevant_post_urls = set(positive_post_urls + list(set(extra_post_urls) - set(positive_post_urls)))
        #print(relevant_post_urls)
        return relevant_post_urls
    except InvalidTagFormat as tf:
        raise tf
    except Exception as ex:
        raise ex

def r34_urls_files_list(positive_tags: list[str], extra_tags: list[str] = None, negative_tags: list[str] = None, relevant_post_date: datetime = None):
    #positive_post_urls = []
    #positive_post_filenames = []
    #extra_post_urls = []
    #extra_post_filenames = []
    #corrupted_posts = []
    if relevant_post_date is None:
        relevant_post_date = datetime.strptime("1900-01-01 00:00:00+00:00", '%Y-%m-%d %H:%M:%S%z')
    c = []
    d = []
    e = []
    relevant_post_urls = []
    relevant_post_filenames = []
    print(positive_tags, extra_tags, negative_tags)
    '''for tag in positive_tags:
        tag = re.sub('[(]', '%28', tag)
        tag = re.sub('[)]', '%29', tag)
    for tag in extra_tags:
        tag = re.sub('[(]', '%28', tag)
        tag = re.sub('[)]', '%29', tag)'''
    try:
        if extra_tags is None or extra_tags == []:
            print('ушли вне экстра')
            extra_tags = list()
            search_pos = r34Py.search(positive_tags, negative_tags)
            #print('search_pos =',search_pos)
            for result in search_pos:
                post_date = result.date
                #print(post_date, relevant_post_date)
                if post_date > relevant_post_date:
                    if not result.video == '':
                        c.append(result.fileurl)
                        c.append(f'{result.date}-{result.id}-{result.video}')
                        d.append(c)
                        c = []
                    else:
                        c.append(result.fileurl)
                        c.append(f'{result.date}-{result.id}-{result.image}')
                        d.append(c)
                        c = []
                '''
                if not result.fileurl=='':    
                    if not result.video == '':
                        if re.search(result.video, result.fileurl):
                            positive_post_urls.append(result.fileurl)
                            positive_post_filenames.append(f'{result.id}-{result.video}')
                    elif not result.image == '':
                        if re.search(result.image, result.fileurl):
                            positive_post_urls.append(result.fileurl)
                            positive_post_filenames.append(f'{result.id}-{result.image}')'''
                '''if not (result.fileurl == '' or result.image == ''):
                    if re.search(result.image, result.fileurl):
                        positive_post_urls.append(result.fileurl)
                        positive_post_filenames.append(f'{result.id}-{result.image}')
                    else:
                        print('corrupted post', result.id)
                        corrupted_posts.append(result.id)
                else:
                    print('corrupted post', result.id)
                    corrupted_posts.append(result.id)'''
        else:
            print('ушли в экстра')
            search_ext = []
            search_pos = r34Py.search(positive_tags, negative_tags)
            for tag in extra_tags:
                smal_search_ext = r34Py.search(tag, negative_tags)
                for post in smal_search_ext:
                    search_ext.append(post)
            for result in search_pos:
                post_date = result.date
                if post_date > relevant_post_date:
                    if not result.video == '':
                        c.append(result.fileurl)
                        c.append(f'{result.date}-{result.id}-{result.video}')
                        d.append(c)
                        c = []
                    else:
                        c.append(result.fileurl)
                        c.append(f'{result.date}-{result.id}-{result.image}')
                        d.append(c)
                        c = []
            for result in search_ext:
                post_date = result.date
                if post_date > relevant_post_date:
                    if not result.video == '':
                        c.append(result.fileurl)
                        c.append(f'{result.date}-{result.id}-{result.video}')
                        e.append(c)
                        c = []
                    else:
                        c.append(result.fileurl)
                        c.append(f'{result.date}-{result.id}-{result.image}')
                        e.append(c)
                        c = []
        extra_nointersection = []
        for i in range(len(e)):
            if e.count(e[i])==1 or e[i] not in extra_nointersection:
                extra_nointersection.append(e[i])
        #extra_intersection = [item for item in e if item not in e]
        except_intersection = [item for item in extra_nointersection if item not in d]
        rel_list = d + except_intersection
        #print('rel_list=',rel_list)
        #relevant_post_urls = set(positive_post_urls + list(set(extra_post_urls) - set(positive_post_urls)))
        #relevant_post_filenames = set(positive_post_filenames + list(set(extra_post_filenames) - set(positive_post_filenames)))


        for i in range(len(rel_list)):
            a, b = rel_list[i]
            relevant_post_urls.append(a)
            relevant_post_filenames.append(b)

        return relevant_post_urls, relevant_post_filenames
    except InvalidTagFormat as tf:
        raise tf
    except Exception as ex:
        raise ex

def r34_download(url, file_name):
    #res = requests.get(url, stream = True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://wimg.rule34.xxx/',
        'Upgrade-Insecure-Requests': '1'
    }
    file_name = re.sub('[/:+#%]', '', file_name)
    if os.path.exists(file_name):
        print('File already exists', file_name)
    else:
        print('File not exists', file_name)
        with requests.get(url, stream=True, headers=headers) as r:
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        #print(r.headers)
        print('File downloaded', file_name)

def download_file(url: str, filepath: Path, blacklist: list[str], relevant_post_date = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://nozomi.la/',
        'Upgrade-Insecure-Requests': '1'
    }
    if relevant_post_date is None:
        relevant_post_date = datetime.strptime("1900-01-01", '%Y-%m-%d')
    filepath.mkdir(parents=True, exist_ok=True)
    try:
        post_data = requests.get(url).json()
        current_post = from_dict(data_class=Post, data=post_data)
        #print(current_post.date, relevant_post_date)
        post_date = datetime.strptime(current_post.date, '%Y-%m-%d %H:%M:%S-%f')
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
            #print(current_post_tag_list)
            #print(current_post.artist, current_post.character, current_post.copyright, current_post.general)
            if not len(set(current_post_tag_list).intersection(blacklist)) > 0:
                for media_meta_data in current_post.imageurls:
                    filename = f'{current_post.date}{media_meta_data.dataid}.{media_meta_data.type}'
                    filename = re.sub('[<>/:#%]', '', filename)
                    image_filepath = filepath.joinpath(filename)
                    if os.path.exists(image_filepath):
                        print('File already exists', image_filepath)
                    else:
                        print('File not exists', image_filepath)
                        with requests.get(media_meta_data.imageurl, stream=True, headers=headers) as r:
                            with open(image_filepath, 'wb') as f: #async with aiofiles.open(image_filepath, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                        print('File downloaded', image_filepath)
            else:
                print('Post in black list',current_post.postid)
    except requests.exceptions.RequestException as e:
        return e
    except Exception as ex:
        return ex