#coding:utf-8

from __future__ import division
from random import sample, randrange, choice
import string
import sys
import shutil
import os
import time
import datetime
import json
import re
import urllib
import urllib2

from datetime import timedelta

from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils import simplejson


# Imaginary function to handle an uploaded file.
from crike_django.models import *
from crike_django.forms import *
from crike_django.settings import MEDIA_ROOT,STATIC_ROOT,TIME_ZONE
from word_utils import download_word, handle_uploaded_file, get_content_from_url
from image_download import download_images_single, is_path_full
from multiprocessing import Process

# Weixin
import hashlib
from lxml import etree
from django.utils.encoding import smart_str
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from alipay.alipay import *
from urllib import urlencode,quote,unquote

#for encode error
reload(sys)
sys.setdefaultencoding('utf-8')

# Utils

def clean_word(request,wordname):
    words = Word.objects.filter(name=wordname)
    for word in words:
        word.delete()
    return HttpResponse("Word "+wordname+" has been cleaned!")

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

def get_lessonemb(book, lesson):
    bookobj = get_bookobj(book)
    if bookobj == None:
        return None
    lessonobjs = filter(lambda x: x.name == lesson, bookobj.lessons)
    if len(lessonobjs) > 0:
        return lessonobjs[0]
    return None

def get_lessonobj(lessonemb):
    objs = lessonemb.book.lesson_set.filter(name=lessonemb.name)
    if len(objs) > 0:
        return objs[0]
    return None

def get_words_from_lesson(book, lesson):
    lessonobj = get_lessonemb(book, lesson)
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

def get_readings_from_paginator(paginator, page):
    try:
        if page is -1:
            return paginator.page(paginator.num_pages)
        readings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        readings = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        readings = paginator.page(paginator.num_pages)

    return readings

def update_book_lesson(lessonemb, lessonobj):
    bookobj = lessonobj.book
    bookobj.lessons.remove(lessonemb)
    bookobj.lessons.append(lessonobj)
    bookobj.save()

def update_exam_lesson(lessonemb, lessonobj):
    examobjs = filter(lambda x: lessonemb in x.lessons, Exam.objects.all())
    for examobj in examobjs:
        examobj.lessons.remove(lessonemb)
        examobj.lessons.append(lessonobj)
        examobj.save()

def delete_exam_lesson(lessonemb):
    examobjs = filter(lambda x: lessonemb in x.lessons, Exam.objects.all())
    for exam in examobjs:
        exam.lessons.remove(lessonemb)
        exam.save()

def delete_lesson_stat(lessonemb):
    stats = LessonStat.objects.filter(lesson=lessonemb)
    for stat in stats:
        stat.delete()

def today():
    return datetime.datetime.now().date()


def now():
    return datetime.datetime.now()


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user:
            p = get_profile(request.user)
            if p is None:
                pass
            elif p.last_visit is None or p.last_visit.date() != today():
                p.point_add(5)
                p.save()

        books = Book.objects.all()
        return render(request, self.template_name, {'books':books})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def lesson_stat_update(stat):
    stat.percent = stat.pick + stat.show + stat.review + stat.fill
    stat.save()

def update_strange_words_lesson(request):
    if request.user.username == '':
        return
    strange_record_list = WordStat.objects.filter(mistake_num__gte=2,
                                                    user=request.user)
    strange_record_list = filter(lambda x: x.mistake_num-x.correct_num>=2, strange_record_list)

    strange_list = []
    for item in strange_record_list:
        strange_list.append(item.word)

    book_obj = Book.objects.get_or_create(name=request.user.username+"_book", is_public=False)[0]
    lesson_embs = filter(lambda x: x.name == 'strange_words', book_obj.lessons)
    lesson_obj = None
    if len(lesson_embs) > 0:
        lesson_emb = lesson_embs[0]
        lesson_obj = get_lessonobj(lesson_emb)
        lesson_obj.book = book_obj
        book_obj.lessons.remove(lesson_emb)
        lesson_obj.words = []
        for word in strange_list:
            lesson_obj.words.append(word.id)

    else:
        lesson_obj = Lesson(name='strange_words', book=book_obj)
        for word in strange_list:
            lesson_obj.words.append(word.id)

    lesson_obj.save()
    book_obj.lessons.append(lesson_obj)
    book_obj.save()


def update_user_from_wer(request):
    profile = get_profile(request.user)
    if profile is None:
        return
    # TODO: update user streak


class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        update_strange_words_lesson(request)
        # TODO:
        # update_user_from_wer(request)

        books = Book.objects.filter(name=request.user.username+"_book")
        todos = []
        for book in books:
            for lesson in book.lessons:
                stat, retval = lesson.lessonstat_set.get_or_create(user=request.user,
                                                                   lesson=lesson)
                lesson.stat = stat
                todos.append({'book':book, 'lesson':lesson})

        stats = LessonStat.objects.filter(user=request.user)
        for stat in stats:
            try:
                lesson = stat.lesson
            except:
                stat.delete()
                continue

            if lesson.name != 'strange_words' and stat.selected:
                lesson.stat = stat
                todos.append({'book':lesson.book, 'lesson':lesson})

            if stat.percent == 100:
                exams = filter(lambda x: lesson in x.lessons, Exam.objects.all())
                for exam in exams:
                    ready = True
                    for lesson in exam.lessons:
                        stat, retval = lesson.lessonstat_set.get_or_create(user=request.user,
                                                               lesson=lesson)
                        if stat.percent != 100:
                            ready = False
                            break
                    if ready:
                        examstat = ExamStat.objects.get_or_create(
                                user=request.user, exam=exam)[0]
                        examstat.save()

        prize_queries = PrizeQuery.objects.filter(user=request.user)
        return render(request, self.template_name, {
            'todos': todos,
            'examstats': ExamStat.objects.filter(user=request.user),
            'header_form': UploadHeadSculptureForm,
            'prize_queries': prize_queries,
        })

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

def play_audio(request, name):
    #word = Word.objects.filter(name=name)[0]
    #return HttpResponse(word.audio.read(), content_type="audio/mpeg")
    path = MEDIA_ROOT+'/audios/'+name+'.mp3'
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type="audio/mpeg")
    else:
        return HttpResponse(None)

def show_image(request, name, num):
    path = MEDIA_ROOT+'/images/'+name+'/'+num+'.jpg'
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type='image/jpeg')
    else:
        return HttpResponse(None)

def download_single_word(word):
    mp3path = MEDIA_ROOT+'/audios/'+word+".mp3"
    imgpath = MEDIA_ROOT+'/images/'+word
    if os.path.exists(mp3path):
        os.remove(mp3path)
    download_word(word)
    if os.path.exists(imgpath):
        shutil.rmtree(imgpath)
    process = Process(target=download_images_single, args=(word,))
    process.start()

def retrieve_word(request, book, lesson, word):
    download_single_word(word)
    imgpath = MEDIA_ROOT+'/images/'+word
    num = 0
    while not is_path_full(imgpath):
        if num > 3:
            break;
        num += 1
        time.sleep(5)

    return HttpResponseRedirect("/admin/book/"+book+"/lesson/"+lesson)

class UserHistoryView(TemplateView):
    template_name = 'crike_django/user_history.html'

    def get(self, request, *args, **kwargs):
        user_history = WordEventRecorder.objects.filter(user=request.user)
        tags = {}
        for history in user_history:
            if history.tag not in tags:
                tags[history.tag] = 0
            tags[history.tag] += 1
        return render(request, self.template_name, {
                'user_history': user_history,
                'tags': tags,
        })

    def delete(self, request, *args, **kwargs):
        WordEventRecorder.objects.filter(user=request.user).delete()
        return HttpResponse('')


def get_profile(user):
    try:
        return user.student
    except:
        try:
            return user.teacher
        except:
            return None


class UserHeadSculptureView(TemplateView):
    template_name = 'crike_django/'

    def get(self, request, *args, **kwargs):
        return HttpResponseForbidden('allowed only via POST')

    def post(self, request, *args, **kwargs):
        form = UploadHeadSculptureForm(request.POST, request.FILES)
        if form.is_valid():
            profile = get_profile(request.user)
            if not profile:
                return redirect(request.META.get('HTTP_REFERER', '/'))
            profile.profile_picture = form.cleaned_data['image']
            profile.save()
            # XXX success hint
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return redirect(request.META.get('HTTP_REFERER', '/'))


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
        word_stats = filter(lambda x: x.accuracy != "100.0%", word_stats)
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
    lessonobj = get_lessonemb(book, lesson)
    lesson_result = LessonStat.objects.get_or_create(user=user,
                                                       lesson=lessonobj)[0]
    setattr(lesson_result, tag, 25)
    lesson_stat_update(lesson_result)
    #print "user %s complete lesson %s part %s %d" % (user, lesson, tag, 25)


def profile_record_right(profile, correct_num):
    if profile:
        if correct_num > 0:
            profile.study_cright += 1
            if profile.study_cright % 10 == 0:
                profile.point_add(5)
        else:
            profile.study_cright = 0


        profile.save()


def profile_record_exam_ret(profile, ret):
    if profile is None:
        return
    if ret == 'true':
        profile.exam_cright += 1
        if profile.exam_cright % 10 == 0:
            profile.point_add(10)
    else:
        profile.exam_cright = 0

    profile.save()


def count_words_learnt(profile):
    if profile is None:
        return

    try:
        stats = WordStat.objects.filter(user=request.user)
    except WordStat.DoesNotExist:
        pass

    words_learnt = 0
    words_mistake_num = 0
    words_correct_num = 0
    for stat in stats:
        words_mistake_num += stat.mistake_num
        words_correct_num += stat.correct_num
        if stat.correct_num > 0:
            words_learnt += 1
    profile.words_learnt = words_learnt
    profile.words_correct_num = words_correct_num
    profile.words_mistake_num = words_mistake_num

    return


def count_lessons_learnt(profile):
    pass


def count_books_learnt(profile):
    pass


def word_event_recorder(request, book, lesson, tag):
    '''
    Update word stat, word event recorder, profile continuous right and points.
    '''
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
                                                    word=word)
    if ret == 'true':
        correct_num = 1
        mistake_num = int(num) - 1
    elif tag == 'show':
        correct_num = 0
        mistake_num = int(num) - 1
    else:
        correct_num = 0
        mistake_num = int(num)

    word_stat.correct_num += correct_num
    word_stat.mistake_num += mistake_num
    word_stat.save()

    wer = WordEventRecorder.objects.create(user=request.user,
                                           word=word,
                                           correct_num=correct_num,
                                           mistake_num=mistake_num)
    wer.save()

    profile = get_profile(request.user)
    if profile:
        profile_record_right(profile, correct_num)
        if correct_num > 0:
            profile.point_add(5/word_stat.correct_num)
            profile.save()


def words_event_recorder(request, book, lesson, tag):
    num = request.POST.get('num').split(',')
    ret = request.POST.get('ret').split(',')
    options = request.POST.get('words').split(',')

    for i,option in enumerate(options):
        word = Word.objects.filter(name=option)[0]
        word_stat, retval = WordStat.objects.get_or_create(user=request.user,
                                                        word=word)
        if ret[i] == 'true':
            correct_num = 1
            mistake_num = int(num[i]) - 1
        else:
            correct_num = 0
            mistake_num = int(num[i])

        word_stat.correct_num += correct_num
        word_stat.mistake_num += mistake_num
        word_stat.save()

        wer = WordEventRecorder.objects.create(user=request.user,
                                               word=word,
                                               correct_num=correct_num,
                                               mistake_num=mistake_num)
        wer.save()

        profile = get_profile(request.user)
        if profile:
            profile_record_right(profile, correct_num)
            if correct_num > 0:
                profile.point_add(5/word_stat.correct_num)
                profile.save()


def create_class_if_need(request, book, lesson):
    # lesson, teachers, students is needed for a Class
    # but now we only get a lesson and a student.
    lesson_obj = get_lessonemb(book, lesson)
    cls, ret = ClassRelation.objects.get_or_create(lesson=lesson_obj)
    profile = get_profile(request.user)
    if profile is not None:
        # 课堂上只要有身份的人！
        cls.students.add(request.user)
    cls.save()


# for learning
class LessonShowView(TemplateView):
    template_name = 'crike_django/lesson_show.html'

    def _success(self, request, book, lesson):
        lesson_success(request, book, lesson, 'show')

    def _record(self, request, book, lesson):
        #word_event_recorder(request, book, lesson, 'show')
        create_class_if_need(request, book, lesson)


    def get(self, request, book, lesson):
        lesson_obj = get_lessonemb(book, lesson)
        if lesson_obj.name != "strange_words":
            lesson_strange = get_lessonemb(request.user.username+"_book", "strange_words")
            if len(lesson_strange.words) > 0:
                lesson_result = LessonStat.objects.get_or_create(user=request.user,
                                                                 lesson=lesson_strange)[0]
                if lesson_result.timestamp.date() != datetime.datetime.now().date():
                    print "need study strange_words first!"
                    return HttpResponseRedirect('/home/')

        words = get_words_from_lesson(book, lesson)
        if len(words) == 0:
            return redirect(request.META.get('HTTP_REFERER', '/'))

        self._record(request, book, lesson)
        lesson_result = LessonStat.objects.get_or_create(user=request.user,
                                                         lesson=lesson_obj)[0]
        #print 'Show with LessonStat: ', lesson_result

        return render(request, self.template_name,
               {'words': words, 'book': book, 'lesson': lesson,
                'lesson_result': lesson_result})

    def post(self, request, book, lesson):
        self._success(request, book, lesson)
        return HttpResponseRedirect('#')

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

        self._record(request, book, lesson)
        if page == '0':
            self._success(request, book, lesson)
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/review')
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/fill?page='+page)

class LessonReviewView(TemplateView):
    template_name='crike_django/lesson_review.html'

    def _success(self, request, book, lesson):
        lesson_success(request, book, lesson, 'review')

    def _record(self, request, book, lesson):
        words_event_recorder(request, book, lesson, 'review')

    def get(self, request, book, lesson):
        words = get_words_from_lesson(book, lesson)
        for word in words:
            we = WordStat.objects.filter(user=request.user, word=word)
            if we:
                we = we[0]
                if we.correct_num+we.mistake_num is 0:
                    ratio = 0
                else:
                    ratio = float(we.correct_num)/float(we.correct_num+we.mistake_num)
                if ratio >= 0.9:
                    word.we = 3
                elif ratio >= 0.6:
                    word.we = 2
                elif ratio >= 0.2:
                    word.we = 1
                else:
                    word.we = 0

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson})

    def post(self, request, book, lesson):
        num = request.POST.get('num')
        ret = request.POST.get('ret')
        words = request.POST.get('words')
        # self._record(request, book, lesson)
        self._success(request, book, lesson)
        return HttpResponseRedirect('/home')

class LessonsChooseView(TemplateView):
    template_name='crike_django/lessons_choose.html'

    def get(self, request):
        update_strange_words_lesson(request)
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
        books = Book.objects.filter(is_public=True).order_by('name')
        if len(books) == 0:
            return render(request, self.template_name,{})

        if not request.user.is_authenticated():
            return render(request, self.template_name, {'books': books})

        '''
        for book in books:
            for lesson in book.lessons:
                lesson_result = LessonStat.objects.get_or_create(user=request.user,
                                                                 lesson=lesson)[0]
                # XXX this result should never save
                lesson.result = lesson_result
                '''

        las = LessonApply.objects.all()

        return render(request, self.template_name, {'books': books, 'lesson_applies':las})


    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        lessons = Lesson.objects.filter(id=id)
        if not lessons:
            return HttpResponse(status=404)
        lesson = lessons[0]
        la = LessonApply.objects.get_or_create(user=request.user,
                                               lesson=lesson,
                                               )[0]
        la.save()

        return HttpResponse(status=204)


class LessonApplyAcceptView(TemplateView):

    def get(self, request, id):
        las = LessonApply.objects.filter(id=id)
        if not las:
            return HttpResponse(status=404)
        la = las[0]
        lesson_result = LessonStat.objects.get_or_create(user=la.user,
                                                         lesson=la.lesson)[0]
        lesson_result.selected = True
        lesson_result.save()

        la.delete()

        return HttpResponseRedirect('/lessonschoose/')

class LessonApplyDeleteView(TemplateView):

    def get(self, request, id):
        las = LessonApply.objects.filter(id=id)
        if not las:
            return HttpResponse(status=404)
        la = las[0]
        la.delete()

        return HttpResponseRedirect('/lessonschoose/')


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
    template_name='crike_django/exam_words.html'

    def get(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        name = exam.name
        words = []
        for lessonobj in exam.lessons:
            words += Word.objects.filter(id__in=lessonobj.words)

        if len(words) == 0:
            return HttpResponseRedirect('/choice/'+id)

        for word in words:
            words_list = filter(lambda x: x.name !=word.name, words)
            count = len(words_list)
            if count > 3:
                options = sample(words_list, 3)
            else:
                options = sample(words_list, count)
            options.insert(randrange(len(options)+1), word)
            word.options = options

        return render(request, self.template_name,
                {'words':words, 'id':id, 'name':name})

    def post(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        ans = request.POST.getlist('ans')
        ques = request.POST.getlist('ques')
        score = 0
        wrong_list =[]

        for i,an in enumerate(ans):
            if an == ques[i]:
                score += 1
            else:
                wrong_list.append(ques[i])

        """
        profile = get_profile(request.user)
        if profile:
            profile_record_exam_ret(profile, ret)
        """

        examstat = ExamStat.objects.get_or_create(user=request.user, exam=exam)[0]
        examstat.score = score
        examstat.score_words = score
        examstat.wrong_e2c = wrong_list
        examstat.save()

        return HttpResponseRedirect('/c2e/'+id)

class C2EView(TemplateView):
    template_name='crike_django/exam_c2e.html'

    def get(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        name = exam.name
        words = []
        for lessonobj in exam.lessons:
            words += Word.objects.filter(id__in=lessonobj.words)

        if len(words) == 0:
            return HttpResponseRedirect('/choice/'+id)

        for word in words:
            words_list = filter(lambda x: x.name !=word.name, words)
            count = len(words_list)
            if count > 3:
                options = sample(words_list, 3)
            else:
                options = sample(words_list, count)
            options.insert(randrange(len(options)+1), word)
            word.options = options

        return render(request, self.template_name,
                {'words':words, 'id':id, 'name':name})

    def post(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        ans = request.POST.getlist('ans')
        ques = request.POST.getlist('ques')
        score = 0
        wrong_list = []

        for i,an in enumerate(ans):
            if an == ques[i]:
                score += 1
            else:
                wrong_list.append(ques[i])

        """
        profile = get_profile(request.user)
        if profile:
            profile_record_exam_ret(profile, ret)
        """

        examstat = ExamStat.objects.get_or_create(user=request.user, exam=exam)[0]
        examstat.score += score
        examstat.score_words += score
        examstat.wrong_c2e = wrong_list
        examstat.save()

        return HttpResponseRedirect('/dictation/'+id)

class DictationView(TemplateView):
    template_name='crike_django/exam_dictation.html'

    def get(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        name = exam.name
        words = []
        for lessonobj in exam.lessons:
            words += Word.objects.filter(id__in=lessonobj.words)

        if len(words) == 0:
            return HttpResponseRedirect('/choice/'+id)

        for word in words:
            words = sample(words, len(words))

        return render(request, self.template_name,
                {'words':words, 'id':id, 'name':name})

    def post(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        ans = request.POST.getlist('ans')
        ques = request.POST.getlist('ques')
        score = 0
        wrong_list = []

        for i,an in enumerate(ans):
            if an == ques[i]:
                score += 1
            else:
                wrong_list.append(ques[i])

        """
        profile = get_profile(request.user)
        if profile:
            profile_record_exam_ret(profile, ret)
        """

        examstat = ExamStat.objects.get_or_create(user=request.user, exam=exam)[0]
        examstat.score += score
        examstat.score_words += score
        examstat.wrong_dictation = wrong_list
        examstat.save()

        if exam.withtrans:
            return HttpResponseRedirect('/trans/'+id)
        else:
            return HttpResponseRedirect('/choice/'+id)

class TransView(TemplateView):
    template_name='crike_django/exam_trans.html'

    def get(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        name = exam.name
        words = []
        for lessonobj in exam.lessons:
            words += Word.objects.filter(id__in=lessonobj.words)

        if len(words) == 0:
            return HttpResponseRedirect('/choice/'+id)

        for word in words:
            if not word.example or not word.example_t:
                continue
            example = word.example
            """
            if example[len(example)-1] == '.':
                example = example[0:len(example)-1]
            """
            words_list = example.split()
            count = len(words_list)
            options = sample(words_list, count)
            word.options = options

        return render(request, self.template_name,
                {'words':words, 'id':id, 'name':name})

    def post(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        retlist = request.POST.getlist('ret')

        words = []
        for lessonobj in exam.lessons:
            words += Word.objects.filter(id__in=lessonobj.words)
        score = 0
        wrong_list = []

        for i,ret in enumerate(retlist):
            if ret == 'true':
                score += 5
            else:
                wrong_list.append(words[i])

        """
        profile = get_profile(request.user)
        if profile:
            profile_record_exam_ret(profile, ret)
        """

        examstat = ExamStat.objects.get_or_create(user=request.user, exam=exam)[0]
        examstat.score += score
        examstat.score_trans = score
        examstat.wrong_trans = wrong_list
        examstat.save()
        if len(exam.choices) == 0 and len(exam.readings) == 0:
            profile = get_profile(request.user)
            if examstat.tag == "done":
                if profile and examstat.score/exam.totalpoints == 1:
                    profile.point_add(5)
            else:
                examstat.tag = "done"
                if profile:
                    profile.point_add(examstat.score)
            examstat.save()
            profile.save()
            return HttpResponseRedirect('/exam_result/'+id)
        elif len(exam.choices) == 0:
            return HttpResponseRedirect('/reading/'+id)

        return HttpResponseRedirect('/choice/'+id)

class ChoiceView(TemplateView):
    template_name='crike_django/exam_choices.html'

    def get(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        name = exam.name
        choices_list = exam.choices

        if len(choices_list) == 0:
            return HttpResponseRedirect('/reading/'+id)

        return render(request, self.template_name,
                {'questions':choices_list,'id':id,'name':name})

    def post(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        length = len(exam.choices)
        choices = exam.choices

        score = 0
        wrong_list = []
        for i in range(length):
            ans = request.POST.get('answer'+str(i+1), None)
            if ans != None and choices[i].rightindex == eval(ans):
                score += 5
                profile = get_profile(request.user)
                if profile:
                    profile_record_exam_ret(profile, 'true')
            else:
                wrong_list.append(str(i+1)+".("+ans+")")


        examstat = ExamStat.objects.get_or_create(user=request.user, exam=exam)[0]
        examstat.score += score
        examstat.score_choices = score
        examstat.wrong_choices = wrong_list
        examstat.save()

        if len(exam.readings) == 0:
            profile = get_profile(request.user)
            if examstat.tag == "done":
                if profile and examstat.score/exam.totalpoints == 1:
                    profile.point_add(5)
            else:
                examstat.tag = "done"
                if profile:
                    profile.point_add(examstat.score)
            examstat.save()
            profile.save()
            return HttpResponseRedirect('/exam_result/'+id)

        return HttpResponseRedirect('/reading/'+id)


class ReadingView(TemplateView):
    template_name='crike_django/exam_readings.html'

    def get(self, request, id):
        exam = Exam.objects.filter(id=id)[0]
        name = exam.name
        readings_list = exam.readings

        if len(readings_list) == 0:
            return HttpResponseRedirect('/exam_result/'+id)

        paginator = Paginator(readings_list, 1)
        page = request.GET.get('page')
        readings = get_readings_from_paginator(paginator, page)

        return render(request, self.template_name,
                {'readings':readings,'id':id,'name':name})

    def post(self, request, id):
        page = request.POST.get('page')
        exam = Exam.objects.filter(id=id)[0]
        length = len(exam.readings)
        reading = None
        curpage = 0
        if page != None and page != '0':
            curpage = eval(page)-2
        elif page == '0':
            curpage = length-1
        reading = exam.readings[curpage]

        score = 0
        wrong_list = []
        for i in range(5):
            ans = request.POST.get('answer'+str(i+1), None)
            if ans != None and reading.questions[i].rightindex == eval(ans):
                score += 5
                profile = get_profile(request.user)
                if profile:
                    profile_record_exam_ret(profile, 'true')
            else:
                wrong_list.append(str(curpage+1)+"_"+str(i+1)+".("+ans+")")

        examstat = ExamStat.objects.get_or_create(user=request.user, exam=exam)[0]
        examstat.score += score
        if curpage == 0:
            examstat.wrong_readings = wrong_list
            examstat.score_readings = score
        else:
            examstat.wrong_readings = examstat.wrong_readings + wrong_list
            examstat.score_readings = examstat.score_readings + score

        examstat.save()

        if page == '0':
            profile = get_profile(request.user)
            if examstat.tag == "done":
                if profile and examstat.score/exam.totalpoints == 1:
                    profile.point_add(5)
            else:
                examstat.tag = "done"
                if profile:
                    profile.point_add(examstat.score)
            examstat.save()
            profile.save()
            return HttpResponseRedirect('/exam_result/'+id)

        return HttpResponseRedirect('/reading/'+id+'/?page='+page)


class ExamResultView(TemplateView):
    template_name='crike_django/exam_result.html'

    def get(self, request, id):
        exams = Exam.objects.filter(id=id)
        if exams is []:
            return HttpResponseRedirect('/home/')

        exam = exams[0]
        examstats = ExamStat.objects.filter(
                user=request.user, exam=exam)
        if examstats is []:
            return HttpResponseRedirect('/home/')

        examstat = examstats[0]
        examstat.total_choices = len(exam.choices)*5
        examstat.total_readings = len(exam.readings)*25
        examstat.total_words = 0
        examstat.total_trans = 0
        for lesson in exam.lessons:
            examstat.total_words += len(lesson.words)*3
            if exam.withtrans:
                examstat.total_trans += len(lesson.words)*5

        return render(request, self.template_name,
                {'examstat':examstat})


class ExamAdminView(TemplateView):
    template_name = 'crike_django/exams_admin.html'

    def get(self, request):
        exams = Exam.objects.all()
        return render(request, self.template_name,
                {'books':Book.objects.all(),'exams':exams})

    def post(self, request, *args, **kwargs):
        examid = request.POST.get('id', None)
        if request.POST.get('delexam', None):
            exam = Exam.objects.filter(id=examid)[0]
            exam.delete()
            return HttpResponseRedirect("/admin/exams")

        examname = request.POST['name']
        lessonids = request.POST.getlist('addlessons')
        if examid:
            exam = Exam.objects.filter(id=examid)[0]
            exam.name = examname
            exam.lessons[:] = []
            exam.totalpoints = 0
        else:
            exam = Exam.objects.get_or_create(name=examname)[0]

        if request.POST.get('withtrans', None):
            exam.withtrans = True;
        else:
            exam.withtrans = False;

        for lessonid in lessonids:
            lesson = Lesson.objects.filter(id=lessonid)[0]
            exam.lessons.append(lesson)
            if exam.withtrans:
                exam.totalpoints += len(lesson.words)*8
            else:
                exam.totalpoints += len(lesson.words)*3

        exam.choices[:] = []
        choices_raw = request.POST.getlist('choice')
        for choice_raw in choices_raw:
            choice = json.loads(choice_raw)
            question = choice['question']
            choiceobj = Choicesingle(question=question)
            choiceobj.answers = choice['choices']
            rightindex = choice.get('rightindex', None)
            if rightindex:
                choiceobj.rightindex = rightindex;
            else:
                choiceobj.rightindex = 0;
            exam.choices.append(choiceobj)

        exam.readings[:] = []
        readings_raw = request.POST.getlist('reading')
        for reading_raw in readings_raw:
            reading = json.loads(reading_raw)
            article = reading['article'].replace("<br>","\n")
            readingobj = Reading(name=reading['name'],
                                        article=article)
            for question in reading['questions']:
                questionobj = Choicesingle(question=question['question'])
                questionobj.answers = question['choices']
                rightindex = question.get('rightindex', None)
                if rightindex:
                    questionobj.rightindex = rightindex;
                else:
                    questionobj.rightindex = 0;

                readingobj.questions.append(questionobj)

            exam.readings.append(readingobj)

        exam.totalpoints += len(exam.choices)*5
        exam.totalpoints += len(exam.readings)*25
        exam.save()
        return HttpResponseRedirect("/admin/exams")


class PrizeAdminView(TemplateView):
    def get(self, request):
        return HttpResponse('FIXME')

    def post(self, request, *args, **kwargs):
        form = PrizeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prize')
        return redirect('prize')


class PrizeQueryView(TemplateView):
    template_name = 'crike_django/prize_query_view.html'

    def get(self, request, prize_query_pk, *args, **kwargs):
        if prize_query_pk is None:
            kwargs.update({'error_message': '请求无效！'})
            return render(request, self.template_name, kwargs)
        prize_query = PrizeQuery.objects.get(pk=prize_query_pk)
        prize_query.done = True
        prize_query.save()
        kwargs.update({'success_message': '已成功执行你的请求！'})
        return render(request, self.template_name, kwargs)


class PrizeDeleteView(TemplateView):

    def get(self, request, prize_pk, *args, **kwargs):
        prize = Prize.objects.get(pk=prize_pk)
        if prize is not None:
            prize.delete()
        return redirect('prize')


class PrizeView(TemplateView):
    template_name = 'crike_django/prize_view.html'

    def get_all(self, request, prize_pk, *args, **kwargs):
        try:
            prize_queries = PrizeQuery.objects.filter(done=False)
        except PrizeQuery.DoesNotExist:
            prize_queries = []

        prizes = Prize.objects.all()
        form = PrizeForm()
        success_message = kwargs.get('success_message', None)
        error_message = kwargs.get('error_message', None)
        return render(request, self.template_name, {
            'prizes':prizes,
            'form': form,
            'prize_queries': prize_queries,
            'success_message': success_message,
            'error_message': error_message,
        })

    def get(self, request, prize_pk, *args, **kwargs):
        '''
        if prize_pk is valid, here will generate a PrizeQuery,
        which attached to current User.
        if prize_pk is null, just show all Prizes.
        '''
        if prize_pk is not None:
            profile = get_profile(request.user)
            if profile is None:
                pass
            else:
                prize = Prize.objects.get(pk=prize_pk)
                if prize.amount <=0:
#TODO when a prize amount get to zero, take it off the shelf
                    kwargs.update({'error_message': 'Prize not available!'})
                    return self.get_all(request, prize_pk, *args, **kwargs)
                ret = profile.point_add(-prize.value)
                if ret is True:
                    profile.save()
                    prize.amount -= 1
                    prize.save()
                    PrizeQuery.objects.create(
                        user=request.user,
                        prize=prize,
                        value=prize.value,
                    )
                    kwargs.update({'success_message': '已成功执行你的请求！'})
                elif ret is False:
                    kwargs.update({'error_message': '点数不足！'})

        return self.get_all(request, prize_pk, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''
        Create a new Prize.
        '''
        form = PrizeForm(request.POST)
        if form.is_valid():
            form.save()

        kwargs.update({'success_message': '已成功执行你的请求！'})
        return self.get_all(request, None, *args, **kwargs)


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
            lessonemb = get_lessonemb(book, lesson)
            lessonobj = get_lessonobj(lessonemb)
            newname = request.POST['newname']
            if not get_lessonemb(book, newname):
                lessonobj.name = newname
                lessonobj.save()
                update_exam_lesson(lessonemb, lessonobj)
                update_book_lesson(lessonemb, lessonobj)
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

            lessonemb = get_lessonemb(book, lesson)
            lessonobj = get_lessonobj(lessonemb)
            word = None
            words = Word.objects.filter(name=request.POST['name'])
            if len(words) > 0:
                word = words[0]
            else:
                word = Word()
                word.name = request.POST['name']
                word.mean = request.POST['mean'].replace('\r','').split('\n')
                word.phonetics = request.POST['phonetics']
                word.structure = request.POST['structure']
                word.extension = request.POST['extension']
                word.remark = request.POST['remark']
                word.example = request.POST['example']
                word.example_t = request.POST['example_t']
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

            lessonobj.words.append(word.id)
            lessonobj.save()
            update_exam_lesson(lessonemb, lessonobj)
            update_book_lesson(lessonemb, lessonobj)

        if request.POST['extra'] == 'delword':
            words = request.POST.getlist('delwords')
            lessonemb = get_lessonemb(book, lesson)
            lessonobj = get_lessonobj(lessonemb)
            for word in words:
                wordobj = Word.objects.filter(name=word)[0]
                if wordobj.id in lessonobj.words:
                    lessonobj.words.remove(wordobj.id)
                lessonobj.save()
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
            update_exam_lesson(lessonemb, lessonobj)
            update_book_lesson(lessonemb, lessonobj)

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
            word.structure = request.POST['structure']
            word.extension = request.POST['extension']
            word.remark = request.POST['remark']
            word.example = request.POST['example']
            word.example_t = request.POST['example_t']
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
                if get_lessonemb(book, lesson):
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
                for lessonemb in bookob.lessons:
                    if lessonemb.name == lesson:
                        lessonobj = get_lessonobj(lessonemb)
                        if lessonobj:
                            lessonobj.delete()
                        bookob.lessons.remove(lessonemb)
                        delete_exam_lesson(lessonemb)
                        delete_lesson_stat(lessonemb)
            bookob.save()
            if len(bookob.lessons) == 0:
                bookob.delete()

        return HttpResponseRedirect("/admin/books/")

class WordPopupView(TemplateView):

    def get(self, request, wordname):
        data = None
        words = Word.objects.filter(name=wordname)
        if not words:
            mp3path = MEDIA_ROOT+'/audios/'+wordname+".mp3"
            if os.path.exists(mp3path):
                os.remove(mp3path)
            download_word(wordname)
            words = Word.objects.filter(name=wordname)

        if words:
            some_data_to_dump = {
               'mean': words[0].mean,
               'phonetics': '['+words[0].phonetics+']',
            }

        else:
            some_data_to_dump = {
               'mean': 'NOT FOUND IN DATABASE',
               'phonetics': '[sorry!]',
            }
        data = simplejson.dumps(some_data_to_dump)
        return HttpResponse(data, mimetype='application/json')

    def post(self, request, wordname):
        words = Word.objects.filter(name=wordname)
        if not words:
            return HttpResponse(status=404)
        else:
            word = words[0]

        """
        book_obj = Book.objects.get_or_create(name=request.user.username+"_book", is_public=False)[0]
        lesson_embs = filter(lambda x: x.name == 'strange_words', book_obj.lessons)
        lesson_obj = None
        if len(lesson_embs) > 0:
            lesson_emb = lesson_embs[0]
            lesson_obj = get_lessonobj(lesson_emb)
            lesson_obj.book = book_obj
            book_obj.lessons.remove(lesson_emb)
            if not word.id in lesson_obj.words:
                lesson_obj.words.append(word.id)
        else:
            lesson_obj = Lesson(name='strange_words', book=book_obj)
            lesson_obj.words.append(word.id)
        lesson_obj.save()
        book_obj.lessons.append(lesson_obj)
        book_obj.save()
        """
        # words add to strange_words need to have a mistake_num greater or equal to 2
        word_stat,ret = WordStat.objects.get_or_create(user=request.user,
                                                   word=word, mistake_num=3)
        word_stat.save()

        return HttpResponse(status=204)


"""
weixin bigger code
"""
IMAGE_URL_BASE = 'http://114.215.113.3/media/images/'
AUDIO_URL_BASE = 'http://114.215.113.3/media/audios/'
URL_BASE = 'http://114.215.113.3/'

class WeixinBiggerView(TemplateView):

    @csrf_exempt
    def get(self, request):
        ret = self.checkSignature(request)
        if ret:
            return HttpResponse(ret)
        else:
            return HttpResponse("Ping, I love you!!!")

    @csrf_exempt
    def post(self, request):
        def gettext(tag):
            if xml.find(tag) is not None:
                return xml.find(tag).text
            else:
                return ''
        xml_str = smart_str(request.body)
        #print xml_str
        xml = etree.fromstring(xml_str)#进行XML解析
        msgType = gettext("MsgType")
        msgid = gettext("MsgId")
        fromUser = gettext("FromUserName")
        toUser = gettext("ToUserName")
        createTime = gettext("CreateTime")

        content = {'mode':'text', 'title':'', 'desc':'',
                'picurl':'', 'url':''}

        if msgType == "event":
            event = gettext("Event")
            if event == "subscribe":
                content['desc'] = """欢迎关注比格！
小格目前有两大技能：
1）我是英文达人
2）我还是印象派油画大师
我能中英互翻，可以语音哦，跟我说话我帮您翻译；
我词汇量巨大，发单词考我，绝对难不倒我；
也可以发图片，我给您画成印象派"""
            elif event == "unsubscribe":
                content['desc'] = "Good bye, seems you don't need me anymore, uuu..."
            content['mode'] = 'text'

        elif msgType == "text" or msgType == "voice":
            if msgType == "text":
                wordname=gettext("Content")#获得用户所输入的内容
            else:
                text_raw=gettext("Recognition")
                wordname=text_raw.replace(u'！',' ').replace(u'。',' ')

            if re.match('^#.+$', wordname):#this is a command
                cmdline = wordname[1:].split(' ')
                cmd = cmdline[0]
                content['mode'] = 'text'
                if cmd == 'h':
                    content['desc'] = """
h: 打印本帮助信息;
l: 列出历史查询单词:
    无参数：全部;
    参数n：最近n个;
d: 删除某单词:
    可接一个或多个单词,
    以空格分隔;
                    """
                elif cmd == 'l':
                    if len(cmdline) == 2 and re.match('^[1-9]+[0-9]*$', cmdline[1]):
                        end = eval(cmdline[1])
                        items = BiggerWord.objects.filter(userid=fromUser).order_by('-time_modified')[:end]
                    else:
                        items = BiggerWord.objects.filter(userid=fromUser).order_by('-time_modified')

                    rets = ['Your list: (%d)'%len(items),]
                    for item in items:
                        rets.append(item.wordname+'\n    ['+str(item.count)+']'+
                                (item.time_modified+timedelta(hours=8)).strftime("%m-%d %H:%M:%S"))
                    content['desc'] = '\n'.join(rets)

                elif cmd == 'd':
                    if len(cmdline) >= 2:
                        rets = []
                        for arg in cmdline[1:]:
                            if re.match('^[A-Za-z]+$', arg):
                                items = BiggerWord.objects.filter(userid=fromUser, wordname=arg)
                                for item in items:
                                    rets.append(item.wordname)
                                    item.delete()
                        content['desc'] = ','.join(rets)+'\ndeleted!'
                    else:
                        content['desc'] = u"请指定您要删除的单词"

            elif re.match('^[A-Za-z]+$', wordname):
                words = Word.objects.filter(name=wordname)
                if not words or len(words[0].mean) == 0:
                    download_word(wordname)

                words = Word.objects.filter(name=wordname)
                if words:#after we try download words
                    content['title']=wordname
                    if words[0].phonetics != '':
                        content['desc']='['+words[0].phonetics+']\n'+'\n'.join(words[0].mean)
                    else:
                        content['desc']='\n'.join(words[0].mean)
                    imgpath = MEDIA_ROOT+'/images/'+wordname+"/0.jpg"
                    if os.path.exists(imgpath):
                        content['picurl']=IMAGE_URL_BASE+wordname+'/0.jpg'
                    elif re.match('^[A-Za-z]+$', wordname):
                        process = Process(target=download_images_single, args=(wordname,))
                        process.start()
                    '''
                    mp3path = MEDIA_ROOT+'/audios/'+wordname+".mp3"
                    if os.path.exists(mp3path):
                        content['url']=AUDIO_URL_BASE+wordname+".mp3"
                        '''
                    content['url'] = 'http://dict.youdao.com/dictvoice?audio='+wordname
                    content['mode'] = 'news'

                else:
                    content['desc'] = "Sorry, we are still thinking about "+wordname
                    content['mode'] = 'text'

                #record this to db, will let user to list their history
                item = BiggerWord.objects.get_or_create(userid=fromUser, wordname=wordname)[0]
                item.count = item.count + 1
                item.save()
            else:
                YOUDAO_URL = 'http://fanyi.youdao.com/openapi.do?keyfrom=bigger&key=1389170092&type=data&doctype=json&version=1.1&q=' \
                             +quote(wordname.encode('utf-8'))
                result = urllib2.urlopen(YOUDAO_URL).read()
                if result:
                    print 'mmmmmmmmmmmmm',result
                    result = json.loads(result)
                    mean = result.get('translation',[])
                    if len(mean) != 0:
                        content['desc'] = wordname+'\n'+'\n'.join(mean)

                if content['desc'] == '':
                    content['desc'] = "Sorry, I don't know "+wordname
                content['mode'] = 'text'

        elif msgType == "image":
            picurl = gettext("PicUrl")
            mediaid = gettext("MediaId")

            """
            content['desc'] = ("服务器升级维护中，暂停服务；"
                               "预计21号恢复服务，给您带来的不便，敬请谅解")
            content['mode'] = 'text'
            xml_str = self.reply_str(fromUser,toUser,createTime,content)
            print xml_str
            return HttpResponse(xml_str)
            """

            tasks = NeuralTask.objects.filter(userid=fromUser, done=False)
            print len(tasks)
            if len(tasks) >= 3:
                content['desc'] = ("十分抱歉，您的排队任务已经超过3个。"
                                  "我们目前的服务能力有限，请您等待前面的任务完成后再试，谢谢！"
                                  "（点击前面的任务消息可以查看是否完成）")
                content['mode'] = 'text'
                xml_str = self.reply_str(fromUser,toUser,createTime,content)
                #print xml_str
                return HttpResponse(xml_str)
 
            task = NeuralTask.objects.create(userid=fromUser, mediaid=mediaid,
                                             msgid=msgid, style="starry_night",
                                             status="prepost", picurl=picurl)
            task.save()

            content['mode'] = 'news'
            content['picurl'] = picurl
            content['url'] = URL_BASE+'get-neural-task-status/'+mediaid
            content['title'] = '比格图片任务卡'
            content['desc'] = '请点击该消息选择画风，跟踪进展，获取处理结果。'


        xml_str = self.reply_str(fromUser,toUser,createTime,content)
        #print xml_str
        return HttpResponse(xml_str)

    @csrf_exempt
    def dispatch(self, request):
        return super(WeixinBiggerView, self).dispatch(request)

    def checkSignature(self, request):
        signature=request.GET.get('signature',None)
        timestamp=request.GET.get('timestamp',None)
        nonce=request.GET.get('nonce',None)
        echostr=request.GET.get('echostr',None)

        #这里的token根据自己需求修改
        token="weixinbigger"

        tmplist=[token,timestamp,nonce]
        tmplist.sort()
        tmpstr="%s%s%s"%tuple(tmplist)
        tmpstr=hashlib.sha1(tmpstr).hexdigest()
        if tmpstr==signature:
            return echostr
        else:
            return None

    def reply_str(self, toUser, fromUser, createTime, content):
        if content['mode'] == 'text':
            xml_str = """<xml>
<ToUserName><![CDATA["""+toUser+"""]]></ToUserName>
<FromUserName><![CDATA["""+fromUser+"""]]></FromUserName>
<CreateTime>"""+createTime+"""</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA["""+content['desc']+"""]]></Content>
</xml>"""
        elif content['mode'] == 'news':
            xml_str = """<xml>
<ToUserName><![CDATA["""+toUser+"""]]></ToUserName>
<FromUserName><![CDATA["""+fromUser+"""]]></FromUserName>
<CreateTime>"""+createTime+"""</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA["""+content['title']+"""]]></Title>
<Description><![CDATA["""+content['desc']+"""]]></Description>
<PicUrl><![CDATA["""+content['picurl']+"""]]></PicUrl>
<Url><![CDATA["""+content['url']+"""]]></Url>
</item>
</Articles>
</xml>"""

        return xml_str

def start_neural_task(task):
    picurl = task.picurl
    mediaid = task.mediaid
    fromUser = task.userid
    style = task.style

    process = Process(target=download_image_from_weixin, args=(picurl, mediaid, ))
    process.start()

    picurl = IMAGE_URL_BASE+'from_weixin/'+mediaid+'.jpg'
    picpath = MEDIA_ROOT+"/images/from_weixin/"+mediaid+".jpg"

    """
    count = 20
    while count > 0 and process.is_alive():
        time.sleep(1)
        count -= 1
    """
    time.sleep(1)

    if os.path.exists(picpath):
        process2 = Process(target=send_image_to_neural_server, args=(picpath, mediaid, fromUser, style, ))
        process2.start()

        task.status = 'posting'
        task.picurl = picurl
        task.save()
    else:
        print "Can not save pic %s from weixin" % mediaid

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

def download_image_from_weixin(picurl, mediaid):
    PIC_DIR = MEDIA_ROOT+"/images/from_weixin/"

    if not os.path.exists(PIC_DIR):
        os.makedirs(PIC_DIR)
    fname = os.path.join(PIC_DIR, '%s.jpg') % mediaid
    try:
        urllib.urlretrieve(picurl, fname)
        if not is_file_valid(fname):
            os.remove(fname)
    except IOError, e:
        # Throw away some gifs...blegh.
        print 'could not save %s' % picurl

def send_image_to_neural_server(fname, mediaid, userid, style):
    requrl = "http://task-manager.anwcl.com/neural-task/"

    try:
        register_openers()
        datagen, headers = multipart_encode(
                {'image':open(fname, "rb"),
                 'image_id':mediaid,
                 'user_id':userid,
                 'style_image_path':style+'.jpg',
                 'image_url':IMAGE_URL_BASE+'from_weixin/'+mediaid+'.jpg'})
        request = urllib2.Request(requrl, datagen, headers)
        urllib2.urlopen(request)
    except IOError, e:
        print '[POST] could not post %s' % mediaid


@csrf_exempt
def neural_task_reply(request):
    if request.method == 'GET':
        #print_request_header(request)
        return HttpResponse(status=403)

    PIC_DIR = MEDIA_ROOT+"/images/to_weixin/"
    mediaid = request.POST.get('image_id', None)
    if not mediaid:
        print "Can't get image_id"
        return HttpResponse(status=403)
    if not os.path.exists(PIC_DIR):
        os.makedirs(PIC_DIR)
    fname = os.path.join(PIC_DIR, '%s.jpg') % mediaid
    tasks = NeuralTask.objects.filter(mediaid=mediaid)
    if len(tasks) > 0:
        task = tasks[0]
        task.done = True
        if request.FILES.get('image', None):
            save_file(request.FILES['image'], fname)
            task.status = 'finished'
            task.save()
            return HttpResponse(status=200)
        else:
            task.status = 'error'#TODO need to modify posted html to let user restart the task
            task.save()
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)


@csrf_exempt
def print_request_header(request):
    regex_http_          = re.compile(r'^HTTP_.+$')
    regex_content_type   = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')

    request_headers = {}
    for header in request.META:
        if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
            request_headers[header] = request.META[header]
            print header, request.META[header]

@csrf_exempt
def get_neural_task_status(request, mediaid):
    tasks = NeuralTask.objects.filter(mediaid=mediaid)
    if len(tasks) == 0:
        print "Can't find task %s" % mediaid
        return HttpResponse(status=403)

    task = tasks[0]
    picpath = MEDIA_ROOT+"/images/from_weixin/"+mediaid+".jpg"

    if task.status == 'prepost':
        return render(request, 'crike_django/neural_task_prepost.html',{'MediaID':mediaid})
    if task.status == 'posting':
        time.sleep(3)
        content = get_content_from_url('http://task-manager.anwcl.com')
        task_list = re.findall(mediaid, content, re.M | re.S)
        if len(task_list) == 0:
            process = Process(target=send_image_to_neural_server, args=(picpath, mediaid, task.userid, task.style, ))
            process.start()
            print 'No task found, post again!'
        else:
            task.status = 'posted'
            task.save()
        return render(request, 'crike_django/neural_task_posted.html', {'MediaID':mediaid})
    if task.status == 'posted':
        return render(request, 'crike_django/neural_task_posted.html', {'MediaID':mediaid})
    if task.status == 'error':
        process = Process(target=send_image_to_neural_server, args=(picpath, mediaid, task.userid, task.style, ))
        process.start()
        task.status = 'posting'
        task.save()
        return render(request, 'crike_django/neural_task_posted.html', {'MediaID':mediaid})
    if task.status == 'finished':
        return render(request, 'crike_django/neural_task_result.html', {'MediaID':mediaid})

@csrf_exempt
def set_neural_task_prepost(request):
    mediaid = request.POST.get('mediaid', None)
    style = request.POST.get('style', None)
    if not mediaid:
        return HttpResponse(status=403)

    tasks = NeuralTask.objects.filter(mediaid=mediaid)
    if len(tasks) == 0:
        print "Can't find task %s" % mediaid
        return HttpResponse(status=403)

    task = tasks[0]

    if task.status == 'prepost':
        task.style = style
        task.save()
        '''
        if task.payed:
            start_neural_task(task)
        else:
            start_payment(task)
            '''
        start_neural_task(task)

    return HttpResponseRedirect("/get-neural-task-status/"+mediaid)

@csrf_exempt
def start_payment(task):
    url = create_partner_trade_by_buyer(task.mediaid,
                                        u"比格油画",
                                        u"您选择了画风 "+task.style,
                                        9.9)
    print 'uuuuu',url
    return HttpResponseRedirect(url)

@csrf_exempt
def set_neural_task_payed(request):
    if notify_verify(request.GET):
        mediaid = request.GET.get('out_trade_no')
        if not mediaid:
            return HttpResponse(status=403)

        tasks = NeuralTask.objects.filter(mediaid=mediaid)
        if len(tasks) == 0:
            print "Can't find task %s" % mediaid
            return HttpResponse(status=403)

        task = tasks[0]
        task.payed = True
        task.save()
        start_neural_task(task)
        trade_no = request.GET.get('trade_no')
        url=send_goods_confirm_by_platform (trade_no)
        req=urllib.urlopen (url)

        return HttpResponseRedirect("/get-neural-task-status/"+mediaid)

    return HttpResponse(status=403)

@csrf_exempt
def notify_neural_task_payed(request):
    if notify_verify(request.POST):
        mediaid = request.GET.get('out_trade_no')
        if not mediaid:
            return HttpResponse(status=403)

        tasks = NeuralTask.objects.filter(mediaid=mediaid)
        if len(tasks) == 0:
            print "Can't find task %s" % mediaid
            return HttpResponse(status=403)

        task = tasks[0]
        task.payed = True
        task.save()
        start_neural_task(task)
        trade_no = request.GET.get('trade_no')
        url=send_goods_confirm_by_platform (trade_no)
        req=urllib.urlopen (url)

        return HttpResponse('success')

    return HttpResponse('fail')
