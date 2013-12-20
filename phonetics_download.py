'''
Created on 2013-12-20

@author: bn
'''

# -*- coding: gbk -*-
import re

try: 
    input = raw_input
except NameError:
    pass

try:
    import urllib.request
    #import urllib.parse
except ImportError:
    import urllib
    urllib.request = __import__('urllib2')
    urllib.parse = __import__('urlparse')
 
urlopen = urllib.request.urlopen
request = urllib.request.Request

def get_content_from_url(url):
    attempts = 0
    content = ''

    while attempts < 5:
        try:
            content = urlopen(url).read().decode('utf-8', 'ignore')
            break
        except Exception as e:
            attempts += 1
            print(e)

    return content

    
def download_from_aiciba(query, path):
    """Download full size images from Bing image search.
 
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    BASE_URL = 'http://www.aiciba.com/'+query
    content = get_content_from_url(BASE_URL)
    phonetic_list = re.findall(
            "\[</strong><strong lang=\"EN-US\" xml:lang=\"EN-US\">([^<>/]*)</strong><strong>\]", content, re.M | re.S)
    print(phonetic_list)

    file = open(path, "a")
    for item in phonetic_list:
        file.write(item.encode('utf-8')+'\n')
    file.close()
 
download_from_aiciba("person", "phonetics.log")
