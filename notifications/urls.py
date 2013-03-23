from django.conf.urls.defaults import patterns, include, url

from notifications.views import notification_redirecter

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^notification/(?P<notification_id>\d+)$',   notification_redirecter,    name='notification_redirecter'),
)

