'''
Created on 2013-12-20

@author: bn
'''

# -*- coding: gbk -*-

import re
from crike_django.models import Word

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

    
def download_from_aiciba(word):
    """Download full size images from Bing image search.
 
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    BASE_URL = 'http://www.aiciba.com/'+word.name
    content = get_content_from_url(BASE_URL)

    phonetics_list = re.findall(
            "\[</strong><strong lang=\"EN-US\" xml:lang=\"EN-US\">([^<>/]*)</strong><strong>\]", content, re.M | re.S)
    print(phonetics_list)
    if len(phonetics_list) > 0:
        word.phonetics =  phonetics_list[0]

    mean_list = []
    mean_span_list = re.findall('<span class=\"label_list\">.*</span>', content, re.M | re.S)
    for mean_span in mean_span_list:
        mean_list.append(re.findall('<label>([^<>/]*)</label>', mean_span, re.M | re.S))
    print(mean_list)
    word.mean = mean_list[0]

    pos_list = re.findall('<strong class=\"fl\">([^<>/]*)</strong>', content, re.M | re.S)
    print(pos_list)
    word.pos = pos_list
 
def download_word(wordname):
    word = Word(name=wordname)
    download_from_aiciba(word)
    return word

#download_from_aiciba("nice")

