# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

from common.models import Album
from common.models import Pic
from common.functions import get_profile_or_None
from common.functions import get_time_string
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from collections import namedtuple

import ipdb
import logging
from datetime import datetime

CarouselPic = namedtuple('CarouselPic', 'pic_url markup_url')

def generate_carousel_imgs(filter_album):
    ret = []
    pics = Pic.objects.filter(album=filter_album)
    for pic in pics:
        # So, this is unlikely to happen, but I'm a perfectionist. If they skip the markup
        # page, pic.group will be None.
        if pic.group:
            markup_url = reverse('markup_album', args=[filter_album.id, pic.group.sequence])
        else:
            markup_url = reverse('markup')
        tup = CarouselPic(pic.get_thumb_url(), markup_url)
        ret.append(tup)
    return ret

# This user has two unfinished albums. Normally, that shouldn't
# be possible, but it can be done. Here's how:
#   1) User creates a album, does not pay for it.
#   2) User comes back without signing in, creates a second album
#      and then is asked to sign in to proceed.
# It's just a result of not making people sign in at the before
# doing anything. It's still worth it.
#
# Anyway. so now we gotta resolve these two albums into a single
# album.
@login_required
@render_to('merge_albums.html')
def merge_albums(request):
    # Where do we send people who don't belong here?
    lost_person_redirect = '/'
    bad_post_value = False

    user_profile = get_profile_or_None(request)
    if not user_profile:
        return redirect( lost_person_redirect )

    albums = Album.objects.filter(finished=False, userprofile=user_profile)
    if len(albums) < 2:
        # Don't have enough albums to merge... They shouldn't be here. This
        # page doesn't make sense for them. Send em away.
        return redirect( lost_person_redirect )
    elif len(albums) > 2:
        # Okay, how did that happen!? Let's just barf, shall we?
        raise MultipleObjectsReturned(
            "So %s has managed to get %s unfinished albums at once. Impressive."
            % (user_profile.user.username, len(albums)) );

    if albums[0].created < albums[1].created:
        older_album = albums[0]
        newer_album = albums[1]
    else:
        older_album = albums[1]
        newer_album = albums[0]
    
    if request.method== 'POST':
        # Actually merge or delete the older album
        if 'delete' in request.POST.keys():
            # Time to delete all the pics in that album
            # and the album itself
            pics = Pic.objects.filter(album=older_album)
            for pic in pics:
                pic.delete()
            older_album.delete()
        elif 'merge' in request.POST.keys():
            pics = Pic.objects.filter(album=older_album)
            for pic in pics:
                pic.album = newer_album
                pic.save()
            older_album.delete()
            newer_album.kick_groups_modified()
        else:
            # Treat this 'POST' like a 'GET'
            bad_post_value = True

        if 'next' in request.GET:
            return redirect( request.GET['next'] )
        else:
            # No idea where to send them. Send them to upload page?
            logging.error("Merge doesn't know where to redirect! %s %s" %  \
                          (request.method, request.build_absolute_uri()))
            return redirect( reverse('upload') )

    elif request.method == 'GET' or bad_post_value:

        oldpic_thumbs = generate_carousel_imgs(older_album)
        older_date_str = get_time_string(older_album.created)
        return {
                   'older_date_str' :  older_date_str,
                   'oldpic_thumbs'  :  oldpic_thumbs,
               }

