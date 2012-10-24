from django.conf.urls.defaults import patterns, include, url
from picdoctors.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$', index),

    # Let these handle their own views:
    (r'', include('skaa.urls')),
    (r'', include('doctor.urls')),
    (r'', include('common.urls')),
    (r'', include('messaging.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() # development only!

