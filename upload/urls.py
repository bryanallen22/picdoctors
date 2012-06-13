from django.conf.urls.defaults import patterns, include, url

from upload.views import upload_handler
from upload.views import delete_handler
from upload.views import group_handler
from upload.views import upload_page
from upload.views import need_cookies

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^upload/$', upload_page, name='upload'),
    
    # if you change this, you had better modify the 'url' param in upload-application.js to match it
    url(r'^upload_handler/$', upload_handler, name='upload_handler'),
    # For grouping images
    url(r'^delete_handler/$', delete_handler, name='delete_handler'),
    url(r'^group_handler/$',  group_handler,  name='group_handler'),
    url(r'^needcookies/$',    need_cookies,   name='need_cookies'),
)

