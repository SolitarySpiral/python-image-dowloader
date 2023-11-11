import requests
import os, re, shutil
from dacite import from_dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from api import _get_post_urls
from data import Post
from exceptions import InvalidTagFormat


url_list = []

def get_urls_list(positive_tags: list[str], negative_tags: list[str] = None, extra_tags: list[str] = None) -> list[str]:
    if negative_tags is None:
        negative_tags = list()
    if extra_tags is None:
        extra_tags = list()
    try:
        positive_post_urls = _get_post_urls(positive_tags)
        #negative_post_urls = _get_post_urls(negative_tags)
        extra_post_urls = _get_post_urls(extra_tags)
        relevant_post_urls = set(positive_post_urls + list(set(extra_post_urls) - set(positive_post_urls))) #- set(negative_post_urls)
        #relevant_post_urls = [x for x in relevant_post_urls if x not in negative_post_urls]
        #print(relevant_post_urls)
        return relevant_post_urls
    except InvalidTagFormat as tf:
        raise tf
    except Exception as ex:
        raise ex
 
def download_file(url: str, filepath: Path, blacklist: list[str]):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://nozomi.la/',
        'Upgrade-Insecure-Requests': '1'
    }
    filepath.mkdir(parents=True, exist_ok=True)
    try:
        post_data = requests.get(url).json()
        current_post = from_dict(data_class=Post, data=post_data)
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
        #if (not current_post.artist in blacklist) and (not current_post.character in blacklist) and (not current_post.copyright in blacklist) and (not current_post.general in blacklist):
            for media_meta_data in current_post.imageurls:
                filename = f'{current_post.date}{media_meta_data.dataid}.{media_meta_data.type}'
                filename = re.sub('[/:#%]', '', filename)
                image_filepath = filepath.joinpath(filename)
                if os.path.exists(image_filepath):
                    print('File already exists', image_filepath)
                else:
                    print('File not exists', image_filepath)
                    with requests.get(media_meta_data.imageurl, stream=True, headers=headers) as r:
                        with open(image_filepath, 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                    print('File downloaded ', image_filepath)
        else:
            print('Post in black list',current_post.postid)
    except requests.exceptions.RequestException as e:
        return e
    except Exception as ex:
        return ex
 
def runner():
    save_dir = 'D:/ghd/img/'
    positive_tags = ['artist:imbi', 'skater']
    extra_tags = ['sarah_(the_last_of_us)']#['artist:Xentho','sherry']#, 'lesdias','artist:IncredibleChris']['artist:imbi'] ['higegepon']
    negative_tags = ['collar', 'butt']
    url_list = get_urls_list(positive_tags)#, negative_tags)#, extra_tags)
    url_list = list(url_list)
    # go to dir
    if not len(url_list) == 0:
        string_tag = ''.join(positive_tags)
        folder_tag = re.sub(r'[;,:\s]', ' ', string_tag)
        if not os.path.exists(save_dir + folder_tag):
            os.makedirs(save_dir + folder_tag)
        os.chdir(save_dir + folder_tag)
        print("Текущая директория изменилась на ", os.getcwd())
        threads= []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for post_url in url_list:
                threads.append(executor.submit(download_file, post_url, Path.cwd(), negative_tags))
                
            for task in as_completed(threads):
                pass

if __name__ == '__main__':
    runner()