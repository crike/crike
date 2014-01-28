#coding:utf-8

from __future__ import division
from random import sample, randrange, choice
import string
import sys
import shutil
import os
import time


from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt


# Imaginary function to handle an uploaded file.
from crike_django.models import *
from crike_django.forms import *
from crike_django.settings import MEDIA_ROOT,STATIC_ROOT
from word_utils import download_word, handle_uploaded_file
from image_download import download_images_single
from multiprocessing import Process

# Utils
def save_file(srcfile, dst):
    try:
        file = open(dst, 'wb')
        file.write(srcfile.read())
        file.close()
        srcfile.close()
    except Exception as e:
        print(e)

def get_or_none(model, **kwargs):
    try:
        return model.objects.filter(**kwargs)
    except model.DoesNotExist:
        return None

def get_bookobj(book):
    bookobjs = Book.objects.filter(name=book)
    if len(bookobjs) > 0:
        return bookobjs[0]
    return None

def get_lessonobj(book, lesson):
    bookobj = get_bookobj(book)
    if bookobj == None:
        return None
    lessonobjs = filter(lambda x: x.name == lesson, bookobj.lessons)
    if len(lessonobjs) > 0:
        return lessonobjs[0]
    return None

def get_words_from_lesson(book, lesson):
    lessonobj = get_lessonobj(book, lesson)
    if lessonobj:
        # https://bitbucket.org/wkornewald/djangotoolbox/pull-request/3/allow-setting-an-actual-object-in-a/diff
        return Word.objects.filter(id__in=lessonobj.words)
    return []

def get_words_from_paginator(paginator, page):
    try:
        if page is -1:
            return paginator.page(paginator.num_pages)
        words = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        words = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        words = paginator.page(paginator.num_pages)

    return words


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        return render(request, self.template_name, {'books':books})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def lesson_stat_update(stat):
    stat.percent = stat.pick + stat.show + stat.dictation + stat.fill
    stat.save()

class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        todos = []
        for book in books:
            for lesson in book.lessons:
                stat = lesson.lessonstat_set.get_or_create(user=request.user)[0]
                lesson_stat_update(stat)
                if stat.percent < 100:
                    lesson.stat = stat
                    todos.append({'book':book, 'lesson':lesson})

        return render(request, self.template_name, {'todos': todos})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

# Also HomeView.
class StudentView(TemplateView):
    template_name = 'crike_django/student_view.html'

    def get(self, request, *args, **kwargs):
        return redirect('home')

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class StudentsAdminView(TemplateView):
    template_name = 'crike_django/students_admin_view.html'

    def get(self, request, *args, **kwargs):
        students = Student.objects.all()
        return render(request, self.template_name, {'students': students})

class TeacherView(TemplateView):
    template_name = 'crike_django/teacher_view.html'

    def get(self, request, *args, **kwargs):
        return redirect('home')

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def hello_crike(request):
    print request
    return HttpResponse("Hello crike!")

def play_audio(request, name):
    #word = Word.objects.filter(name=name)[0]
    #return HttpResponse(word.audio.read(), content_type="audio/mpeg")
    path = MEDIA_ROOT+'/audios/'+name
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type="audio/mpeg")
    else:
        return HttpResponse(None)

def show_image(request, name, num):
    path = MEDIA_ROOT+'/images/'+name+'/'+num
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type='image/jpeg')
    else:
        return HttpResponse(None)

def retrieve_word(request, book, lesson, word):
    mp3path = MEDIA_ROOT+'/audios/'+word+".mp3"
    imgpath = MEDIA_ROOT+'/images/'+word
    if os.path.exists(mp3path):
        os.remove(mp3path)
    download_word(word)
    if os.path.exists(imgpath):
        shutil.rmtree(imgpath)
    process = Process(target=download_images_single, args=(word,))
    process.start()
    time.sleep(8)
    return HttpResponseRedirect("/admin/book/"+book+"/lesson/"+lesson)

class UserHistoryView(TemplateView):
    template_name = 'crike_django/user_history.html'
    
    def get(self, request, *args, **kwargs):
        user_history = WordEventRecorder.objects.filter(user=request.user)
        return render(request, self.template_name, {'user_history': user_history})

    def delete(self, request, *args, **kwargs):
        WordEventRecorder.objects.filter(user=request.user).delete()
        return HttpResponse('')

class WordStatView(TemplateView):
    template_name = 'crike_django/word_stat.html'

    def get(self, request, *args, **kwargs):
        word_stats = WordStat.objects.filter(user=request.user)
        for stat in word_stats:
            tries = stat.correct_num + stat.mistake_num
            if tries is 0:
                stat.accuracy = 0
            else:
                stat.accuracy = "%.1f%%" % (stat.correct_num * 100 / tries)
        return render(request, self.template_name, {'word_stats': word_stats})

    def delete(self, request, *args, **kwargs):
        WordStat.objects.filter(user=request.user).delete()
        # Fill the view with a success message
        return HttpResponse('')

class WordsAdminView(TemplateView):
    template_name = 'crike_django/words_admin.html'

    def get(self, request, *args, **kwargs):
        words = Word.objects.all()
        if len(words) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name, {'Words':words})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def show_lessons(request, book):#TODO
    template_name='crike_django/lessons_list.html'

    words = Word.objects.all()
    if len(words) != 0:
        request.encoding = "utf-8"

    return render(request, template_name, {'Words':words})

class WordDeleteView(TemplateView):

    def get(self, request, *args, **kwargs):
        id = request.GET['id']
        template = 'crike_django/word_delete.html'
        params = { 'id': id }
        return render(request, template, params)

    def post(self, request, *args, **kwargs):
        id = request.POST['id']
        word = Word.objects.filter(id=id)[0]
        audiofile = MEDIA_ROOT+'/audios/'+word.name+'.mp3'
        if os.path.exists(audiofile):
            os.remove(audiofile)
        word.delete()
        return HttpResponseRedirect("/admin/words/")

def delete_lesson(request, book, lesson):
    template = 'crike_django/lesson_delete.html'
    params = { 'book':book, 'lesson':lesson }
    return render(request, template, params)


def lesson_success(request, book, lesson, tag):
    user = request.user
    # profile = request.user.profile
    lessonobj = get_lessonobj(book, lesson)
    lesson_result = LessonStat.objects.get_or_create(user=user,
                                                       lesson=lessonobj)[0]
    setattr(lesson_result, tag, 25)
    lesson_result.save()
    print "user %s complete lesson %s part %s %d" % (user, lesson, tag, 25)


def word_event_recorder(request, book, lesson, tag):
    try:
        page_str = request.POST.get('page') or request.GET.get('page')
        page = int(page_str) - 1
    except:
        page = 0
    num = request.POST.get('num', 1)
    ret = request.POST.get('ret', True)
    words_list = get_words_from_lesson(book, lesson)
    paginator = Paginator(words_list, 1)
    word = get_words_from_paginator(paginator, page)[0]

    word_stat, retval = WordStat.objects.get_or_create(user=request.user,
                                                    word=word,
                                                    lesson=get_lessonobj(book, lesson),
                                                    tag=tag)
    if ret == 'true' or tag == 'show':
        correct_num = 1
        mistake_num = int(num) - 1
    else:
        correct_num = 0
        mistake_num = int(num)
    
    word_stat.correct_num += correct_num
    word_stat.mistake_num += mistake_num
    word_stat.save()

    wer = WordEventRecorder.objects.create(user=request.user,
                                           word=word,
                                           lesson=get_lessonobj(book,lesson),
                                           correct_num=correct_num,
                                           mistake_num=mistake_num,
                                           tag=tag)
    wer.save()

    print word, request.user, lesson


# for learning
class LessonShowView(TemplateView):
    template_name = 'crike_django/lesson_show.html'

    def _success(self, request, book, lesson):
        lesson_success(request, book, lesson, 'show')

    def _record(self, request, book, lesson):
        word_event_recorder(request, book, lesson, 'show')

    def get(self, request, book, lesson):
        lesson_obj = get_lessonobj(book, lesson)
        words_list = get_words_from_lesson(book, lesson)
        if len(words_list) == 0:
            return render(request, self.template_name,
                   {'book': book, 'lesson': lesson})
        paginator = Paginator(words_list, 1)
        page = request.GET.get('page')
        words = get_words_from_paginator(paginator, page)
        print "nnnnnnnnn"
        print "word %s show!" % words[0]
        print "nnnnnnnnn"

        self._record(request, book, lesson)
        lesson_result = LessonStat.objects.get_or_create(user=request.user,
                                                         lesson=lesson_obj)[0]
        pick = lesson_result.pick
        print 'Show with LessonStat: ', lesson_result
        if page and eval(page) == len(words_list):
            return render(request, self.template_name,
                    {'words': words, 'book': book, 'lesson': lesson, 'done':'True',
                    'lesson_result': lesson_result})

        return render(request, self.template_name,
               {'words': words, 'book': book, 'lesson': lesson,
                'lesson_result': lesson_result})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class LessonPickView(TemplateView):
    template_name = 'crike_django/lesson_pick.html'

    def _success(self, request, book, lesson):
        lesson_success(request, book, lesson, 'pick')

    def _record(self, request, book, lesson):
        word_event_recorder(request, book, lesson, 'pick')

    def get(self, request, book, lesson):
        words_list = get_words_from_lesson(book, lesson)
        paginator = Paginator(words_list, 1)
        page = request.GET.get('page')
        words = get_words_from_paginator(paginator, page)

        words_list = filter(lambda x: x.name !=words[0].name, words_list)
        count = len(words_list)
        if count > 3:
            options = sample(words_list, 3)
        else:
            options = sample(words_list, count)
        options.insert(randrange(len(options)+1), words[0])

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson, 'options':options})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
        ret = request.POST.get('ret')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num, page, ret
        print "nnnnnnnnnnnnnnnn"

        self._record(request, book, lesson)

        # This case means success of Choice Questions.
        if page == '0':
            self._success(request, book, lesson)
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/fill')

        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/pick?page='+page)


class LessonFillView(TemplateView):
    template_name='crike_django/lesson_fill.html'

    def _success(self, request, book, lesson):
        lesson_success(request, book, lesson, 'fill')

    def _record(self, request, book, lesson):
        word_event_recorder(request, book, lesson, 'fill')

    def get(self, request, book, lesson):
        words_list = get_words_from_lesson(book, lesson)
        paginator = Paginator(words_list, 1)
        page = request.GET.get('page')
        words = get_words_from_paginator(paginator, page)

        """
        options = sys.modules['__builtin__'].list(words[0].name)
        options = sample(options, len(options))
        options.insert(randrange(len(options)+1), choice(string.letters).lower())
        options.insert(randrange(len(options)+1), choice(string.letters).lower())
        options.insert(randrange(len(options)+1), choice(string.letters).lower())
        """

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
        ret = request.POST.get('ret')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num, page, ret
        print "nnnnnnnnnnnnnnnn"

        self._record(request, book, lesson)
        if page == '0':
            self._success(request, book, lesson)
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/dictation')
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/fill?page='+page)

class LessonDictationView(TemplateView):
    template_name='crike_django/lesson_dictation.html'

    def _success(self, request, book, lesson):
        lesson_success(request, book, lesson, 'dictation')

    def _record(self, request, book, lesson):
        word_event_recorder(request, book, lesson, 'dictation')

    def get(self, request, book, lesson):
        words_list = get_words_from_lesson(book, lesson)
        paginator = Paginator(words_list, 8)
        page = request.GET.get('page')
        words = get_words_from_paginator(paginator, page)

        words_list = filter(lambda x: x.name !=words[0].name, words_list)
        count = len(words_list)
        if count > 3:
            options = sample(words_list, 3)
        else:
            options = sample(words_list, count)
        options.insert(randrange(len(options)+1), words[0])

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson, 'options':options})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num
        print "nnnnnnnnnnnnnnnn"
        self._record(request, book, lesson)
        if page == '0':
            self._success(request, book, lesson)
            return HttpResponseRedirect('/home')#TODO goto a result show page
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/dictation?page='+page)

class BooksStudyView(TemplateView):
    template_name='crike_django/books_study.html'

    def get(self, request):
#TODO only enable the student's available books!!!
        """
        if not book:
            book = Book.objects.first().name;#TODO get this from student infor

        try:
            bookobj = Book.objects.filter(name=book)[0]
            request.encoding = "utf-8"
            return render(request, self.template_name,{'book':bookobj})
        except Exception as e:
            print e
            return HttpResponseRedirect('/error/')#TODO error page
        """
        books = Book.objects.all()
        if len(books) == 0:
            return render(request, self.template_name,{})

        if not request.user.is_authenticated():
            return render(request, self.template_name, {'books': books})

        for book in books:
            for lesson in book.lessons:
                lesson_result = LessonStat.objects.get_or_create(user=request.user,
                                                                   lesson=lesson)[0]
                # XXX this result should never save
                lesson.result = lesson_result

        return render(request, self.template_name, {'books': books})


    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect("/study/books/")

def exam_creator(book, unit):
    words_list = []
    if book != '':
        bookob = get_bookobj(book)
        if bookob == None:
            return words_list
    else:
        if len(Book.objects.all()) > 0:
            bookob = Book.objects.all()[0]#TODO get user's current book?
        else:
            return words_list
    if unit == 0:
        for lessonobj in bookob.lessons:
            words_list += Word.objects.filter(id__in=lessonobj.words)
    else:
        for lessonobj in bookob.lessons[(unit-1)*3:unit*3]:
            words_list += Word.objects.filter(id__in=lessonobj.words)
    return words_list

class ExamView(TemplateView):
    template_name='crike_django/exam_view.html'

    def get(self, request, book, unit):
        if unit != '':
            unit = eval(unit)
            words_list = exam_creator(book, unit)
        else:
            words_list = exam_creator(book, 0)

        if len(words_list) == 0:
            return render(request, self.template_name,
                    { 'book':book, 'unit':unit})

        paginator = Paginator(words_list, 1)
        page = request.GET.get('page')
        words = get_words_from_paginator(paginator, page)

        words_list = filter(lambda x: x.name !=words[0].name, words_list)
        count = len(words_list)
        if count > 3:
            options = sample(words_list, 3)
        else:
            options = sample(words_list, count)
        options.insert(randrange(len(options)+1), words[0])

        score = request.GET.get('score')
        return render(request, self.template_name,
                {'words':words, 'options':options, 'book':book, 'unit':unit, 'score':score})

    def post(self, request, book, unit):
        page = request.POST.get('page')
        num = request.POST.get('num')
        ret = request.POST.get('ret')
        score = request.POST.get('score')
        if score != 'None':
            score = eval(score)
        else:
            score = 0
        if ret == 'true':
            score += 1
        print "nnnnnnnnnnnnnnnn"
        print num, page, ret, score
        print "nnnnnnnnnnnnnnnn"
        if page == '0':
            return HttpResponseRedirect('/home')#TODO show exam result
        return HttpResponseRedirect('/exam/book/'+book+'/unit/'+str(unit)+'/?page='+page+'&score='+str(score))

# for management
class LessonAdminView(TemplateView):
    template_name='crike_django/lesson_admin.html'
    addwordform = AddWordForm()

    def get(self, request, book, lesson):
        words = get_words_from_lesson(book, lesson)
        if len(words) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson,
                    'AddWordForm':self.addwordform})

    def post(self, request, book, lesson):
        if request.POST['extra'] == 'rename':
            bookobj = Book.objects.filter(name=book)[0]
            lessonobj = get_lessonobj(book, lesson)
            newname = request.POST['newname']
            if not get_lessonobj(book, newname):
                bookobj.lessons.remove(lessonobj)
                lessonobj.name = newname
                bookobj.lessons.append(lessonobj)
                bookobj.save()
                return HttpResponseRedirect("/admin/book/"+book+"/lesson/"+newname)
            else:
                words = get_words_from_lesson(book, lesson)
                return render(request, self.template_name,
                        {'words':words, 'book':book, 'lesson':lesson,
                            'AddWordForm':self.addwordform, 'showform':'RenameForm',
                            'warning':'重名了，重新起个吧'})

        if request.POST['extra'] == 'addword':
            addwordform = AddWordForm(request.POST, request.FILES)
            if not addwordform.is_valid():
                return render(request, self.template_name,
                        {'words':words, 'book':book, 'lesson':lesson,
                            'AddWordForm':addwordform, 'showform':'AddWordForm',
                            'warning':'Double check your inputs please!'})

            words = get_words_from_lesson(book, lesson)
            if len(words) > 0 and len(words.filter(name=request.POST['name'])) > 0:
                return render(request, self.template_name,
                        {'words':words, 'book':book, 'lesson':lesson,
                            'AddWordForm':self.addwordform, 'showform':'AddWordForm',
                            'warning':'已经存在，可以使用修改功能哦'})

            word = None
            words = Word.objects.filter(name=request.POST['name'])
            if len(words) > 0:
                word = words[0]
            else:
                word = Word()
                word.name = request.POST['name']
                word.mean = request.POST['mean'].replace('\r','').split('\n')
                word.phonetics = request.POST['phonetics']
                if request.FILES.get('audio', None):
                    save_file(request.FILES['audio'], MEDIA_ROOT+"/audios/"+word.name+".mp3")
                imagepath = MEDIA_ROOT+"/images/"+word.name
                if not os.path.exists(imagepath):
                    os.makedirs(imagepath)
                if request.FILES.get('image0', None):
                    save_file(request.FILES['image0'], imagepath+"/0.jpg")
                if request.FILES.get('image1', None):
                    save_file(request.FILES['image1'], imagepath+"/1.jpg")
                if request.FILES.get('image2', None):
                    save_file(request.FILES['image2'], imagepath+"/2.jpg")
                word.save()

            bookobj = Book.objects.filter(name=book)[0]
            lessonobj = get_lessonobj(book, lesson)
            bookobj.lessons.remove(lessonobj)
            lessonobj.words.append(word.id)
            bookobj.lessons.append(lessonobj)
            bookobj.save()

        if request.POST['extra'] == 'delword':
            words = request.POST.getlist('delwords')
            bookobj = Book.objects.filter(name=book)[0]
            lessonobj = get_lessonobj(book, lesson)
            bookobj.lessons.remove(lessonobj)
            for word in words:
                wordobj = Word.objects.filter(name=word)[0]
                lessonobj.words.remove(wordobj.id)
                if request.POST.get('delinfos', None):
                    wordobj.delete()
                if request.POST.get('delaudio', None):
                    audiofile = MEDIA_ROOT+'/audios/'+word+'.mp3'
                    if os.path.exists(audiofile):
                        os.remove(audiofile)
                if request.POST.get('delimage', None):
                    imagepath = MEDIA_ROOT+'/images/'+word
                    if os.path.exists(imagepath):
                        shutil.rmtree(imagepath)
            bookobj.lessons.append(lessonobj)
            bookobj.save()

        if request.POST['extra'] == 'updword':
            words = get_words_from_lesson(book, lesson)
            addwordform = AddWordForm(request.POST, request.FILES)
            if not addwordform.is_valid():
                return render(request, self.template_name,
                        {'words':words, 'book':book, 'lesson':lesson,
                            'AddWordForm':addwordform, 'showform':'UpdWordForm',
                            'warning':'Double check your inputs please!'})

            words = Word.objects.filter(name=request.POST['name'])
            word = words[0]
            word.mean = request.POST['mean'].replace('\r','').split('\n')
            word.phonetics = request.POST['phonetics']
            word.save()
            if request.FILES.get('audio', None):
                audiofile = MEDIA_ROOT+'/audios/'+word.name+'.mp3'
                if os.path.exists(audiofile):
                    os.remove(audiofile)
                save_file(request.FILES['audio'], audiofile)
            imagepath = MEDIA_ROOT+"/images/"+word.name
            if not os.path.exists(imagepath):
                os.makedirs(imagepath)
            if request.FILES.get('image0', None):
                imagefile = imagepath+'/0.jpg'
                if os.path.exists(imagefile):
                    os.remove(imagefile)
                save_file(request.FILES['image0'], imagefile)
            if request.FILES.get('image1', None):
                imagefile = imagepath+'/1.jpg'
                if os.path.exists(imagefile):
                    os.remove(imagefile)
                save_file(request.FILES['image1'], imagefile)
            if request.FILES.get('image2', None):
                imagefile = imagepath+'/2.jpg'
                if os.path.exists(imagefile):
                    os.remove(imagefile)
                save_file(request.FILES['image2'], imagefile)


        return HttpResponseRedirect("/admin/book/"+book+"/lesson/"+lesson)

class BooksAdminView(TemplateView):
    template_name='crike_django/books_admin.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        uploadform = UploadFileForm()

        if len(books) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name,
                {'books':books, 'Uploadform':uploadform})

    #功能：上传文件，然后把文件用handle_uploaded_file处理
    def post(self, request, *args, **kwargs):
        books = Book.objects.all()
        if request.POST['extra'] == 'add':
            uploadform = UploadFileForm(request.POST, request.FILES)
            if not uploadform.is_valid():
                return render(request, self.template_name,
                        {'books':books, 'Uploadform':uploadform,
                         'Showform':'uploadform'})

            book = request.POST['book']
            lesson = request.POST['lesson']
            if get_or_none(Book, name=book):
                if get_lessonobj(book, lesson):
                    return render(request, self.template_name,
                            {'books':books,'Uploadform':uploadform,
                             'Showform':'uploadform',
                             'Uploadwarning':'Duplicated Lesson!!'})

            handle_uploaded_file(request.POST['book'],
                    request.POST['lesson'],
                    request.FILES['file'])
            return HttpResponseRedirect('/admin/books/')

        elif request.POST['extra'] == 'delete':
            book = request.POST['delbook']
            lessons = request.POST.getlist('dellessons')
            bookob = Book.objects.filter(name=book)[0]
            for lesson in lessons:
                for lessonobj in bookob.lessons:
                    if lessonobj.name == lesson:
                        bookob.lessons.remove(lessonobj)
            bookob.save()
            if len(bookob.lessons) == 0:
                bookob.delete()

        return HttpResponseRedirect("/admin/books/")

