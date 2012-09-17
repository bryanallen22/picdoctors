from django.conf.urls.defaults import patterns, include, url

from skaa.markupviews import markup_page, markups_handler, pic_instruction_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
#    url(r'^markup/(?P<group_id>\d+)/$',         markup_page,     name='markup'),
#    url(r'^markups_handler/$',                  markups_handler, name='markups_handler'),
#    url(r'^markups_handler/(?P<markup_id>\d+)$', markups_handler, name='markups_handler'),
#    url(r'^pic_instruction_handler/$', pic_instruction_handler,   name='pic_instruction_handler'),
)

