from django.conf.urls import patterns, include, url, handler404, handler500
from views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from common.errors import wheres_waldo_404

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


handler404 = 'views.wheres_waldo_404'
handler500 = 'views.oh_sob_500'

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
    (r'', include('notifications.urls')),
    

    url(r'^500/$',    oh_sob_500,     name='error500'),
    url(r'^404/$',    wheres_waldo_404,     name='error404'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() # development only!

