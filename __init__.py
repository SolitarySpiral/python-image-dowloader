"""Nozomi package configuration."""
import os, re, time
from pathlib import Path
from itertools import repeat
from functools import partial
# import our folder nozomi
from nozomi import api

import asyncio
from threading import Thread
import multiprocessing

'''# Preporations and call api
async def nozomi_tag_load(pos_tag, neg_tag = None, extra_tag = None):
    string_tag = ''.join(pos_tag)
    folder_tag = re.sub(r'[;,:\s]', ' ', string_tag)
    # Gets all posts with the tags
    if not os.path.exists(save_dir + folder_tag):
        os.makedirs(save_dir + folder_tag)
    os.chdir(save_dir + folder_tag)
    print("Текущая директория изменилась на ", os.getcwd())
    start_time = datetime.datetime.now()
    print(start_time, " Начата загрузка тега ", pos_tag)
    Posts = api.get_posts_with_tags(pos_tag, neg_tag, extra_tag)
    with multiprocessing.Pool() as pool:
        for post in Posts: #api.get_posts_with_tags(pos_tag, neg_tag, extra_tag):
            pool.imap_unordered(api.download_media, (post, Path.cwd(),))
    end_time = datetime.datetime.now()
    print(end_time, " Завершена загрузка тега ", pos_tag)
'''


async def main():
    start = time.perf_counter()
    print("Запущено: ", start)

    save_dir = 'D:/ghd/img/'
    #pool_size = 16  # your "parallelness"
    #pool = Pool(pool_size)
    positive_tags = ['artist:imbi']
    extra_tags = ['sarah_(the_last_of_us)']#['artist:Xentho','sherry']#, 'lesdias','artist:IncredibleChris']['artist:imbi']
    negative_tags = ['dragon_ball']

    # go to dir
    string_tag = ''.join(positive_tags)
    folder_tag = re.sub(r'[;,:\s]', ' ', string_tag)
    if not os.path.exists(save_dir + folder_tag):
        os.makedirs(save_dir + folder_tag)
    os.chdir(save_dir + folder_tag)
    print("Текущая директория изменилась на ", os.getcwd())
    # Gets all posts with the tags
    Posts = api.get_posts_with_tags(positive_tags, negative_tags, extra_tags)
    print("Мы получили посты")
    print("Начата загрузка тега ", positive_tags)
    tasks= []
    for post in Posts:
        tasks.append(asyncio.create_task(api.download_media(post, Path.cwd()))) #создание запросов
        await asyncio.sleep(0)
    await asyncio.wait(tasks)

    #tasks = [asyncio.create_task(api.download_media(post, Path.cwd())) for post in Posts]
    #results = await asyncio.gather(*tasks, return_exceptions=True)

    # the end
    end = time.perf_counter()
    print(f"it took: {end - start:.2f}s")
    '''
    # It works!
    threads = []
    for post in Posts:
        t = Thread(target=api.download_media, args=(post, Path.cwd(),))
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()
    '''
    # It works also
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(
    #    asyncio.wait([
    #        api.download_media(post, Path.cwd())
    #        for post in Posts
    #     ])
    #)
    #loop.close()
    ''' # Doesn't work at all
    with multiprocessing.Pool() as pool:
        #for post in Posts: #api.get_posts_with_tags(positive_tags, negative_tags, extra_tags):
        L= pool.imap(partial(api.download_media, b=Path.cwd()), Posts)
        #pool.starmap(api.download_media, zip(Posts, repeat(Path.cwd())))
        #pool.close
        #pool.join
        assert L
        end_time = datetime.datetime.now()
    print(end_time, " Завершена загрузка тега ", positive_tags)
    '''
    '''
    # for reload  #['loli']
    positive_tags = ['Riley_Anderson']
    positive_tags2 = ['Riley']
    positive_tags3 = ['insideout']
    positive_tags4 = ['rileyandersen']
    positive_tags5 = ['artist:7738']
    positive_tags6 = ['artist:ugaromix']
    positive_tags7 = ['Vanellope']
    positive_tags8 = ['シュガー・ラッシュ']
    positive_tags9 = ['artist:omsgarou']
    positive_tags10 = ['Sarah']
    positive_tags11 = ['vanellope']
    positive_tags12 = ['sarah_(the_last_of_us)']
    positive_tags13 = ['crumbles']
    positive_tags13 = ['ponchi', 'uzumaki_himawari']
    positive_tags14 = ['higegepon'] #is the same ['ひ~げぇぽん'] or ['pixiv_id_54698934']
    positive_tags15 = ['artist:imbi']
    positive_tags16 = ['マリー・ローズ']
    positive_tags17 = ['marie']
    positive_tags18 = ['marie_rose']
    positive_tags19 = ['marierose']
    positive_tags20 = ['artist:ターちゃん']
    positive_tags2 = ['opossumachine']
    positive_tags3 = ['gawr_gura']
    positive_tags4 = ['vanellope_von_schweetz']
    positive_tags = ['lesdias']
    #positive_tags3 = ['artist:bayern']
    #positive_tags4 = ['sherry']
    #positive_tags5 = ['Sherry_Birkin']
    #positive_tags6 = ['marlene_wallace']
    '''
    '''
    --buffer size problem
    positive_tags = ['artist:PossumMachine⚠️']
    positive_tags2 = ['artist:Libidoll']
    positive_tags3 = ['artist:AliceBunnie']
    positive_tags4 = ['artist:ターちゃん']
    positive_tags5 = ['artist:SPICYdias']
    '''

    # 4. Make tasks for every positive tags list
    #task1 = asyncio.create_task(nozomi_tag_load(pos_tag=positive_tags))#, extra_tag=extra_tags))


    #await task1

#main start program
if __name__ == '__main__':
    asyncio.run(main())
    #multiprocessing.freeze_support()



''' GARBAGE BELOW...

string_tag = ''.join(positive_tags2)
folder_tag = ''.join(string_tag)
if not os.path.exists(save_dir + folder_tag):
    os.makedirs(save_dir + folder_tag)
os.chdir(save_dir + folder_tag)
print("Текущая директория изменилась на ", os.getcwd())
for post in api.get_posts_with_tags(positive_tags2, negative_tags):
    pool.apply_async(api.download_media, (post, Path.cwd(),))

print("Завершен 2 поток")
string_tag = ''.join(positive_tags3)
folder_tag = ''.join(string_tag)
if not os.path.exists(save_dir + folder_tag):
    os.makedirs(save_dir + folder_tag)
os.chdir(save_dir + folder_tag)
print("Текущая директория изменилась на ", os.getcwd())
for post in api.get_posts_with_tags(positive_tags3, negative_tags):
    pool.apply_async(api.download_media, (post, Path.cwd(),))

print("Завершен 3 поток")
string_tag = ''.join(positive_tags4)
folder_tag = ''.join(string_tag)
if not os.path.exists(save_dir + folder_tag):
    os.makedirs(save_dir + folder_tag)
os.chdir(save_dir + folder_tag)
print("Текущая директория изменилась на ", os.getcwd())
for post in api.get_posts_with_tags(positive_tags4, negative_tags):
    pool.apply_async(api.download_media, (post, Path.cwd(),))

print("Завершен 4 поток")
pool.close()
#pool.join()
'''
'''
urls = [
    'https://nozomi.la/post/26905532.html#veigar',
    "https://nozomi.la/post/26932594.html#cho'gath",
    'https://nozomi.la/post/25802243.html#nautilus'
]

# Retrieve all of the post metadata using the URLs
posts = api.get_posts(urls)

# Download the posts
os.chdir('D:/ghd/img')
print("Текущая директория изменилась на folder:", os.getcwd())
for post in posts:
    api.download_media(post, Path.cwd())'''