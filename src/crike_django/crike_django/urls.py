
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *
from crike_django import views
from crike_django import settings
from django.conf.urls.static import static

from crike_django.views import *

admin.autodiscover()

urlpatterns = patterns('',
# accounts management for administrators
    url(r'^$', TemplateView.as_view(template_name='registration/index.html'), name='index' ),
    url(r'^auth', TemplateView.as_view(template_name='registration/auth.html'), name='auth'),
    url(r'^home$', HomeView.as_view(), name='home'),
    url(r'^lesson$', LessonView.as_view(), name='lesson'),
    url(r'^exam$', ExamView.as_view(), name='exam'),
    url(r'^accounts/', include('registration.backends.default.urls')),

# resource management for teachers
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^show_all_words/', views.show_all_words),
    url(r'^delete/', WordDeleteView.as_view(), name='delete_word'),
    url(r'^upload/', views.upload_file),
    url(r'^media/audios/(?P<name>.*?)/?$', views.play_audio),
    url(r'^show/(?P<dic>.*?)/(?P<lesson>.*?)/?$', views.show_words),
    url(r'^show/', views.show_dicts, name='dict'),
    url(r'^delete_lesson/(?P<dic>.*?)/(?P<lesson>.*?)/?$', views.delete_lesson, name='delete_Lesson'),
    url(r'^delete_lesson_confirm/(?P<dic>.*?)/(?P<lesson>.*?)/?$', views.delete_lesson_confirm, name='delete_Lesson_confirm'),

# Study process for students
    url(r'^lesson_show/', LessonShowView.as_view(), name='lesson_show'),
    url(r'^lesson_pick/', LessonPickView.as_view(), name='lesson_pick'),
)#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
