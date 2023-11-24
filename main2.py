import os, re
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
r34Py = rule34Py()
semaphore = asyncio.Semaphore(20)
import api

async def download_async(post_url, path, internal_neg, relevant_date):
        async with semaphore:
            await api.async_download_file(post_url, path, internal_neg, relevant_date)

async def runner():
    #---- variants
    small_multilist = []
    full_multilist = []
    workers = 100
    from_r34 = False 
    save_dir = 'D:/ghd/img/'
    relevant_date = None
    negative_tags = [] 
    extra_tags = []
    positive_tags = []
    # ----
    positive_tags = ['higegepon']
    extra_tags = ['artist:ひ~げぇぽん','pixiv_id_54698934']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #----
    if not from_r34:
        '''for NOZOMI.la'''
        if not full_multilist == '':
            print(full_multilist)
            for i in range(len(full_multilist)):
                internal_pos, internal_ext, internal_neg = full_multilist[i]
                url_list = api.get_urls_list(internal_pos, internal_ext)#(positive_tags, extra_tags)
                url_list = list(url_list)
                url_list.sort()
                if not len(url_list) == 0:
                    string_tag = ''.join(internal_pos)
                    folder_tag = re.sub(r'[<>/;,:\s]', ' ', string_tag)
                    if not os.path.exists(save_dir + folder_tag):
                        os.makedirs(save_dir + folder_tag)
                    os.chdir(save_dir + folder_tag)
                    print("Текущая директория изменилась на ", os.getcwd())
                    tasks= []
                    for post_url in url_list:
                        tasks.append(asyncio.create_task(download_async(post_url, Path.cwd(), internal_neg, relevant_date)))
                    await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач
    
                    '''threads= []
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor(max_workers=workers) as executor:
                        for post_url in url_list:
                            task = loop.run_in_executor(executor, download_async, post_url, Path.cwd(), internal_neg, relevant_date)
                            threads.append(task)
                        loop.run_until_complete(asyncio.gather(*threads))'''
    else:
        '''FOR RULE34.xxx'''
        if not full_multilist == []:
            print(full_multilist)
            for i in range(len(full_multilist)):
                internal_pos, internal_ext, internal_neg = full_multilist[i]
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
                threads= []
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    for i in range(len(urls)):#for result in search:
                        try:
                            if not (filenames[i] == '' and urls[i] == ''):
                                threads.append(executor.submit(api.r34_download, urls[i], filenames[i]))
                        except Exception as ex:
                            print(ex)
                            pass
                        
                    for task in as_completed(threads):
                        pass
if __name__ == '__main__':
    asyncio.run(runner())
