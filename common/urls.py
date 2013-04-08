from django.conf.urls import patterns, include, url

from common.signinviews import skaa_signin, doc_signin, signout
from common.resetpasswordviews import reset_password
from common.albumviews import album, approve_album, make_album_shareable
from common.feedbackviews import feedback
from common.album_approvalviews import album_approval_page
from common.faqviews import faq
from common.howitworksviews import howitworks
from common.account_settings_views import account_settings, account_settings_delete_card
from common.account_settings_views import change_password, change_email
from common.account_settings_views import update_roles
from common.permissionfunctions import permission_denied

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^signin/$',                           skaa_signin,                  name='skaa_signin'),
    url(r'^doc_signin/$',                       doc_signin,                   name='doc_signin'),
    url(r'^signout/$',                          signout,                      name='signout'),
    url(r'^reset_password/$',                   reset_password,               name='reset_password'),
    url(r'^album/(?P<album_id>\d+)$',           album,                        name='album'),
    url(r'^approve_album/$',                    approve_album,                name='approve_album'),
    url(r'^feedback/$',                         feedback,                     name='feedback'),
    url(r'^album_approval_page/$',              album_approval_page,          name='album_approval_page'),
    url(r'^album_approval_page/(?P<page>\d+)$', album_approval_page,          name='album_approval_page_with_page'),
    url(r'^account_settings/$',                 account_settings,             name='account_settings'),
    url(r'^account_settings_delete_card/$',     account_settings_delete_card, name='account_settings_delete_card'),
    url(r'^faq/$',                              faq,                          name='faq'),
    url(r'^howitworks/$',                       howitworks,                   name='howitworks'),
    url(r'^change_password/$',                  change_password,              name='change_password'),
    url(r'^change_email/$',                     change_email,                 name='change_email'),
    url(r'^update_roles/$',                     update_roles,                 name='update_roles'),
    url(r'^make_album_shareable/$',             make_album_shareable,         name='make_album_shareable'),
    url(r'^permission_denied/$',                permission_denied,            name='permission_denied'),
)

