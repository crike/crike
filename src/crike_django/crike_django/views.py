#coding:utf-8
from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# Imaginary function to handle an uploaded file.
from crike_django.models import *
from crike_django.forms import *
from crike_django.settings import MEDIA_ROOT,STATIC_ROOT
from word_utils import *

# TODO: Upload file的view
# 规定具体的get/post对应事件

class DictView(TemplateView):
    template_name = 'crike_django/dict_view.html'

    def get(self, request, *args, **kwargs):
        # 1.取出所有/指定词典，然后用模版渲染
        # 2.按页进行分页，使用pagination
        basic_dicts = BasicDict.objects.all()
        p = Paginator(basic_dicts, 20).page(1)
        return render(request, self.template_name, {
            'p_dicts': p,
        })

    # 当前此post方法仅为上传word至dict使用
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word', None)
        word_translated = request.POST.get('word_translated', None)
        dict_type = request.POST.get('dict_type', 'BasicDict')

        bd = BasicDict.objects.get(dict_type=dict_type)
        bd[word] = word_translated
        bd.save()
        return

def import_dict():
    pass

#功能：上传文件，然后把文件用handle_uploaded_file处理
def upload_file(request):
    upload_template = 'crike_django/upload_file.html'
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            dictname = request.POST['dict']
            lesson = request.POST['lesson']
            if len(Dict.objects(name=dictname)) > 0:
                dic = Dict.objects(name=dictname).first()
                if len(dic.lessons.objects(name=lesson)) > 0:
                    return render(request, upload_template, {'form':form, 'warning':'Duplicated Lesson!!'})
            handle_uploaded_file(request.POST['dict'], 
                    request.POST['lesson'],             
                    request.FILES['file'])
            return HttpResponseRedirect('/show/')
    else:
        form = UploadFileForm()
    return render(request, upload_template, {'form': form})

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

"""
def display_image(request, name):
    path = STATIC_ROOT+'/images/'+name
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type="image/jpeg")
    else:
        return HttpResponse(None)
"""

def show_words(request):
    template_name='crike_django/words_list.html'

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
        audiofile = MEDIA_ROOT+'/'+word.name+'.mp3'
        if os.path.exists(audiofile):
            os.remove(audiofile)
        word.delete()
        template = 'crike_django/words_list.html'
        params = {'Words': Word.objects.all()}
        return HttpResponseRedirect("/show/")

class LessonView(TemplateView):
    template_name='crike_django/lesson_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

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
