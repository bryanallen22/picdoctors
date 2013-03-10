from django.conf.urls.defaults import patterns, include, url

from skaa.markupviews import markup_page, markup_page_album, markups_handler, pic_instruction_handler
from skaa.uploadviews import upload_handler, delete_pic_handler, group_pic_handler, upload_page, need_cookies
from skaa.jobsviews import job_page, reject_doctors_work, request_modification
from skaa.setpriceviews import set_price, increase_price, create_hold_handler
from skaa.mergealbumsviews import merge_albums
from skaa.accept_workviews import accept_work
from skaa.rejectviews import refund, switch_doctor, switch_doctor_endpoint, refund_user_endpoint
from skaa.account_settings_views import become_a_pic_doctor

# Uncomment the next two lines to enable the admin:
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^markup/(?P<sequence>\d+)/$',                    markup_page,              name='markup'),
    url(r'^markup/(?P<album_id>\d+)/(?P<sequence>\d+)/$',  markup_page_album,        name='markup_album'),
    url(r'^markups_handler/$',                             markups_handler,          name='markups_handler'),
    url(r'^markups_handler/(?P<markup_id>\d+)$',           markups_handler,          name='markups_handler'),
    url(r'^pic_instruction_handler/$',                     pic_instruction_handler,  name='pic_instruction_handler'),

    url(r'^upload/$',                                      upload_page,              name='upload'),

    # if you change this, you had better modify the 'url' param in upload-application.js to match it
    url(r'^upload_handler/$',                              upload_handler,           name='upload_handler'),
    url(r'^delete_pic_handler/$',                          delete_pic_handler,       name='delete_pic_handler'),
    url(r'^group_pic_handler/$',                           group_pic_handler,        name='group_pic_handler'),
    url(r'^need_cookies/$',                                need_cookies,             name='need_cookies'),
    url(r'^jobs/$',                                        job_page,                 name='job_page'),
    url(r'^jobs/(?P<page>\d+)$',                           job_page,                 name='job_page_with_page'),
    url(r'^jobs/(?P<page>\d+)/(?P<job_id>\d+)/$',          job_page,                 name='job_page_with_page_and_id'),
    url(r'^set_price/$',                                   set_price,                name='set_price'),
    url(r'^increase_price/(?P<job_id>\d+)$',               increase_price,           name='increase_price'),
    url(r'^create_hold_handler/$',                         create_hold_handler,      name='create_hold_handler'),
    url(r'^merge_albums/$',                                merge_albums,             name='merge_albums'),
    url(r'^accept_work/(?P<job_id>\d+)$',                  accept_work,              name='accept_work'),
    url(r'^request_modification/$',                        request_modification,     name='request_modification'),
    url(r'^refund/(?P<job_id>\d+)$',                       refund,                   name='refund'),
    url(r'^switch_doctor/(?P<job_id>\d+)$',                switch_doctor,            name='switch_doctor'),
    url(r'^refund_user/$',                                 refund_user_endpoint,     name='refund_user_endpoint'),
    url(r'^switch_doctor/$',                               switch_doctor_endpoint,   name='switch_doctor_endpoint'),
    url(r'^become_a_pic_doctor/$',                         become_a_pic_doctor,      name='become_a_pic_doctor'),
)

