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

# Upload file的view
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

def upload_file(request, handle_uploaded_file=None):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form})

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

def home():
    return HttpResponse("Hello crike!")
