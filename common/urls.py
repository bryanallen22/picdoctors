from django.conf.urls import patterns, include, url

from common.signinviews import skaa_signin, doc_signin, signout, check_unique_nickname
from common.resetpasswordviews import reset_password
from common.albumviews import album, approve_album
from common.feedbackviews import feedback
from common.album_approvalviews import album_approval_page
from common.howitworksviews import howitworks
from common.permissionfunctions import permission_denied
from common.navbarviews import async_album_info
from common.ember_album_endpoints import *
from common.ember_profile_endpoints import *
from common.alive_endpoints import *
from common.ember_home import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^signin/$',                                   skaa_signin,                  name='skaa_signin'),
    url(r'^doc_signin/$',                               doc_signin,                   name='doc_signin'),
    url(r'^signout/$',                                  signout,                      name='signout'),
    url(r'^reset_password/$',                           reset_password,               name='reset_password'),
    url(r'^album/(?P<album_id>\d+)$',                   album,                        name='album'),
    url(r'^approve_album/$',                            approve_album,                name='approve_album'),
    url(r'^feedback/$',                                 feedback,                     name='feedback'),
    url(r'^album_approval_page/$',                      album_approval_page,          name='album_approval_page'),
    url(r'^album_approval_page/(?P<page>\d+)$',         album_approval_page,          name='album_approval_page_with_page'),
    url(r'^howitworks/$',                               howitworks,                   name='howitworks'),
    url(r'^check_unique_nickname/$',                    check_unique_nickname,        name='check_unique_nickname'),
    url(r'^permission_denied/$',                        permission_denied,            name='permission_denied'),
    url(r'^async_album_info/$',                         async_album_info,             name='async_album_info'),

    # Ember single page app
    url(r'^home/$',                                     home,                         name='home'),

    # Ember restendpoints
    url(r'^api/users/(?P<user_id>-?\d+)$',              users_endpoint,               name='users_endpoint'),
    url(r'^api/albums/(?P<album_id>\d+)$',              albums_endpoint,              name='albums_endpoint'),
    url(r'^api/markups$',                               markups_endpoint,             name='markups_endpoint'),
    url(r'^api/markups/(?P<markup_id>\d+)$',            markups_endpoint,             name='markups_endpoint'),
    url(r'^api/pics/(?P<pic_id>\d+)$',                  pics_endpoint,                name='pics_endpoint'),
    url(r'^api/messages$',                              messages_endpoint,            name='messages_endpoint'),
    url(r'^api/emailConfigs/(?P<user_id>\d+)$',         email_config_endpoint,        name='email_config_endpoint'),
    url(r'^api/roles/(?P<role_id>\d+)$',                remove_role,                  name='remove_role'),
    url(r'^api/roles$',                                 add_role,                     name='add_role'),
    url(r'^api/hookup_stripe$',                         hookup_stripe,                name='hookup_stripe'),
    url(r'^api/SkaaLiveOn$',                            skaa_live_on,                 name='skaa_live_on'),
    url(r'^api/creditcards$',                           creditcards,                  name='creditcards'),
    url(r'^api/creditcards/(?P<card_id>.+)$',           creditcards,                  name='creditcards'),
    url(r'^change_password/$',                          change_password,              name='change_password'),
)

