from django.conf.urls.defaults import patterns, include, url

from job.views import index

urlpatterns = patterns('',
    url(r'^jobtmp/$',  index, name='index'), 
#   url(r'^job_doc/(?P<doc_id>\d+)/$',         markup_page,     name='markup'),
 #   url(r'^job_user/(?P<user_id>\d+)/$',       markups_handler, name='markups_handler'),
 #   url(r'^markups_handler/(?P<markup_id>\d+)$', markups_handler, name='markups_handler'),
 #   url(r'^pic_instruction_handler/$', pic_instruction_handler,   name='pic_instruction_handler'),
)

