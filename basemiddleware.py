from common.functions import get_profile_or_None
from common.functions import get_unfinished_album
from common.models import Album
from notifications.models import Notification
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
import settings

import ipdb

class BaseMiddleware(object):
    def process_request(self, request):

        profile = get_profile_or_None(request)
        album = None
        invalid_album_state = False

        try:
            album = Album.get_unfinished(request)
        except MultipleObjectsReturned:
            invalid_album_state = True

        skaa = True if not profile else profile.isa('skaa')

        request.has_cart = False
        if (skaa and                     # has to be a skaa
            not invalid_album_state and  # just 1 album, don't need to merge
            album):                      # has to be an album
            request.has_cart = True
            request.pic_count = album.get_picture_count()
            request.async_album_info_url = reverse( 'async_album_info' )


        request.notifications = Notification.GetRecentNotifications(profile, 8)
        request.new_notification_cnt = len([n for n in request.notifications if n.viewed == False])

        request.IS_PRODUCTION = settings.IS_PRODUCTION
        request.DEPLOY_TYPE = settings.DEPLOY_TYPE
        request.PRODUCTION_TESTING = settings.PRODUCTION_TESTING if hasattr(settings, 'PRODUCTION_TESTING') else False
        request.SITE_URL = settings.SITE_URL
        request.STRIPE_CLIENT_ID = settings.STRIPE_CLIENT_ID
        return None

