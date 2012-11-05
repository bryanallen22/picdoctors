from django.conf.urls.defaults import patterns, include, url

from messaging.messageviews import message, message_handler
# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    url(r'^message/(?P<job_id>\d+)$',           message,            name='message'),
    url(r'^message_handler/$',                  message_handler,    name='message_handler'),
)

