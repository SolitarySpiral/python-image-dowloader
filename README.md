# python image-downloader

[![Build Status](https://travis-ci.com/Alfa-Q/python-nozomi.svg?token=NAcpuTjLC6CrUpWrqz9p&branch=master)](https://travis-ci.com/Alfa-Q/python-nozomi)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/20c7f3716811466c9e2d55786885951e)](https://app.codacy.com/gh/Alfa-Q/python-nozomi/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/20c7f3716811466c9e2d55786885951e)](https://app.codacy.com/gh/Alfa-Q/python-nozomi/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![PyPI version](https://badge.fury.io/py/python-nozomi.svg)](https://badge.fury.io/py/python-nozomi)
[![Python version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-green)](https://www.python.org/downloads/release/python-370/)

nozomi.la API in Python.
with rule34 API now!

# Release 3.2.0
- Code rewrite
- Add multiprocessing and folder to download
- Russian comments for messages
- Readable folders with `artist:Name` tags in `artist Name`
- Main file to launch is `__main__`
- isues resolved

## The original author and code
https://github.com/Alfa-Q/python-nozomi

# How to use
## Rule34 API
### Скачать посты c rule34
``` python
workers = 20
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
workers = 20
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
workers = 20
from_r34 = False
relevant_date = datetime.strptime("2023-07-11", '%Y-%m-%d')
negative_tags = []
positive_tags = ['artist:imbi']
extra_tags = []
```
### Скачать посты по пересечению двух тегов и с исключением другого:
```python
workers = 20
from_r34 = False
relevant_date = None
negative_tags = ['butt']
positive_tags = ['artist:imbi', 'skater']
extra_tags = []

#positive_tags = ['ponchi', 'uzumaki_himawari']
```
### Скачать посты по одному персонажу, совместив разные варианты тегов персонажа (японские теги тоже работают):
```python
workers = 20
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
workers = 20
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
workers = 20
from_r34 = False
positive_tags = ['lesdias']
extra_tags = ['artist:SPICYdias', 'pixiv_id_15079627', 'artist:irispoplar', 'irispoplar', 'pixiv_id_25423811']
```
