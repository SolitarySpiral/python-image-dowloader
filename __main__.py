import api
import os, re
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
r34Py = rule34Py()



 
def runner():
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
    small_multilist = []
    full_multilist = []
    workers = 20
    from_r34 = True #False#True
    save_dir = 'D:/ghd/img/'
    relevant_date = None #datetime.strptime("2023-01-01", '%Y-%m-%d')
    negative_tags = [] #['butt']
    extra_tags = []
    #---r34 tags
    #positive_tags = ['<3_eyes', 'diane_foxington']
    #positive_tags = ['nopanani']
    #positive_tags = ['jashinn']
    #positive_tags = ['kgovipositors']
    

    #---nozomi tags
    #positive_tags = ['artist:imbi']
    #positive_tags = ['artist:IncredibleChris']
    positive_tags = ['murahachiro']
    #extra_tags = [] #['artist:Xentho','sherry']
    
    #positive_tags = ['artist:CTFBM']
    #extra_tags = ['pixiv_id_2534125']

    #positive_tags = ['konarofu']
    
    #positive_tags = ['atela']

    #positive_tags = ['mingaru']

    #positive_tags = ['neku_oneneko']

    #----FOR SINGLE DOWNLOADING (USE ONLY SINGLE OR MULTI AT ONCE)
    #Unlock the lines below to load the individual tags above

    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    #----

    '''
    ===Multidownloading  Rule 34===

    You should input your tags in positive_tags, extra_tags and\or negative_tags. Next 3 strings don't change.
    For good work You have to cancel the list "small_multilist = []" at the end

    positive_tags = ['nopanani']
    extra_tags = []
    negative_tags = ['big_ass', 'animated']
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    '''
    ''' # <-- HERE IS UNLOCK MULTI for RULE 34
    from_r34 = True
    #1
    positive_tags = ['nopanani']
    extra_tags = []
    negative_tags = ['big_ass', 'animated']
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #2
    positive_tags = ['jashinn']
    extra_tags = []
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #3
    positive_tags = ['kgovipositors']
    extra_tags = []
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []'''
    '''
    ===Multidownloading NOZOMI===
    
    You should input your tags in positive_tags, extra_tags and\or negative_tags. Next 3 strings don't change.
    For good work You have to cancel the list "small_multilist = []" at the end

    positive_tags = ['Riley_Anderson']
    extra_tags = ['Riley', 'rileyandersen', 'riley_andersen']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    '''
    ''' # <-- HERE IS UNLOCK MULTI for NOZOMI
    from_r34 = False # <-- stay it here
    #1
    positive_tags = ['Riley_Anderson']
    extra_tags = ['Riley', 'rileyandersen', 'riley_andersen']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #2
    positive_tags = ['Vanellope']
    extra_tags = ['vanellope', 'vanellope_von_schweetz']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #3
    positive_tags = ['Sarah']
    extra_tags = ['sarah_(the_last_of_us)', 'sarah_miller']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #4
    positive_tags = ['higegepon']
    extra_tags = ['artist:ひ~げぇぽん','pixiv_id_54698934']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #5
    positive_tags = ['marie_rose']
    extra_tags = ['マリー・ローズ','marie', 'marierose']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #6
    positive_tags = ['opossumachine']
    extra_tags = ['artist:PossumMachine⚠️']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #7
    positive_tags = ['artist:7738']
    extra_tags = ['hebe', 'pixiv_id_66553761']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #8
    positive_tags = ['artist:ボッシー']
    extra_tags = ['pixiv_id_13450661']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #9
    positive_tags = ['artist:omsgarou']
    extra_tags = ['pixiv_id_2297160']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #10
    positive_tags = ['artist:ターちゃん']
    extra_tags = ['pixiv_id_947930']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #11
    positive_tags = ['artist:Libidoll']
    extra_tags = ['pixiv_id_1043474']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #12
    positive_tags = ['artist:AliceBunnie']
    extra_tags = ['pixiv_id_25867890']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #13
    positive_tags = ['lesdias']
    extra_tags = ['artist:SPICYdias', 'pixiv_id_15079627', 'artist:irispoplar', 'irispoplar', 'pixiv_id_25423811']
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #14
    positive_tags = ['flatculture']
    extra_tags = []
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #15
    positive_tags = ['asakuraf']
    extra_tags = []
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    #15
    positive_tags = ['crumbles']
    extra_tags = []
    negative_tags = []
    small_multilist.extend((positive_tags, extra_tags, negative_tags))
    full_multilist.append(small_multilist)
    small_multilist = []
    '''
    # pos only
    #positive_tags = ['ponchi', 'uzumaki_himawari']
    #positive_tags = ['gawr_gura']

    '''there is no need to change the code below'''
    if not from_r34:
        '''for NOZOMI.la'''
        if not full_multilist == '':
            print(full_multilist)
            for i in range(len(full_multilist)):
                internal_pos, internal_ext, internal_neg = full_multilist[i]
                url_list = api.get_urls_list(internal_pos, internal_ext)#(positive_tags, extra_tags)
                url_list = list(url_list)
                url_list.sort()
                # go to dir
                if not len(url_list) == 0:
                    string_tag = ''.join(internal_pos)
                    folder_tag = re.sub(r'[<>;,:\s]', ' ', string_tag)
                    if not os.path.exists(save_dir + folder_tag):
                        os.makedirs(save_dir + folder_tag)
                    os.chdir(save_dir + folder_tag)
                    print("Текущая директория изменилась на ", os.getcwd())
                    threads= []
                    with ThreadPoolExecutor(max_workers=workers) as executor:
                        for post_url in url_list:
                            threads.append(executor.submit(api.download_file, post_url, Path.cwd(), internal_neg, relevant_date))
                            
                        for task in as_completed(threads):
                            pass
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
                folder_tag = re.sub(r'[<>;,:\s]', ' ', string_tag)
                folder_tag = 'RULE_34 '+ folder_tag
                if not os.path.exists(save_dir + folder_tag):
                    os.makedirs(save_dir + folder_tag)
                os.chdir(save_dir + folder_tag)
                print("Текущая директория изменилась на ", os.getcwd())
                threads= []
                #print(urls)
                #print(filenames)
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
    runner()
