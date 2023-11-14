__version__tuple__ = ("1", "4", "10")
__author__ = ("b3yc0d3")
__email__ = ("b3yc0d3@gmail.com")

__version__ = ".".join(__version__tuple__) # xx.xx.xx


# Variables
__base_url__ = "https://rule34.xxx/"
__api_url__ = "https://api.rule34.xxx/"
#__useragent__ = f"Mozilla/5.0 (compatible; rule34Py/{__version__})"     'Accept-Encoding': 'gzip, deflate, br',
# 'Referer':'https://wimg.rule34.xxx//',
__headers__ = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
    'Accept': 'text/html, application/xhtml+xml, application/xml, application/json;q=0.9, image/webp, */*;q=0.8',
    #'Accept-Encoding': 'gzip, deflate, br'
}
