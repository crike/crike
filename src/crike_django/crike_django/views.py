#coding:utf-8
from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# Imaginary function to handle an uploaded file.
from crike_django.models import *
from crike_django.forms import *
from crike_django.settings import MEDIA_ROOT,STATIC_ROOT
from word_utils import *
from random import sample, randrange

# TODO: Upload file的view
# 规定具体的get/post对应事件

class DictView(TemplateView):
    template_name = 'crike_django/dict_view.html'

    def get(self, request, *args, **kwargs):
        # 1.取出所有/指定词典，然后用模版渲染
        # 2.按页进行分页，使用pagination
        basic_dicts = Dict.objects.all()
        p = Paginator(basic_dicts, 20).page(1)
        return render(request, self.template_name, {
            'p_dicts': p,
        })

    # 当前此post方法仅为上传word至dict使用
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word', None)
        word_translated = request.POST.get('word_translated', None)
        dict_type = request.POST.get('dict_type', 'BasicDict')

        bd = Dict.objects.get(dict_type=dict_type)
        bd[word] = word_translated
        bd.save()
        return

def import_dict():
    pass

class StudentView(TemplateView):
    template_name = 'crike_django/student_view.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class TeacherView(TemplateView):
    template_name = 'crike_django/teacher_view.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def hello_crike(request):
    print request
    return HttpResponse("Hello crike!")

def play_audio(request, name):
    #word = Word.objects(name=name).first()
    #return HttpResponse(word.audio.read(), content_type="audio/mpeg")
    path = MEDIA_ROOT+'/audios/'+name
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type="audio/mpeg")
    else:
        return HttpResponse(None)

   #def display_image(request, name):
   #    path = STATIC_ROOT+'/images/'+name
   #    if os.path.exists(path):
   #        file = open(path, 'rb')
   #        return HttpResponse(file.read(), content_type='image/jpeg')
   #    else:
   #        return HttpResponse(None)

def show_all_words(request):
    template_name='crike_django/words_list.html'

    words = Word.objects.all()
    if len(words) != 0:
        request.encoding = "utf-8"

    return render(request, template_name, {'Words':words})

def show_words(request, dic, lesson):
    template_name='crike_django/words_list.html'

    words = []
    for lessonob in Dict.objects(name=dic)[0].lessons:
        if lessonob.name == lesson:
            words = lessonob.words
    if len(words) != 0:
        request.encoding = "utf-8"

    return render(request, template_name, {'Words':words, 'dic':dic, 'lesson':lesson})

def show_lessons(request, dic):#TODO
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
        word = Word.objects(id=id)[0]
        audiofile = MEDIA_ROOT+'/audios/'+word.name+'.mp3'
        if os.path.exists(audiofile):
            os.remove(audiofile)
        word.delete()
        return HttpResponseRedirect("/show_all_words/")

def delete_lesson(request, dic, lesson):
    template = 'crike_django/lesson_delete.html'
    params = { 'dic':dic, 'lesson':lesson }
    return render(request, template, params)

def show_lib(request):
    return render(request, 'crike_django/lib.html', {})

class LessonShowView(TemplateView):
    template_name='crike_django/lesson_show.html'

    def get(self, request, *args, **kwargs):
        dic = request.GET.get('dic')
        lesson = request.GET.get('lesson')
        words_list = []
        dicob = Dict.objects(name=dic).first()
        for lessonobj in dicob.lessons:
            if lessonobj.name == lesson:
                words_list = lessonobj.words

        paginator = Paginator(words_list, 1)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        return render(request, self.template_name,
               {'words':words, 'dic':dic, 'lesson':lesson})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class LessonPickView(TemplateView):
    template_name='crike_django/lesson_pick.html'

    def get(self, request, *args, **kwargs):
        dic = request.GET.get('dic')
        lesson = request.GET.get('lesson')
        words_list = []
        dicob = Dict.objects(name=dic).first()
        for lessonobj in dicob.lessons:
            if lessonobj.name == lesson:
                words_list = lessonobj.words

        paginator = Paginator(words_list, 1)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        words_list.remove(words[0])
        options = sample(words_list, 3)
        options.insert(randrange(len(options)+1), words[0])

        return render(request, self.template_name,
               {'words':words, 'dic':dic, 'lesson':lesson, 'options':options})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class LessonView(TemplateView):
    template_name='crike_django/lesson_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class DictsView(TemplateView):
    template_name='crike_django/dicts_list.html'
    dicts = Dict.objects.all()

    def get(self, request, *args, **kwargs):
        uploadform = UploadFileForm()
        if len(self.dicts) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name,
                {'Dicts':self.dicts, 'Uploadform':uploadform})

    #功能：上传文件，然后把文件用handle_uploaded_file处理
    def post(self, request, *args, **kwargs):
        if request.POST['extra'] == 'add':
            uploadform = UploadFileForm(request.POST, request.FILES)
            if uploadform.is_valid():
                dictname = request.POST['dict']
                lesson = request.POST['lesson']
                if len(Dict.objects(name=dictname)) > 0:
                    dic = Dict.objects(name=dictname).first()
                    for item in dic.lessons:
                        if item.name == lesson:
                            return render(request, self.template_name,
                                    {'Dicts':self.dicts,'Uploadform':uploadform,
                                      'Showform':'uploadform', 'Uploadwarning':'Duplicated Lesson!!'})

                handle_uploaded_file(request.POST['dict'],
                        request.POST['lesson'],
                        request.FILES['file'])
                return HttpResponseRedirect('/dicts/')
            return render(request, self.template_name,
                    {'Dicts':self.dicts, 'Uploadform':uploadform, 'Showform':'uploadform'})

        elif request.POST['extra'] == 'delete':
            dic = request.POST['deldic']
            print request.POST
            lessons = request.POST.getlist('dellessons')
            dicob = Dict.objects(name=dic).first()
            for lesson in lessons:
                for lessonobj in dicob.lessons:
                    if lessonobj.name == lesson:
                        dicob.lessons.remove(lessonobj)
            dicob.save()

        return HttpResponseRedirect("/dicts/")

class ExamView(TemplateView):
    template_name='crike_django/exam_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class HomeView(TemplateView):
    template_name='crike_django/home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")
