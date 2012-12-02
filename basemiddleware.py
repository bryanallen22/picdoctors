from common.functions import get_profile_or_None
from common.functions import get_unfinished_album
from common.models import Album
import pdb

class BaseMiddleware(object):
    def process_request(self, request):

        profile = get_profile_or_None(request)
        album = None
        invalid_album_state = False

        try:
            album = Album.get_unfinished(request)
        except MultipleObjectsReturned:
            invalid_album_state = True

        if profile and not profile.is_doctor and not album:
            request.has_cart = True

            # multiple albums (throw up ?)
            if invalid_album_state:
                request.pic_count = "?"
            else:
                request.pic_count = 0

            return None

        elif not album or (profile and profile.is_doctor):
            request.has_cart = False
            return None

        else:
            request.has_cart = True 
            pic_count = 0

            if album:
                pic_count = album.get_picture_count()

            request.pic_count = pic_count

            return None

