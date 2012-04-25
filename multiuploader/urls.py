from django.conf.urls.defaults import patterns, include, url

from multiuploader.views import upload_handler
from multiuploader.views import upload_page

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^upload/$', upload_page, name='upload'),
    
    # if you change this, you had better modify the 'url' param in upload-application.js to match it
    url(r'^upload_handler/$', upload_handler, name='upload_handler'),
)

