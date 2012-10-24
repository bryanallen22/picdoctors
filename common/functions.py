
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse

from common.models import Batch

import logging
from datetime import datetime, timedelta
import urllib
import urlparse

import pdb
import pytz

def get_profile_or_None(request):
    """ Get the request user profile if they are logged in """
    if request.user.is_authenticated():
        return request.user.get_profile()
    return None
   
def get_time_string(prev_date):
    """
    Returns a user friendly string saying how long ago prev_date occurred.
    This is nice because formatting times to the various parts of the world
    is a recipe for disaster.

    The string should fit a sentence like this:
        Uploaded __________.
        
    Examples:
        21 minutes ago
        2 hours ago
        on 10 Oct 2012
    """
    # When comparing against db, we need tz aware utc time
    # I'm not sure what happened, this was working a week ago w/o it.
    # Did we change something?
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    yesterday = now - timedelta(days=1)
    hour_ago = now - timedelta(hours=1)

    # Created in the future? (Don't do this.)
    if prev_date > now:
        ret = "in the future, on %s" % (prev_date.isoformat(' '))
        logging.error("get_time_string() for obj in the future! %s" %
                      (prev_date.isoformat(' ')))
    # Created in the last hour?
    elif prev_date > hour_ago:
        delta = now - prev_date
        minutes = int(round(delta.seconds / 60.0)) 
        if minutes == 0:
            ret = "Less than a minute ago"
        elif minutes == 1:
            ret = "%s minute ago" % ( minutes )
        else:
            ret = "%s minutes ago" % ( minutes )

    # Created in the last day?
    elif prev_date > yesterday:
        delta = now - prev_date
        hours = int(round(delta.seconds / 3600.0)) 
        if hours == 1:
            ret = "%s hour ago" % ( hours )
        else:
            ret = "%s hours ago" % ( hours )

    # Created over a day ago
    else:
        ret = "on " + prev_date.strftime("%d %b %Y")

    return ret

def get_unfinished_batch(request):
    batch = None
    redirect_url = None
    try:
        batch = Batch.get_unfinished(request)
        if not batch:
            redirect_url = reverse('upload')
    except MultipleObjectsReturned:
        # Too many open unfinished batches. Resolve them.

        redirect_url = '%s?next=%s' % (reverse('merge_batches'),
                               urllib.quote( request.get_full_path() ));

    return (batch, redirect_url)