
from django.views.generic import *
from django.http import *

from crike_django.models import *

class DictView(TemplateView):
    template_name = 'crike_django/dict_view.html'

class StudentView(TemplateView):
    template_name = 'crike_django/student_view.html'

class TeacherView(TemplateView):
    template_name = 'crike_django/teacher_view.html'

def home():
    return HttpResponse("Hello world")
