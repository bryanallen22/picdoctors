from django.conf.urls.defaults import patterns, include, url

from markup.views import markup_page

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^markup/$', markup_page, name='markup'),
)

