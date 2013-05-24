from annoying.decorators import ajax_request
from skaa.uploadviews import pic_json

@ajax_request
def async_album_info(request):
    try:
        album = Album.get_unfinished(request)
    except MultipleObjectsReturned:
        return {}

    pic_array = []
    pics = Pic.objects.filter(album=album)

    for pic in pics:
        pic_array.append(pic_json(pic))

    return {
        'pics' : pics,
        'url'  : reverse( 'upload' ),
    }

