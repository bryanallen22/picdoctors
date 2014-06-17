from django.conf.urls import patterns, include, url

from landings.views import *

urlpatterns = patterns('',
    url(r'^photo-retouching/$',
        landing_general_retouching,
        name='landing_general_retouching'),

    url(r'^photo-restoration/$',
        landing_photo_restoration,
        name='landing_photo_restoration'),

    url(r'^bridal-photo-retouching/$',
        landing_bridal_photo_retouching,
        name='landing_bridal_photo_retouching'),

    url(r'^wedding-retouching/$',
        landing_wedding_retouching,
        name='landing_wedding_retouching'),

    url(r'^family-photo-retouching/$',
        landing_family_photo_retouching,
        name='landing_family_photo_retouching'),
)

