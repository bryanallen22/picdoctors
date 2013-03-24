from django.conf.urls import patterns, include, url

from notifications.views import notification_redirecter, notification_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^notification/(?P<notification_id>\d+)$',   notification_redirecter,    name='notification_redirecter'),
    url(r'^notification_handler/$',                   notification_handler,       name='notification_handler'),
)

