from django.conf.urls.defaults import patterns, include, url
from picdoctors.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'picdoctors.views.home', name='home'),
    # url(r'^picdoctors/', include('picdoctors.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # Clockstone template pages -- keep 'em the same name to be consistent with the internal links
    url(r'^$', index),

    # Let these handle their own views:
    (r'', include('upload.urls')),
    (r'', include('markup.urls')),
    (r'', include('signin.urls')),
    (r'', include('job.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() # development only!

