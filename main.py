import os
import re
import sys
import math
import time
import logging
from pathlib import Path

import yaml
import requests
import aiohttp
import aiofiles
import asyncio
import vk_api
from pytils import numeral

from multi import get_multi
import api
from datetime import datetime
from dacite import from_dict
from pathlib import Path
from data import Post

from filter import check_for_duplicates
from functions import (
    download_photo,
    download_photos
)
from tqdm.asyncio import tqdm

BASE_DIR = Path('D:/ghd/').resolve() #Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR.joinpath("img") #'D:/ghd/img/'
#CONFIG_PATH = BASE_DIR.joinpath("config.yaml")

#with open(CONFIG_PATH, encoding="utf-8") as ymlFile:
#    config = yaml.load(ymlFile.read(), Loader=yaml.Loader)

logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)

logger = logging.getLogger('vk_api')
logger.disabled = True

loop = asyncio.get_event_loop()

class Utils:
    def create_dir(self, dir_path: Path):
        if not dir_path.exists():
            dir_path.mkdir()

    def remove_dir(self, dir_path: Path):
        if dir_path.exists():
            dir_path.rmdir()

class NozomiDownloader:
    def __init__(self, huge_tag_list: list) -> None:
        self.huge_tag_list = huge_tag_list

    async def get_posts(self, session, url, internal_neg):
        #получаем текущий пост
        async with session.get(url) as response:
            if response.status == 200:
                post_data = await response.json()
            else:
                return

        #форматируем пост в датакласс и получаем дату в нормальном виде
        current_post = from_dict(data_class=Post, data=post_data)
        if current_post.date is None or current_post.date == '':
            post_date = datetime.strptime('1990-01-01', '%Y-%m-%d')
        else:
            post_date = datetime.strptime(current_post.date, '%Y-%m-%d %H:%M:%S-%f')
        normal_post_date = datetime.strftime(post_date, '%Y-%m-%d %H%M%S')

        #получаем список тегов для сравнения с негативными тегами
        current_post_tag_list = []
        for i in range(len(current_post.artist)):
            current_post_tag_list.append(current_post.artist[i].tag)
        for i in range(len(current_post.character)):
            current_post_tag_list.append(current_post.character[i].tag)
        for i in range(len(current_post.copyright)):
            current_post_tag_list.append(current_post.copyright[i].tag)
        for i in range(len(current_post.general)):
            current_post_tag_list.append(current_post.general[i].tag)

        if len(set(current_post_tag_list).intersection(internal_neg)) <= 0:
            nozomi_img_counter = 1
            """
            Проходимся по всем вложениям поста и отбираем только картинки
            """
            for i, image in enumerate(current_post.imageurls):
                if image != "":
                    filename = f'{normal_post_date}-{nozomi_img_counter}-{image.dataid}.{image.type}'
                    filename = re.sub('[<>/:#%]', '', filename)
                    self.photos.append({
                        "filename": filename,
                        "url": image.imageurl
                    })
                nozomi_img_counter += 1

    async def main(self, dublicateflag: bool =True):
        for i in range(len(self.huge_tag_list)):
            internal_pos, internal_ext, internal_neg = self.huge_tag_list[i]
            logging.info("Запрашиваем список url")
            url_list = api.get_urls_list(internal_pos, internal_ext)
            string_tag = ''.join(internal_pos)
            folder_tag = re.sub(r'[<>/;,:\s]', ' ', string_tag)
            photos_path = DOWNLOADS_DIR.joinpath(folder_tag)
            utils.create_dir(photos_path)
            print(photos_path)
            self.photos = []
            time_start = time.time()
            futures = []
            logging.info("получаем посты")
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
                for i, url in enumerate(url_list):
                    futures.append(self.get_posts(session,url, internal_neg))

                for future in tqdm(asyncio.as_completed(futures), total=len(futures)):
                    #await asyncio.sleep(0.2)
                    await future
            
                            
            # Скачиваем фотографии со стены группы
            os.chdir(photos_path)               
            logging.info("Начинаем загрузку")
            await download_photos(self.photos)

            time_finish = time.time()
            download_time = math.ceil(time_finish - time_start)

            logging.info("{} {} за {}".format(
                numeral.choose_plural(len(self.photos), "Скачена, Скачены, Скачены"),
                numeral.get_plural(len(self.photos), "фотография, фотографии, фотографий"),
                numeral.get_plural(download_time, "секунду, секунды, секунд")
            ))

            if dublicateflag:
                logging.info("Проверка на дубликаты")
                dublicates_count = check_for_duplicates(photos_path)
                logging.info(f"Дубликатов удалено: {dublicates_count}")
                logging.info(f"Итого скачено: {len(self.photos) - dublicates_count} фото")
            else:
                logging.info(f"Итого скачено: {len(self.photos)} фото")

class Rule34Downloader:
    def __init__(self, huge_tag_list: list) -> None:
        self.huge_tag_list = huge_tag_list

    async def main(self, dublicateflag: bool =True):
        for i in range(len(self.huge_tag_list)):
            internal_pos, internal_ext, internal_neg = self.huge_tag_list[i]
            logging.info("Запрашиваем список url")
            #url_list = api.get_urls_list(internal_pos, internal_ext)
            urls, filenames = api.r34_urls_files_list(internal_pos, internal_ext, internal_neg)
            string_tag = ''.join(internal_pos)
            folder_tag = re.sub(r'[<>/;,:\s]', ' ', string_tag)
            folder_tag = 'RULE_34 '+ folder_tag
            folder_tag = folder_tag.rstrip()
            photos_path = DOWNLOADS_DIR.joinpath(folder_tag)
            utils.create_dir(photos_path)
            print(photos_path)
            self.photos = []
            time_start = time.time()
            logging.info("проверяем длины постов")
            if len(urls) != len(filenames):
                logging.exception("не совпадают длины список url {} и filenames {} для тега {}", len(urls), len(filenames), internal_pos)
                exit()
            
            for i, url in enumerate(urls):
                #futures.append(self.get_posts(session,url, internal_neg))
                self.photos.append({
                    "filename": filenames[i],
                    "url": url
                })
            
                            
            # Скачиваем фотографии со стены группы
            os.chdir(photos_path)               
            logging.info("Начинаем загрузку")
            await download_photos(self.photos)

            time_finish = time.time()
            download_time = math.ceil(time_finish - time_start)

            logging.info("{} {} за {}".format(
                numeral.choose_plural(len(self.photos), "Скачена, Скачены, Скачены"),
                numeral.get_plural(len(self.photos), "фотография, фотографии, фотографий"),
                numeral.get_plural(download_time, "секунду, секунды, секунд")
            ))
            if dublicateflag:
                logging.info("Проверка на дубликаты")
                dublicates_count = check_for_duplicates(photos_path)
                logging.info(f"Дубликатов удалено: {dublicates_count}")
                logging.info(f"Итого скачено: {len(self.photos) - dublicates_count} фото")
            else:
                logging.info(f"Итого скачено: {len(self.photos)} фото")


if __name__ == '__main__':
    utils = Utils()
    utils.create_dir(DOWNLOADS_DIR)

    print("1. Скачать все фотографии с Nozomi")
    print("2. Скачать все фотографии с Rule34.xxx")

    while True:
        time.sleep(0.1)
        downloader_type = input("> ")
        if downloader_type == "1":
            print("Проверять дубликаты? 1- Да 2-Нет")
            dublicate_flag = input("> ")
            downloader = NozomiDownloader(huge_tag_list=get_multi(from_r34= False))
            print(downloader.huge_tag_list)
            if dublicate_flag == "1":
                loop.run_until_complete(downloader.main())
                break
            elif dublicate_flag == "2":
                loop.run_until_complete(downloader.main(dublicateflag=False))
                break
            else:
                logging.info("Неправильный код выбора проверки дубликатов") 
        if downloader_type == "2":
            print("Проверять дубликаты? 1- Да 2-Нет")
            dublicate_flag = input("> ")
            downloader = Rule34Downloader(huge_tag_list=get_multi(from_r34= True))
            print(downloader.huge_tag_list)
            if dublicate_flag == "1":
                loop.run_until_complete(downloader.main())
                break
            elif dublicate_flag == "2":
                loop.run_until_complete(downloader.main(dublicateflag=False))
                break
            else:
                logging.info("Неправильный код выбора проверки дубликатов")           
        else:
            logging.info("Неправильная команда")
