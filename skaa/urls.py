from django.conf.urls.defaults import patterns, include, url

from skaa.markupviews import markup_page, markups_handler, pic_instruction_handler
from skaa.uploadviews import upload_handler, delete_pic_handler, group_pic_handler, upload_page, need_cookies
from skaa.jobviews import index, generate_job
# Uncomment the next two lines to enable the admin:
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^markup/(?P<sequence>\d+)/$',         markup_page,     name='markup'),
    url(r'^markups_handler/$',                  markups_handler, name='markups_handler'),
    url(r'^markups_handler/(?P<markup_id>\d+)$', markups_handler, name='markups_handler'),
    url(r'^pic_instruction_handler/$', pic_instruction_handler,   name='pic_instruction_handler'),
   
    url(r'^upload/$', upload_page, name='upload'),
    
    # if you change this, you had better modify the 'url' param in upload-application.js to match it
    url(r'^upload_handler/$', upload_handler, name='upload_handler'),
    # For grouping images
    url(r'^delete_pic_handler/$', delete_pic_handler, name='delete_pic_handler'),
    url(r'^group_pic_handler/$',  group_pic_handler,  name='group_pic_handler'),
    url(r'^need_cookies/$',       need_cookies,       name='need_cookies'),
    url(r'^job/$',                 index,              name='index'),
    url(r'^fake_job_creator/$',    generate_job,   name='generate_job'),

)

