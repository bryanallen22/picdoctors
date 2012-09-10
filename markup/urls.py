from django.conf.urls.defaults import patterns, include, url

from markup.views import markup_page, create_markup, markups_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^markup/(?P<group_id>\d+)/$',          markup_page,     name='markup'),
    url(r'^markups_handler/$',                   create_markup,   name='create_markup'),
    url(r'^markups_handler/(?P<group_id>\d+)$', markups_handler, name='markups_handler'),
)

