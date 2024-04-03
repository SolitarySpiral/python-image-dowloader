import json
from pathlib import Path

import aiohttp
import aiofiles
import asyncio
from tqdm.asyncio import tqdm

async def download_photo(session: aiohttp.ClientSession, photo_url: str, photo_path: Path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://nozomi.la/',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        if not photo_path.exists():
                async with session.get(photo_url, headers = headers) as response:
                    if response.status == 200:
                        async with aiofiles.open(photo_path, "wb") as f:
                            await f.write(await response.read())
    except Exception as e:
        print(e)

async def download_photos(photos: list):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5)) as session:
        #async with asyncio.Semaphore(2) as sem:    
            futures = []
            filepath = Path.cwd()
            for i, photo in enumerate(photos):#range(len(photos)):
                filename = photo["filename"]
                #print(filename)
                photo_url = photo["url"]
                #print(photo_url)
                photo_path = filepath.joinpath(filename)
                #print(photo_path)
                futures.append(download_photo(session, photo_url, photo_path))


            for future in tqdm(asyncio.as_completed(futures), total=len(futures)):
                    #await asyncio.sleep(0.1)
                    await future

