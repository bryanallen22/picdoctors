from django.conf.urls.defaults import patterns, include, url

from common.signinviews import skaa_signin, doc_signin, signout
from common.contactviews import contact, message_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^signin/$',                           skaa_signin,        name='skaa_signin'),
    url(r'^doc_signin/$',                       doc_signin,         name='doc_signin'),
    url(r'^signout/$',                          signout,            name='signout'),
    url(r'^contact/(?P<job_id>\d+)$',           contact,            name='contact'),
    url(r'^message_handler/$',                  message_handler,    name='message_handler'),
)

