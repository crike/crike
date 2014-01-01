# coding:gbk
'''
Created on 2013-12-20

@author: bn
'''

import time
import re
import os
import threading
from multiprocessing import Process
from crike_django.models import Word, Lesson, Dict
from crike_django.settings import MEDIA_ROOT

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

    
def download_from_iciba(word):
    """Download full size images from Bing image search.
 
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    BASE_URL = 'http://www.iciba.com/'+word.name
    content = get_content_from_url(BASE_URL)

    phonetics_list = re.findall(
            "\[</strong><strong lang=\"EN-US\" xml:lang=\"EN-US\">(.+?)</strong><strong>\]", content, re.M | re.S)
    if len(phonetics_list) > 0:
        word.phonetics =  phonetics_list[0]
        print word.phonetics

        mean_list = []
        mean_span_list = re.findall('<span class=\"label_list\">(.+?)</span>', content, re.M | re.S)
        for mean_span in mean_span_list:
            label_list = re.findall('<label>(.+?)</label>', mean_span, re.M | re.S)
            labels = ''
            for label in label_list:
                labels += label
            mean_list.append(labels)
        word.mean = mean_list
        print mean_list

        pos_list = re.findall('<strong class=\"fl\">(.+?)</strong>', content, re.M | re.S)
        word.pos = pos_list
        print pos_list
                
        word.save()

        if not os.path.exists(PATH+word.name+'.mp3'):
            audio_list = re.findall('asplay\(\'(http://res.iciba.com/resource/amp3.+?\.mp3)\'\)', content, re.M | re.S)
            download_audio_from_iciba(audio_list[0], word)
    else:
        print(content)
        print(word.name+' download failed!')

def get_data_from_req(req):
    attempts = 0
    binary = ''
    while attempts < 5:
        download_lock.acquire()
        try:
            binary = urlopen(req)
            time.sleep(2) # be nice to web host
            download_lock.release()
            break
        except Exception as e:
            time.sleep(2) # be nice to web host
            download_lock.release()
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

def download_audio_from_google(word):
    try:
        mp3file = get_data_from_req(
                "https://ssl.gstatic.com/dictionary/static/sounds/de/0/"+word.name+".mp3")
        filepath = os.path.join(PATH, word.name+'.mp3')
        file = open(filepath, 'wb')
        file.write(mp3file.read())
        file.close()
        #word.audio.put(mp3file.read(), content_type='audio/mp3')
    except Exception as e:
        print(e)

def download_audio_from_iciba(url, word):
    try:
        mp3file = get_data_from_req(url)
        print url

        filepath = os.path.join(PATH, word.name+'.mp3')
        file = open(filepath, 'wb')
        file.write(mp3file.read())
        file.close()
        #word.audio.put(mp3file.read(), content_type='audio/mp3')
    except Exception as e:
        print(e)

def download_word(wordname):
    word = Word(name=wordname)
    download_from_iciba(word)
    #download_audio_from_google(word)
    return word

def download_thread_single_engine(word, engine):
    count = 0

    process = Process(target=engine, args=(word,))
    while not isinstance(process, Process):
        print("Process init failed")
        process = Process(target=engine, args=(word,))
    process.start()
    time.sleep(1)

    while process.is_alive():
        print str(process)+ ' ' + word.name + ' ' + str(count)
        time.sleep(5)
        count += 1
        if count == 10:
            process.terminate()
            break

class download_thread(threading.Thread):
    def __init__(self, words):
        threading.Thread.__init__(self)
        self.words = words

    def run(self):
        words_lock.acquire()
        num = len(self.words)
        print self.words

        while num > 0:
            wordname = self.words.pop()
            words_lock.release()
            if not wordname.isalpha() or len(Word.objects(name=wordname)) > 0:
                words_lock.acquire()
                continue

            if len(Word.objects(name=wordname)) > 0:
                word = Word.objects(name=wordname)[0]
            else:
                word = Word(name=wordname)
                print('Start downloading "%s"' % wordname)
                download_thread_single_engine(word, download_from_iciba)

            if not os.path.exists(PATH+wordname+'.mp3'):
                print('Try another engine')
                download_thread_single_engine(word, download_audio_from_google)

            words_lock.acquire()
            num = len(self.words)

        words_lock.release()

def install_proxy():
    if use_proxy == False:
        return
    proxy_support = urllib.request.ProxyHandler({"http":http_proxy})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    return

PATH = MEDIA_ROOT + '/audios/'
use_proxy = False
http_proxy = "http://localhost:8086"
words_lock = threading.Lock()
download_lock = threading.Lock()

def handle_uploaded_file(dictname, lessonname, words_file):
    if use_proxy == True:
        install_proxy()

    if not os.path.exists(PATH):
        os.makedirs(PATH)

    lesson = Lesson(name=lessonname)
    words = words_file.read().split()
    tempwords = words[:]

    thread1 = download_thread(tempwords)
    thread1.start()
    print('Thread 1 started!')
    time.sleep(2)
    thread2 = download_thread(tempwords)
    thread2.start()
    print('Thread 2 started!')

    thread1.join()
    print('Thread 1 Done!')
    thread2.join()
    print('Thread 2 Done!')
    """
    thread1 = download_thread(tempwords)
    thread1.start()
    print('Thread 1 started!')
    thread1.join()
    print('Thread 1 Done!')
    """


    for word in words:
        if word.isalpha() == False:
            continue
        if len(Word.objects(name=word)) > 0:
            wordrecord = Word.objects(name=word)[0]
            lesson.words.append(wordrecord)

    if len(Dict.objects(name=dictname)) == 0:
        dic = Dict(name=dictname)
        dic.lessons.append(lesson)
        dic.save()
    else:
        dic = Dict.objects(name=dictname).first()
        dic.lessons.append(lesson)
        dic.save()

