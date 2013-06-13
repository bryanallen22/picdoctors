
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from annoying.functions import get_object_or_None

from common.models import Album

import logging; log = logging.getLogger('pd')
import urllib
import urlparse

from datetime import datetime, timedelta
import pytz
from django.utils.timezone import utc

import re
import os

import ipdb

def get_profile_or_None(request):
    """ Get the request user profile if they are logged in """
    if request.user.is_authenticated():
        return request.user
    return None

def get_datetime():
    return datetime.utcnow().replace(tzinfo=utc)

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
    now = get_datetime()
    yesterday = now - timedelta(days=1)
    hour_ago = now - timedelta(hours=1)

    # Created in the future? (Don't do this.)
    if prev_date > now:
        ret = "in the future, on %s" % (prev_date.isoformat(' '))
        log.error("get_time_string() for obj in the future! %s" %
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

def get_unfinished_album(request):
    album = None
    redirect_url = None
    try:
        album = Album.get_unfinished(request)
        if not album:
            redirect_url = reverse('upload')
    except MultipleObjectsReturned:
        # Too many open unfinished albums. Resolve them.

        redirect_url = '%s?next=%s' % (reverse('merge_albums'),
                               urllib.quote( request.get_full_path() ));

    return (album, redirect_url)


def get_referer_view_and_id(request, default=None):

    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    if referer[0] != request.META.get('HTTP_HOST'):
        return default

    if len(referer) > 2:
        return referer[1], referer[2]

    return default

def raise_error(request):
    """
    Raise an error immediately. Useful for debugging production environment.
    """
    raise Exception("You asked for it.")

