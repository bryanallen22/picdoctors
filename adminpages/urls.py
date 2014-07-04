from django.conf.urls import patterns, url

from adminpages.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^loginas/$',
        loginas,
        name='loginas'),
)

