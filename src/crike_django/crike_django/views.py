
from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator
from django.shortcuts import render

from crike_django.models import *

# Upload file��view
# �涨�����get/post��Ӧ�¼�
class DictView(TemplateView):
    template_name = 'crike_django/dict_view.html'

    def get(self, request, *args, **kwargs):
        # 1.ȡ������/ָ���ʵ䣬Ȼ����ģ����Ⱦ
        # 2.��ҳ���з�ҳ��ʹ��pagination
        basic_dicts = BasicDict.objects.all()
        p = Paginator(basic_dicts, 20).page(1)
        return render(request, self.template_name, {
            'p_dicts': p,
        })

    # ��ǰ��post������Ϊ�ϴ�word��dictʹ��
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
