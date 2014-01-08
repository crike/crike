
import os
import time
import json
import re
import requests
import urllib2
import threading
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
        if len(os.listdir(BASE_PATH)) >= pics_per_word:
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
        if len(os.listdir(BASE_PATH)) >= pics_per_word:
            break

        r = requests.get(BASE_URL % start, verify=False)
        for image_info in json.loads(r.text)['responseData']['results']:
            urllist =  re.findall('http.+\.[j|J][p|P][g|G]', image_info['unescapedUrl'])
            if len(urllist) == 0:
                continue
            url = urllist[0]
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


def get_dir_len(path):
    if os.path.exists(path):
        return len(os.listdir(path))
    else:
        return 0


def download_thread_single_engine(wordname, engine):
    lastlen = get_dir_len('images/'+wordname)
    count = 0

    process = Process(target=engine, args=(wordname, 'images'))
    while not isinstance(process, Process):
        print("Process init failed")
        process = Process(target=engine, args=(wordname, 'images'))
    process.start()
    time.sleep(1)

    while process.is_alive():
        print str(process)+ ' ' + wordname + ' ' + str(count)
        time.sleep(10)
        currentlen = get_dir_len('images/'+wordname)

        if currentlen == lastlen:
            count += 1
            if count == 10:
                process.terminate()
                break
        else:
            count = 0
            lastlen = currentlen

    return lastlen


class download_thread(threading.Thread):
    def __init__(self, words):
        threading.Thread.__init__(self)
        self.words = words

    def run(self):
        words_lock.acquire()
        num = len(self.words)
        print self.words
        words_lock.release()

        while num > 0:
            words_lock.acquire()
            wordname = self.words.pop()
            words_lock.release()
            if not wordname.isalpha():
                continue
            elif os.path.exists('images/'+wordname) and len(os.listdir('images/'+wordname)) > pics_per_word:
                continue
        
            print('Start downloading "%s"' % wordname)
            lastlen = download_thread_single_engine(wordname, download_from_bing)

            if lastlen < pics_per_word:
                print('Try another engine')
                download_thread_single_engine(wordname, download_thru_googleapi)

            words_lock.acquire()
            num = len(self.words)
            words_lock.release()
        


def main():
    """For images downloading to filesystem, then manually filter them"""
    if use_proxy == True:
        install_proxy()

    words = open(filename).read().split()

    thread1 = download_thread(words)
    thread1.start()
    print('Thread 1 started!')
    time.sleep(2)
    thread2 = download_thread(words)
    thread2.start()
    print('Thread 2 started!')

    thread1.join()
    print('Thread 1 Done!')
    thread2.join()
    print('Thread 2 Done!')

            

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
pics_per_word = 4
words_lock = threading.Lock()

if __name__ == '__main__':
    filename = get_file()
    start = time.time()
    main()
    print("Elapsed Time:", (time.time() - start))

