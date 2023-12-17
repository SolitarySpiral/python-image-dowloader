# python image-downloader

nozomi.la API in Python.
with rule34 API now!

# Release 3.3.0
- Исправление асинхронной загрузки.
- Добавлен файл для проверки наличия дублей изображений, которые используются в разных постах с одинаковым названием. (большая нагрузка на систему)
- Пофикшена проблема с повторной загрузкой, в которой создавались дубли файлов с другим порядковым номером.
- Ещё больше тегов в мульти. (18+)

``` python
filename = '!ids.txt'
r_filename = '!fnames.txt'
tags_filename = '!tags_counts.txt'
```
- В мульти указано свыше 40 артистов и наборов тегов для загрузки общим объемом свыше 180к файлов и 80+ гигабайт данных. 

## The original author and code
https://github.com/Alfa-Q/python-nozomi

# How to use
- Не рекомендуется скачивать очень крупные теги, возвращающие в результате более 10 тысяч id постов. Например "loli", "animated"
- При скачивании с nozomi количество файлов может превышать количество постов. Это норма. С rule34: 1 пост - 1 файл, но размер файлов значительно больше.
- Изменение лимита для семафоров может привести к непредсказуемым последствиям, вплоть до сломанных файлов или бана вашего IP.
- rule34 работает постранично для АПИ. Если получать не по 100 результатов, в набор постов могут попасть не все файлы, могут возникать непредвиденные ошибки. Лучше подождать пару минут, пока идет получение списка постов, чем недождаться и словить "api abuse"
- В ```__main__``` сохранен код для многопоточной загрузки. При желании, можно использовать его, вместо асинхронного вызова для всего списка постов.
- Для работы с данным ПО достаточно запустить ```__main__``` файл в VS Code. Если не запускается, вероятно, нужно установить недостающие библиотеки в python. например asyncio, aiohttp, aiofiles, bs4 (beautiful soup)
- Для первичного запуска рекомендуется сначала использовать только позитивный тег, без негативных и экстра тегов в режиме single. Это облегчит освоение в коде основного файла, и как оно работает.
## Rule34 API
### Мультизагрузка
``` python
'''
----FOR SINGLE DOWNLOADING (USE ONLY SINGLE OR MULTI AT ONCE)
Unlock the lines below to load the individual tags above
'''
#small_multilist.extend((positive_tags, extra_tags, negative_tags))
#full_multilist.append(small_multilist)
'''
----FOR MULTI DOWNLOADING
Unlock one of the function and select: 1) from_r34 - true/false 2)with date - true/false

the tags are inside multi.py
'''
from_r34 = True
with_date = True

#full_multilist = multi.get_multi(from_r34)
#or
full_multilist = multi.get_multi_with_date(from_r34)
# ---
```
- мультизагрузка для NOZOMI - ```from_r34 = False```
### Скачать посты c rule34
``` python
from_r34 = True
save_dir = 'D:/ghd/img/'
relevant_date = None
negative_tags = []
extra_tags = []
#---r34 tags
positive_tags = ['nopanani'] 
```
## Nozomi API
### Скачать все посты по одному тегу:
```python
from_r34 = False
save_dir = 'D:/ghd/img/'
relevant_date = None
negative_tags = []
positive_tags = ['artist:imbi']
extra_tags = []
```
или
```python
positive_tags = ['crumbles']
```
### Скачать посты по одному тегу, новее конкретной даты:
```python
from_r34 = False
relevant_date = datetime.strptime("2023-07-11", '%Y-%m-%d')
negative_tags = []
positive_tags = ['artist:imbi']
extra_tags = []
```
### Скачать посты по пересечению двух тегов и с исключением другого:
```python
from_r34 = False
relevant_date = None
negative_tags = ['butt']
positive_tags = ['artist:imbi', 'skater']
extra_tags = []

#positive_tags = ['ponchi', 'uzumaki_himawari']
```
### Скачать посты по одному персонажу, совместив разные варианты тегов персонажа (японские теги тоже работают):
```python
from_r34 = False
relevant_date = None
negative_tags = []
positive_tags = ['Riley_Anderson']
extra_tags = ['Riley', 'rileyandersen']

#positive_tags = ['Vanellope']
#extra_tags = ['vanellope', 'vanellope_von_schweetz']

#positive_tags = ['Sarah']
#extra_tags = ['sarah_(the_last_of_us)', 'sarah_miller']

#positive_tags = ['marie_rose']
#extra_tags = ['マリー・ローズ','marie', 'marierose']
```
### Скачать все посты одного автора более углубленно:
```python
from_r34 = False
relevant_date = None
negative_tags = []
positive_tags = ['higegepon']
extra_tags = ['artist:ひ~げぇぽん','pixiv_id_54698934']

#positive_tags = ['opossumachine']
#extra_tags = ['artist:PossumMachine⚠️']

#positive_tags = ['artist:7738']
#extra_tags = ['hebe', 'pixiv_id_66553761']

#positive_tags = ['artist:ボッシー']
#extra_tags = ['pixiv_id_13450661']
```
### Скачать все посты нескольких авторов, где их общие работы схлопываются и скачиваются единожды:
```python
from_r34 = False
positive_tags = ['lesdias']
extra_tags = ['artist:SPICYdias', 'pixiv_id_15079627', 'artist:irispoplar', 'irispoplar', 'pixiv_id_25423811']
```
