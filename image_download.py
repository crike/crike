
import os
import time
import json
import re
import requests
import urllib2
from multiprocessing import Process
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError
 
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
            content = urlopen(url).read().decode('gbk', 'ignore')
            break
        except Exception as e:
            attempts += 1
            print(e)

    return content

    
def download_from_bing(query, path):
    """Download full size images from Bing image search.
 
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    # BASE_URL = 'http://image.baidu.com/i?tn=baiduimage&ie=utf-8&word=' + query
    BASE_URL = 'http://cn.bing.com/images/search?q='+query
    content = get_content_from_url(BASE_URL)
    urllist = re.findall('imgurl:&quot;(http[^&]+.\.jpg)&quot', content, re.M | re.S)

    BASE_PATH = os.path.join(path, query)
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)
 
    x = 0
    for imgurl in urllist:
        if len(os.listdir(BASE_PATH)) > pics_per_word:
            break

        try:
            image_r = requests.get(imgurl)
        except ConnectionError, e:
            print 'could not download %s' % imgurl
            continue

        file = open(os.path.join(BASE_PATH, 'bing_%s.jpg') % x, 'w')
        try:
            Image.open(StringIO(image_r.content)).save(file, 'JPEG')
            x += 1
        except IOError, e:
            # Throw away some gifs...blegh.
            print 'could not save %s' % imgurl
            continue
        finally:
            file.close()
 
        # Be nice to web host and they'll be nice back :)
        time.sleep(1.5)


def download_thru_googleapi(query, path):
    """Download full size images from Google image search.
 
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
            'v=1.0&q=' + query + '&start=%d'
    # BASE_URL = 'http://image.baidu.com/i?tn=baiduimage&ie=utf-8&word=' + query
 
    BASE_PATH = os.path.join(path, query)
 
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)
 
    start = 0 # Google's start query string parameter for pagination.
    while start < 16: # Google will only return a max of 56 results.
        if len(os.listdir(BASE_PATH)) > pics_per_word:
            break

        r = requests.get(BASE_URL % start, verify=False)
        for image_info in json.loads(r.text)['responseData']['results']:
            urllist =  re.findall('http.+\.[j|J][p|P][g|G]', image_info['unescapedUrl'])
            if len(urllist) == 0:
                continue
            url = urllist[0]
            print url
            try:
                image_r = requests.get(url)
                if image_r.content == 0:
                    print 'could not download %s' % url
                    continue
            except ConnectionError, e:
                print 'could not download %s' % url
                continue
 
            # Remove file-system path characters from name.
            title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '').replace(' ','_').replace('|','')
 
            file = open(os.path.join(BASE_PATH, 'google_%s.jpg') % title, 'w')
            try:
                Image.open(StringIO(image_r.content)).save(file, 'JPEG')
            except IOError, e:
                # Throw away some gifs...blegh.
                print 'could not save %s' % url
                continue
            finally:
                file.close()
 
        print start
        start += 4 # 4 images per page.
 
        # Be nice to Google and they'll be nice back :)
        time.sleep(2)
 
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
    """For images downloading to filesystem, then manually filter them"""
    if use_proxy == True:
        install_proxy()

    words = open(filename).read().split()
    for i in range(0, len(words), 2):
        wordname1 = words[i]
        if len(words)-1 < i+1:
            wordname2 = '0'
        else:
            wordname2 = words[i+1]
        process1 = None
        process2 = None
        
        if not wordname1.isalpha():
            pass
        elif os.path.exists('images/'+wordname1) and len(os.listdir('images/'+wordname1)) > pics_per_word:
            pass
        else:
            process1 = Process(target=download_from_bing, args=(wordname1, 'images'))

        if not wordname2.isalpha():
            pass
        elif os.path.exists('images/'+wordname2) and len(os.listdir('images/'+wordname2)) > pics_per_word:
            pass
        else:
            # process2 = Process(target=download_thru_googleapi, args=(wordname2, 'images'))
            process2 = Process(target=download_from_bing, args=(wordname2, 'images'))

        if process1:
            process1.start()
        time.sleep(2)
        if process2:
            process2.start()

        time.sleep(5)
        
        if os.path.exists('images/'+wordname1):
            lastlen1 = len(os.listdir('images/'+wordname1))
        else:
            lastlen1 = 0
        if os.path.exists('images/'+wordname2):
            lastlen2 = len(os.listdir('images/'+wordname2))
        else:
            lastlen2 = 0

        while process1 and process1.is_alive() or \
              process2 and process2.is_alive():
            time.sleep(20)
            if os.path.exists('images/'+wordname1):
                currentlen1 = len(os.listdir('images/'+wordname1))
            else:
                currentlen1 = 0
            if os.path.exists('images/'+wordname2):
                currentlen2 = len(os.listdir('images/'+wordname2))
            else:
                currentlen2 = 0
            
            if process1 and process1.is_alive() and currentlen1 == lastlen1:
                process1.terminate()

            if process2 and process2.is_alive() and currentlen2 == lastlen2:
                process2.terminate()

            lastlen1 = currentlen1
            lastlen2 = currentlen2

        """
        if process1 != '':
            process1.join()
            print("%s Done!" % wordname1)
        if process2 != '':
            process2.join()
            print("%s Done!" % wordname2)
        """
            

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
pics_per_word = 4

start = time.time()
if __name__ == '__main__':
    main()
print("Elapsed Time:", (time.time() - start))

