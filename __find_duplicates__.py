from difflib import SequenceMatcher
import os
from concurrent.futures import ProcessPoolExecutor

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()# используем quick_ratio, оно быстрее чем просто ratio, но чуть менее точная, слишком неточная

def deleter(files):
    '''сравниваем каждый элемент из списка файлов с другим, если есть точнось 0.9'''
    for word1 in files:
        for word2 in files:
            if word1 != word2 and similar(word1,word2)>= 0.9:
                print(word1, word2)
                os.remove(word2)
                files.remove(word2)
                print('Удалено', word2)

if __name__ == '__main__':
    #a = '2023-12-05 202800-1-fe892dea6535776e171fc77de831b2a4b3683a6fe635032a832fb9cb723e005d.jpg'
    #b = '2023-12-05 084526-1-fe892dea6535776e171fc77de831b2a4b3683a6fe635032a832fb9cb723e005d.jpg'
    #print(similar(a, b))

    d = 'D:/ghd/img/' #папка с папками других изображений
    folders = os.listdir(d) #получаем список папок
    for folder in folders: #к каждой папке применяем поиск дубликатов используя пул процессов
        os.chdir(d+folder)
        print(os.getcwd())
        filelist = os.listdir(d+folder)
        with ProcessPoolExecutor(os.cpu_count()) as ex:
            ex.submit(deleter,filelist)
