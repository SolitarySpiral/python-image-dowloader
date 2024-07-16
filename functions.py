import logging
from pytils import numeral
from pathlib import Path

import aiohttp
import aiofiles
import asyncio
from api import headersNozomi
from tqdm.asyncio import tqdm


async def download_photos(photos: list, downloads_dir: Path):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=8)
    ) as session:
        filepath = Path.cwd()
        futures = [
            download_photo(
                session,
                photo["url"],
                filepath.joinpath(photo["filename"]),
                photo["postid"],
                downloads_dir,
            )
            for photo in photos
        ]
        for future in tqdm(asyncio.as_completed(futures), total=len(futures)):
            await future


async def download_photo(
    session: aiohttp.ClientSession,
    photo_url: str,
    photo_path: Path,
    postid: str,
    downloads_dir: Path,
):
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Referer": "https://nozomi.la/",
    #     "Upgrade-Insecure-Requests": "1",
    # }
    try:
        if not photo_path.exists():
            async with session.get(photo_url, headers=headersNozomi) as response:
                if response.status == 200:
                    async with aiofiles.open(photo_path, "wb") as f:
                        await f.write(await response.read())
                    # Writing postid after successful download
                    postids_file = downloads_dir.joinpath("postids.txt")
                    async with aiofiles.open(postids_file, "a") as f:
                        await f.write(f"{postid}\n")
    except Exception as e:
        print(e)


def download_time_log(photos, download_time):
    logging.info(
        "{} {} for {}".format(
            numeral.choose_plural(len(photos), "Downloaded, Downloaded, Downloaded"),
            numeral.get_plural(len(photos), "photograph, photographs, photographs"),
            numeral.get_plural(download_time, "second, seconds, seconds"),
        )
    )
