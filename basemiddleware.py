from common.functions import get_profile_or_None
from common.functions import get_unfinished_album
from common.models import Album
from notifications.models import Notification
from django.core.exceptions import MultipleObjectsReturned

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

        request.notifications = Notification.GetRecentNotifications(profile, 5)

        return None

