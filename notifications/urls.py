from django.conf.urls import patterns, include, url

from notifications.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^notification/(?P<notification_id>\d+)$',   notification_redirecter,    name='notification_redirecter'),
    url(r'^notification_handler/$',                   notification_handler,       name='notification_handler'),
    url(r'^clear_notifications/(?P<notification_id>\d+)$',   clear_notifications, name='clear_notifications'),
)

