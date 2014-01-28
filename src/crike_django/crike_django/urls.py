
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required


from registration.forms import RegistrationFormTermsOfService
from registration.backends.simple.views import RegistrationView


from crike_django import views
from crike_django import settings
from crike_django.views import *
from crike_django.forms import *


admin.autodiscover()

#TODO rename all url names and addresses
urlpatterns = patterns('',
# accounts management for administrators
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^auth', TemplateView.as_view(template_name='registration/auth.html'), name='auth'),
    url(r'^home$', HomeView.as_view(), name='home'), #TODO need read current user's learning process info
    url(r'^study$', BooksStudyView.as_view(), name='study'),#TODO need get exam unit from user's info
    url(r'^exam/book/(?P<book>.*?)/unit/(?P<unit>.*?)/?$', ExamView.as_view(), name='exam'),
    url(r'^accounts/register/$',
          RegistrationView.as_view(form_class=CrikeRegistrationForm),
          name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^student$', StudentView.as_view(), name='student'),
    url(r'^teacher$', TeacherView.as_view(), name='teacher'),
    url(r'^word/stat$', login_required(WordStatView.as_view()), name='word_stat'),
    url(r'^user/history$', login_required(UserHistoryView.as_view()), name='user_history'),
    url(r'^admin/students/?$', StudentsAdminView.as_view(), name='students_admin'),

    # This is an interim implement to redirect when registration complete.
    url(r'^users/(?P<username>.*)/?$', RedirectView.as_view(url=reverse_lazy('index'))),

# resource management for teachers
    url(r'^admin/books/', BooksAdminView.as_view(), name='books'),
    url(r'^admin/words/', WordsAdminView.as_view(), name='words'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^delete/', WordDeleteView.as_view(), name='delete_word'),
    url(r'^media/audios/(?P<name>.*?)/?$', views.play_audio),
    url(r'^media/images/(?P<name>.*?)/(?P<num>.*?)/?$', views.show_image),
    url(r'^admin/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/word/(?P<word>.*?)/?$', views.retrieve_word),
    url(r'^admin/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/?$', LessonAdminView.as_view()),

# Study process for students
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/show/?$', login_required(LessonShowView.as_view()), name='lesson_show_view'),
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/pick/?$', login_required(LessonPickView.as_view()), name='lesson_pick_view'),
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/fill/?$', login_required(LessonFillView.as_view()), name='lesson_fill_view'),
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/dictation/?$', login_required(LessonDictationView.as_view()), name='lesson_dictation_view'),
    url(r'^study/books/$', BooksStudyView.as_view(), name='books_study_view'),
)#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
