# coding:utf-8
import os
import time
import json
import re
import urllib2
import threading
from multiprocessing import Process
from crike_django.settings import MEDIA_ROOT
import urllib
 
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

    
class download_from_bing_thread(threading.Thread):
    def __init__(self, query, path):
        threading.Thread.__init__(self)
        self.query = query
        self.path = path

    def run(self):
        # BASE_URL = 'http://image.baidu.com/i?tn=baiduimage&ie=utf-8&word=' + self.query
        BASE_URL = 'http://cn.bing.com/images/search?q='+self.query
        content = get_content_from_url(BASE_URL)
        imginfos = re.findall('imgurl:&quot;([^<>]*?) kB', content, re.M | re.S)

        BASE_PATH = os.path.join(self.path, self.query)
        if not os.path.exists(BASE_PATH):
            os.makedirs(BASE_PATH)
     
        for imginfo in imginfos:
            if threadstop == self.query or len(os.listdir(BASE_PATH)) >= pics_per_word:
                break

            sizes = re.findall('t2=\"[^<>/"]* ([^<>/" ]*?)$', imginfo, re.M | re.S)
            if len(sizes) == 0 or eval(sizes[0]) > 500:
                continue
            urls = re.findall('^(http[^&]+\.[j|J][p|P][g|G])&quot', imginfo, re.M | re.S)
            if len(urls) == 0:
                continue
            imgurl = urls[0]
            
            title = get_dir_len(BASE_PATH)
            fname = os.path.join(BASE_PATH, '%s.jpg') % title
            try:
                urllib.urlretrieve(imgurl, fname)
                if not is_file_valid(fname):
                    os.remove(fname)
            except IOError, e:
                # Throw away some gifs...blegh.
                print 'could not save %s' % imgurl
                continue
     
            # Be nice to web host and they'll be nice back :)
            time.sleep(1.5)


class download_from_google_thread(threading.Thread):
    def __init__(self, query, path):
        threading.Thread.__init__(self)
        self.query = query
        self.path = path

    def run(self):
        BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
                'v=1.0&q=' + self.query + '&start=%d'
        # BASE_URL = 'http://image.baidu.com/i?tn=baiduimage&ie=utf-8&word=' + query
     
        BASE_PATH = os.path.join(self.path, self.query)
     
        if not os.path.exists(BASE_PATH):
            os.makedirs(BASE_PATH)
     
        start = 0 # Google's start query string parameter for pagination.
        while start < 16: # Google will only return a max of 56 results.
            if len(os.listdir(BASE_PATH)) >= pics_per_word:
                break

            content = get_content_from_url(BASE_URL % start)
            if type(content) == unicode or type(content) == str:
                continue
            for image_info in json.loads(content.text)['responseData']['results']:
                urllist =  re.findall('http.+\.[j|J][p|P][g|G]', image_info['unescapedUrl'])
                if len(urllist) == 0:
                    continue
                url = urllist[0]
                # Remove file-system path characters from name.
                # title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '').replace(' ','_').replace('|','')
                title = get_dir_len(BASE_PATH)
                fname = os.path.join(BASE_PATH, '%s.jpg') % title
                try:
                    urllib.urlretrieve(url, fname)
                    if not is_file_valid(fname):
                        os.remove(fname)
                except IOError, e:
                    # Throw away some gifs...blegh.
                    print 'could not save %s' % url
                    continue
     
            print start
            start += 4 # 4 images per page.
     
            # Be nice to Google and they'll be nice back :)
            time.sleep(2)
     

def is_file_valid(file):
    try:
        if type(file) == unicode or type(file) == str:
            if os.path.getsize(file) < 10000:
                return False
            file = open(file,"rb")
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
    count = 0;
    if os.path.exists(path):
        for item in os.listdir(path):
            if is_file_valid(path+'/'+item):
                count += 1
        return count
    else:
        return 0

def is_path_full(path):
    return get_dir_len(path) >= pics_per_word

def download_controller(wordname, engine):
    lastlen = get_dir_len(os.path.join(IMG_PATH, wordname))
    count = 0

    thread = engine(wordname, IMG_PATH)
    thread.daemon = True
    thread.start()
    time.sleep(1)

    while thread.is_alive():
        print str(thread)+ ' ' + wordname + ' ' + str(count)
        time.sleep(10)
        currentlen = get_dir_len(os.path.join(IMG_PATH, wordname))

        if currentlen == lastlen:
            count += 1
            if count == 10:
                threadstop = wordname
                break
        else:
            count = 0
            lastlen = currentlen

    return lastlen

def get_word_from_queue(words):
    words_lock.acquire()
    wordname = None
    for word in words:
        BASE_PATH = os.path.join(IMG_PATH, word)
        if is_path_full(BASE_PATH):
            words.remove(word)
            continue
        else:
            words.remove(word)
            wordname = word
            break

    words_lock.release()
    return wordname

class download_thread(threading.Thread):
    def __init__(self, words):
        threading.Thread.__init__(self)
        self.words = words

    def run(self):
        wordname = get_word_from_queue(self.words)
        while wordname:
            print('Start downloading "%s"' % wordname)
            lastlen = download_controller(wordname, download_from_bing_thread)

            """
            if lastlen < pics_per_word:
                print('Try another engine')
                download_controller(wordname, download_from_google_thread)
            """
            wordname = get_word_from_queue(self.words)

def download_images_single(word):
    download_controller(word, download_from_bing_thread)
    if not is_path_full(os.path.join(IMG_PATH, word)):
        print('Try another engine')
        download_controller(word, download_from_google_thread)

def download_images(words):
    thread1 = download_thread(words)
    thread1.daemon = True
    thread1.start()
    print('Image Thread 1 started!')

    thread2 = download_thread(words)
    thread2.daemon = True
    thread2.start()
    print('Image Thread 2 started!')

    thread3 = download_thread(words)
    thread3.daemon = True
    thread3.start()
    print('Image Thread 3 started!')
            
    thread4 = download_thread(words)
    thread4.daemon = True
    thread4.start()
    print('Image Thread 4 started!')

def main():
    """For images downloading to filesystem, then manually filter them"""
    if use_proxy == True:
        install_proxy()

    words = open(filename).read().split()

    thread1 = download_thread(words)
    thread1.start()
    print('Thread 1 started!')
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

IMG_PATH = MEDIA_ROOT + '/images'
http_proxy = "http://localhost:8086"
use_proxy = False
http_proxys = {'http':http_proxy}
pics_per_word = 3
words_lock = threading.Lock()
url_lock = threading.Lock()
threadstop = ''

if __name__ == '__main__':
    filename = get_file()
    start = time.time()
    main()
    print("Elapsed Time:", (time.time() - start))

