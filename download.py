'''
Created on 2013-12-5

@author: bn
'''

# -*- coding: gbk -*-

import os.path
import time


try: input = raw_input
except NameError: pass

try:
    import urllib.request
except ImportError:
    import urllib
    urllib.request = __import__('urllib2')
    urllib.parse = __import__('urlparse')
    
urlopen = urllib.request.urlopen
request = urllib.request.Request

http_proxy = "http://localhost:8086"
use_proxy = False
http_proxys = {'http':http_proxy}

filename = input("Input a file name: ");

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
    while attempts < 10:
        try:
            binary = urlopen(req)
            break
        except Exception as e:
            attempts += 1
            print("Attempts: "+str(attempts))
            print(e)
    return binary

def main():
    words = open(filename).read().split()
    
    for wordname in words:
        
        if wordname.isalpha() == False:
            continue
        
        wordfilename = wordname.lower()+'.mp3'
        
        if os.path.exists(wordfilename) and os.path.getsize(wordfilename) > 0: #TODO MD5
            continue
        
        if use_proxy == True:
            install_proxy()
    
        try:
            mp3file = get_data_from_req("https://ssl.gstatic.com/dictionary/static/sounds/de/0/"+wordfilename)
            output = open(wordfilename,'wb')
            output.write(mp3file.read())
            output.close()
        except Exception as e:
            print(e)

start = time.time()
if __name__ == '__main__':
    main()

print("Elapsed Time:", (time.time() - start))