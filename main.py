import os
import re
import math
import time
import logging
from pathlib import Path

import aiohttp
import asyncio

from pytils import numeral

from multi import get_multi
import api
from datetime import datetime
from dacite import from_dict
from pathlib import Path
from data import Post

from filter import handle_photo_processing
from functions import download_photos, download_time_log
from api import headersR34, headersNozomi
from tqdm.asyncio import tqdm

BASE_DIR = Path('D:/ghd/').resolve() #Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR.joinpath("img") #'D:/ghd/img/'

logging.basicConfig(
    format='%(asctime)s - %(message)s',datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO
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
                                "url": image.imageurl
                            }
                            for i, image in enumerate(current_post.imageurls)
                            if image.imageurl  # Ensure the URL is not empty
                        )
                else:
                    raise Exception(f"Failed to fetch data, status: {response.status}")
        except Exception as e:
            self.errors.append(f"Error fetching {url}: {e}")
            print(f"Error fetching {url}: {e}")

    async def main(self, duplicateflag: bool =True):
        for i in range(len(self.huge_tag_list)):
            internal_pos, internal_ext, internal_neg = self.huge_tag_list[i]
            time_start = time.time()
            logging.info("Requesting a list of urls")
            url_list = api.get_urls_list(
                internal_pos, 
                internal_ext
            )
            folder_tag = re.sub(r"[<>/;,:\s]", " ", "".join(internal_pos))
            photos_path = DOWNLOADS_DIR.joinpath(folder_tag)
            utils.create_dir(
                photos_path
            ) # Assuming utils.create_dir is previously defined
            print(photos_path)
            self.photos = []
            
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=8)
            ) as session:
                futures = [
                    self.get_posts(session, url, internal_neg) for url in url_list
                ]

                for future in tqdm(asyncio.as_completed(futures), total=len(futures)):
                    await future
            
            os.chdir(photos_path)               
            logging.info("Let's start downloading")
            await download_photos(self.photos, headersNozomi)

            time_finish = time.time()

            download_time_log(self.photos, (math.ceil(time_finish - time_start)))

            handle_photo_processing(self.photos, photos_path, duplicateflag)

class Rule34Downloader:
    def __init__(self, huge_tag_list: list) -> None:
        self.huge_tag_list = huge_tag_list

    async def main(self, duplicateflag: bool =True):
        for i in range(len(self.huge_tag_list)):
            internal_pos, internal_ext, internal_neg = self.huge_tag_list[i]
            time_start = time.time()
            logging.info("Requesting a list of urls")
            urls, filenames = api.r34_urls_files_list(
                internal_pos, internal_ext, internal_neg
            )
            folder_tag = re.sub(r'[<>/;,:\s]', ' ', ''.join(internal_pos))
            folder_tag = 'RULE_34 '+ folder_tag
            folder_tag = folder_tag.rstrip()
            photos_path = DOWNLOADS_DIR.joinpath(folder_tag)
            utils.create_dir(photos_path)
            print(photos_path)
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
                #futures.append(self.get_posts(session,url, internal_neg))
                self.photos.append({
                    "filename": filenames[i],
                    "url": url
                })
            
            os.chdir(photos_path)               
            logging.info("Let's start downloading")
            await download_photos(self.photos, headersR34)

            time_finish = time.time()

            download_time_log(self.photos, (math.ceil(time_finish - time_start)))

            handle_photo_processing(self.photos, photos_path, duplicateflag)

# Check if the __name__ is set to __main__ to ensure the script is being run directly
if __name__ == '__main__':
    utils = Utils()
    utils.create_dir(DOWNLOADS_DIR)

    print("1. Download all photos from Nozomi")
    print("2. Download all photos from Rule34.xxx")

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
            print(downloader.huge_tag_list)

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
