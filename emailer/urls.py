from django.conf.urls import patterns, include, url

from emailer.views import debug_spam_emails

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^debug_spam_emails/$',        debug_spam_emails,       name='debug_spam_emails'),
)

