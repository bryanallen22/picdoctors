from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse

from annoying.decorators import ajax_request

from common.models import Pic, Album

# No require_login_as because the cart is valid
# for people who haven't even logged in.
@ajax_request
def async_album_info(request):
    try:
        album = Album.get_unfinished(request)
    except MultipleObjectsReturned:
        return {}

    pic_array = []
    pics = Pic.objects.filter(album=album)

    thumb_json = lambda pic: { 'name' : pic.title, 'thumbnail_url' : pic.get_thumb_url() }
    pic_array = [ thumb_json(pic) for pic in pics ]

    return {
        'pics' : pic_array,
        'url'  : reverse( 'upload' ),
    }

