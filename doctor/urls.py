from django.conf.urls.defaults import patterns, include, url

from doctor.jobsviews import doc_job_page, new_job_page, apply_for_job
from skaa.uploadviews import doc_upload_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
#    url(r'^markup/(?P<group_id>\d+)/$',         markup_page,     name='markup'),
#    url(r'^markups_handler/$',                  markups_handler, name='markups_handler'),
#    url(r'^markups_handler/(?P<markup_id>\d+)$', markups_handler, name='markups_handler'),
#    url(r'^pic_instruction_handler/$', pic_instruction_handler,   name='pic_instruction_handler'),
    url(r'^doc_jobs/$',                 doc_job_page,              name='doc_job_page'),
    url(r'^doc_jobs/(?P<page>\d+)$',    doc_job_page,              name='doc_job_page_with_page'),
    url(r'^new_jobs/$',                 new_job_page,              name='new_job_page'),
    url(r'^new_jobs/(?P<page>\d+)$',    new_job_page,              name='new_job_page_with_page'),
    url(r'^apply_for_job$',             apply_for_job,             name='apply_for_job'),
    url(r'^doc_upload_handler/$',       doc_upload_handler,        name='doc_upload_handler'),
)

