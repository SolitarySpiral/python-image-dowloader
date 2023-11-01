"""Test the functionality of the api functions."""

import os
from pathlib import Path

import pytest

from nozomi import api
from nozomi.data import Post


@pytest.mark.integration
@pytest.mark.parametrize('url', [
    'https://nozomi.la/post/26905532.html#veigar',
    "https://nozomi.la/post/26932594.html#cho'gath",
    'https://nozomi.la/post/25802243.html#nautilus'
])
def test_get_post_single_img(url: str):
    post = api.get_post(url)
    assert isinstance(post, Post)


@pytest.mark.integration
@pytest.mark.parametrize('url', [
    'https://nozomi.la/post/25937459.html#pixiv_id_31112502'
])
def test_get_post_multi_img(url: str):
    post = api.get_post(url)
    assert isinstance(post, Post)
    assert len(post.imageurls) > 1


@pytest.mark.integration
@pytest.mark.parametrize('urls', [
    ['https://nozomi.la/post/490332.html'],
    ['https://nozomi.la/post/490332.html', 'https://nozomi.la/post/26652067.html'],
    ['https://nozomi.la/post/490332.html', 'https://nozomi.la/post/26652067.html', 'https://nozomi.la/post/4067925.html']
])
def test_get_posts_single_img(urls):
    count = 0
    for post in api.get_posts(urls):
        count += 1
        assert isinstance(post, Post)
    assert len(urls) == count


@pytest.mark.integration
@pytest.mark.parametrize('positive_tags', [
    (['akali', 'sakimichan']),
    (['veigar'])
])
def test_retrieval_positive_tags(positive_tags):
    for post in api.get_posts_with_tags(positive_tags=positive_tags, negative_tags=[]):
        assert isinstance(post, Post)


@pytest.mark.integration
@pytest.mark.parametrize('positive_tags, negative_tags', [
    (['akali', 'sakimichan'], ['nudity']),
    (['veigar'], ['nudity'])
])
def test_retrieval_negative_tags(positive_tags, negative_tags):
    for post in api.get_posts_with_tags(positive_tags=positive_tags, negative_tags=negative_tags):
        assert isinstance(post, Post)


@pytest.mark.integration
@pytest.mark.parametrize('positive_tags, negative_tags', [
    (['akali', 'sakimichan'], [])
])
def test_download_single_img(positive_tags, negative_tags):
    repeat = 10
    for post in api.get_posts_with_tags(positive_tags=positive_tags, negative_tags=negative_tags):
        [image_name] = api.download_media(post, Path.cwd())
        os.remove(Path.cwd().joinpath(image_name))
        repeat -= 1
        if repeat == 0:
            break


@pytest.mark.integration
@pytest.mark.parametrize('url', [
    'https://nozomi.la/post/25937459.html#pixiv_id_31112502'
])
def test_download_multi_img(url):
    post = api.get_post(url)
    assert len(post.imageurls) > 0
    image_names = api.download_media(post, Path.cwd())
    assert len(image_names) == len(post.imageurls)
    for image_name in image_names:
        os.remove(Path.cwd().joinpath(image_name))
