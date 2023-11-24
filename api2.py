import asyncio
import aiohttp
import aiofiles

async def download_file(url: str, filepath: Path, blacklist: list[str], relevant_post_date = None):
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
