
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *

from crike_django.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    # url(r'^crike_django/', include('crike_django.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
