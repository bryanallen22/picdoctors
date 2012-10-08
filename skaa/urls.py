from django.conf.urls.defaults import patterns, include, url

from skaa.markupviews import markup_page, markup_page_batch, markups_handler, pic_instruction_handler
from skaa.uploadviews import upload_handler, delete_pic_handler, group_pic_handler, upload_page, need_cookies
from skaa.jobsviews import job_page, accept_doctors_work, reject_doctors_work
from skaa.setpriceviews import set_price
from skaa.mergebatchesviews import merge_batches

# Uncomment the next two lines to enable the admin:
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^markup/(?P<sequence>\d+)/$',                    markup_page,              name='markup'),
    url(r'^markup/(?P<batch_id>\d+)/(?P<sequence>\d+)/$',  markup_page_batch,        name='markup_batch'),
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
    url(r'^set_price/$',                                   set_price,                name='set_price'),
    url(r'^merge_batches/$',                               merge_batches,            name='merge_batches'),
    url(r'^accept_doctors_work/$',                         accept_doctors_work,      name='accept_doctors_work'),
    url(r'^reject_doctors_work/$',                         reject_doctors_work,      name='reject_doctors_work'),
)

