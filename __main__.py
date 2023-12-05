import os, re
from datetime import datetime
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
from helpers import save_ids_to_file, remove_duplicates, tag_counts, load_dictionary, save_dictionary, merge_dictionaries
import multi
r34Py = rule34Py()
semaphoreNozomi = asyncio.Semaphore(30) #Not recommends change it
semaphore34 = asyncio.Semaphore(10) #Not recommends change it
import api

from threading import Thread
from urllib3 import HTTPConnectionPool
from multiprocessing import Process, cpu_count, Queue, JoinableQueue, Event


async def download_async(post_url, path, internal_neg, relevant_date):
        async with semaphoreNozomi:
            await api.async_nozomi_download_file(post_url, path, internal_neg, relevant_date)

async def r34_download_async(url, file_name):
        async with semaphore34:
            await api.async_r34_download_file(url, file_name)

async def runner():
    '''You should always have the following variables filled in in one instance for 1 upload
    from_r34 = True/False
    save_dir = 'D:/ghd/img/'
    relevant_date = use None or datetime.strptime("2023-07-11", '%Y-%m-%d') !!NOT WORKING WITH Rule34!!
    negative_tags = [] when not used; or ['monochrome']
    positive_tags = ['artist:imbi'] when 1 tag; or ['artist:imbi', 'skater'] when intersection of tags
    extra_tags = []

    A few examples below

    Rule34.xxx - hard restriction 1000 posts.
    If you want to download from r34:
    from_r34 = True
    '''
    #---- declaration variants
    filename = '!ids.txt'
    r_filename = '!fnames.txt'
    tags_filename = '!tags_counts.txt'
    small_multilist = []
    full_multilist = []
    from_r34 = True #False#True
    with_date = False
    save_dir = 'D:/ghd/img/'
    relevant_date = None #datetime.strptime("2023-01-01", '%Y-%m-%d')
    negative_tags = []
    extra_tags = []
    positive_tags = []
    # ----
    #---r34 tags
    positive_tags = ['nopanani']
    #positive_tags = ['jashinn']
    #positive_tags = ['kgovipositors']
    
    #positive_tags = ['egg_implantation ']
    #extra_tags = ['oviposition', 'ovipositor', 'tentacle_ovipositor',
    #              'vaginal_oviposition', 'oral_oviposition', 'anal_oviposition', 'urethral_oviposition', 'nipple_oviposition',
    #              'vaginal_egg_implantation', 'oral_egg_implantation', 'anal_egg_implantation', 'urethral_egg_implantation', 'nipple_egg_implantation',
    #              'egg_bulge', 'eggnant', 'egg_inflation']
    #---nozomi tags
    #positive_tags = ['sabamen']
    #positive_tags = ['artist:ねこみかーる']
    #extra_tags = ['pixiv_id_1522712']
    '''
    #----FOR SINGLE DOWNLOADING (USE ONLY SINGLE OR MULTI AT ONCE)
    #Unlock the lines below to load the individual tags above
    '''
    #small_multilist.extend((positive_tags, extra_tags, negative_tags))
    #full_multilist.append(small_multilist)
    '''
    #----FOR MULTI DOWNLOADING
    #Unlock one of the function and select: 1) from_r34 - true/false 2)with date - true/false

    the tags are inside multi.py
    '''
    from_r34 = False
    #with_date = False

    full_multilist = multi.get_multi(from_r34)
    #or
    #full_multilist = multi.get_multi_with_date(from_r34)
    # ---
    '''there is no need to change the code below'''
    if not from_r34:
        '''for NOZOMI.la'''
        if not full_multilist == '':
            print(full_multilist)
            for i in range(len(full_multilist)):
                #multi check date
                if with_date:
                    internal_pos, internal_ext, internal_neg, relevant_date = full_multilist[i]
                else:    
                    internal_pos, internal_ext, internal_neg = full_multilist[i]
                #очистка списка тегов перед началось проверок и загрузок
                tag_counts.clear()
                merged_dictionary = sorted_dict = dictionary1 = {}

                url_list = api.get_urls_list(internal_pos, internal_ext)#(positive_tags, extra_tags)
                url_list = list(url_list)
                url_list.sort()
                # go to dir
                if not len(url_list) == 0:
                    string_tag = ''.join(internal_pos)
                    folder_tag = re.sub(r'[<>/;,:\s]', ' ', string_tag)
                    if not os.path.exists(save_dir + folder_tag):
                        os.makedirs(save_dir + folder_tag)
                    os.chdir(save_dir + folder_tag)
                    print("Текущая директория изменилась на ", os.getcwd())
                    # загрузка файлов                   
                    if not os.path.exists(filename):
                        print('ids File not exists:', filename)
                        with HTTPConnectionPool(host='https://j.nozomi.la/', maxsize=10) as conn:
                            tasks= []
                            for post_url in url_list:
                                tasks.append(asyncio.create_task(download_async(post_url, Path.cwd(), internal_neg, relevant_date)))
                            await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач
                        
                        '''threads= []
                        with ThreadPoolExecutor(max_workers=20) as executor:
                            for post_url in url_list:
                                threads.append(executor.submit(api.download_file, post_url, Path.cwd(), internal_neg, relevant_date))'''
                        
                        '''Processes = []
                        with ProcessPoolExecutor(max_workers=16) as p_executor:
                            for post_url in url_list:
                                Processes.append(p_executor.submit(api.download_file, post_url, Path.cwd(), internal_neg, relevant_date))
                        p_executor.shutdown'''

                        


                        save_ids_to_file(url_list, filename) # Сохранение списка id в файл
                        print(f'File {filename} saved with {len(url_list)} ids')
                        # сохранение тегов
                        sorted_dict = {k: tag_counts[k] for k in sorted(tag_counts)}
                        with open(tags_filename, "w", encoding="utf-8") as file:
                            for tag, count in sorted_dict.items():
                                file.write(f"{tag}: {count}\n")
                        print(f'File {tags_filename} saved with {len(sorted_dict)} new tags')
                    else:
                        # Чтение id из файла
                        with open(filename, 'r') as file:
                            lines = file.read().splitlines()
                            list1_from_file = [str(line) for line in lines]
                        print(f'File exists: {filename} with {len(list1_from_file)} ids')
                        # Получение уникальных id из второго списка, отсутствующих в первом списке
                        list2_unique = remove_duplicates(list1_from_file, url_list)

                        tasks= []
                        for post_url in list2_unique:
                            tasks.append(asyncio.create_task(download_async(post_url, Path.cwd(), internal_neg, relevant_date)))
                        await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач


                        # Дописывание оставшихся id в файл
                        with open(filename, 'a') as file:
                            for id in list2_unique:
                                file.write(str(id) + '\n')
                        print(f'File {filename} saved with {len(list2_unique)} new ids')
                        # сохранение тегов
                        sorted_dict = {k: tag_counts[k] for k in sorted(tag_counts)}
                        with open(tags_filename, "w", encoding="utf-8") as file:
                            for tag, count in sorted_dict.items():
                                file.write(f"{tag}: {count}\n")
                        print(f'File {tags_filename} saved with {len(sorted_dict)} new tags')
    else:
        '''FOR RULE34.xxx'''
        if not full_multilist == []:
            print(full_multilist)
            for i in range(len(full_multilist)):
                #multi check date
                if with_date:
                    internal_pos, internal_ext, internal_neg, relevant_date = full_multilist[i]
                else:    
                    internal_pos, internal_ext, internal_neg = full_multilist[i]
                #очистка списка тегов перед началось проверок и загрузок
                tag_counts.clear()
                merged_dictionary = sorted_dict = dictionary1 = {}
                urls, filenames = api.r34_urls_files_list(internal_pos, internal_ext, internal_neg, relevant_date)
                urls = list(urls)
                filenames = list(filenames)
                string_tag = ''.join(internal_pos)
                folder_tag = re.sub(r'[<>;/,:\s]', ' ', string_tag)
                folder_tag = 'RULE_34 '+ folder_tag
                if not os.path.exists(save_dir + folder_tag):
                    os.makedirs(save_dir + folder_tag)
                os.chdir(save_dir + folder_tag)
                print("Текущая директория изменилась на ", os.getcwd())
                # загрузка файлов
                if not os.path.exists(filename) and not os.path.exists(r_filename):
                    print('urls File not exists:', filename)
                    print('filenames File not exists:', r_filename)
                    tasks= []
                    for i in range(len(urls)):
                        tasks.append(asyncio.create_task(r34_download_async(urls[i], filenames[i])))
                    await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач
                    save_ids_to_file(urls, filename) # Сохранение списка url в файл
                    print(f'File {filename} saved with {len(urls)} ids')
                    save_ids_to_file(filenames, r_filename) # Сохранение списка filenames в файл
                    print(f'File {r_filename} saved with {len(filenames)} ids')
                    # сохранение тегов
                    if os.path.exists(tags_filename):
                            print('tags File exists:', tags_filename)
                            # Загрузка первого словаря из файла
                            dictionary1 = load_dictionary(tags_filename)
                            # Слияние словарей
                            merged_dictionary = merge_dictionaries(dictionary1, tag_counts)
                            sorted_dict = {k: merged_dictionary[k] for k in sorted(merged_dictionary)}
                            # Сохранение словаря в файл
                            save_dictionary(merged_dictionary, tags_filename)
                            print(f'File {tags_filename} saved with {len(merged_dictionary)} tags')
                    else:
                        print('tags File not exists:', tags_filename)
                        sorted_dict = {k: tag_counts[k] for k in sorted(tag_counts)}
                        # создание нового, если не существует
                        with open(tags_filename, "w", encoding="UTF-8") as file:
                            for tag, count in sorted_dict.items():
                                file.write(f"{tag}: {count}\n")
                        print(f'File {tags_filename} saved with {len(sorted_dict)} new tags')
                else:
                    try:
                    # загрузка файлов
                        # Чтение id из файла
                        with open(filename, 'r') as file:
                            lines = file.read().splitlines()
                            list1_from_file = [str(line) for line in lines]
                        print(f'File exists: {filename} with {len(list1_from_file)} ids')
                        # Получение уникальных id из второго списка, отсутствующих в первом списке
                        urls_unique = remove_duplicates(list1_from_file, urls)
                        # Чтение id из файла
                        with open(r_filename, 'r') as file:
                            lines = file.read().splitlines()
                            list1_from_file = [str(line) for line in lines]
                        print(f'File exists: {r_filename} with {len(list1_from_file)} filenames')
                        # Получение уникальных id из второго списка, отсутствующих в первом списке
                        filenames_unique = remove_duplicates(list1_from_file, filenames)                      
                        tasks= []
                        for i in range(len(urls_unique)):
                            tasks.append(asyncio.create_task(r34_download_async(urls_unique[i], filenames_unique[i])))
                        await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач
                    #cохранение файлов
                        # Дописывание оставшихся id в файл
                        with open(filename, 'a') as file:
                            for id in urls_unique:
                                file.write(str(id) + '\n')
                        print(f'File {filename} saved with {len(urls_unique)} new ids')
                        with open(r_filename, 'a') as file:
                            for id in filenames_unique:
                                file.write(str(id) + '\n')
                        print(f'File {r_filename} saved with {len(filenames_unique)} new filenames')
                    # сохранение тегов
                        if os.path.exists(tags_filename):
                            # Загрузка первого словаря из файла
                            dictionary1 = load_dictionary(tags_filename)
                            # Слияние словарей
                            merged_dictionary = merge_dictionaries(dictionary1, tag_counts)
                            sorted_dict = {k: merged_dictionary[k] for k in sorted(merged_dictionary)}
                            # Сохранение словаря в файл
                            save_dictionary(merged_dictionary, tags_filename)
                            print(f'File {tags_filename} saved with {len(merged_dictionary)} tags')
                        else:
                            sorted_dict = {k: tag_counts[k] for k in sorted(tag_counts)}
                            # создание нового, если не существует
                            with open(tags_filename, "w", encoding="UTF-8") as file:
                                for tag, count in sorted_dict.items():
                                    file.write(f"{tag}: {count}\n")
                            print(f'File {tags_filename} saved with {len(sorted_dict)} new tags')

                    except FileNotFoundError:
                        print('the file of urls or filenames doesnt exist. You should delete another file and retry')
                        exit()


if __name__ == '__main__':
    asyncio.run(runner())