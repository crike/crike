
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView


from registration.forms import RegistrationFormTermsOfService
from registration.backends.default.views import RegistrationView


from crike_django import views
from crike_django import settings
from crike_django.views import *
from crike_django.forms import *


admin.autodiscover()

#TODO rename all url names and addresses
urlpatterns = patterns('',
# accounts management for administrators
    url(r'^$', HomeView.as_view(), name='index' ),
    url(r'^auth', TemplateView.as_view(template_name='registration/auth.html'), name='auth'),
    url(r'^home$', HomeView.as_view(), name='home'), #TODO need read current user's learning process info
    url(r'^study$', BookStudyView.as_view(), name='study'),
    url(r'^exam$', ExamView.as_view(), name='exam'),
    url(r'^accounts/register/$',
          RegistrationView.as_view(form_class=CrikeRegistrationForm),
          name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),

    # This is an interim implement to redirect when registration complete.
    url(r'^users/(?P<username>.*)/?$', RedirectView.as_view(url=reverse_lazy('index'))),

# resource management for teachers
    url(r'^admin/(?P<book>.*?)/(?P<lesson>.*?)/?$', LessonAdminView.as_view()),
    url(r'^admin/books/', BooksAdminView.as_view(), name='books'),
    url(r'^admin/words/', WordsAdminView.as_view(), name='words'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^delete/', WordDeleteView.as_view(), name='delete_word'),
    url(r'^media/audios/(?P<name>.*?)/?$', views.play_audio),

# Study process for students
    url(r'^study/(?P<book>.*?)/(?P<lesson>.*?)/show/?$', LessonShowView.as_view(), name='lesson_show_view'),
    url(r'^study/(?P<book>.*?)/(?P<lesson>.*?)/pick/?$', LessonPickView.as_view(), name='lesson_pick_view'),
    url(r'^study/(?P<book>.*?)/(?P<lesson>.*?)/fill/?$', LessonFillView.as_view(), name='lesson_fill_view'),
    url(r'^study/(?P<book>.*?)/(?P<lesson>.*?)/dictation/?$', LessonDictationView.as_view(), name='lesson_dictation_view'),
    url(r'^study/(?P<book>.*?)/?$', BookStudyView.as_view(), name='book_study_view'),
)#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
