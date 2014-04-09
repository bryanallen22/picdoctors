from django.conf.urls import patterns, include, url

from messaging.messageviews import contact, message_handler
# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    #url(r'^contact/(?P<job_id>\d+)$',           contact,            name='contact'),
    url(r'^message_handler/$',                  message_handler,    name='message_handler'),
)

