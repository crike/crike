
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *
from crike_django import views

from crike_django.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(home)?$', HomeView.as_view(), name='home'),
    url(r'^lesson$', LessonView.as_view(), name='lesson'),
    url(r'^exam$', ExamView.as_view(), name='exam'),
    # url(r'^crike_django/', include('crike_django.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^testdb/', views.testdb),
    url(r'^show/', views.show_words),
    url(r'^delete/', WordDeleteView.as_view(), name='delete_word'),
    url(r'^upload/', views.upload_file),
    url(r'^listen/', views.listen),
)
