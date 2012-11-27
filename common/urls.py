from django.conf.urls.defaults import patterns, include, url

from common.signinviews import skaa_signin, doc_signin, signout
from common.resetpasswordviews import reset_password
from common.albumviews import album, approve_album
from common.feedbackviews import feedback
from common.album_approvalviews import album_approval_page
from common.functions import go_pro

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^signin/$',                           skaa_signin,                name='skaa_signin'),
    url(r'^doc_signin/$',                       doc_signin,                 name='doc_signin'),
    url(r'^signout/$',                          signout,                    name='signout'),
    url(r'^reset_password/$',                   reset_password,             name='reset_password'),
    url(r'^album/(?P<album_id>\d+)$',           album,                      name='album'),
    url(r'^approve_album/$',                    approve_album,              name='approve_album'),
    url(r'^feedback/$',                         feedback,                   name='feedback'),
    url(r'^album_approval_page/$',              album_approval_page,        name='album_approval_page'),
    url(r'^album_approval_page/(?P<page>\d+)$', album_approval_page,        name='album_approval_page_with_page'),
    url(r'^go_pro/$',                           go_pro,                     name='go_pro'),
)

