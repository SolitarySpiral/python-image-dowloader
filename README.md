# python image-downloader

nozomi.la API with rule34 API in Python.
- Выведено из эксплуатации. Нецелевое решение. nozomi.la больше не рабоает.

# Release 4.1.0
- interactive launch
- the ability to remove duplicates
- complete refactoring of the application
- The multi lists over 40 artists and tag sets for uploading with a total volume of over 200k files and 100+ gigabytes of data.

# Some recomends
- It is not recommended to download very large tags that return more than 10 thousand post ids as a result. For example, "loli", "animated"
- When downloading from nozomi, the number of files may exceed the number of posts. This is the norm. With rule34: 1 post - 1 file, but the file size is much larger.
- Changing the limit for downloading can lead to unpredictable consequences, including broken files or your IP being banned. (recomends 3-10)
- rule34 works page by page for API. If you receive more than 100 results, not all files may be included in the set of posts, and unexpected errors may occur and catch "api abuse"
# How to start 
- Create venv with requirements.txt in Visual Studio Code.
- To work with this software, it is enough to run ``main.py `` file in VS Code.
- You can change the list of artists and tags for downloading in ``multi.py``
