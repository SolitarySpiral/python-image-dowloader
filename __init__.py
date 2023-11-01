"""Nozomi package configuration."""
import os
import re 
from pathlib import Path
# import our folder nozomi
from nozomi import api
# from multiprocessing import Pool
import asyncio
from multiprocessing.pool import ThreadPool as Pool

pool_size = 8  # your "parallelness"
pool = Pool(pool_size)
# 1. directory for load stream
save_dir = 'D:/ghd/img/'

# Preporations and call api
async def nozomi_tag_load(pos_tag, neg_tag):
    string_tag = ''.join(pos_tag)
    folder_tag = re.sub(r'[;,:\s]', ' ', string_tag)
    # Gets all posts with the tags
    if not os.path.exists(save_dir + folder_tag):
        os.makedirs(save_dir + folder_tag)
    os.chdir(save_dir + folder_tag)
    print("Текущая директория изменилась на ", os.getcwd())
    print("Начата загрузка тега ", pos_tag)
    for post in api.get_posts_with_tags(pos_tag, neg_tag):
        pool.apply_async(api.download_media, (post, Path.cwd(),))
    print("Завершена загрузка тега ", pos_tag)

async def main():
    # 2. The tags that the posts retrieved must contain
    #positive_tags = ['loli']  #['crumbles']['ponchi', 'uzumaki_himawari']#['higegepon']['artist:imbi']
    positive_tags = ['artist:7738']
    positive_tags2 = ['artist:ugaromix']
    positive_tags3 = ['Vanellope']
    positive_tags4 = ['シュガー・ラッシュ']

    '''positive_tags = ['Riley_Anderson']
    positive_tags2 = ['Riley']
    positive_tags3 = ['insideout']
    positive_tags4 = ['rileyandersen']'''

    # 3. The blacklisted tags
    negative_tags = ['dragon_ball']
    # 4. Make tasks for every positive tags list
    task1 = asyncio.create_task(nozomi_tag_load(positive_tags, negative_tags))
    task2 = asyncio.create_task(nozomi_tag_load(positive_tags2, negative_tags))
    task3 = asyncio.create_task(nozomi_tag_load(positive_tags3, negative_tags))
    task4 = asyncio.create_task(nozomi_tag_load(positive_tags4, negative_tags))
 
    await task1
    await task2
    await task3
    await task4
#main start program
asyncio.run(main())
# the end program and close pool
pool.close()
print("Завершено!")

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