from django.conf.urls import patterns, include, url, handler404, handler500
from views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from common.errors import wheres_waldo_404
from views import privacy_policy, terms_of_service

from common.functions import raise_error
from django.conf.urls.static import static

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
    (r'', include('emailer.urls')),

    url(r'^500/$',                  oh_sob_500,            name='error500'),
    url(r'^404/$',                  wheres_waldo_404,      name='error404'),
    url(r'^raise/$',                raise_error,           name='raise_error'),
    url(r'^privacy_policy/$',       privacy_policy,        name='privacy_policy'),
    url(r'^terms_of_service/$',     terms_of_service,      name='terms_of_service'),
    url(r'^doc_terms_of_service/$', doc_terms_of_service,  name='doc_terms_of_service'),
    url(r'^dmca/$',                 dmca,                  name='dmca'),
) + static('/static/', document_root=settings.STATIC_ROOT)
