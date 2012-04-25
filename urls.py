from django.conf.urls.defaults import patterns, include, url
from picdoctors.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'picdoctors.views.home', name='home'),
    # url(r'^picdoctors/', include('picdoctors.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # Clockstone template pages -- keep 'em the same name to be consistent with the internal links
    url(r'^$', index),
    url(r'^markup$', markup),

    # Let upload stuff handle it's own views:
    (r'', include('multiuploader.urls')),

)

urlpatterns += staticfiles_urlpatterns() # development only!

