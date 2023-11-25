import os, re
from datetime import datetime
from pathlib import Path
import asyncio
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
import multi
r34Py = rule34Py()
semaphoreNozomi = asyncio.Semaphore(20) #Not recommends change it
semaphore34 = asyncio.Semaphore(10) #Not recommends change it
import api

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
    #positive_tags = ['nopanani']
    positive_tags = ['jashinn']
    #positive_tags = ['kgovipositors']
    
    #positive_tags = ['egg_implantation ']
    #extra_tags = ['oviposition', 'ovipositor', 'vaginal_oviposition', 'oral_oviposition', 'anal_oviposition', 'urethral_oviposition', 'nipple_oviposition','vaginal_egg_implantation', 'oral_egg_implantation', 'anal_egg_implantation', 'urethral_egg_implantation', 'nipple_egg_implantation','egg_bulge', 'eggnant', 'egg_inflation']
    #---nozomi tags
    #positive_tags = ['artist:IncredibleChris']
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
    from_r34 = True
    with_date = True

    #full_multilist = multi.get_multi(from_r34)
    #or
    full_multilist = multi.get_multi_with_date(from_r34)
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
                    tasks= []
                    for post_url in url_list:
                        tasks.append(asyncio.create_task(download_async(post_url, Path.cwd(), internal_neg, relevant_date)))
                    await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач
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
                tasks= []
                for i in range(len(urls)):
                    tasks.append(asyncio.create_task(r34_download_async(urls[i], filenames[i])))
                await asyncio.gather(*tasks) # ожидает результаты выполнения всех задач
                #threads= []
                #with ThreadPoolExecutor(max_workers=workers) as executor:
                #    for i in range(len(urls)):#for result in search:
                #        try:
                #            if not (filenames[i] == '' and urls[i] == ''):
                #                threads.append(executor.submit(api.r34_download, urls[i], filenames[i]))
                #        except Exception as ex:
                #            print(ex)
                #            pass
                #        
                #    for task in as_completed(threads):
                #        pass


if __name__ == '__main__':
    asyncio.run(runner())
