# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

from common.models import Batch
from common.functions import get_profile_or_None

import stripe

import pdb
import logging

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

    return {}

