"""Nozomi package configuration."""
import os
import re
import datetime
import time 
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
    start_time = datetime.datetime.now()
    print(start_time, " Начата загрузка тега ", pos_tag)
    for post in api.get_posts_with_tags(pos_tag, neg_tag):
        pool.apply_async(api.download_media, (post, Path.cwd(),))
    end_time = datetime.datetime.now()
    print(end_time, " Завершена загрузка тега ", pos_tag)

async def main():
    # 2. The tags that the posts retrieved must contain
    positive_tags = ['sherry']
    #positive_tags2 = ['artist:SPICYdias']
    #positive_tags3 = ['artist:bayern']
    #positive_tags4 = ['sherry']
    #positive_tags5 = ['Sherry_Birkin']
    #positive_tags6 = ['marlene_wallace']
    # 3. The blacklisted tags
    negative_tags = ['artist:sherry']
    
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
    positive_tags14 = ['higegepon']
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
    task1 = asyncio.create_task(nozomi_tag_load(positive_tags, negative_tags))
    #task2 = asyncio.create_task(nozomi_tag_load(positive_tags2, negative_tags))
    #task3 = asyncio.create_task(nozomi_tag_load(positive_tags3, negative_tags))
    #task4 = asyncio.create_task(nozomi_tag_load(positive_tags4, negative_tags))
    #task5 = asyncio.create_task(nozomi_tag_load(positive_tags5, negative_tags))
    #task6 = asyncio.create_task(nozomi_tag_load(positive_tags6, negative_tags))

    await task1
    #await task2
    #await task3
    #await task4
    #await task5
    #await task6
    '''
    # for reload
    task1 = asyncio.create_task(nozomi_tag_load(positive_tags, negative_tags))
    task2 = asyncio.create_task(nozomi_tag_load(positive_tags2, negative_tags))
    task3 = asyncio.create_task(nozomi_tag_load(positive_tags3, negative_tags))
    task4 = asyncio.create_task(nozomi_tag_load(positive_tags4, negative_tags))
    task5 = asyncio.create_task(nozomi_tag_load(positive_tags5, negative_tags))
    task6 = asyncio.create_task(nozomi_tag_load(positive_tags6, negative_tags))
    task7 = asyncio.create_task(nozomi_tag_load(positive_tags7, negative_tags))
    task8 = asyncio.create_task(nozomi_tag_load(positive_tags8, negative_tags))
    task9 = asyncio.create_task(nozomi_tag_load(positive_tags9, negative_tags))
    task10 = asyncio.create_task(nozomi_tag_load(positive_tags10, negative_tags))
    task11 = asyncio.create_task(nozomi_tag_load(positive_tags11, negative_tags))
    task12 = asyncio.create_task(nozomi_tag_load(positive_tags12, negative_tags))
    task13 = asyncio.create_task(nozomi_tag_load(positive_tags13, negative_tags))
    task14 = asyncio.create_task(nozomi_tag_load(positive_tags14, negative_tags))
    task15 = asyncio.create_task(nozomi_tag_load(positive_tags15, negative_tags))
    task16 = asyncio.create_task(nozomi_tag_load(positive_tags16, negative_tags))
    task17 = asyncio.create_task(nozomi_tag_load(positive_tags17, negative_tags))
    task18 = asyncio.create_task(nozomi_tag_load(positive_tags18, negative_tags))
    task19 = asyncio.create_task(nozomi_tag_load(positive_tags19, negative_tags))

    await task1
    await task2
    await task3
    await task4
    await task5
    await task6
    await task7
    await task8
    await task9
    await task10
    await task11
    await task12
    await task13
    await task14
    await task15
    await task16
    await task17
    await task18
    await task19
    '''
#main start program
main_time = datetime.datetime.now()
print("Запущено: ", main_time)
asyncio.run(main())
# the end program and close pool
pool.close()
main_time_end = datetime.datetime.now()
print(main_time_end, " Завершено! Длительность: ", main_time_end - main_time)

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