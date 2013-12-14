
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='crike_django/home.html'), name='home'),
    # url(r'^crike_django/', include('crike_django.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
