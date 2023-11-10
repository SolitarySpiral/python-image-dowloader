# python-nozomi

[![Build Status](https://travis-ci.com/Alfa-Q/python-nozomi.svg?token=NAcpuTjLC6CrUpWrqz9p&branch=master)](https://travis-ci.com/Alfa-Q/python-nozomi)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/20c7f3716811466c9e2d55786885951e)](https://app.codacy.com/gh/Alfa-Q/python-nozomi/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/20c7f3716811466c9e2d55786885951e)](https://app.codacy.com/gh/Alfa-Q/python-nozomi/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![PyPI version](https://badge.fury.io/py/python-nozomi.svg)](https://badge.fury.io/py/python-nozomi)
[![Python version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-green)](https://www.python.org/downloads/release/python-370/)

nozomi.la API in Python.

## Huge my own update 3.0.0
- Code rewrite
- Add multiprocessing and folder to download
- Russian comments for messages
- Readable folders with `artist:Name` tags in `artist Name`
- Main file to launch is `__main__`

1. Select dir to load images
```
save_dir = 'D:/ghd/img/'
```
2. Input positiv tag (multiple tags doesn't work, only one) (and extra tag, to down load 2 simple tag to one folder)
3. Black list tags (doesn't work)
4. Run and wait.

- original author and code https://github.com/Alfa-Q/python-nozomi

## Features

- Retrieving media posts
- Downloading media

## Installation

```
$ pip install python-nozomi
```

## Upgrade

```
$ pip install python-nozomi --upgrade
```

## Example Usage

Retrieve and download a single post provided a URL

```python
from pathlib import Path
from nozomi import api

url = 'https://nozomi.la/post/26905532.html#veigar'

# Retrieve post metadata using the URL
post = api.get_post(url)

# Download the post
api.download_media(post, Path.cwd())
```

Retrieve and download multiple posts provided a list of URLs

```python
from pathlib import Path
from nozomi import api

urls = [
    'https://nozomi.la/post/26905532.html#veigar',
    "https://nozomi.la/post/26932594.html#cho'gath",
    'https://nozomi.la/post/25802243.html#nautilus'
]

# Retrieve all of the post metadata using the URLs
posts = api.get_posts(urls)

# Download the posts
for post in posts:
    api.download_media(post, Path.cwd())
```

Retrieve and download all posts containing certain tags

```python
# The tags that the posts retrieved must contain
positive_tags = ['veigar', 'wallpaper']

# Gets all posts with the tags 'veigar', 'wallpaper'
for post in api.get_posts_with_tags(positive_tags):
    api.download_media(post, Path.cwd())
```

Retrieve all posts containing certain tags, ignoring blacklisted tags

```python
# The blacklisted tags
negative_tags = ['chogath']

# Gets all posts with the tags 'veigar' and 'wallpaper' without the 'chogath' tag.
for post in api.get_posts_with_tags(positive_tags, negative_tags):
    api.download_media(post, Path.cwd())
```
