from common.functions import get_profile_or_None
from common.functions import get_unfinished_album
from common.models import Album
from notifications.models import Notification
from django.core.exceptions import MultipleObjectsReturned
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
        
        if not skaa:
            request.has_cart = False
        else:
            request.has_cart = True

            # multiple albums (throw up ?)
            if invalid_album_state:
                request.pic_count = "?"
            elif album:
                request.pic_count = album.get_picture_count()
            else:
                request.pic_count = 0

        request.notifications = Notification.GetRecentNotifications(profile, 8)
        request.new_notification_cnt = len([n for n in request.notifications if n.viewed == False])

        request.IS_PRODUCTION = settings.IS_PRODUCTION
        request.deploy_type = settings.DEPLOY_TYPE
        request.PRODUCTION_TESTING = settings.PRODUCTION_TESTING if hasattr(settings, 'PRODUCTION_TESTING') else False

        return None

