'''
Created on 2013-12-5

@author: bn
'''

# -*- coding: utf-8 -*-

import os.path
import time
import bson
from pymongo import Connection


try: 
    input = raw_input
except NameError:
    pass

try:
    import urllib.request
except ImportError:
    import urllib
    urllib.request = __import__('urllib2')
    urllib.parse = __import__('urlparse')
    
urlopen = urllib.request.urlopen
request = urllib.request.Request


def install_proxy():
    if use_proxy == False:
        return
    proxy_support = urllib.request.ProxyHandler({"http":http_proxy})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    return


def get_data_from_req(req):
    attempts = 0
    binary = ''
    while attempts < 5:
        try:
            binary = urlopen(req)
            time.sleep(1) # be nice to web host
            break
        except Exception as e:
            attempts += 1
            print("Attempts: "+str(attempts))
            print(e)
    return binary


def is_file_valid(file):
    try:
        first_char = file.read(1) #get the first character
        if not first_char:
            print "file is empty" #first character is the empty string..
            return False
        else:
            file.seek(0)
            return True
    except Exception as e:
        print(e)
        return False

def main():
    """For audio downloading and persistence"""

    con = Connection()
    db = con.audiodb

    if use_proxy == True:
        install_proxy()

    words = open(filename).read().split()
    for wordname in words:
        if wordname.isalpha() == False:
            continue
        wordfilename = wordname.lower()+'.mp3'
        wordrecord = wordname.lower()+'_mp3'
        num = db.audiodb.find({"file_name":wordrecord}).count()
        if num > 0:
            print("Already got "+"\""+wordname+"\"")
            continue
        try:
            mp3file = get_data_from_req(
                    "https://ssl.gstatic.com/dictionary/static/sounds/de/0/"+wordfilename)
            if not is_file_valid(mp3file):
                continue
            bin = bson.Binary(mp3file.read())
            db.audiodb.save({"file_name":wordrecord, "mp3":bin})
            print("Done!")
        except Exception as e:
            print(e)


def get_file():
    filename = input("Input a file name: ")
    if not os.path.exists(filename):
        print "%s doesn't exists" % filename
        filename = get_file()
    elif not os.path.getsize(filename):
        print "%s is empty" % filename
        filename = get_file()
    else:
        pass

    return filename

http_proxy = "http://localhost:8086"
use_proxy = False
http_proxys = {'http':http_proxy}
filename = get_file()

start = time.time()
if __name__ == '__main__':
    main()
print("Elapsed Time:", (time.time() - start))

