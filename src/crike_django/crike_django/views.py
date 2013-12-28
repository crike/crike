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
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/show/')
    else:
        form = UploadFileForm()
    return render(request, 'crike_django/upload_file.html', {'form': form})

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

def testdb(request):
    # test
    # entry = Word(name='test')
    wordname = "apple"
    if len(Word.objects(name=wordname)) > 0:
        e = Word.objects(name=wordname)[0]
    else:
        e = download_word(wordname)
        e.save()
    print "word:"+e["name"]+': ['+e["phonetics"]+'] '+e["pos"][0]+' '+e["mean"][0]
    ret =  e["name"]+': ['+e["phonetics"]+'] '+e["pos"][0]+' '+e["mean"][0]
    return HttpResponse(ret.encode("utf-8"))

def listen(request):
    id = request.GET['id']
    word = Word.objects(id=id).first()
    response = HttpResponse(word.audio.read(), content_type="audio/mpeg")
    return response

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
        os.remove(word.audio)
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
