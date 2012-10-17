# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

from common.models import Batch
from common.models import Pic
from common.functions import get_profile_or_None
from common.functions import get_time_string
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from collections import namedtuple
import stripe

import pdb
import logging
from datetime import datetime

CarouselPic = namedtuple('CarouselPic', 'pic_url markup_url')

def generate_carousel_imgs(filter_batch):
    ret = []
    pics = Pic.objects.filter(batch=filter_batch)
    for pic in pics:
        # So, this is unlikely to happen, but I'm a perfectionist. If they skip the markup
        # page, pic.group will be None.
        if pic.group:
            markup_url = reverse('markup_batch', args=[filter_batch.id, pic.group.sequence])
        else:
            markup_url = reverse('markup')
        tup = CarouselPic(pic.get_thumb_url(), markup_url)
        ret.append(tup)
    return ret

# This user has two unfinished batches. Normally, that shouldn't
# be possible, but it can be done. Here's how:
#   1) User creates a batch, does not pay for it.
#   2) User comes back without signing in, creates a second batch
#      and then is asked to sign in to proceed.
# It's just a result of not making people sign in at the before
# doing anything. It's still worth it.
#
# Anyway. so now we gotta resolve these two batches into a single
# batch.
@login_required
@render_to('merge_batches.html')
def merge_batches(request):
    # Where do we send people who don't belong here?
    lost_person_redirect = '/'
    bad_post_value = False

    user_profile = get_profile_or_None(request)
    if not user_profile:
        return redirect( lost_person_redirect )

    batches = Batch.objects.filter(finished=False, userprofile=user_profile)
    if len(batches) < 2:
        # Don't have enough batches to merge... They shouldn't be here. This
        # page doesn't make sense for them. Send em away.
        return redirect( lost_person_redirect )
    elif len(batches) > 2:
        # Okay, how did that happen!? Let's just barf, shall we?
        raise MultipleObjectsReturned(
            "So %s has managed to get %s unfinished batches at once. Impressive."
            % (user_profile.user.username, len(batches)) );

    if batches[0].created < batches[1].created:
        older_batch = batches[0]
        newer_batch = batches[1]
    else:
        older_batch = batches[1]
        newer_batch = batches[0]
    
    if request.method== 'POST':
        # Actually merge or delete the older batch
        if 'delete' in request.POST.keys():
            # Time to delete all the pics in that batch
            # and the batch itself
            pics = Pic.objects.filter(batch=older_batch)
            for pic in pics:
                pic.delete()
            older_batch.delete()
        elif 'merge' in request.POST.keys():
            pics = Pic.objects.filter(batch=older_batch)
            for pic in pics:
                pic.batch = newer_batch
                pic.save()
            older_batch.delete()
            newer_batch.kick_groups_modified()
        else:
            # Treat this 'POST' like a 'GET'
            bad_post_value = True

        if request.GET['next']:
            return redirect( request.GET['next'] )
        else:
            # No idea where to send them. Send them to upload page?
            logging.error("Merge doesn't know where to redirect! %s %s" %  \
                          (request.method, request.build_absolute_uri()))
            return redirect( reverse('upload') )

    elif request.method == 'GET' or bad_post_value:

        oldpic_thumbs = generate_carousel_imgs(older_batch)
        older_date_str = get_time_string(older_batch.created)
        return {
                   'older_date_str' :  older_date_str,
                   'oldpic_thumbs'  :  oldpic_thumbs,
               }

