import os, re
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
from helpers import save_ids_to_file, remove_duplicates, tag_counts, load_dictionary, save_dictionary, merge_dictionaries
import multi, api
r34Py = rule34Py()
semaphoreNozomi = asyncio.Semaphore(24) #Not recommends change it
semaphore34 = asyncio.Semaphore(8) #Not recommends change it



async def r34_download_async(sess, url, file_name):
        async with semaphore34:
            await api.async_r34_download_file(sess, url, file_name)

async def runner():
    '''You should always have the following variables filled in in one instance for 1 upload
    from_r34 = True/False
    save_dir = 'D:/ghd/img/'
    relevant_date = use None or datetime.strptime("2023-07-11", '%Y-%m-%d')
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
    tags_filename = '!tags_counts.txt'
    full_multilist = []
    save_dir = 'D:/ghd/img/'

    '''
    #----FOR MULTI DOWNLOADING
    #Unlock one of the function and select: 1) from_r34 - true/false 2)with date - true/false

    the tags are inside multi.py
    '''
    from_r34 = True
    full_multilist = multi.get_multi(from_r34)

    # ---
    '''there is no need to change the code below'''
    if not from_r34:
        '''for NOZOMI.la'''
        if full_multilist != '':
            print(full_multilist)
            for i in range(len(full_multilist)):
                #multi check date   
                internal_pos, internal_ext, internal_neg = full_multilist[i]
                #очистка списка тегов перед началось проверок и загрузок
                tag_counts.clear()
                sorted_dict = {}

                url_list = api.get_urls_list(internal_pos, internal_ext)
                url_list = list(url_list)
                url_list.sort()
                # go to dir
                if len(url_list) != 0:
                    string_tag = ''.join(internal_pos)
                    folder_tag = re.sub(r'[<>/;,:\s]', ' ', string_tag)
                    if not os.path.exists(save_dir + folder_tag):
                        os.makedirs(save_dir + folder_tag)
                    os.chdir(save_dir + folder_tag)
                    print("Текущая директория изменилась на ", os.getcwd())
                    # загрузка файлов                   
                    if not os.path.exists(filename):
                        print('ids File not exists:', filename)
                        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
                            async with semaphoreNozomi:
                                tasks= []
                                for post_url in url_list:
                                    tasks.append(asyncio.create_task(api.async_nozomi_download_file(session, semaphoreNozomi, post_url, internal_neg)))
                                await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач'''
                        

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
                        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
                            async with semaphoreNozomi:
                                tasks= []
                                for post_url in list2_unique:
                                    tasks.append(asyncio.create_task(api.async_nozomi_download_file(session, semaphoreNozomi, post_url, internal_neg)))
                                await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач'''


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
        if full_multilist != []:
            print(full_multilist)
            for i in range(len(full_multilist)):
                #multi check date
                internal_pos, internal_ext, internal_neg = full_multilist[i]
                #очистка списка тегов перед началось проверок и загрузок
                tag_counts.clear()
                sorted_dict = {}
                urls, filenames = api.r34_urls_files_list(internal_pos, internal_ext, internal_neg)
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
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
                    async with semaphore34:
                        tasks= []
                        for i in range(len(urls)):
                            tasks.append(asyncio.create_task(api.async_r34_download_file(session, semaphore34, urls[i], filenames[i])))
                        await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач'''

                    '''threads= []
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        for i in range(len(urls)):
                                threads.append(executor.submit(api.r34_download, urls[i], filenames[i]))'''
                    
                    '''save_ids_to_file(urls, filename) # Сохранение списка url в файл
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
                        with open(tags_filename, "w", encoding="utf-8") as file:
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
                        filenames_unique = remove_duplicates(list1_from_file, filenames) '''

                    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
                        async with semaphore34:
                            tasks= []
                            for i in range(len(urls)):
                                tasks.append(asyncio.create_task(api.async_r34_download_file(session, semaphore34, urls[i], filenames[i])))
                            await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач'''

                    '''threads= []
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        for i in range(len(urls_unique)):
                            threads.append(executor.submit(api.r34_download, urls_unique[i], filenames_unique[i]))'''

                    '''#cохранение файлов
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
                            with open(tags_filename, "w", encoding="utf-8") as file:
                                for tag, count in sorted_dict.items():
                                    file.write(f"{tag}: {count}\n")
                            print(f'File {tags_filename} saved with {len(sorted_dict)} new tags')

                    except FileNotFoundError:
                        print('the file of urls or filenames doesnt exist. You should delete another file and retry')
                        exit()'''


if __name__ == '__main__':
    asyncio.run(runner())