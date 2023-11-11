import requests
import os, re, shutil
from datetime import datetime
from dacite import from_dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from api import _get_post_urls
from data import Post
from exceptions import InvalidTagFormat


url_list = []

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
                    filename = re.sub('[/:#%]', '', filename)
                    image_filepath = filepath.joinpath(filename)
                    if os.path.exists(image_filepath):
                        print('File already exists', image_filepath)
                    else:
                        print('File not exists', image_filepath)
                        with requests.get(media_meta_data.imageurl, stream=True, headers=headers) as r:
                            with open(image_filepath, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                        print('File downloaded', image_filepath)
            else:
                print('Post in black list',current_post.postid)
    except requests.exceptions.RequestException as e:
        return e
    except Exception as ex:
        return ex
 
def runner():
    '''You should always have the following variables filled in in one instance for 1 upload
    save_dir = 'D:/ghd/img/'
    relevant_date = use None or datetime.strptime("2023-07-11", '%Y-%m-%d')
    negative_tags = [] when not used; or ['monochrome']
    positive_tags = ['artist:imbi'] when 1 tag; or ['artist:imbi', 'skater'] when intersection of tags
    extra_tags = []

    A few examples below
    '''
    save_dir = 'D:/ghd/img/'
    relevant_date = None #datetime.strptime("2023-07-11", '%Y-%m-%d')
    negative_tags = [] #['butt']
    #positive_tags = ['artist:imbi'] #['artist:IncredibleChris']
    #extra_tags = [] #['artist:Xentho','sherry']
    
    
    positive_tags = ['Riley_Anderson']
    extra_tags = ['Riley', 'rileyandersen']

    #positive_tags = ['Vanellope']
    #extra_tags = ['vanellope', 'vanellope_von_schweetz']

    #positive_tags = ['Sarah']
    #extra_tags = ['sarah_(the_last_of_us)', 'sarah_miller']

    #positive_tags = ['higegepon']
    #extra_tags = ['artist:ひ~げぇぽん','pixiv_id_54698934']

    #positive_tags = ['marie_rose']
    #extra_tags = ['マリー・ローズ','marie', 'marierose']

    #positive_tags = ['opossumachine']
    #extra_tags = ['artist:PossumMachine⚠️']

    #positive_tags = ['artist:7738']
    #extra_tags = ['hebe', 'pixiv_id_66553761']

    #positive_tags = ['artist:ボッシー']
    #extra_tags = ['pixiv_id_13450661']

    #positive_tags = ['artist:omsgarou']
    #extra_tags = ['pixiv_id_2297160']

    #positive_tags = ['artist:ターちゃん']
    #extra_tags = ['pixiv_id_947930']

    #positive_tags = ['artist:Libidoll']
    #extra_tags = ['pixiv_id_1043474']

    #positive_tags = ['artist:AliceBunnie']
    #extra_tags = ['pixiv_id_25867890']

    #positive_tags = ['lesdias']
    #extra_tags = ['artist:SPICYdias', 'pixiv_id_15079627', 'artist:irispoplar', 'irispoplar', 'pixiv_id_25423811']

    # pos only

    #positive_tags = ['crumbles']
    #positive_tags = ['ponchi', 'uzumaki_himawari']
    #positive_tags = ['gawr_gura']

    '''there is no need to change the code below'''
    url_list = get_urls_list(positive_tags, extra_tags)
    url_list = list(url_list)
    url_list.sort()
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
                threads.append(executor.submit(download_file, post_url, Path.cwd(), negative_tags, relevant_date))
                
            for task in as_completed(threads):
                pass

if __name__ == '__main__':
    runner()
