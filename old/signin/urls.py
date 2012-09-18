from django.conf.urls.defaults import patterns, include, url

from signin.views import signin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^signin/$',     signin,     name='signin'),
)

