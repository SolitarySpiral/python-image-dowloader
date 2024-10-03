import logging
from pytils import numeral
from pathlib import Path

import aiohttp
import aiofiles
import asyncio
#from api import headersNozomi, headersR34
from tqdm.asyncio import tqdm

async def download_photos(photos: list, headers):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=5)
    ) as session:
        filepath = Path.cwd()
        futures = [
            download_photo(
                session, 
                photo["url"], 
                filepath.joinpath(photo["filename"]),
                headers
            )
            for photo in photos
        ]

        for future in tqdm(asyncio.as_completed(futures), total=len(futures)):
            await future

async def download_photo(
        session: aiohttp.ClientSession, 
        photo_url: str, 
        photo_path: Path,
        headers):
    try:
        if not photo_path.exists():
            async with session.get(photo_url, headers = headers) as response:
                async with aiofiles.open(photo_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        await f.write(chunk)
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