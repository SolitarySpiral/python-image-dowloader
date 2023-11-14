import api
import os, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from rule34Py import rule34Py
from rule34Py.__vars__ import __headers__
r34Py = rule34Py()


#url_list = []

 
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
    workers = 20
    from_r34 = True #False#True
    save_dir = 'D:/ghd/img/'
    relevant_date = None #datetime.strptime("2023-07-11", '%Y-%m-%d')
    negative_tags = [] #['butt']
    extra_tags = ['jashinn']
    #---r34 tags
    
    positive_tags = ['nopanani'] 
    #positive_tags = ['jashinn']
    #positive_tags = ['kgovipositors']
    

    #---nozomi tags
    #positive_tags = ['artist:imbi'] #['artist:IncredibleChris']
    #extra_tags = [] #['artist:Xentho','sherry']
    
    #positive_tags = ['artist:CTFBM']
    #extra_tags = ['pixiv_id_2534125']

    #positive_tags = ['konarofu']
    
    #positive_tags = ['atela']

    #positive_tags = ['mingaru']

    #positive_tags = ['neku_oneneko']

    #positive_tags = ['Riley_Anderson']
    #extra_tags = ['Riley', 'rileyandersen']

    #positive_tags = ['Vanellope']
    #extra_tags = ['vanellope', 'vanellope_von_schweetz']

    #positive_tags = ['Sarah']
    #extra_tags = ['sarah_(the_last_of_us)', 'sarah_miller']

    #positive_tags = ['higegepon']
    #extra_tags = ['artist:ひ~げぇぽん','pixiv_id_54698934']

    #positive_tags = ['marie_rose']
    #extra_tags = ['マリー・ローズ','marie', 'marierose']

    #positive_tags = ['opossumachine']
    #extra_tags = ['artist:PossumMachine⚠️']

    #positive_tags = ['artist:7738']
    #extra_tags = ['hebe', 'pixiv_id_66553761']

    #positive_tags = ['artist:ボッシー']
    #extra_tags = ['pixiv_id_13450661']

    #positive_tags = ['artist:omsgarou']
    #extra_tags = ['pixiv_id_2297160']

    #positive_tags = ['artist:ターちゃん']
    #extra_tags = ['pixiv_id_947930']

    #positive_tags = ['artist:Libidoll']
    #extra_tags = ['pixiv_id_1043474']

    #positive_tags = ['artist:AliceBunnie']
    #extra_tags = ['pixiv_id_25867890']

    #positive_tags = ['lesdias']
    #extra_tags = ['artist:SPICYdias', 'pixiv_id_15079627', 'artist:irispoplar', 'irispoplar', 'pixiv_id_25423811']

    # pos only

    #positive_tags = ['crumbles']
    #positive_tags = ['ponchi', 'uzumaki_himawari']
    #positive_tags = ['gawr_gura']

    '''there is no need to change the code below'''
    if not from_r34:
        '''for NOZOMI.la'''
        url_list = api.get_urls_list(positive_tags, extra_tags)
        url_list = list(url_list)
        url_list.sort()
        # go to dir
        if not len(url_list) == 0:
            string_tag = ''.join(positive_tags)
            folder_tag = re.sub(r'[;,:\s]', ' ', string_tag)
            if not os.path.exists(save_dir + folder_tag):
                os.makedirs(save_dir + folder_tag)
            os.chdir(save_dir + folder_tag)
            print("Текущая директория изменилась на ", os.getcwd())
            threads= []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                for post_url in url_list:
                    threads.append(executor.submit(api.download_file, post_url, Path.cwd(), negative_tags, relevant_date))
                    
                for task in as_completed(threads):
                    pass
    else:
        #search = r34Py.search(positive_tags, ignore_max_limit=True)
        urls, filenames = api.r34_urls_files_list(positive_tags, extra_tags)
        urls = list(urls)
        filenames = list(filenames)
        string_tag = ''.join(positive_tags)
        folder_tag = re.sub(r'[;,:\s]', ' ', string_tag)
        folder_tag = 'RULE__34 '+ folder_tag
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
    runner()
